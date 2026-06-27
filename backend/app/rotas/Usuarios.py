# Rotas de gerenciamento de usuários
# Permite criar novos usuários e consultar os dados do usuário autenticado

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from app.banco_dados import obterBancoDados
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterUsuarioAtual
import uuid

roteador = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Instância do hasher de senhas (mesma configuração usada em Autenticacao.py)
pwd = PasswordHash.recommended()

# Schema de entrada do cadastro PÚBLICO — não inclui Funcao de propósito.
# A função é sempre forçada para Cliente no servidor, impedindo que alguém se cadastre como Gerente.
class UsuarioCriar(BaseModel):
    Nome: str
    Email: EmailStr  # Pydantic valida o formato do email automaticamente
    Senha: str
    Telefone: str | None = None
    Condominio: str | None = None

# Schema de entrada da criação INTERNA (somente Gerente) — aqui a Funcao pode ser definida,
# permitindo cadastrar perfis privilegiados (Supervisor, Funcionario, Gerente)
class UsuarioCriarEquipe(UsuarioCriar):
    Funcao: UsuarioFuncao

# Schema de saída — retorna dados públicos do usuário (sem senha ou hash)
class UsuarioSaida(BaseModel):
    ID: uuid.UUID
    Nome: str
    Email: str
    Funcao: UsuarioFuncao
    Telefone: str | None
    Condominio: str | None

    class Config:
        from_attributes = True  # Permite serializar objetos ORM diretamente

# Função interna que persiste um usuário com uma Funcao já decidida pelo servidor.
# Centraliza a checagem de email duplicado e a gravação, evitando duplicação entre as duas rotas.
async def _persistirUsuario(payload: UsuarioCriar, funcao: UsuarioFuncao, db: AsyncSession) -> Usuario:
    # Bloqueia cadastros com email já existente para evitar duplicatas
    resultado = await db.execute(select(Usuario).where(Usuario.Email == payload.Email))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    usuario = Usuario(
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
# Regra de segurança: a função é SEMPRE Cliente; ninguém pode se autopromover a Gerente/Supervisor.
@roteador.post("/", response_model=UsuarioSaida)
async def criarUsuario(payload: UsuarioCriar, db: AsyncSession = Depends(obterBancoDados)):
    return await _persistirUsuario(payload, UsuarioFuncao.Cliente, db)

# POST /usuarios/equipe — criação INTERNA de usuários com função privilegiada.
# Regra de negócio: apenas o Gerente pode criar Supervisor, Funcionario ou outro Gerente.
@roteador.post("/equipe", response_model=UsuarioSaida)
async def criarUsuarioEquipe(
    payload: UsuarioCriarEquipe,
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    # Somente Gerente tem permissão; qualquer outra função recebe 403
    if usuarioAtual.Funcao != UsuarioFuncao.Gerente:
        raise HTTPException(status_code=403, detail="Apenas o Gerente pode criar usuários da equipe")
    return await _persistirUsuario(payload, payload.Funcao, db)

# GET /usuarios/eu — retorna os dados do usuário que está fazendo a requisição
@roteador.get("/eu", response_model=UsuarioSaida)
async def obterEu(usuarioAtual: Usuario = Depends(obterUsuarioAtual)):
    return usuarioAtual
