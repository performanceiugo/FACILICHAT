# Refresh token opaco com rotação e detecção de reuso por família (item S15 do plano).
#
# Formato entregue ao cliente: "{ID}.{segredo}". O `ID` é a chave primária (lookup indexado,
# O(1)); só o hash sha256 do segredo fica no banco — o mesmo espírito de uma senha: mesmo com um
# vazamento do banco, ninguém recupera o valor original para se passar pelo usuário.
#
# Rotação: cada uso troca o token por um novo (mesma família, `FamiliaID` constante desde o
# login). Reuso de um token já trocado é sinal de furto/replay — nesse caso a família INTEIRA é
# revogada, não só o token usado, para não deixar uma cópia roubada continuar valendo em paralelo.

import hashlib
import secrets
import uuid
from datetime import timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuracoes import configuracoes
from app.modelos.RefreshToken import RefreshToken
from app.tempo import agoraUtc


# Levantada para QUALQUER motivo de rejeição (malformado, inexistente, expirado, já revogado) —
# a rota trata todos os casos da mesma forma: 401 + forçar novo login.
class RefreshInvalido(Exception):
    pass


def _hashSegredo(segredo: str) -> str:
    return hashlib.sha256(segredo.encode("utf-8")).hexdigest()


def _dividirValor(valor: str) -> tuple[uuid.UUID, str]:
    try:
        idBruto, segredo = valor.split(".", 1)
        return uuid.UUID(idBruto), segredo
    except ValueError:
        raise RefreshInvalido("Formato de refresh token inválido")


# Cria um elo de família (o primeiro, no login, ou o próximo, numa rotação) e devolve o valor
# opaco a entregar ao cliente. Antes de inserir, limpa entradas já vencidas — mesma estratégia
# "sem Redis" da denylist do S14 (ver `servicos/revogacao.py`): sem TTL automático, a limpeza
# acontece "na unha" a cada novo registro.
async def _criarToken(db: AsyncSession, usuarioID: uuid.UUID, empresaID: uuid.UUID, familiaID: uuid.UUID) -> str:
    await db.execute(delete(RefreshToken).where(RefreshToken.ExpiraEm < agoraUtc()))

    id_ = uuid.uuid4()
    segredo = secrets.token_urlsafe(32)
    agora = agoraUtc()
    db.add(RefreshToken(
        ID=id_,
        SegredoHash=_hashSegredo(segredo),
        FamiliaID=familiaID,
        UsuarioID=usuarioID,
        EmpresaID=empresaID,
        CriadoEm=agora,
        ExpiraEm=agora + timedelta(days=configuracoes.REFRESH_TOKEN_EXPIRE_DIAS),
    ))
    await db.commit()
    return f"{id_}.{segredo}"


# Chamada no login: abre uma família nova para a sessão que está começando.
async def criarFamiliaRefresh(db: AsyncSession, usuarioID: uuid.UUID, empresaID: uuid.UUID) -> str:
    return await _criarToken(db, usuarioID, empresaID, familiaID=uuid.uuid4())


# Núcleo de POST /autenticacao/atualizar: valida o token recebido, detecta reuso e devolve o
# próximo elo da família + a quem ele pertence, para a rota montar o novo access token.
async def rotacionar(db: AsyncSession, valorRecebido: str) -> tuple[str, uuid.UUID, uuid.UUID]:
    id_, segredo = _dividirValor(valorRecebido)

    resultado = await db.execute(select(RefreshToken).where(RefreshToken.ID == id_))
    registro = resultado.scalar_one_or_none()
    if not registro or registro.SegredoHash != _hashSegredo(segredo):
        raise RefreshInvalido("Refresh token não encontrado")

    if registro.ExpiraEm < agoraUtc():
        raise RefreshInvalido("Refresh token expirado")

    if registro.RevogadoEm is not None:
        await revogarFamilia(db, registro.FamiliaID)
        raise RefreshInvalido("Refresh token reutilizado — sessão revogada por segurança")

    registro.RevogadoEm = agoraUtc()
    await db.flush()  # garante que a revogação acima é vista antes do DELETE de vencidos em _criarToken
    novoValor = await _criarToken(db, registro.UsuarioID, registro.EmpresaID, registro.FamiliaID)
    return novoValor, registro.UsuarioID, registro.EmpresaID


# Revoga TODOS os tokens ainda válidos de uma família — usada no reuso detectado acima e no
# logout (que precisa encerrar a família inteira, não só o token que estava na mão do cliente).
async def revogarFamilia(db: AsyncSession, familiaID: uuid.UUID) -> None:
    agora = agoraUtc()
    resultado = await db.execute(
        select(RefreshToken).where(RefreshToken.FamiliaID == familiaID, RefreshToken.RevogadoEm.is_(None))
    )
    for registro in resultado.scalars():
        registro.RevogadoEm = agora
    await db.commit()


# Revoga TODAS as famílias de refresh de um usuário (item S14: troca de senha e mudança de
# função) — diferente de `revogarFamilia`, que só encerra UMA sessão/dispositivo, esta encerra
# TODOS os dispositivos logados daquele usuário de uma vez. Usada quando o nível de acesso do
# usuário muda (OWASP Session Management Cheat Sheet: regenerar/invalidar sessão em troca de
# senha e em mudança de privilégio). Não revoga o `jti` do access token em uso agora — quem chama
# esta função também deve denylistar o `jti` da própria requisição quando o tiver à mão (ver
# `servicos/revogacao.py`); sem isso, o access token do usuário-alvo permanece válido até expirar
# (no máximo 15min, pela janela curta do item S15).
async def revogarTodasFamiliasDoUsuario(db: AsyncSession, usuarioID: uuid.UUID) -> None:
    agora = agoraUtc()
    resultado = await db.execute(
        select(RefreshToken).where(RefreshToken.UsuarioID == usuarioID, RefreshToken.RevogadoEm.is_(None))
    )
    for registro in resultado.scalars():
        registro.RevogadoEm = agora
    await db.commit()


# Localiza a família a partir do valor bruto do token, sem rotacionar nada — usada pelo logout,
# que recebe o refresh token ainda "vivo" e só precisa do FamiliaID para revogar tudo.
async def obterFamiliaPorValor(db: AsyncSession, valorRecebido: str) -> uuid.UUID | None:
    try:
        id_, segredo = _dividirValor(valorRecebido)
    except RefreshInvalido:
        return None
    resultado = await db.execute(select(RefreshToken).where(RefreshToken.ID == id_))
    registro = resultado.scalar_one_or_none()
    if not registro or registro.SegredoHash != _hashSegredo(segredo):
        return None
    return registro.FamiliaID
