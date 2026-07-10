# Rotas de gerenciamento de usuarios
# Permite criar novos usuarios e consultar os dados do usuario autenticado

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime, timezone
from app.banco_dados import obterBancoDados
from app.configuracoes import configuracoes
from app.modelos.Condominio import Condominio
from app.modelos.Empresa import Empresa, EmpresaStatus
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterBancoDadosComTenant, obterPayloadTokenAtual, obterUsuarioAtual
from app.servicos.hasher import pwd
from app.servicos.revogacao import registrarRevogacao
from app.servicos.refresh import revogarTodasFamiliasDoUsuario
from app.servicos.seguranca import aplicarRateLimitAutenticacao
import uuid

roteador = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Schema de entrada do cadastro PUBLICO - nao inclui Funcao de proposito.
# A funcao e sempre forcada para Cliente no servidor, impedindo que alguem se cadastre como Gestor.
# EmpresaID permanece no contrato para compatibilidade do frontend atual, mas a rota publica nao
# confia mais nele: quando o cadastro publico esta habilitado, ele precisa bater com a Empresa
# explicitamente liberada em configuracao.
class UsuarioCriar(BaseModel):
    EmpresaID: uuid.UUID
    Nome: str
    Email: EmailStr  # Pydantic valida o formato do email automaticamente
    Senha: str
    Telefone: str | None = None
    Condominio: str | None = None


# Schema de entrada da criacao INTERNA (somente Gestor) - aqui a Funcao pode ser definida,
# permitindo cadastrar perfis privilegiados (Supervisor, Funcionario, RH, Financeiro, Gestor)
class UsuarioCriarEquipe(UsuarioCriar):
    Funcao: UsuarioFuncao


# Schema de entrada da troca da propria senha (item S14) - exige a senha atual (Authentication
# Cheat Sheet da OWASP) para confirmar que quem esta trocando e o dono legitimo da conta.
class SenhaAlterar(BaseModel):
    SenhaAtual: str
    SenhaNova: str = Field(min_length=8)


# Schema de entrada da troca de funcao de um usuario (item S14) - so o Gestor usa esta rota.
class FuncaoAlterar(BaseModel):
    Funcao: UsuarioFuncao


# Schema de saida - retorna dados publicos do usuario (sem senha ou hash)
class UsuarioSaida(BaseModel):
    ID: uuid.UUID
    EmpresaID: uuid.UUID
    Nome: str
    Email: str
    Funcao: UsuarioFuncao
    Telefone: str | None
    CondominioID: uuid.UUID | None
    Condominio: str | None

    model_config = ConfigDict(from_attributes=True)


def _normalizarNomeCondominio(nomeCondominio: str | None) -> str | None:
    if not nomeCondominio:
        return None

    nomeNormalizado = nomeCondominio.strip()
    if not nomeNormalizado:
        return None

    return nomeNormalizado


# Cliente representa o responsavel de um Condominio/contrato; sem esse vinculo a regra de negocio
# da Fase 0.6 fica quebrada logo no cadastro.
def _validarCondominioObrigatorioParaCliente(funcao: UsuarioFuncao, nomeCondominio: str | None) -> None:
    if funcao == UsuarioFuncao.Cliente and not nomeCondominio:
        raise HTTPException(
            status_code=400,
            detail="Cliente precisa informar o Condominio/contrato responsavel",
        )


# Resolve o nome livre recebido no payload para uma entidade Condominio real do tenant.
# Reaproveita o registro existente quando o nome ja foi cadastrado naquela Empresa e cria um novo
# quando ainda nao existe, mantendo a transicao compativel com o frontend atual.
async def _resolverCondominio(
    empresaID: uuid.UUID, nomeCondominio: str | None, db: AsyncSession
) -> Condominio | None:
    nomeNormalizado = _normalizarNomeCondominio(nomeCondominio)
    if not nomeNormalizado:
        return None

    resultado = await db.execute(
        select(Condominio).where(
            Condominio.EmpresaID == empresaID,
            func.lower(Condominio.Nome) == nomeNormalizado.lower(),
        )
    )
    condominio = resultado.scalar_one_or_none()
    if condominio:
        return condominio

    condominio = Condominio(EmpresaID=empresaID, Nome=nomeNormalizado)
    db.add(condominio)
    await db.flush()
    return condominio


# Enforca a regra de branding desta fase: cada Condominio/contrato tem um unico responsavel Cliente
# (o sindico). Outros perfis da equipe nao entram nessa restricao.
async def _validarResponsavelUnicoPorCondominio(
    funcao: UsuarioFuncao, condominioID: uuid.UUID | None, db: AsyncSession
) -> None:
    if funcao != UsuarioFuncao.Cliente or not condominioID:
        return

    resultado = await db.execute(
        select(Usuario.ID).where(
            Usuario.Funcao == UsuarioFuncao.Cliente,
            Usuario.CondominioID == condominioID,
        )
    )
    if resultado.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Este Condominio ja possui um responsavel Cliente cadastrado",
        )


# Resolve o unico tenant permitido para cadastro publico. A rota falha fechada por padrao e so aceita
# EmpresaID quando ele bate exatamente com CADASTRO_PUBLICO_EMPRESA_ID, evitando signup em tenant alheio.
async def _resolverEmpresaCadastroPublico(empresaIDPayload: uuid.UUID, db: AsyncSession) -> uuid.UUID:
    if not configuracoes.CADASTRO_PUBLICO_HABILITADO or not configuracoes.CADASTRO_PUBLICO_EMPRESA_ID:
        raise HTTPException(
            status_code=403,
            detail="Cadastro publico indisponivel; solicite convite ou acesso ao Gestor da Empresa",
        )

    try:
        empresaIDPermitida = uuid.UUID(configuracoes.CADASTRO_PUBLICO_EMPRESA_ID)
    except ValueError:
        raise HTTPException(status_code=500, detail="Configuracao de cadastro publico invalida")

    if empresaIDPayload != empresaIDPermitida:
        raise HTTPException(
            status_code=403,
            detail="Cadastro publico indisponivel para esta Empresa",
        )

    resultado = await db.execute(
        select(Empresa).where(Empresa.ID == empresaIDPermitida, Empresa.Status == EmpresaStatus.Ativa)
    )
    if not resultado.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Cadastro publico indisponivel para esta Empresa",
        )

    return empresaIDPermitida


# Serializa o usuario para a API preservando o campo textual `Condominio` como compatibilidade de
# contrato enquanto o frontend ainda nao consome a entidade completa.
def _serializarUsuario(usuario: Usuario, condominioNome: str | None) -> UsuarioSaida:
    return UsuarioSaida(
        ID=usuario.ID,
        EmpresaID=usuario.EmpresaID,
        Nome=usuario.Nome,
        Email=usuario.Email,
        Funcao=usuario.Funcao,
        Telefone=usuario.Telefone,
        CondominioID=usuario.CondominioID,
        Condominio=condominioNome or usuario.Condominio,
    )


# Funcao interna que persiste um usuario com uma Funcao e EmpresaID ja decididos pelo servidor.
# Centraliza a checagem de email duplicado e a gravacao, evitando duplicacao entre as duas rotas.
async def _persistirUsuario(
    payload: UsuarioCriar, funcao: UsuarioFuncao, empresaID: uuid.UUID, db: AsyncSession
) -> tuple[Usuario, str | None]:
    resultado = await db.execute(select(Usuario).where(Usuario.Email == payload.Email))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Nao foi possivel concluir o cadastro com os dados informados")

    nomeCondominio = _normalizarNomeCondominio(payload.Condominio)
    _validarCondominioObrigatorioParaCliente(funcao, nomeCondominio)

    condominio = await _resolverCondominio(empresaID, nomeCondominio, db)
    await _validarResponsavelUnicoPorCondominio(funcao, condominio.ID if condominio else None, db)

    usuario = Usuario(
        EmpresaID=empresaID,
        Nome=payload.Nome,
        Email=payload.Email,
        SenhaHash=pwd.hash(payload.Senha),
        Funcao=funcao,
        Telefone=payload.Telefone,
        Condominio=condominio.Nome if condominio else nomeCondominio,
        CondominioID=condominio.ID if condominio else None,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario, condominio.Nome if condominio else nomeCondominio


# POST /usuarios/ - cadastro PUBLICO (sem autenticacao).
# Regra de seguranca: a funcao e SEMPRE Cliente e a Empresa so pode ser a liberada em configuracao.
@roteador.post("/", response_model=UsuarioSaida)
async def criarUsuario(
    payload: UsuarioCriar,
    request: Request,
    db: AsyncSession = Depends(obterBancoDados),
):
    aplicarRateLimitAutenticacao("signup-publico", request, payload.Email)
    empresaID = await _resolverEmpresaCadastroPublico(payload.EmpresaID, db)
    usuario, condominioNome = await _persistirUsuario(payload, UsuarioFuncao.Cliente, empresaID, db)
    return _serializarUsuario(usuario, condominioNome)


# POST /usuarios/equipe - criacao INTERNA de usuarios com funcao privilegiada.
# Regra de negocio: apenas o Gestor pode criar Supervisor, Funcionario, RH, Financeiro ou outro Gestor,
# sempre dentro da propria Empresa (tenant) do Gestor que esta criando - nunca de outra Empresa.
@roteador.post("/equipe", response_model=UsuarioSaida)
async def criarUsuarioEquipe(
    payload: UsuarioCriarEquipe,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Apenas o Gestor pode criar usuarios da equipe")

    usuario, condominioNome = await _persistirUsuario(payload, payload.Funcao, usuarioAtual.EmpresaID, db)
    return _serializarUsuario(usuario, condominioNome)


# GET /usuarios/eu - retorna os dados do usuario que esta fazendo a requisicao.
@roteador.get("/eu", response_model=UsuarioSaida)
async def obterEu(
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
    db: AsyncSession = Depends(obterBancoDadosComTenant),
):
    condominioNome = usuarioAtual.Condominio
    if usuarioAtual.CondominioID:
        resultado = await db.execute(select(Condominio.Nome).where(Condominio.ID == usuarioAtual.CondominioID))
        condominioNome = resultado.scalar_one_or_none() or condominioNome
    return _serializarUsuario(usuarioAtual, condominioNome)


# PATCH /usuarios/eu/senha - troca a propria senha (item S14, parte final do S14).
# Regra de seguranca: exige a senha atual antes de aceitar a nova (OWASP Authentication Cheat
# Sheet). Ao concluir, revoga TODAS as sessoes do usuario - a que fez a troca (denylist do jti
# atual) e qualquer outro dispositivo logado (todas as familias de refresh) - forcando um novo
# login em todo lugar. Segue a recomendacao da OWASP Session Management Cheat Sheet de invalidar
# sessoes existentes numa troca de senha.
@roteador.patch("/eu/senha")
async def alterarSenha(
    payload: SenhaAlterar,
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
    payloadToken: dict = Depends(obterPayloadTokenAtual),
    db: AsyncSession = Depends(obterBancoDadosComTenant),
):
    if not pwd.verify(payload.SenhaAtual, usuarioAtual.SenhaHash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    usuarioAtual.SenhaHash = pwd.hash(payload.SenhaNova)
    await db.commit()

    jti = payloadToken.get("jti")
    expiracao = payloadToken.get("exp")
    if jti and expiracao:
        await registrarRevogacao(
            db,
            usuarioAtual.EmpresaID,
            usuarioAtual.ID,
            jti,
            datetime.fromtimestamp(expiracao, tz=timezone.utc),
        )
    await revogarTodasFamiliasDoUsuario(db, usuarioAtual.ID)

    return {"mensagem": "Senha alterada. Faca login novamente."}


# PATCH /usuarios/{usuarioID}/funcao - troca a funcao de outro usuario (item S14, parte final).
# Regra de negocio: so o Gestor pode mudar funcao, e somente dentro da propria Empresa (tenant) -
# `obterBancoDadosComTenant` ja escopa a query via RLS, e o check explicito abaixo e defesa em
# profundidade (mesmo padrao usado no item S2/C7), nunca alterando usuario de outra Empresa.
# Ao concluir, revoga todas as familias de refresh do usuario-alvo (OWASP: invalidar sessao em
# mudanca de privilegio) - o access token que ele ja tem em maos continua valendo ate expirar (no
# maximo 15min, janela curta do S15), pois nao temos o jti de um dispositivo que nao e o desta
# requisicao.
@roteador.patch("/{usuarioID}/funcao", response_model=UsuarioSaida)
async def alterarFuncao(
    usuarioID: uuid.UUID,
    payload: FuncaoAlterar,
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
    db: AsyncSession = Depends(obterBancoDadosComTenant),
):
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Apenas o Gestor pode alterar a funcao de um usuario")

    resultado = await db.execute(select(Usuario).where(Usuario.ID == usuarioID))
    usuarioAlvo = resultado.scalar_one_or_none()
    if not usuarioAlvo or usuarioAlvo.EmpresaID != usuarioAtual.EmpresaID:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    usuarioAlvo.Funcao = payload.Funcao
    await db.commit()
    await db.refresh(usuarioAlvo)

    await revogarTodasFamiliasDoUsuario(db, usuarioAlvo.ID)

    condominioNome = usuarioAlvo.Condominio
    if usuarioAlvo.CondominioID:
        resultado = await db.execute(select(Condominio.Nome).where(Condominio.ID == usuarioAlvo.CondominioID))
        condominioNome = resultado.scalar_one_or_none() or condominioNome
    return _serializarUsuario(usuarioAlvo, condominioNome)
