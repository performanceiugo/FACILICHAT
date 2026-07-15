# Rotas de relatorios executivos do Gestor.
# Consolida metricas reais dos chamados sem misturar dados entre Empresas.

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modelos.Chamados import Chamado, ChamadoStatus
from app.modelos.Mensagens import AutorTipo, Mensagem
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.rotas.Autenticacao import obterBancoDadosComTenant, obterUsuarioAtual
from app.tempo import agoraUtc


# Agrupa os endpoints consumidos pelo dashboard web do Gestor.
roteador = APIRouter(prefix="/relatorios", tags=["Relatorios"])


# Contrato do resumo executivo; medias sem amostra permanecem nulas.
class VisaoGeralSaida(BaseModel):
    TotalAbertos: int
    SlaEstourado: int
    PrimeiraRespostaMediaMinutos: float | None
    ResolucaoMediaMinutos: float | None
    AtualizadoEm: datetime


# Contrato de carga operacional por supervisor; medias sem amostra permanecem nulas.
class SupervisorRelatorioSaida(BaseModel):
    ID: UUID
    Nome: str
    Abertos: int
    Atrasados: int
    PrimeiraRespostaMediaMinutos: float | None


# GET /relatorios/visao-geral — calcula os quatro KPIs previstos para o dashboard.
@roteador.get("/visao-geral", response_model=VisaoGeralSaida)
async def obterVisaoGeral(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    # O relatorio agrega toda a operacao da Empresa e, por isso, e exclusivo do Gestor.
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Sem permissao para acessar a visao geral")

    agora = agoraUtc()
    statusFinais = (ChamadoStatus.Concluido, ChamadoStatus.Cancelado)

    # Abertos e SLA vencido usam somente chamados ativos do tenant autenticado.
    resumoChamados = await db.execute(
        select(
            func.count(Chamado.ID),
            func.count(
                case(
                    (
                        and_(Chamado.PrazoSLA.is_not(None), Chamado.PrazoSLA < agora),
                        Chamado.ID,
                    )
                )
            ),
        ).where(
            Chamado.EmpresaID == usuarioAtual.EmpresaID,
            Chamado.Status.not_in(statusFinais),
        )
    )
    totalAbertos, slaEstourado = resumoChamados.one()

    # A primeira resposta e a primeira mensagem humana interna posterior a abertura.
    primeiraRespostaPorChamado = (
        select(
            Chamado.ID.label("ChamadoID"),
            func.min(Mensagem.Criacao).label("PrimeiraResposta"),
            Chamado.Criacao.label("CriacaoChamado"),
        )
        .join(Mensagem, Mensagem.ChamadoID == Chamado.ID)
        .where(
            Chamado.EmpresaID == usuarioAtual.EmpresaID,
            Mensagem.EmpresaID == usuarioAtual.EmpresaID,
            Mensagem.AutorTipo.in_((AutorTipo.Supervisor, AutorTipo.Funcionario)),
            Mensagem.Criacao >= Chamado.Criacao,
        )
        .group_by(Chamado.ID, Chamado.Criacao)
        .subquery()
    )
    primeiraRespostaMedia = await db.scalar(
        select(
            func.avg(
                func.extract(
                    "epoch",
                    primeiraRespostaPorChamado.c.PrimeiraResposta
                    - primeiraRespostaPorChamado.c.CriacaoChamado,
                )
                / 60.0
            )
        )
    )

    # A resolucao usa a ultima atualizacao registrada quando o chamado foi concluido.
    resolucaoMedia = await db.scalar(
        select(
            func.avg(func.extract("epoch", Chamado.Atualizacao - Chamado.Criacao) / 60.0)
        ).where(
            Chamado.EmpresaID == usuarioAtual.EmpresaID,
            Chamado.Status == ChamadoStatus.Concluido,
            Chamado.Criacao.is_not(None),
            Chamado.Atualizacao.is_not(None),
            Chamado.Atualizacao >= Chamado.Criacao,
        )
    )

    # Arredonda apenas na borda da API para preservar a precisao do calculo no banco.
    return VisaoGeralSaida(
        TotalAbertos=totalAbertos,
        SlaEstourado=slaEstourado,
        PrimeiraRespostaMediaMinutos=round(float(primeiraRespostaMedia), 2) if primeiraRespostaMedia is not None else None,
        ResolucaoMediaMinutos=round(float(resolucaoMedia), 2) if resolucaoMedia is not None else None,
        AtualizadoEm=agora,
    )


# GET /relatorios/supervisores — compara carga e primeira resposta com lastro real.
@roteador.get("/supervisores", response_model=list[SupervisorRelatorioSaida])
async def obterRelatorioSupervisores(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    # A comparacao atravessa toda a operacao da Empresa e, por isso, e exclusiva do Gestor.
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail="Sem permissao para acessar o relatorio de supervisores")

    agora = agoraUtc()
    statusFinais = (ChamadoStatus.Concluido, ChamadoStatus.Cancelado)

    # Mantem supervisores sem chamados na resposta para o Gestor enxergar toda a equipe.
    cargaPorSupervisor = await db.execute(
        select(
            Usuario.ID,
            Usuario.Nome,
            func.count(
                case(
                    (
                        and_(
                            Chamado.ID.is_not(None),
                            Chamado.Status.not_in(statusFinais),
                        ),
                        Chamado.ID,
                    )
                )
            ).label("Abertos"),
            func.count(
                case(
                    (
                        and_(
                            Chamado.ID.is_not(None),
                            Chamado.Status.not_in(statusFinais),
                            Chamado.PrazoSLA.is_not(None),
                            Chamado.PrazoSLA < agora,
                        ),
                        Chamado.ID,
                    )
                )
            ).label("Atrasados"),
        )
        .outerjoin(
            Chamado,
            and_(
                Chamado.SupervisorID == Usuario.ID,
                Chamado.EmpresaID == usuarioAtual.EmpresaID,
            ),
        )
        .where(
            Usuario.EmpresaID == usuarioAtual.EmpresaID,
            Usuario.Funcao == UsuarioFuncao.Supervisor,
        )
        .group_by(Usuario.ID, Usuario.Nome)
        .order_by(Usuario.Nome)
    )

    # A primeira resposta valida autoria e atribuicao: conta apenas mensagem do supervisor
    # responsavel, posterior a abertura, sem confundir resposta de outro membro da equipe.
    primeiraRespostaPorChamado = (
        select(
            Chamado.SupervisorID.label("SupervisorID"),
            Chamado.ID.label("ChamadoID"),
            Chamado.Criacao.label("CriacaoChamado"),
            func.min(Mensagem.Criacao).label("PrimeiraResposta"),
        )
        .join(
            Mensagem,
            and_(
                Mensagem.ChamadoID == Chamado.ID,
                Mensagem.EmpresaID == usuarioAtual.EmpresaID,
                Mensagem.AutorID == Chamado.SupervisorID,
                Mensagem.AutorTipo == AutorTipo.Supervisor,
                Mensagem.Criacao >= Chamado.Criacao,
            ),
        )
        .where(
            Chamado.EmpresaID == usuarioAtual.EmpresaID,
            Chamado.SupervisorID.is_not(None),
            Chamado.Criacao.is_not(None),
        )
        .group_by(Chamado.SupervisorID, Chamado.ID, Chamado.Criacao)
        .subquery()
    )
    mediasResultado = await db.execute(
        select(
            primeiraRespostaPorChamado.c.SupervisorID,
            func.avg(
                func.extract(
                    "epoch",
                    primeiraRespostaPorChamado.c.PrimeiraResposta
                    - primeiraRespostaPorChamado.c.CriacaoChamado,
                )
                / 60.0
            ).label("PrimeiraRespostaMediaMinutos"),
        ).group_by(primeiraRespostaPorChamado.c.SupervisorID)
    )
    mediasPorSupervisor = {
        linha.SupervisorID: linha.PrimeiraRespostaMediaMinutos
        for linha in mediasResultado
    }

    # Arredonda apenas na borda da API e preserva null para supervisores sem resposta registrada.
    return [
        SupervisorRelatorioSaida(
            ID=linha.ID,
            Nome=linha.Nome,
            Abertos=linha.Abertos,
            Atrasados=linha.Atrasados,
            PrimeiraRespostaMediaMinutos=(
                round(float(mediasPorSupervisor[linha.ID]), 2)
                if mediasPorSupervisor.get(linha.ID) is not None
                else None
            ),
        )
        for linha in cargaPorSupervisor
    ]
