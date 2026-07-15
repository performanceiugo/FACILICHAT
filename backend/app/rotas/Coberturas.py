# Rotas de registro e confirmação das coberturas operacionais.
# Supervisor e Gestor mantêm a escala; o tenant sempre vem da sessão autenticada.

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modelos.CoberturaTurno import CoberturaTurno
from app.modelos.Condominio import Condominio
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterBancoDadosComTenant, obterUsuarioAtual
from app.tempo import agoraUtc


# Agrupa operações de escala/cobertura usadas pela Supervisão.
roteador = APIRouter(prefix="/coberturas", tags=["Coberturas"])


# Dados necessários para registrar um posto e período que precisam de cobertura.
class CoberturaCriar(BaseModel):
    CondominioID: UUID
    Posto: str = Field(min_length=1, max_length=120)
    Turno: str = Field(min_length=1, max_length=80)
    Inicio: datetime
    Fim: datetime

    # Um turno precisa ter duração positiva; períodos invertidos nunca entram na escala.
    @model_validator(mode="after")
    def validarPeriodo(self):
        if self.Fim <= self.Inicio:
            raise ValueError("Fim deve ser posterior ao início")
        return self


# Funcionário escolhido para assumir uma cobertura previamente registrada.
class CoberturaConfirmar(BaseModel):
    ResponsavelID: UUID


# Contrato comum das rotas de cobertura, serializado diretamente do ORM.
class CoberturaSaida(BaseModel):
    ID: UUID
    EmpresaID: UUID
    CondominioID: UUID
    Posto: str
    Turno: str
    Inicio: datetime
    Fim: datetime
    ResponsavelID: UUID | None
    ConfirmadaEm: datetime | None

    model_config = ConfigDict(from_attributes=True)


# Restringe manutenção da escala aos papéis operacionais internos previstos.
def exigirOperacao(usuarioAtual: Usuario) -> None:
    if usuarioAtual.Funcao not in (UsuarioFuncao.Supervisor, UsuarioFuncao.Gestor):
        raise HTTPException(status_code=403, detail="Sem permissão para gerenciar coberturas")


# POST /coberturas — registra um período ainda descoberto para acompanhamento.
@roteador.post("/", response_model=CoberturaSaida)
async def criarCobertura(
    payload: CoberturaCriar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirOperacao(usuarioAtual)
    condominioExiste = await db.scalar(
        select(Condominio.ID).where(
            Condominio.ID == payload.CondominioID,
            Condominio.EmpresaID == usuarioAtual.EmpresaID,
        )
    )
    if condominioExiste is None:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")

    cobertura = CoberturaTurno(
        EmpresaID=usuarioAtual.EmpresaID,
        CondominioID=payload.CondominioID,
        Posto=payload.Posto.strip(),
        Turno=payload.Turno.strip(),
        Inicio=payload.Inicio,
        Fim=payload.Fim,
    )
    db.add(cobertura)
    await db.commit()
    await db.refresh(cobertura)
    return cobertura


# GET /coberturas — lista a escala do tenant para operação e conferência.
@roteador.get("/", response_model=list[CoberturaSaida])
async def listarCoberturas(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirOperacao(usuarioAtual)
    resultado = await db.execute(
        select(CoberturaTurno)
        .where(CoberturaTurno.EmpresaID == usuarioAtual.EmpresaID)
        .order_by(CoberturaTurno.Inicio)
    )
    return resultado.scalars().all()


# PATCH /coberturas/{id}/confirmar — vincula um Funcionário real do mesmo tenant.
@roteador.patch("/{coberturaID}/confirmar", response_model=CoberturaSaida)
async def confirmarCobertura(
    coberturaID: UUID,
    payload: CoberturaConfirmar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirOperacao(usuarioAtual)
    cobertura = await db.scalar(
        select(CoberturaTurno).where(
            CoberturaTurno.ID == coberturaID,
            CoberturaTurno.EmpresaID == usuarioAtual.EmpresaID,
        )
    )
    if cobertura is None:
        raise HTTPException(status_code=404, detail="Cobertura não encontrada")

    funcionario = await db.scalar(
        select(Usuario).where(
            Usuario.ID == payload.ResponsavelID,
            Usuario.EmpresaID == usuarioAtual.EmpresaID,
            Usuario.Funcao == UsuarioFuncao.Funcionario,
        )
    )
    if funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário responsável não encontrado")

    cobertura.ResponsavelID = funcionario.ID
    cobertura.ConfirmadaEm = agoraUtc()
    await db.commit()
    await db.refresh(cobertura)
    return cobertura
