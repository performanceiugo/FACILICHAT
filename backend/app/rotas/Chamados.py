# Rotas de gerenciamento de chamados (solicitações de serviço)
# Clientes criam chamados; supervisores e gestores visualizam todos; clientes veem apenas os seus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from sqlalchemy.orm import aliased
from pydantic import BaseModel, ConfigDict, Field
from app.modelos.Chamados import Chamado, ChamadoFila, ChamadoStatus, ChamadoPrioridade
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterBancoDadosComTenant, obterUsuarioAtual
from app.servicos.chamados import montarChamadosIrmaos
from app.tempo import agoraUtc
from datetime import datetime  # ainda usado nas anotações dos schemas de saída
import uuid

roteador = APIRouter(prefix="/chamados", tags=["Chamados"])

# Schema de entrada — dados obrigatórios e opcionais para abrir um novo chamado.
# Limites de tamanho (item M1): Categoria não pode ser vazia e os campos de texto livre têm teto,
# como defesa contra payloads abusivos (Resumo comporta o relato do cliente, mas não é ilimitado).
class ChamadoCriar(BaseModel):
    Fila: ChamadoFila
    Categoria: str = Field(min_length=1, max_length=80)
    Resumo: str | None = Field(default=None, max_length=2000)
    Prioridade: ChamadoPrioridade = ChamadoPrioridade.Media

class ChamadosIrmaosCriar(BaseModel):
    Chamados: list[ChamadoCriar]

# Schema de saída — campos retornados ao frontend após criar ou listar chamados
class ChamadoSaida(BaseModel):
    ID: uuid.UUID
    EmpresaID: uuid.UUID
    ClienteID: uuid.UUID
    ClienteNome: str | None = None
    GrupoOrigemID: uuid.UUID | None
    SupervisorID: uuid.UUID | None
    SupervisorNome: str | None = None
    Fila: ChamadoFila
    Categoria: str
    Status: ChamadoStatus
    Prioridade: ChamadoPrioridade
    Resumo: str | None
    Criacao: datetime

    model_config = ConfigDict(from_attributes=True)  # Permite serializar objetos ORM diretamente


# Combina o chamado com os nomes carregados por join, sem depender de lazy loading assíncrono.
def montarChamadoSaida(
    chamado: Chamado,
    clienteNome: str | None = None,
    supervisorNome: str | None = None,
) -> ChamadoSaida:
    return ChamadoSaida(
        ID=chamado.ID,
        EmpresaID=chamado.EmpresaID,
        ClienteID=chamado.ClienteID,
        ClienteNome=clienteNome,
        GrupoOrigemID=chamado.GrupoOrigemID,
        SupervisorID=chamado.SupervisorID,
        SupervisorNome=supervisorNome,
        Fila=chamado.Fila,
        Categoria=chamado.Categoria,
        Status=chamado.Status,
        Prioridade=chamado.Prioridade,
        Resumo=chamado.Resumo,
        Criacao=chamado.Criacao,
    )

# POST /chamados/ — cria um novo chamado vinculado ao usuário autenticado
@roteador.post("/", response_model=ChamadoSaida)
async def criarChamado(
    payload: ChamadoCriar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    chamado = Chamado(
        EmpresaID=usuarioAtual.EmpresaID,  # regra de ouro do multi-tenant: nasce escopado ao tenant do criador
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

# POST /chamados/irmaos — cria 2+ chamados ligados pelo mesmo GrupoOrigemID
@roteador.post("/irmaos", response_model=list[ChamadoSaida])
async def criarChamadosIrmaos(
    payload: ChamadosIrmaosCriar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    if len(payload.Chamados) < 2:
        raise HTTPException(status_code=400, detail="Tickets irmãos exigem pelo menos 2 chamados")

    chamados = montarChamadosIrmaos(payload.Chamados, usuarioAtual)
    db.add_all(chamados)
    await db.commit()
    for chamado in chamados:
        await db.refresh(chamado)
    return chamados

# GET /chamados/ — lista chamados; gestores e supervisores veem todos, clientes veem apenas os seus
@roteador.get("/", response_model=list[ChamadoSaida])
async def listarChamados(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
    supervisor_id: uuid.UUID | None = None,
):
    # Regra de ouro do multi-tenant: toda consulta é filtrada pela Empresa do usuário logado,
    # antes de qualquer outra regra de visibilidade por papel.
    cliente = aliased(Usuario)
    supervisor = aliased(Usuario)
    consulta = (
        select(
            Chamado,
            cliente.Nome.label("ClienteNome"),
            supervisor.Nome.label("SupervisorNome"),
        )
        .join(
            cliente,
            and_(
                cliente.ID == Chamado.ClienteID,
                cliente.EmpresaID == usuarioAtual.EmpresaID,
            ),
        )
        .outerjoin(
            supervisor,
            and_(
                supervisor.ID == Chamado.SupervisorID,
                supervisor.EmpresaID == usuarioAtual.EmpresaID,
            ),
        )
        .where(Chamado.EmpresaID == usuarioAtual.EmpresaID)
    )

    # O filtro individual existe para a visão operacional do Gestor. Validar o papel e o tenant do
    # supervisor evita que o UUID seja usado para consultar ou enumerar usuários de outra Empresa.
    if supervisor_id is not None:
        if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
            raise HTTPException(status_code=403, detail="Somente o Gestor pode filtrar por supervisor")

        supervisorResultado = await db.execute(
            select(Usuario.ID).where(
                Usuario.ID == supervisor_id,
                Usuario.EmpresaID == usuarioAtual.EmpresaID,
                Usuario.Funcao == UsuarioFuncao.Supervisor,
            )
        )
        if supervisorResultado.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Supervisor não encontrado")

        # Retorna somente a fila atribuída ao supervisor validado, mantendo a ordem mais recente.
        consulta = consulta.where(Chamado.SupervisorID == supervisor_id)
    if usuarioAtual.Funcao in (UsuarioFuncao.Gestor, UsuarioFuncao.Supervisor):
        # Acesso total dentro da Empresa: retorna todos os chamados em ordem cronológica decrescente
        resultado = await db.execute(consulta.order_by(Chamado.Criacao.desc()))
    else:
        # Acesso restrito: cliente vê apenas os chamados que ele mesmo abriu
        resultado = await db.execute(
            consulta
            .where(Chamado.ClienteID == usuarioAtual.ID)
            .order_by(Chamado.Criacao.desc())
        )
    # Os nomes tornam a tabela pesquisável sem expor qualquer usuário fora da Empresa autenticada.
    return [
        montarChamadoSaida(linha.Chamado, linha.ClienteNome, linha.SupervisorNome)
        for linha in resultado
    ]

# PATCH /chamados/{chamadoID}/status — atualiza o status de um chamado existente
@roteador.patch("/{chamadoID}/status", response_model=ChamadoSaida)
async def atualizarStatus(
    chamadoID: uuid.UUID,
    status: ChamadoStatus,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    # Autorização: mudar status é operação interna — só Supervisor e Gestor podem.
    # Impede que um Cliente altere o status de qualquer chamado (falha de IDOR).
    if usuarioAtual.Funcao not in (UsuarioFuncao.Supervisor, UsuarioFuncao.Gestor):
        raise HTTPException(status_code=403, detail="Sem permissão para alterar o status do chamado")

    # Filtra também por EmpresaID: impede que alguém altere um chamado de outro tenant só por
    # adivinhar/enumerar o UUID (IDOR entre empresas).
    resultado = await db.execute(
        select(Chamado).where(Chamado.ID == chamadoID, Chamado.EmpresaID == usuarioAtual.EmpresaID)
    )
    chamado = resultado.scalar_one_or_none()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    # Regra de negócio: chamado em estado terminal (Concluído/Cancelado) não pode ser reaberto
    if chamado.Status in (ChamadoStatus.Concluido, ChamadoStatus.Cancelado):
        raise HTTPException(status_code=409, detail="Chamado finalizado não pode ter o status alterado")

    chamado.Status = status
    chamado.Atualizacao = agoraUtc()  # timezone-aware, compatível com a coluna DateTime(timezone=True)
    await db.commit()
    await db.refresh(chamado)
    return chamado

# Schema de entrada da atribuição de supervisor — SupervisorID nulo remove a atribuição atual.
class SupervisorAtribuir(BaseModel):
    SupervisorID: uuid.UUID | None = None

# PATCH /chamados/{chamadoID}/supervisor — atribui, troca ou remove o supervisor responsável
@roteador.patch("/{chamadoID}/supervisor", response_model=ChamadoSaida)
async def atribuirSupervisor(
    chamadoID: uuid.UUID,
    payload: SupervisorAtribuir,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual)
):
    # Autorização: decidir quem cuida de qual chamado é decisão de gestão — só o Gestor atribui.
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Somente o Gestor pode atribuir o supervisor responsável")

    # Filtra também por EmpresaID: impede atribuir um chamado de outro tenant só por adivinhar o UUID.
    resultado = await db.execute(
        select(Chamado).where(Chamado.ID == chamadoID, Chamado.EmpresaID == usuarioAtual.EmpresaID)
    )
    chamado = resultado.scalar_one_or_none()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    supervisorNome: str | None = None
    if payload.SupervisorID is not None:
        # O supervisor precisa existir com esse papel na mesma Empresa — evita atribuir um
        # usuário de outro tenant ou de outro perfil só por adivinhar/enumerar o UUID.
        supervisorResultado = await db.execute(
            select(Usuario).where(
                Usuario.ID == payload.SupervisorID,
                Usuario.EmpresaID == usuarioAtual.EmpresaID,
                Usuario.Funcao == UsuarioFuncao.Supervisor,
            )
        )
        supervisor = supervisorResultado.scalar_one_or_none()
        if supervisor is None:
            raise HTTPException(status_code=404, detail="Supervisor não encontrado")
        supervisorNome = supervisor.Nome

    chamado.SupervisorID = payload.SupervisorID
    await db.commit()
    await db.refresh(chamado)

    clienteResultado = await db.execute(select(Usuario.Nome).where(Usuario.ID == chamado.ClienteID))
    clienteNome = clienteResultado.scalar_one_or_none()
    return montarChamadoSaida(chamado, clienteNome, supervisorNome)
