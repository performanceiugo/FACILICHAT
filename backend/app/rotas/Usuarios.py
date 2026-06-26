# Rotas de gerenciamento de usuários
# Permite criar novos usuários e consultar os dados do usuário autenticado

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from BancoDados import obterBancoDados
from Modelos.Usuarios import Usuario, UsuarioFuncao
from Rotas.Autenticacao import obterUsuarioAtual
import uuid

roteador = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Instância do hasher de senhas (mesma configuração usada em Autenticacao.py)
pwd = PasswordHash.recommended()

# Schema de entrada — dados necessários para cadastrar um novo usuário
class UsuarioCriar(BaseModel):
    Nome: str
    Email: EmailStr  # Pydantic valida o formato do email automaticamente
    Senha: str
    Funcao: UsuarioFuncao
    Telefone: str | None = None
    Condominio: str | None = None

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

# POST /usuarios/ — cadastra um novo usuário no sistema
@roteador.post("/", response_model=UsuarioSaida)
async def criarUsuario(payload: UsuarioCriar, db: AsyncSession = Depends(obterBancoDados)):
    # Bloqueia cadastros com email já existente para evitar duplicatas
    resultado = await db.execute(select(Usuario).where(Usuario.Email == payload.Email))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    usuario = Usuario(
        Nome=payload.Nome,
        Email=payload.Email,
        SenhaHash=pwd.hash(payload.Senha),  # Armazena apenas o hash — nunca a senha em texto puro
        Funcao=payload.Funcao,
        Telefone=payload.Telefone,
        Condominio=payload.Condominio,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario

# GET /usuarios/eu — retorna os dados do usuário que está fazendo a requisição
@roteador.get("/eu", response_model=UsuarioSaida)
async def obterEu(usuarioAtual: Usuario = Depends(obterUsuarioAtual)):
    return usuarioAtual
