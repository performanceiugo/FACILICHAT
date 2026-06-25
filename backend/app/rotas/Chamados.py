from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from BancoDados import obterBancoDados
from Modelos.Chamados import Chamado, ChamadoFila, ChamadoStatus, ChamadoPrioridade
from Modelos.Usuarios import Usuario
from Rotas.Autenticacao import obterUsuarioAtual
from datetime import datetime
import uuid

roteador = APIRouter(prefix="/chamados", tags=["Chamados"])

class ChamadoCriar(BaseModel):
    Fila: ChamadoFila
    Categoria: str
    Resumo: str | None = None
    Prioridade: ChamadoPrioridade = ChamadoPrioridade.Media

class ChamadoSaida(BaseModel):
    ID: uuid.UUID
    ClienteID: uuid.UUID
    Fila: ChamadoFila
    Categoria: str
    Status: ChamadoStatus
    Prioridade: ChamadoPrioridade
    Resumo: str | None
    Criacao: datetime

    class Config:
        from_attributes = True

@roteador.post("/", response_model=ChamadoSaida)
async def criarChamado(
    payload: ChamadoCriar,
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    chamado = Chamado(
        ClienteID=usuarioAtual.ID,
        Fila=payload.Fila,
        Categoria=payload.Categoria,
        Resumo=payload.Resumo,
        Prioridade=payload.Prioridade,
    )
    db.add(chamado)
    await db.commit()
    await db.refresh(chamado)
    return chamado

@roteador.get("/", response_model=list[ChamadoSaida])
async def listarChamados(
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    if usuarioAtual.Funcao.value in ("Gerente", "Supervisor"):
        resultado = await db.execute(select(Chamado).order_by(Chamado.Criacao.desc()))
    else:
        resultado = await db.execute(
            select(Chamado)
            .where(Chamado.ClienteID == usuarioAtual.ID)
            .order_by(Chamado.Criacao.desc())
        )
    return resultado.scalars().all()

@roteador.patch("/{chamadoID}/status", response_model=ChamadoSaida)
async def atualizarStatus(
    chamadoID: uuid.UUID,
    status: ChamadoStatus,
    db: AsyncSession = Depends(obterBancoDados),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    resultado = await db.execute(select(Chamado).where(Chamado.ID == chamadoID))
    chamado = resultado.scalar_one_or_none()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    chamado.Status = status
    chamado.Atualizacao = datetime.utcnow()
    await db.commit()
    await db.refresh(chamado)
    return chamado
