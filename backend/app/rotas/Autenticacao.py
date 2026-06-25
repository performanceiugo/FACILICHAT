from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta
from BancoDados import obterBancoDados
from Modelos.Usuarios import Usuario
from Configuracoes import configuracoes
import uuid

roteador = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])
pwd = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/autenticacao/login")

def criarToken(usuarioID: str, funcao: str) -> str:
    expiracao = datetime.utcnow() + timedelta(minutes=configuracoes.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": usuarioID,
        "funcao": funcao,
        "exp": expiracao
    }
    return jwt.encode(payload, configuracoes.JWT_SECRET, algorithm=configuracoes.JWT_ALGORITHM)

async def obterUsuarioAtual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(obterBancoDados)
):
    try:
        payload = jwt.decode(token, configuracoes.JWT_SECRET, algorithms=[configuracoes.JWT_ALGORITHM])
        usuarioID = payload.get("sub")
        if not usuarioID:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    resultado = await db.execute(select(Usuario).where(Usuario.ID == uuid.UUID(usuarioID)))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario

@roteador.post("/login")
async def login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(obterBancoDados)
):
    resultado = await db.execute(select(Usuario).where(Usuario.Email == formulario.username))
    usuario = resultado.scalar_one_or_none()

    if not usuario or not pwd.verify(formulario.password, usuario.SenhaHash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    token = criarToken(str(usuario.ID), usuario.Funcao.value)
    return {
        "token_acesso": token,
        "tipo_token": "bearer",
        "funcao": usuario.Funcao.value,
        "nome": usuario.Nome
    }
