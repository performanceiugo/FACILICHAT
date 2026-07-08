# Rotas de gerenciamento de usuarios
# Permite criar novos usuarios e consultar os dados do usuario autenticado

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from pydantic import BaseModel, ConfigDict, EmailStr
from pwdlib import PasswordHash
from app.banco_dados import obterBancoDados
from app.modelos.Condominio import Condominio
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterUsuarioAtual
import uuid

roteador = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Instancia do hasher de senhas (mesma configuracao usada em Autenticacao.py)
pwd = PasswordHash.recommended()

# Schema de entrada do cadastro PUBLICO - nao inclui Funcao de proposito.
# A funcao e sempre forcada para Cliente no servidor, impedindo que alguem se cadastre como Gestor.
# EmpresaID: como o signup publico nao e autenticado, nao ha tenant no token para resolver - por
# ora o cliente informa a Empresa explicitamente (paliativo ate a Fase 7 trazer um fluxo real de
# convite/onboarding por Empresa). Isso nao e escalonamento de privilegio: so define a qual Empresa
# o novo Cliente pertence, sempre com Funcao=Cliente forcada no servidor.
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
        raise HTTPException(status_code=400, detail="Email ja cadastrado")

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
# Regra de seguranca: a funcao e SEMPRE Cliente; ninguem pode se autopromover a Gestor/Supervisor.
@roteador.post("/", response_model=UsuarioSaida)
async def criarUsuario(payload: UsuarioCriar, db: AsyncSession = Depends(obterBancoDados)):
    usuario, condominioNome = await _persistirUsuario(payload, UsuarioFuncao.Cliente, payload.EmpresaID, db)
    return _serializarUsuario(usuario, condominioNome)


# POST /usuarios/equipe - criacao INTERNA de usuarios com funcao privilegiada.
# Regra de negocio: apenas o Gestor pode criar Supervisor, Funcionario, RH, Financeiro ou outro Gestor,
# sempre dentro da propria Empresa (tenant) do Gestor que esta criando - nunca de outra Empresa.
@roteador.post("/equipe", response_model=UsuarioSaida)
async def criarUsuarioEquipe(
    payload: UsuarioCriarEquipe,
    db: AsyncSession = Depends(obterBancoDados),
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
    db: AsyncSession = Depends(obterBancoDados),
):
    condominioNome = usuarioAtual.Condominio
    if usuarioAtual.CondominioID:
        resultado = await db.execute(select(Condominio.Nome).where(Condominio.ID == usuarioAtual.CondominioID))
        condominioNome = resultado.scalar_one_or_none() or condominioNome
    return _serializarUsuario(usuarioAtual, condominioNome)
