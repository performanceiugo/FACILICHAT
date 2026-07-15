# Ponto de entrada ÚNICO para gerenciar o banco de dados de desenvolvimento do FaciliChat.
#
# Por que este arquivo existe: antes havia 7 scripts espalhados em backend/scripts/ (bootstrap de
# Empresa, seed de demonstração, aplicação de RLS, verificação de isolamento e três migrações
# incrementais "aplicar_fase_*/aplicar_m5"). As migrações incrementais só serviam para remendar
# bancos de dev antigos — mas como `Base.metadata.create_all` já cria o schema COMPLETO a partir
# dos modelos atuais, em desenvolvimento (sem dados de produção a preservar) o correto é dropar e
# recriar. Este CLI consolida tudo num lugar visível, com subcomandos.
#
# Uso (a partir de backend/, ou via `docker compose exec backend python scripts/gerenciar_banco.py <cmd>`):
#   python scripts/gerenciar_banco.py reset [--semear]     # zera o banco: dropa tudo, recria e aplica RLS
#   python scripts/gerenciar_banco.py criar-empresa "<Nome>" <CNPJ> "<Gestor>" <email> <senha>
#   python scripts/gerenciar_banco.py criar-superadmin "<Nome>" <email> <senha>   # Superadmin da Iugo
#   python scripts/gerenciar_banco.py semear               # popula dados de demonstração (idempotente; recusa em AMBIENTE=producao)
#   python scripts/gerenciar_banco.py limpar-demo          # remove usuários/chamados de demonstração (idempotente)
#   python scripts/gerenciar_banco.py aplicar-rls          # (re)aplica as políticas de app/rls.sql
#   python scripts/gerenciar_banco.py verificar-rls        # testa o isolamento multi-tenant
#
# Fluxo típico de dev do zero:
#   reset  →  criar-empresa ...  →  semear

import argparse
import asyncio
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta

# Garante que a raiz do backend (pasta-pai de scripts/) esteja no sys.path para achar o pacote `app`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, func, select, text

from app.banco_dados import AsyncSessionLocal, Base, engine
from app.configuracoes import configuracoes
from app.modelos.Chamados import Chamado, ChamadoFila, ChamadoPrioridade, ChamadoStatus
from app.modelos.Condominio import Condominio
from app.modelos.Empresa import Empresa, EmpresaStatus
from app.modelos.Mensagens import AutorTipo, Mensagem
from app.modelos.RefreshToken import RefreshToken
from app.modelos.SessaoRevogada import SessaoRevogada
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.servicos.hasher import pwd  # mesmo hasher (argon2) usado pelas rotas de autenticação
from app.tempo import agoraUtc
import app.modelos  # importa todos os modelos para o create_all conhecer todas as tabelas

# Caminho do arquivo de políticas RLS — fonte da verdade das políticas do Postgres, aplicadas fora
# do ciclo do create_all (que só cria tabelas/colunas, não políticas).
CAMINHO_RLS_SQL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "rls.sql"
)


# ---------------------------------------------------------------------------
# Dados de demonstração (usados pelo subcomando `semear`)
# ---------------------------------------------------------------------------

# Todos os usuários de demonstração usam esta senha; e-mails ficam no domínio DOMINIO_DEMO,
# que também serve de marcador de idempotência do seed.
# Atualizada no item M1 para cumprir a política de senha (mínimo 15 caracteres — OWASP sem MFA):
# a senha antiga "Senha123" (8) ficaria abaixo do mínimo que a própria API passou a exigir.
SENHA_PADRAO = "FaciliChat2026Demo"
DOMINIO_DEMO = "@demo.facilichat.dev"

# Clientes de demonstração (moradores que abrem chamados), cada um em um condomínio diferente.
CLIENTES = [
    {"Nome": "Maria Silva",  "Email": f"maria{DOMINIO_DEMO}",  "Condominio": "Cond. Jardim das Flores"},
    {"Nome": "João Souza",   "Email": f"joao{DOMINIO_DEMO}",   "Condominio": "Ed. Solar das Acácias"},
    {"Nome": "Ana Costa",    "Email": f"ana{DOMINIO_DEMO}",    "Condominio": "Res. Bosque Verde"},
    {"Nome": "Carlos Lima",  "Email": f"carlos{DOMINIO_DEMO}", "Condominio": "Cond. Vista Alegre"},
]

# Supervisor de demonstração — responsável atribuído a alguns chamados e autor de respostas no chat.
SUPERVISOR = {"Nome": "Roberto Supervisor", "Email": f"supervisor{DOMINIO_DEMO}"}

# Conjunto de chamados de demonstração. Cada item define fila, categoria, prioridade, status, o índice
# do cliente (em CLIENTES), há quantos dias foi aberto, se tem supervisor atribuído, e o roteiro do chat.
# O chat usa autores Cliente / Supervisor / Sistema (o Sistema narra mudanças de status, sem jargão).
CHAMADOS = [
    {
        "cliente": 0, "fila": ChamadoFila.Operacional, "categoria": "Elétrica",
        "prioridade": ChamadoPrioridade.Alta, "status": ChamadoStatus.EmAndamento,
        "dias": 3, "supervisor": True,
        "resumo": "A lâmpada da garagem do subsolo está queimada há dois dias, está muito escuro à noite.",
        "chat": [
            (AutorTipo.Cliente, "Boa noite, a luz da garagem no subsolo apagou e está perigoso para quem chega tarde."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
            (AutorTipo.Supervisor, "Oi Maria, vamos trocar a lâmpada ainda hoje. Já estamos cuidando."),
            (AutorTipo.Sistema, "Seu chamado está em andamento."),
        ],
    },
    {
        "cliente": 1, "fila": ChamadoFila.Operacional, "categoria": "Hidráulica",
        "prioridade": ChamadoPrioridade.Critica, "status": ChamadoStatus.Recebido,
        "dias": 0, "supervisor": False,
        "resumo": "Vazamento forte embaixo da pia da churrasqueira, está alagando a área comum.",
        "chat": [
            (AutorTipo.Cliente, "Tem um vazamento grande na churrasqueira, a água não para de sair!"),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
        ],
    },
    {
        "cliente": 2, "fila": ChamadoFila.Operacional, "categoria": "Limpeza",
        "prioridade": ChamadoPrioridade.Baixa, "status": ChamadoStatus.Concluido,
        "dias": 8, "supervisor": True,
        "resumo": "Solicitação de limpeza extra do salão de festas após evento do fim de semana.",
        "chat": [
            (AutorTipo.Cliente, "O salão ficou bem sujo depois da festa de sábado, dá para reforçar a limpeza?"),
            (AutorTipo.Supervisor, "Claro! Agendamos a limpeza para segunda de manhã."),
            (AutorTipo.Sistema, "Seu chamado foi concluído. Qualquer coisa, estamos por aqui."),
        ],
    },
    {
        "cliente": 3, "fila": ChamadoFila.Operacional, "categoria": "Segurança",
        "prioridade": ChamadoPrioridade.Alta, "status": ChamadoStatus.Agendado,
        "dias": 2, "supervisor": True,
        "resumo": "O portão da garagem está fechando sozinho e batendo nos carros que entram.",
        "chat": [
            (AutorTipo.Cliente, "O portão eletrônico está com defeito, fechou quase em cima do meu carro."),
            (AutorTipo.Supervisor, "Vamos chamar o técnico do portão. Ele tem disponibilidade para quinta."),
            (AutorTipo.Sistema, "Sua visita técnica foi agendada."),
        ],
    },
    {
        "cliente": 0, "fila": ChamadoFila.RH, "categoria": "Atestado",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Recebido,
        "dias": 1, "supervisor": False,
        "resumo": "Envio de atestado médico do porteiro do turno da noite para justificar a falta.",
        "chat": [
            (AutorTipo.Cliente, "Preciso enviar o atestado do porteiro que faltou ontem, para onde mando?"),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
        ],
    },
    {
        "cliente": 1, "fila": ChamadoFila.RH, "categoria": "Escala",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.EmAndamento,
        "dias": 4, "supervisor": True,
        "resumo": "Dúvida sobre a escala de folga dos funcionários da portaria no feriado.",
        "chat": [
            (AutorTipo.Cliente, "Como fica a portaria no feriado da próxima semana?"),
            (AutorTipo.Supervisor, "Estou revisando a escala e já te retorno com a cobertura confirmada."),
            (AutorTipo.Sistema, "Seu chamado está em andamento."),
        ],
    },
    {
        "cliente": 2, "fila": ChamadoFila.Financeiro, "categoria": "Cobrança",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Recebido,
        "dias": 1, "supervisor": False,
        "resumo": "Cobrança de taxa extra que não reconheço no boleto deste mês.",
        "chat": [
            (AutorTipo.Cliente, "Apareceu uma taxa extra no meu boleto que eu não reconheço. Podem verificar?"),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
        ],
    },
    {
        "cliente": 3, "fila": ChamadoFila.Financeiro, "categoria": "2ª via de boleto",
        "prioridade": ChamadoPrioridade.Baixa, "status": ChamadoStatus.Concluido,
        "dias": 6, "supervisor": True,
        "resumo": "Pedido de segunda via do boleto do condomínio que venceu ontem.",
        "chat": [
            (AutorTipo.Cliente, "Perdi o boleto deste mês, consigo a segunda via?"),
            (AutorTipo.Supervisor, "Enviei a segunda via para o seu e-mail cadastrado."),
            (AutorTipo.Sistema, "Seu chamado foi concluído. Qualquer coisa, estamos por aqui."),
        ],
    },
    {
        "cliente": 0, "fila": ChamadoFila.Operacional, "categoria": "Elevador",
        "prioridade": ChamadoPrioridade.Critica, "status": ChamadoStatus.EmAndamento,
        "dias": 1, "supervisor": True,
        "resumo": "O elevador social parou entre andares e ficou travado com pessoas dentro.",
        "chat": [
            (AutorTipo.Cliente, "O elevador social travou! Já liberaram as pessoas, mas ele segue parado."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
            (AutorTipo.Supervisor, "A empresa de manutenção do elevador já está a caminho."),
            (AutorTipo.Sistema, "Seu chamado está em andamento."),
        ],
    },
    {
        "cliente": 1, "fila": ChamadoFila.Operacional, "categoria": "Jardinagem",
        "prioridade": ChamadoPrioridade.Baixa, "status": ChamadoStatus.Recebido,
        "dias": 5, "supervisor": False,
        "resumo": "A grama da área de lazer está muito alta e cheia de mato.",
        "chat": [
            (AutorTipo.Cliente, "Dá para agendar a poda do jardim? A grama está bem alta."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
        ],
    },
    {
        "cliente": 2, "fila": ChamadoFila.Financeiro, "categoria": "Reembolso",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Agendado,
        "dias": 3, "supervisor": True,
        "resumo": "Solicitação de reembolso de um conserto emergencial pago pelo morador.",
        "chat": [
            (AutorTipo.Cliente, "Paguei o encanador na emergência do fim de semana, como peço o reembolso?"),
            (AutorTipo.Supervisor, "Vamos analisar o comprovante na próxima reunião de condomínio."),
            (AutorTipo.Sistema, "Sua solicitação foi agendada para análise."),
        ],
    },
    {
        "cliente": 3, "fila": ChamadoFila.Operacional, "categoria": "Portaria",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Cancelado,
        "dias": 7, "supervisor": False,
        "resumo": "Interfone do apartamento 32 sem áudio — morador não escuta a portaria.",
        "chat": [
            (AutorTipo.Cliente, "Meu interfone está mudo, não escuto a portaria chamando."),
            (AutorTipo.Cliente, "Pode cancelar, era mau contato e já consegui resolver sozinho, obrigado!"),
            (AutorTipo.Sistema, "Seu chamado foi cancelado a seu pedido."),
        ],
    },
]


# ---------------------------------------------------------------------------
# Helpers de schema e RLS
# ---------------------------------------------------------------------------

# Cria todas as tabelas/colunas a partir dos modelos atuais (idempotente — não recria o existente).
async def criar_tabelas() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Lê app/rls.sql e executa cada comando isoladamente (asyncpg não aceita múltiplos statements por
# chamada). O SQL usa DROP POLICY IF EXISTS, então é idempotente.
async def aplicar_rls() -> None:
    with open(CAMINHO_RLS_SQL, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    script_sem_comentarios = re.sub(r"(?m)^\s*--.*$", "", script_sql)
    async with engine.begin() as conn:
        for comando in [c.strip() for c in script_sem_comentarios.split(";") if c.strip()]:
            await conn.execute(text(comando))


# ---------------------------------------------------------------------------
# Helpers de seed (idempotentes por e-mail/nome)
# ---------------------------------------------------------------------------

def _normalizar_condominio(nome: str | None) -> str | None:
    if not nome:
        return None
    nome_normalizado = nome.strip()
    return nome_normalizado or None


# Busca um Condomínio do tenant pelo nome (case-insensitive) ou o cria.
async def _obter_ou_criar_condominio(db, empresa_id, nome):
    nome_normalizado = _normalizar_condominio(nome)
    if not nome_normalizado:
        return None

    resultado = await db.execute(
        select(Condominio).where(
            Condominio.EmpresaID == empresa_id,
            func.lower(Condominio.Nome) == nome_normalizado.lower(),
        )
    )
    condominio = resultado.scalar_one_or_none()
    if condominio:
        return condominio

    condominio = Condominio(EmpresaID=empresa_id, Nome=nome_normalizado)
    db.add(condominio)
    await db.flush()
    return condominio


# Busca um usuário pelo e-mail (único) ou o cria com a função e o condomínio indicados.
async def _obter_ou_criar_usuario(db, empresa_id, nome, email, funcao, condominio=None):
    resultado = await db.execute(select(Usuario).where(Usuario.Email == email))
    usuario = resultado.scalar_one_or_none()
    if usuario:
        return usuario

    condominio_ref = await _obter_ou_criar_condominio(db, empresa_id, condominio)
    usuario = Usuario(
        EmpresaID=empresa_id,
        Nome=nome,
        Email=email,
        SenhaHash=pwd.hash(SENHA_PADRAO),
        Funcao=funcao,
        Condominio=condominio_ref.Nome if condominio_ref else None,
        CondominioID=condominio_ref.ID if condominio_ref else None,
    )
    db.add(usuario)
    await db.flush()  # garante o ID disponível para vincular aos chamados
    return usuario


# ---------------------------------------------------------------------------
# Helpers da verificação de isolamento multi-tenant
# ---------------------------------------------------------------------------

# Abre uma sessão já escopada ao tenant (mesma estratégia da API) e limpa a variável ao final.
@asynccontextmanager
async def _sessao_tenant(empresa_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.empresa_id', :empresa_id, false)"),
            {"empresa_id": str(empresa_id)},
        )
        try:
            yield session
        finally:
            await session.execute(text("RESET app.empresa_id"))
            await session.rollback()


# Cria um bloco mínimo de dados dentro de um tenant: condomínio, cliente responsável e chamado.
async def _criar_dados_tenant(empresa_id: uuid.UUID, rotulo: str):
    async with _sessao_tenant(empresa_id) as session:
        condominio = Condominio(EmpresaID=empresa_id, Nome=f"Condominio {rotulo}")
        session.add(condominio)
        await session.flush()

        usuario = Usuario(
            EmpresaID=empresa_id,
            Nome=f"Cliente {rotulo}",
            Email=f"{rotulo.lower()}@teste.local",
            SenhaHash="hash-temporario",
            Funcao=UsuarioFuncao.Cliente,
            Condominio=condominio.Nome,
            CondominioID=condominio.ID,
        )
        session.add(usuario)
        await session.flush()

        chamado = Chamado(
            EmpresaID=empresa_id,
            ClienteID=usuario.ID,
            Fila=ChamadoFila.Operacional,
            Categoria="Teste RLS",
            Resumo=f"Chamado {rotulo}",
            Prioridade=ChamadoPrioridade.Media,
        )
        session.add(chamado)
        await session.commit()
        return condominio.ID, usuario.ID, chamado.ID


# Descobre se o papel atual do banco ignora RLS (superuser/bypassrls) no ambiente local.
async def _papel_ignora_rls() -> bool:
    async with AsyncSessionLocal() as session:
        resultado = await session.execute(
            text(
                "select coalesce(rolsuper, false) or coalesce(rolbypassrls, false) "
                "from pg_roles where rolname = current_user"
            )
        )
        return bool(resultado.scalar_one())


# Confirma a camada do app: mesmo com dois tenants, queries por EmpresaID retornam só o bloco pedido.
async def _validar_filtros_aplicacao(empresa_id, esperado_cond, esperado_user, esperado_chamado):
    async with AsyncSessionLocal() as session:
        condominios = (await session.execute(
            select(Condominio.ID).where(Condominio.EmpresaID == empresa_id).order_by(Condominio.Nome.asc())
        )).scalars().all()
        usuarios = (await session.execute(
            select(Usuario.ID).where(Usuario.EmpresaID == empresa_id).order_by(Usuario.Email.asc())
        )).scalars().all()
        chamados = (await session.execute(
            select(Chamado.ID).where(Chamado.EmpresaID == empresa_id).order_by(Chamado.Criacao.asc())
        )).scalars().all()

    assert condominios == [esperado_cond], f"Filtro por EmpresaID falhou em Condominios: {condominios}"
    assert usuarios == [esperado_user], f"Filtro por EmpresaID falhou em Usuarios: {usuarios}"
    assert chamados == [esperado_chamado], f"Filtro por EmpresaID falhou em Chamados: {chamados}"


# Quando o papel do banco NÃO burla RLS, confirma também a trava secundária do Postgres.
async def _validar_visibilidade_tenant(empresa_id, esperado_cond, esperado_user, esperado_chamado):
    async with _sessao_tenant(empresa_id) as session:
        condominios = (await session.execute(select(Condominio.ID).order_by(Condominio.Nome.asc()))).scalars().all()
        usuarios = (await session.execute(select(Usuario.ID).order_by(Usuario.Email.asc()))).scalars().all()
        chamados = (await session.execute(select(Chamado.ID).order_by(Chamado.Criacao.asc()))).scalars().all()

    assert condominios == [esperado_cond], f"Tenant {empresa_id} viu condominios indevidos: {condominios}"
    assert usuarios == [esperado_user], f"Tenant {empresa_id} viu usuarios indevidos: {usuarios}"
    assert chamados == [esperado_chamado], f"Tenant {empresa_id} viu chamados indevidos: {chamados}"


# Remove os dados temporários no mesmo tenant que os criou (respeitando a RLS durante a limpeza).
async def _limpar_dados_tenant(empresa_id: uuid.UUID) -> None:
    async with _sessao_tenant(empresa_id) as session:
        await session.execute(delete(Chamado).where(Chamado.EmpresaID == empresa_id))
        await session.execute(delete(Usuario).where(Usuario.EmpresaID == empresa_id))
        await session.execute(delete(Condominio).where(Condominio.EmpresaID == empresa_id))
        await session.commit()


# ---------------------------------------------------------------------------
# Subcomandos do CLI
# ---------------------------------------------------------------------------

# `reset` — zera o banco de dev do zero. Dropa o schema public inteiro (tabelas, enums, políticas),
# recria e aplica a RLS. Substitui as antigas migrações incrementais: em dev não há dado a preservar,
# então recriar a partir dos modelos é o caminho correto e sem remendos.
async def cmd_reset(args) -> None:
    async with engine.begin() as conn:
        # DROP SCHEMA ... CASCADE remove tudo que pertence ao schema (inclusive os tipos ENUM criados
        # pelo SQLAlchemy); recriar deixa o banco limpo para o create_all reconstruir do zero.
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await criar_tabelas()
    await aplicar_rls()
    print("Banco resetado: schema recriado, tabelas criadas e RLS aplicada.")

    if args.semear:
        await _semear()


# `criar-empresa` — bootstrap da primeira Empresa (tenant) + primeiro Gestor, numa única transação
# (se o Gestor falhar, a Empresa também não é persistida — evita tenant órfão). É o ponto de entrada
# do sistema, já que o cadastro público fica fechado e /usuarios/equipe exige um Gestor autenticado.
async def cmd_criar_empresa(args) -> None:
    await criar_tabelas()  # garante que as tabelas existem (idempotente)

    async with AsyncSessionLocal() as db:
        empresa = Empresa(Nome=args.nome, CNPJ=args.cnpj)
        db.add(empresa)
        await db.flush()  # empresa.ID preenchido antes de criar o Usuario que o referencia

        gestor = Usuario(
            EmpresaID=empresa.ID,
            Nome=args.gestor,
            Email=args.email,
            SenhaHash=pwd.hash(args.senha),
            Funcao=UsuarioFuncao.Gestor,
        )
        db.add(gestor)
        await db.commit()

    print(f"Empresa criada: {args.nome} ({args.cnpj})")
    print(f"Gestor criado com sucesso: {args.email}")


# Empresa que hospeda o Superadmin da plataforma. A documentação posiciona a Iugo ACIMA dos tenants,
# mas o schema exige `Usuario.EmpresaID NOT NULL` (ver modelos/Usuarios.py) — então ela precisa
# existir como uma linha em `Empresas`. Decisão de produto de 09/07/2026: manter o schema intacto.
EMPRESA_PLATAFORMA_NOME = "Iugo Performance"

# CNPJ é `unique NOT NULL` e não há validação de dígito verificador em lugar nenhum do projeto.
# Este é um PLACEHOLDER de desenvolvimento — passe `--cnpj` com o CNPJ real ao rodar em produção.
EMPRESA_PLATAFORMA_CNPJ_PADRAO = "00.000.000/0001-00"


# `criar-superadmin` — bootstrap do primeiro Superadmin (Iugo Performance).
#
# Por que existe: `POST /plataforma/empresas` exige um Superadmin já autenticado (`exigirSuperadmin`
# em rotas/Plataforma.py), e nada no backend criava o primeiro — um ovo-e-galinha que travava o
# acesso ao painel de plataforma.
#
# Idempotente, ao contrário de `criar-empresa`: pode rodar de novo sem duplicar nada. Isso importa
# porque ele é um passo de provisionamento, executado à mão em cada ambiente.
async def cmd_criar_superadmin(args) -> None:
    await criar_tabelas()  # garante que as tabelas existem (idempotente)

    async with AsyncSessionLocal() as db:
        # --- Empresa da plataforma: reutiliza se já existir ---------------------------------
        resultado = await db.execute(select(Empresa).where(Empresa.Nome == args.empresa_nome))
        empresa = resultado.scalar_one_or_none()

        if empresa is None:
            empresa = Empresa(
                Nome=args.empresa_nome, CNPJ=args.cnpj, Status=EmpresaStatus.Ativa, EhPlataforma=True
            )
            db.add(empresa)
            await db.flush()  # empresa.ID preenchido antes de o Usuario referenciá-lo
            print(f"Empresa da plataforma criada: {args.empresa_nome} ({args.cnpj})")
        else:
            # Empresa suspensa faz `obterUsuarioAtual` responder 403 — o Superadmin ficaria trancado
            # para fora da própria plataforma. Reativar é a única saída sensata aqui.
            if empresa.Status == EmpresaStatus.Suspensa:
                empresa.Status = EmpresaStatus.Ativa
                print(f"Empresa da plataforma reativada: {empresa.Nome}")
            else:
                print(f"Empresa da plataforma já existia: {empresa.Nome}")
            # Corrige instalações que rodaram este bootstrap antes do campo existir (ambiente
            # gravado sem o flag) — reutilizar a Empresa da Iugo sempre a marca como plataforma.
            if not empresa.EhPlataforma:
                empresa.EhPlataforma = True
                print("Empresa da plataforma marcada como EhPlataforma=True (correção)")

        # --- Usuário Superadmin --------------------------------------------------------------
        resultado = await db.execute(select(Usuario).where(Usuario.Email == args.email))
        usuario = resultado.scalar_one_or_none()

        if usuario is not None:
            # Já é Superadmin: nada a fazer. É o caminho da idempotência (rodar 2x é seguro).
            if usuario.Funcao == UsuarioFuncao.Superadmin:
                await db.commit()  # persiste uma eventual reativação da Empresa
                print(f"Superadmin já existia, nada a fazer: {args.email}")
                return

            # NÃO promover um usuário existente. Um comando de bootstrap que transforma qualquer
            # conta em Superadmin é escalonamento de privilégio disfarçado — quem tiver acesso ao
            # shell promoveria o próprio Cliente. Falha alto e explícito.
            raise SystemExit(
                f"ERRO: o e-mail {args.email} já pertence a um usuário com perfil "
                f"{usuario.Funcao.value}. Este comando não promove usuários existentes a "
                f"Superadmin. Use outro e-mail."
            )

        superadmin = Usuario(
            EmpresaID=empresa.ID,
            Nome=args.nome,
            Email=args.email,
            SenhaHash=pwd.hash(args.senha),  # argon2, mesmo hasher das rotas
            Funcao=UsuarioFuncao.Superadmin,
        )
        db.add(superadmin)
        await db.commit()

    print(f"Superadmin criado com sucesso: {args.email} (Empresa: {args.empresa_nome})")


# `semear` — popula os dados de demonstração (clientes, supervisor, chamados e histórico de chat)
# na primeira Empresa existente. Idempotente: não semeia de novo se já houver chamados demo.
async def _semear() -> None:
    # Guarda de ambiente (item S10): usuários demo nascem com SENHA_PADRAO, previsível e igual em
    # toda instalação — inaceitável em produção. Falha cedo, sem sequer tocar no banco, em vez de
    # confiar em alguém lembrar de não rodar este comando lá.
    if configuracoes.AMBIENTE == "producao":
        print("Recusado: AMBIENTE=producao. `semear` só roda em dev/staging (ver docs/setup.md).")
        sys.exit(1)

    await criar_tabelas()

    async with AsyncSessionLocal() as db:
        # Idempotência: se já existir qualquer cliente de demonstração COM chamados, não semeia de novo.
        ja_existe = await db.execute(
            select(func.count(Chamado.ID))
            .join(Usuario, Usuario.ID == Chamado.ClienteID)
            .where(Usuario.Email.like(f"%{DOMINIO_DEMO}"))
        )
        if (ja_existe.scalar() or 0) > 0:
            print("Dados de demonstração já semeados — nada a fazer (idempotente).")
            return

        # Reaproveita a primeira Empresa existente (criada por `criar-empresa`) — este seed é
        # multi-tenant-aware, mas não cria Empresa: pressupõe que o bootstrap já rodou.
        resultado_empresa = await db.execute(select(Empresa).order_by(Empresa.Criacao).limit(1))
        empresa = resultado_empresa.scalar_one_or_none()
        if not empresa:
            print("Nenhuma Empresa encontrada — rode `criar-empresa` antes de semear.")
            return

        supervisor = await _obter_ou_criar_usuario(
            db, empresa.ID, SUPERVISOR["Nome"], SUPERVISOR["Email"], UsuarioFuncao.Supervisor
        )
        clientes = []
        for c in CLIENTES:
            clientes.append(await _obter_ou_criar_usuario(
                db, empresa.ID, c["Nome"], c["Email"], UsuarioFuncao.Cliente, c["Condominio"]
            ))

        agora = agoraUtc()

        # Cria cada chamado com data de abertura escalonada e o histórico de chat correspondente.
        for item in CHAMADOS:
            aberto_em = agora - timedelta(days=item["dias"], hours=2)
            chamado = Chamado(
                EmpresaID=empresa.ID,
                ClienteID=clientes[item["cliente"]].ID,
                SupervisorID=supervisor.ID if item["supervisor"] else None,
                Fila=item["fila"],
                Categoria=item["categoria"],
                Status=item["status"],
                Prioridade=item["prioridade"],
                Resumo=item["resumo"],
                Criacao=aberto_em,
                Atualizacao=aberto_em,
            )
            db.add(chamado)
            await db.flush()  # obtém o ID do chamado para vincular as mensagens

            # Insere as mensagens do chat em ordem, espaçadas em minutos a partir da abertura.
            for i, (autor_tipo, conteudo) in enumerate(item["chat"]):
                # Cliente e Supervisor têm autor; Sistema/IA não têm AutorID (nullable).
                if autor_tipo == AutorTipo.Cliente:
                    autor_id = clientes[item["cliente"]].ID
                elif autor_tipo == AutorTipo.Supervisor:
                    autor_id = supervisor.ID
                else:
                    autor_id = None
                db.add(Mensagem(
                    EmpresaID=empresa.ID,
                    ChamadoID=chamado.ID,
                    AutorID=autor_id,
                    AutorTipo=autor_tipo,
                    Conteudo=conteudo,
                    Criacao=aberto_em + timedelta(minutes=15 * (i + 1)),
                ))

        await db.commit()

    print(f"Seed concluído: {len(CLIENTES)} clientes, 1 supervisor e {len(CHAMADOS)} chamados criados.")
    print(f"Login dos clientes demo: <email>{DOMINIO_DEMO} / senha: {SENHA_PADRAO}")


async def cmd_semear(args) -> None:
    await _semear()


# `limpar-demo` — apaga os usuários de demonstração (marcados pelo domínio DOMINIO_DEMO) e tudo que
# depende deles (chamados, mensagens, refresh tokens, sessões revogadas). Item S10: existe para dar
# um jeito documentado de rotacionar/remover os dados de seed em ambientes compartilhados (ex.:
# staging), sem precisar resetar o banco inteiro. Idempotente: rodar sem usuários demo não faz nada.
async def _limpar_demo() -> None:
    async with AsyncSessionLocal() as db:
        resultado = await db.execute(select(Usuario.ID).where(Usuario.Email.like(f"%{DOMINIO_DEMO}")))
        ids_demo = [linha[0] for linha in resultado.all()]
        if not ids_demo:
            print("Nenhum usuário de demonstração encontrado — nada a limpar (idempotente).")
            return

        # Chamados onde um usuário demo é o Cliente OU o Supervisor (o supervisor de demonstração
        # também é um usuário demo, então este filtro cobre os dois lados do seed).
        resultado_chamados = await db.execute(
            select(Chamado.ID).where(
                Chamado.ClienteID.in_(ids_demo) | Chamado.SupervisorID.in_(ids_demo)
            )
        )
        ids_chamados = [linha[0] for linha in resultado_chamados.all()]

        # Ordem respeita as foreign keys: mensagens e chamados antes dos usuários que eles referenciam.
        if ids_chamados:
            await db.execute(delete(Mensagem).where(Mensagem.ChamadoID.in_(ids_chamados)))
            await db.execute(delete(Chamado).where(Chamado.ID.in_(ids_chamados)))
        await db.execute(delete(RefreshToken).where(RefreshToken.UsuarioID.in_(ids_demo)))
        await db.execute(delete(SessaoRevogada).where(SessaoRevogada.UsuarioID.in_(ids_demo)))
        await db.execute(delete(Usuario).where(Usuario.ID.in_(ids_demo)))
        await db.commit()

    print(f"Limpeza concluída: {len(ids_demo)} usuários demo e {len(ids_chamados)} chamados removidos.")


async def cmd_limpar_demo(args) -> None:
    await _limpar_demo()


# `aplicar-rls` — (re)aplica só as políticas de app/rls.sql (útil após mexer no arquivo de políticas
# sem precisar resetar o banco inteiro).
async def cmd_aplicar_rls(args) -> None:
    await aplicar_rls()
    print("Políticas de RLS aplicadas com sucesso.")


# `verificar-rls` — cria duas Empresas temporárias, grava dados em cada tenant e confirma que cada
# sessão só enxerga os próprios registros (filtros do app + RLS do Postgres). Limpa tudo ao final.
async def cmd_verificar_rls(args) -> None:
    tag = uuid.uuid4().hex[:8]
    empresa_a_id: uuid.UUID | None = None
    empresa_b_id: uuid.UUID | None = None
    rls_disponivel = not await _papel_ignora_rls()

    try:
        async with AsyncSessionLocal() as session:
            empresa_a = Empresa(Nome=f"Empresa A {tag}", CNPJ=f"tmp-a-{tag}", Status=EmpresaStatus.Ativa)
            empresa_b = Empresa(Nome=f"Empresa B {tag}", CNPJ=f"tmp-b-{tag}", Status=EmpresaStatus.Ativa)
            session.add_all([empresa_a, empresa_b])
            await session.commit()
            empresa_a_id = empresa_a.ID
            empresa_b_id = empresa_b.ID

        cond_a, user_a, chamado_a = await _criar_dados_tenant(empresa_a_id, f"A-{tag}")
        cond_b, user_b, chamado_b = await _criar_dados_tenant(empresa_b_id, f"B-{tag}")

        await _validar_filtros_aplicacao(empresa_a_id, cond_a, user_a, chamado_a)
        await _validar_filtros_aplicacao(empresa_b_id, cond_b, user_b, chamado_b)

        if rls_disponivel:
            await _validar_visibilidade_tenant(empresa_a_id, cond_a, user_a, chamado_a)
            await _validar_visibilidade_tenant(empresa_b_id, cond_b, user_b, chamado_b)
            print("OK: filtros por EmpresaID e RLS validados para Condominios, Usuarios e Chamados.")
        else:
            print("OK: filtros por EmpresaID validados. RLS do Postgres foi pulada porque o papel local bypassa RLS.")
    finally:
        if empresa_a_id:
            await _limpar_dados_tenant(empresa_a_id)
        if empresa_b_id:
            await _limpar_dados_tenant(empresa_b_id)

        async with AsyncSessionLocal() as session:
            if empresa_a_id:
                await session.execute(delete(Empresa).where(Empresa.ID == empresa_a_id))
            if empresa_b_id:
                await session.execute(delete(Empresa).where(Empresa.ID == empresa_b_id))
            await session.commit()


# ---------------------------------------------------------------------------
# CLI (argparse)
# ---------------------------------------------------------------------------

def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gerenciar_banco.py",
        description="Gerenciamento do banco de dados de desenvolvimento do FaciliChat.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_reset = sub.add_parser("reset", help="Dropa tudo, recria as tabelas e aplica a RLS")
    p_reset.add_argument("--semear", action="store_true", help="Também popula os dados de demonstração")
    p_reset.set_defaults(func=cmd_reset)

    p_empresa = sub.add_parser("criar-empresa", help="Cria a 1ª Empresa (tenant) + 1º Gestor")
    p_empresa.add_argument("nome", help="Nome da Empresa")
    p_empresa.add_argument("cnpj", help="CNPJ da Empresa")
    p_empresa.add_argument("gestor", help="Nome do Gestor")
    p_empresa.add_argument("email", help="E-mail do Gestor")
    p_empresa.add_argument("senha", help="Senha do Gestor")
    p_empresa.set_defaults(func=cmd_criar_empresa)

    # Bootstrap do Superadmin da plataforma. Separado de `criar-empresa` porque cria um perfil
    # global (não o Gestor de um tenant) e porque é idempotente — pode rodar de novo sem erro.
    p_super = sub.add_parser("criar-superadmin", help="Cria o 1º Superadmin da plataforma (Iugo)")
    p_super.add_argument("nome", help="Nome do Superadmin")
    p_super.add_argument("email", help="E-mail do Superadmin")
    p_super.add_argument("senha", help="Senha do Superadmin")
    p_super.add_argument(
        "--empresa-nome",
        default=EMPRESA_PLATAFORMA_NOME,
        help=f"Empresa que hospeda o Superadmin (padrão: {EMPRESA_PLATAFORMA_NOME})",
    )
    p_super.add_argument(
        "--cnpj",
        default=EMPRESA_PLATAFORMA_CNPJ_PADRAO,
        help="CNPJ da Empresa da plataforma — o padrão é placeholder de dev; informe o real em produção",
    )
    p_super.set_defaults(func=cmd_criar_superadmin)

    p_semear = sub.add_parser("semear", help="Popula dados de demonstração (idempotente; recusa em AMBIENTE=producao)")
    p_semear.set_defaults(func=cmd_semear)

    p_limpar_demo = sub.add_parser("limpar-demo", help="Remove usuários/chamados de demonstração (idempotente)")
    p_limpar_demo.set_defaults(func=cmd_limpar_demo)

    p_rls = sub.add_parser("aplicar-rls", help="(Re)aplica as políticas de app/rls.sql")
    p_rls.set_defaults(func=cmd_aplicar_rls)

    p_verif = sub.add_parser("verificar-rls", help="Testa o isolamento multi-tenant")
    p_verif.set_defaults(func=cmd_verificar_rls)

    return parser


def main() -> None:
    args = construir_parser().parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
