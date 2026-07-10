# Rotas de relatorios executivos do Gestor.
# Consolida metricas reais dos chamados sem misturar dados entre Empresas.

from datetime import datetime

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
