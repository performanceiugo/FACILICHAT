# Denylist de sessão por `jti` (item S14 do plano).
#
# Guarda quais tokens JWT foram explicitamente revogados (logout) antes de expirar, para que
# `obterUsuarioAtual`/`obterTenantAtual` (rotas/Autenticacao.py) os rejeitem mesmo dentro da janela
# de validade original. Sem Redis no stack atual, a "expiração" da entrada é feita por limpeza
# ativa (DELETE de linhas já vencidas) a cada novo registro, em vez de TTL automático.

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modelos.SessaoRevogada import SessaoRevogada
from app.tempo import agoraUtc


# Registra o `jti` de um token como revogado. Antes de inserir, apaga as entradas já vencidas —
# substitui o TTL automático que uma denylist em Redis teria, mantendo a tabela pequena sem exigir
# um job periódico separado.
async def registrarRevogacao(
    db: AsyncSession, empresaID, usuarioID, jti: str, expiraEm: datetime
) -> None:
    await db.execute(delete(SessaoRevogada).where(SessaoRevogada.ExpiraEm < agoraUtc()))
    db.add(SessaoRevogada(Jti=jti, EmpresaID=empresaID, UsuarioID=usuarioID, ExpiraEm=expiraEm))
    await db.commit()


# Checa se um `jti` está na denylist. Usada a cada requisição autenticada — consulta por chave
# primária (`Jti`), então é uma busca indexada barata mesmo com o crescimento da tabela.
async def tokenRevogado(db: AsyncSession, jti: str | None) -> bool:
    if not jti:
        return False
    resultado = await db.execute(select(SessaoRevogada.Jti).where(SessaoRevogada.Jti == jti))
    return resultado.scalar_one_or_none() is not None
