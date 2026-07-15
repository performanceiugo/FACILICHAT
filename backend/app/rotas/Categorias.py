# Rotas de gerenciamento do catálogo de categorias de chamado.
# Autoatendimento do Gestor: cada Empresa mantém seu próprio catálogo (Fase 4 — manutenção
# operacional). Desativar uma categoria não afeta os chamados que já a referenciam.

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modelos.CategoriaChamado import CategoriaChamado
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterBancoDadosComTenant, obterUsuarioAtual

roteador = APIRouter(prefix="/categorias", tags=["Categorias"])


class CategoriaCriar(BaseModel):
    Nome: str = Field(min_length=1, max_length=80)


# Nome e Ativa são independentes: o Gestor pode renomear sem mexer no status e vice-versa.
class CategoriaAtualizar(BaseModel):
    Nome: str | None = Field(default=None, min_length=1, max_length=80)
    Ativa: bool | None = None


class CategoriaSaida(BaseModel):
    ID: uuid.UUID
    EmpresaID: uuid.UUID
    Nome: str
    Ativa: bool

    model_config = ConfigDict(from_attributes=True)


# Manutenção de catálogo é decisão de gestão — só o Gestor cria/edita/ativa/desativa categorias.
def _exigirGestor(usuarioAtual: Usuario) -> None:
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Apenas o Gestor pode gerenciar categorias")


# GET /categorias/ — lista o catálogo completo do tenant (inclui inativas, para a tela de manutenção
# distinguir "desativar" de "nunca existiu"); a tela de abertura de chamado filtra as ativas no cliente.
@roteador.get("/", response_model=list[CategoriaSaida])
async def listarCategorias(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    _exigirGestor(usuarioAtual)
    resultado = await db.execute(
        select(CategoriaChamado)
        .where(CategoriaChamado.EmpresaID == usuarioAtual.EmpresaID)
        .order_by(CategoriaChamado.Nome)
    )
    return resultado.scalars().all()


# POST /categorias/ — cria uma categoria nova no catálogo do tenant.
@roteador.post("/", response_model=CategoriaSaida)
async def criarCategoria(
    payload: CategoriaCriar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    _exigirGestor(usuarioAtual)
    nome = payload.Nome.strip()

    duplicada = await db.execute(
        select(CategoriaChamado.ID).where(
            CategoriaChamado.EmpresaID == usuarioAtual.EmpresaID,
            CategoriaChamado.Nome.ilike(nome),
        )
    )
    if duplicada.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Já existe uma categoria com esse nome")

    categoria = CategoriaChamado(EmpresaID=usuarioAtual.EmpresaID, Nome=nome)
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    return categoria


# PATCH /categorias/{categoriaID} — edita o nome e/ou ativa/desativa; nunca exclui (anti-amnésia:
# chamados antigos continuam apontando para a categoria mesmo desativada).
@roteador.patch("/{categoriaID}", response_model=CategoriaSaida)
async def atualizarCategoria(
    categoriaID: uuid.UUID,
    payload: CategoriaAtualizar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    _exigirGestor(usuarioAtual)

    resultado = await db.execute(
        select(CategoriaChamado).where(
            CategoriaChamado.ID == categoriaID,
            CategoriaChamado.EmpresaID == usuarioAtual.EmpresaID,
        )
    )
    categoria = resultado.scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if payload.Nome is not None:
        nome = payload.Nome.strip()
        duplicada = await db.execute(
            select(CategoriaChamado.ID).where(
                CategoriaChamado.EmpresaID == usuarioAtual.EmpresaID,
                CategoriaChamado.Nome.ilike(nome),
                CategoriaChamado.ID != categoriaID,
            )
        )
        if duplicada.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Já existe uma categoria com esse nome")
        categoria.Nome = nome

    if payload.Ativa is not None:
        categoria.Ativa = payload.Ativa

    await db.commit()
    await db.refresh(categoria)
    return categoria
