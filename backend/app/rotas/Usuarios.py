# Rotas de gerenciamento de usuários
# Permite criar novos usuários e consultar os dados do usuário autenticado

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict, EmailStr
from pwdlib import PasswordHash
from app.banco_dados import obterBancoDados
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterUsuarioAtual
import uuid

roteador = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Instância do hasher de senhas (mesma configuração usada em Autenticacao.py)
pwd = PasswordHash.recommended()

# Schema de entrada do cadastro PÚBLICO — não inclui Funcao de propósito.
# A função é sempre forçada para Cliente no servidor, impedindo que alguém se cadastre como Gestor.
# EmpresaID: como o signup público não é autenticado, não há tenant no token para resolver — por
# ora o cliente informa a Empresa explicitamente (paliativo até a Fase 7 trazer um fluxo real de
# convite/onboarding por Empresa). Isso não é escalonamento de privilégio: só define a qual Empresa
# o novo Cliente pertence, sempre com Funcao=Cliente forçada no servidor.
class UsuarioCriar(BaseModel):
    EmpresaID: uuid.UUID
    Nome: str
    Email: EmailStr  # Pydantic valida o formato do email automaticamente
    Senha: str
    Telefone: str | None = None
    Condominio: str | None = None

# Schema de entrada da criação INTERNA (somente Gestor) — aqui a Funcao pode ser definida,
# permitindo cadastrar perfis privilegiados (Supervisor, Funcionario, RH, Financeiro, Gestor)
class UsuarioCriarEquipe(UsuarioCriar):
    Funcao: UsuarioFuncao

# Schema de saída — retorna dados públicos do usuário (sem senha ou hash)
class UsuarioSaida(BaseModel):
    ID: uuid.UUID
    EmpresaID: uuid.UUID
    Nome: str
    Email: str
    Funcao: UsuarioFuncao
    Telefone: str | None
    Condominio: str | None

    model_config = ConfigDict(from_attributes=True)  # Permite serializar objetos ORM diretamente

# Função interna que persiste um usuário com uma Funcao e EmpresaID já decididos pelo servidor.
# Centraliza a checagem de email duplicado e a gravação, evitando duplicação entre as duas rotas.
async def _persistirUsuario(
    payload: UsuarioCriar, funcao: UsuarioFuncao, empresaID: uuid.UUID, db: AsyncSession
) -> Usuario:
    # Bloqueia cadastros com email já existente para evitar duplicatas
    resultado = await db.execute(select(Usuario).where(Usuario.Email == payload.Email))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    usuario = Usuario(
        EmpresaID=empresaID,
        Nome=payload.Nome,
        Email=payload.Email,
        SenhaHash=pwd.hash(payload.Senha),  # Armazena apenas o hash — nunca a senha em texto puro
        Funcao=funcao,
        Telefone=payload.Telefone,
        Condominio=payload.Condominio,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario

# POST /usuarios/ — cadastro PÚBLICO (sem autenticação).
# Regra de segurança: a função é SEMPRE Cliente; ninguém pode se autopromover a Gestor/Supervisor.
@roteador.post("/", response_model=UsuarioSaida)
async def criarUsuario(payload: UsuarioCriar, db: AsyncSession = Depends(obterBancoDados)):
    return await _persistirUsuario(payload, UsuarioFuncao.Cliente, payload.EmpresaID, db)

# POST /usuarios/equipe — criação INTERNA de usuários com função privilegiada.
# Regra de negócio: apenas o Gestor pode criar Supervisor, Funcionario, RH, Financeiro ou outro Gestor,
# sempre dentro da própria Empresa (tenant) do Gestor que está criando — nunca de outra Empresa.
@roteador.post("/equipe", response_model=UsuarioSaida)
async def criarUsuarioEquipe(
    payload: UsuarioCriarEquipe,
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    # Somente Gestor tem permissão; qualquer outra função recebe 403
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Apenas o Gestor pode criar usuários da equipe")
    return await _persistirUsuario(payload, payload.Funcao, usuarioAtual.EmpresaID, db)

# GET /usuarios/eu — retorna os dados do usuário que está fazendo a requisição
@roteador.get("/eu", response_model=UsuarioSaida)
async def obterEu(usuarioAtual: Usuario = Depends(obterUsuarioAtual)):
    return usuarioAtual
