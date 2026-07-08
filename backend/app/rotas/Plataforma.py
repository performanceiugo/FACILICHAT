# Rotas globais da plataforma (Iugo Performance).
# Superadmins gerenciam Empresas (tenants) e criam o primeiro Gestor de cada uma.

from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.banco_dados import obterBancoDados
from app.modelos.Empresa import Empresa, EmpresaStatus
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterUsuarioAtual

roteador = APIRouter(prefix="/plataforma", tags=["Plataforma"])
pwd = PasswordHash.recommended()


class PrimeiroGestorCriar(BaseModel):
    Nome: str
    Email: EmailStr
    Senha: str
    Telefone: str | None = None


class EmpresaCriar(BaseModel):
    Nome: str
    CNPJ: str
    Gestor: PrimeiroGestorCriar


class EmpresaStatusAtualizar(BaseModel):
    Status: EmpresaStatus


class EmpresaSaida(BaseModel):
    ID: uuid.UUID
    Nome: str
    CNPJ: str
    Status: EmpresaStatus
    Criacao: datetime

    class Config:
        from_attributes = True


class EmpresaComGestorSaida(BaseModel):
    Empresa: EmpresaSaida
    GestorID: uuid.UUID


def exigirSuperadmin(usuario: Usuario) -> None:
    if usuario.Funcao != UsuarioFuncao.Superadmin:
        raise HTTPException(status_code=403, detail="Apenas Superadmin pode acessar a plataforma")


@roteador.get("/empresas", response_model=list[EmpresaSaida])
async def listarEmpresas(
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirSuperadmin(usuarioAtual)
    resultado = await db.execute(select(Empresa).order_by(Empresa.Criacao.desc()))
    return resultado.scalars().all()


@roteador.post("/empresas", response_model=EmpresaComGestorSaida)
async def criarEmpresaComPrimeiroGestor(
    payload: EmpresaCriar,
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirSuperadmin(usuarioAtual)

    cnpjExistente = await db.execute(select(Empresa).where(Empresa.CNPJ == payload.CNPJ))
    if cnpjExistente.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="CNPJ ja cadastrado")

    emailExistente = await db.execute(select(Usuario).where(Usuario.Email == payload.Gestor.Email))
    if emailExistente.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email do gestor ja cadastrado")

    empresa = Empresa(Nome=payload.Nome, CNPJ=payload.CNPJ, Status=EmpresaStatus.Ativa)
    db.add(empresa)
    await db.flush()

    gestor = Usuario(
        EmpresaID=empresa.ID,
        Nome=payload.Gestor.Nome,
        Email=payload.Gestor.Email,
        SenhaHash=pwd.hash(payload.Gestor.Senha),
        Funcao=UsuarioFuncao.Gestor,
        Telefone=payload.Gestor.Telefone,
    )
    db.add(gestor)
    await db.commit()
    await db.refresh(empresa)
    await db.refresh(gestor)

    return {"Empresa": empresa, "GestorID": gestor.ID}


@roteador.patch("/empresas/{empresaID}/status", response_model=EmpresaSaida)
async def atualizarStatusEmpresa(
    empresaID: uuid.UUID,
    payload: EmpresaStatusAtualizar,
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirSuperadmin(usuarioAtual)

    resultado = await db.execute(select(Empresa).where(Empresa.ID == empresaID))
    empresa = resultado.scalar_one_or_none()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")

    empresa.Status = payload.Status
    await db.commit()
    await db.refresh(empresa)
    return empresa
