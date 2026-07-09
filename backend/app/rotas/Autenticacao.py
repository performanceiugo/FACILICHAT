# Rotas de autenticação e utilitários de segurança JWT
# Responsável por: login, geração de token e validação do usuário atual em rotas protegidas

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import jwt
from jwt import PyJWTError
from pwdlib import PasswordHash
from datetime import datetime, timedelta
from app.banco_dados import obterBancoDados
from app.modelos.Usuarios import Usuario
from app.modelos.Empresa import Empresa, EmpresaStatus
from app.configuracoes import configuracoes
import uuid

roteador = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])

# Instância do hasher de senhas com algoritmo recomendado (argon2)
pwd = PasswordHash.recommended()

# Informa ao FastAPI onde está o endpoint de login para o fluxo OAuth2 (exibido no Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/autenticacao/login")

# Gera um token JWT com o ID, função e tenant (Empresa) do usuário, válido pelo tempo configurado
# em JWT_EXPIRE_MINUTES. O empresa_id viaja no token para que o front nunca precise informar o
# tenant (regra da Fase 0.7 — "tenant vem do token").
def criarToken(usuarioID: str, funcao: str, empresaID: str) -> str:
    expiracao = datetime.utcnow() + timedelta(minutes=configuracoes.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": usuarioID,  # subject: identificador único do usuário
        "funcao": funcao,
        "empresa_id": empresaID,
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
        usuarioUUID = uuid.UUID(usuarioID)
    except (PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    resultado = await db.execute(select(Usuario).where(Usuario.ID == usuarioUUID))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    resultadoEmpresa = await db.execute(select(Empresa).where(Empresa.ID == usuario.EmpresaID))
    empresa = resultadoEmpresa.scalar_one_or_none()
    if not empresa or empresa.Status == EmpresaStatus.Suspensa:
        raise HTTPException(status_code=403, detail="Empresa suspensa")
    return usuario

# Dependência leve — extrai só o tenant (EmpresaID) do token, sem carregar o Usuario inteiro do banco.
# Existe separada de obterUsuarioAtual para rotas/serviços que só precisam do escopo do tenant
# (ex.: filtros de query), evitando um SELECT extra quando o usuário completo não é necessário.
async def obterTenantAtual(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    try:
        payload = jwt.decode(token, configuracoes.JWT_SECRET, algorithms=[configuracoes.JWT_ALGORITHM])
        empresaID = payload.get("empresa_id")
        if not empresaID:
            raise HTTPException(status_code=401, detail="Token sem tenant")
        return uuid.UUID(empresaID)
    except (PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

# Dependência que entrega uma sessão de banco já escopada ao tenant via RLS (trava secundária,
# ver backend/app/rls.sql): define a variável de sessão Postgres `app.empresa_id` a partir do
# token ANTES de qualquer query da rota rodar. Rotas que leem/gravam dados sensíveis a tenant devem
# preferir esta dependência a `obterBancoDados` puro sempre que praticável.
async def obterBancoDadosComTenant(
    empresaID: uuid.UUID = Depends(obterTenantAtual),
    db: AsyncSession = Depends(obterBancoDados),
):
    # Usa escopo de sessão (não transação-local) para que o tenant continue aplicado mesmo após
    # commits internos da rota. No finally, o valor é limpo para não vazar para a próxima
    # requisição quando a conexão voltar ao pool.
    await db.execute(
        text("SELECT set_config('app.empresa_id', :empresa_id, false)"),
        {"empresa_id": str(empresaID)},
    )
    try:
        yield db
    finally:
        await db.execute(text("RESET app.empresa_id"))

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

    # Nome da Empresa vai junto na resposta do login (não no JWT) só para exibição na UI
    # (ex.: "Admin · Cefram" no cabeçalho do painel) — o backend nunca confia nesse campo depois.
    resultadoEmpresa = await db.execute(select(Empresa).where(Empresa.ID == usuario.EmpresaID))
    empresa = resultadoEmpresa.scalar_one_or_none()
    if not empresa or empresa.Status == EmpresaStatus.Suspensa:
        raise HTTPException(status_code=403, detail="Empresa suspensa")

    token = criarToken(str(usuario.ID), usuario.Funcao.value, str(usuario.EmpresaID))

    return {
        "token_acesso": token,
        "tipo_token": "bearer",
        "funcao": usuario.Funcao.value,
        "nome": usuario.Nome,
        "empresa_id": str(usuario.EmpresaID),
        "empresa_nome": empresa.Nome if empresa else None,
    }
