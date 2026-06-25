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
pwd = PasswordHash.recommended()

class UsuarioCriar(BaseModel):
    Nome: str
    Email: EmailStr
    Senha: str
    Funcao: UsuarioFuncao
    Telefone: str | None = None
    Condominio: str | None = None

class UsuarioSaida(BaseModel):
    ID: uuid.UUID
    Nome: str
    Email: str
    Funcao: UsuarioFuncao
    Telefone: str | None
    Condominio: str | None

    class Config:
        from_attributes = True

@roteador.post("/", response_model=UsuarioSaida)
async def criarUsuario(payload: UsuarioCriar, db: AsyncSession = Depends(obterBancoDados)):
    resultado = await db.execute(select(Usuario).where(Usuario.Email == payload.Email))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    usuario = Usuario(
        Nome=payload.Nome,
        Email=payload.Email,
        SenhaHash=pwd.hash(payload.Senha),
        Funcao=payload.Funcao,
        Telefone=payload.Telefone,
        Condominio=payload.Condominio,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario

@roteador.get("/eu", response_model=UsuarioSaida)
async def obterEu(usuarioAtual: Usuario = Depends(obterUsuarioAtual)):
    return usuarioAtual
