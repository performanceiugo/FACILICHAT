# Rotas de relatorios executivos do Gestor.
# Consolida metricas reais dos chamados sem misturar dados entre Empresas.

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modelos.CategoriaChamado import CategoriaChamado
from app.modelos.Chamados import Chamado, ChamadoStatus
from app.modelos.CoberturaTurno import CoberturaTurno
from app.modelos.Empresa import EmpresaConfiguracao
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


# Configuração efetiva do alerta de gargalo para a Empresa autenticada.
class ConfiguracaoGargaloSaida(BaseModel):
    LimiteGargaloHoras: int


# Alteração controlada do limite; evita valores inúteis ou abusivamente altos.
class ConfiguracaoGargaloAtualizar(BaseModel):
    LimiteGargaloHoras: int = Field(ge=1, le=720)


# Chamado parado além do limite, com duração sempre derivada da última atualização.
class GargaloSaida(BaseModel):
    ID: UUID
    Categoria: str
    Resumo: str | None
    SupervisorID: UUID | None
    Atualizacao: datetime
    TempoParadoHoras: float
    LimiteGargaloHoras: int


# Cobertura atual ou futura que ainda não possui Funcionário confirmado.
class CoberturaDescobertaSaida(BaseModel):
    ID: UUID
    CondominioID: UUID
    Posto: str
    Turno: str
    Inicio: datetime
    Fim: datetime


# Lastro objetivo do desempenho: volume atribuído, fechamento real e gargalos ativos.
class DesempenhoSupervisorSaida(BaseModel):
    ID: UUID
    Nome: str
    Recebidos: int
    Resolvidos: int
    Parados: int
    TaxaResolucaoPercentual: float | None


# Padrão inicial usado somente enquanto a Empresa ainda não salvou sua configuração própria.
LIMITE_GARGALO_PADRAO_HORAS = 72


# Garante que relatórios e edição compartilhem a mesma regra de autorização do Gestor.
def exigirGestor(usuarioAtual: Usuario, detalhe: str) -> None:
    if usuarioAtual.Funcao != UsuarioFuncao.Gestor:
        raise HTTPException(status_code=403, detail=detalhe)


# Lê o limite persistido do tenant ou devolve o padrão inicial sem criar dados em um GET.
async def obterLimiteGargalo(db: AsyncSession, empresaID: UUID) -> int:
    limite = await db.scalar(
        select(EmpresaConfiguracao.LimiteGargaloHoras).where(
            EmpresaConfiguracao.EmpresaID == empresaID
        )
    )
    return limite if limite is not None else LIMITE_GARGALO_PADRAO_HORAS


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


# GET /relatorios/configuracao-gargalo — expõe o limite efetivo da Empresa ao Gestor.
@roteador.get("/configuracao-gargalo", response_model=ConfiguracaoGargaloSaida)
async def obterConfiguracaoGargalo(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirGestor(usuarioAtual, "Sem permissão para acessar a configuração de gargalo")
    limite = await obterLimiteGargalo(db, usuarioAtual.EmpresaID)
    return ConfiguracaoGargaloSaida(LimiteGargaloHoras=limite)


# PATCH /relatorios/configuracao-gargalo — persiste o limite somente no tenant autenticado.
@roteador.patch("/configuracao-gargalo", response_model=ConfiguracaoGargaloSaida)
async def atualizarConfiguracaoGargalo(
    payload: ConfiguracaoGargaloAtualizar,
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirGestor(usuarioAtual, "Sem permissão para alterar a configuração de gargalo")
    configuracao = await db.scalar(
        select(EmpresaConfiguracao).where(
            EmpresaConfiguracao.EmpresaID == usuarioAtual.EmpresaID
        )
    )
    if configuracao is None:
        configuracao = EmpresaConfiguracao(
            EmpresaID=usuarioAtual.EmpresaID,
            LimiteGargaloHoras=payload.LimiteGargaloHoras,
        )
        db.add(configuracao)
    else:
        configuracao.LimiteGargaloHoras = payload.LimiteGargaloHoras
    await db.commit()
    return ConfiguracaoGargaloSaida(LimiteGargaloHoras=configuracao.LimiteGargaloHoras)


# GET /relatorios/gargalos — lista chamados ativos parados além do limite configurado.
@roteador.get("/gargalos", response_model=list[GargaloSaida])
async def obterGargalos(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirGestor(usuarioAtual, "Sem permissão para acessar os gargalos")
    agora = agoraUtc()
    limite = await obterLimiteGargalo(db, usuarioAtual.EmpresaID)
    instanteLimite = agora - timedelta(hours=limite)
    statusFinais = (ChamadoStatus.Concluido, ChamadoStatus.Cancelado)

    # Atualizacao é a única fonte do tempo parado; registros sem esse fato não são estimados.
    resultado = await db.execute(
        select(Chamado, CategoriaChamado.Nome.label("CategoriaNome"))
        .join(CategoriaChamado, CategoriaChamado.ID == Chamado.CategoriaID)
        .where(
            Chamado.EmpresaID == usuarioAtual.EmpresaID,
            Chamado.Status.not_in(statusFinais),
            Chamado.Atualizacao.is_not(None),
            Chamado.Atualizacao <= instanteLimite,
        )
        .order_by(Chamado.Atualizacao.asc())
    )
    return [
        GargaloSaida(
            ID=linha.Chamado.ID,
            Categoria=linha.CategoriaNome,
            Resumo=linha.Chamado.Resumo,
            SupervisorID=linha.Chamado.SupervisorID,
            Atualizacao=linha.Chamado.Atualizacao,
            TempoParadoHoras=round((agora - linha.Chamado.Atualizacao).total_seconds() / 3600, 2),
            LimiteGargaloHoras=limite,
        )
        for linha in resultado
    ]


# GET /relatorios/coberturas-descobertas — alerta o Gestor antes ou durante o turno sem responsável.
@roteador.get("/coberturas-descobertas", response_model=list[CoberturaDescobertaSaida])
async def obterCoberturasDescobertas(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirGestor(usuarioAtual, "Sem permissão para acessar as coberturas descobertas")
    agora = agoraUtc()

    # Turnos encerrados deixam de exigir ação; confirmação requer responsável e momento registrado.
    resultado = await db.execute(
        select(CoberturaTurno)
        .where(
            CoberturaTurno.EmpresaID == usuarioAtual.EmpresaID,
            CoberturaTurno.Fim >= agora,
            or_(
                CoberturaTurno.ResponsavelID.is_(None),
                CoberturaTurno.ConfirmadaEm.is_(None),
            ),
        )
        .order_by(CoberturaTurno.Inicio)
    )
    return [
        CoberturaDescobertaSaida(
            ID=cobertura.ID,
            CondominioID=cobertura.CondominioID,
            Posto=cobertura.Posto,
            Turno=cobertura.Turno,
            Inicio=cobertura.Inicio,
            Fim=cobertura.Fim,
        )
        for cobertura in resultado.scalars().all()
    ]


# GET /relatorios/desempenho-supervisores — compara fatos de atribuição e fechamento, sem nota subjetiva.
@roteador.get("/desempenho-supervisores", response_model=list[DesempenhoSupervisorSaida])
async def obterDesempenhoSupervisores(
    db: AsyncSession = Depends(obterBancoDadosComTenant),
    usuarioAtual: Usuario = Depends(obterUsuarioAtual),
):
    exigirGestor(usuarioAtual, "Sem permissão para acessar o desempenho dos supervisores")
    agora = agoraUtc()
    limite = await obterLimiteGargalo(db, usuarioAtual.EmpresaID)
    instanteLimite = agora - timedelta(hours=limite)
    statusFinais = (ChamadoStatus.Concluido, ChamadoStatus.Cancelado)

    # Outer join conserva supervisores sem amostra e todos os casos ficam escopados ao tenant.
    resultado = await db.execute(
        select(
            Usuario.ID,
            Usuario.Nome,
            func.count(Chamado.ID).label("Recebidos"),
            func.count(
                case((Chamado.Status == ChamadoStatus.Concluido, Chamado.ID))
            ).label("Resolvidos"),
            func.count(
                case(
                    (
                        and_(
                            Chamado.Status.not_in(statusFinais),
                            Chamado.Atualizacao.is_not(None),
                            Chamado.Atualizacao <= instanteLimite,
                        ),
                        Chamado.ID,
                    )
                )
            ).label("Parados"),
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

    # Taxa só existe quando há chamados recebidos; zero amostra permanece explicitamente nulo.
    return [
        DesempenhoSupervisorSaida(
            ID=linha.ID,
            Nome=linha.Nome,
            Recebidos=linha.Recebidos,
            Resolvidos=linha.Resolvidos,
            Parados=linha.Parados,
            TaxaResolucaoPercentual=(
                round((linha.Resolvidos / linha.Recebidos) * 100, 2)
                if linha.Recebidos > 0
                else None
            ),
        )
        for linha in resultado
    ]


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
