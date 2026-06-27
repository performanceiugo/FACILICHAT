# Rotas de autenticação e utilitários de segurança JWT
# Responsável por: login, geração de token e validação do usuário atual em rotas protegidas

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta
from app.banco_dados import obterBancoDados
from app.modelos.Usuarios import Usuario
from app.configuracoes import configuracoes
import uuid

roteador = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])

# Instância do hasher de senhas com algoritmo recomendado (argon2)
pwd = PasswordHash.recommended()

# Informa ao FastAPI onde está o endpoint de login para o fluxo OAuth2 (exibido no Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/autenticacao/login")

# Gera um token JWT com o ID e função do usuário, válido pelo tempo configurado em JWT_EXPIRE_MINUTES
def criarToken(usuarioID: str, funcao: str) -> str:
    expiracao = datetime.utcnow() + timedelta(minutes=configuracoes.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": usuarioID,  # subject: identificador único do usuário
        "funcao": funcao,
        "exp": expiracao
    }
    return jwt.encode(payload, configuracoes.JWT_SECRET, algorithm=configuracoes.JWT_ALGORITHM)

# Dependência injetável — decodifica o token da requisição e retorna o usuário autenticado
# Usada em todas as rotas protegidas com Depends(obterUsuarioAtual)
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

# POST /autenticacao/login — recebe email e senha, retorna o token JWT e dados básicos do usuário
@roteador.post("/login")
async def login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(obterBancoDados)
):
    resultado = await db.execute(select(Usuario).where(Usuario.Email == formulario.username))
    usuario = resultado.scalar_one_or_none()

    # Rejeita se o usuário não existe ou a senha não confere com o hash armazenado
    if not usuario or not pwd.verify(formulario.password, usuario.SenhaHash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    token = criarToken(str(usuario.ID), usuario.Funcao.value)
    return {
        "token_acesso": token,
        "tipo_token": "bearer",
        "funcao": usuario.Funcao.value,
        "nome": usuario.Nome
    }
