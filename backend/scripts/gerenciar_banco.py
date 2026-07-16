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
#   python scripts/gerenciar_banco.py reset [--semear]     # zera o banco: dropa tudo, recria, cria o
#                                                           # papel restrito da API e aplica RLS
#   python scripts/gerenciar_banco.py criar-empresa "<Nome>" <CNPJ> "<Gestor>" <email> <senha>
#   python scripts/gerenciar_banco.py criar-superadmin "<Nome>" <email> <senha>   # Superadmin da Iugo (avulso/credenciais customizadas)
#   python scripts/gerenciar_banco.py semear               # popula base de testes (idempotente; recusa em AMBIENTE=producao)
#   python scripts/gerenciar_banco.py limpar-demo          # remove usuários/chamados de demonstração (idempotente)
#   python scripts/gerenciar_banco.py aplicar-rls          # garante o papel restrito e (re)aplica app/rls.sql
#   python scripts/gerenciar_banco.py verificar-rls        # testa o isolamento multi-tenant com o papel restrito
#
# Papéis do Postgres (item F08-01): este script conecta com DOIS papéis, lidos de variáveis
# distintas — nunca o mesmo papel que a API usa. DATABASE_URL_ADMIN é o papel administrativo (dono
# do schema/tabelas), usado aqui só para DDL (criar/dropar schema, criar tabelas, criar o papel
# restrito e aplicar RLS/grants). DATABASE_URL é o papel RESTRITO — o mesmo que a API usa em
# produção/dev — usado para semear dados e para `verificar-rls` provar o isolamento com a
# credencial real da aplicação. Ver backend/.env.example e docker-compose.yml.
#
# Fluxo típico de dev do zero:
#   reset  →  criar-empresa ...  →  semear
#
# `semear` agora entrega a base de testes completa num único passo: além do tenant principal
# (clientes/supervisor/chamados), cria também o Superadmin padrão da plataforma e uma 2ª Empresa de
# demonstração com 3 supervisores — sem exigir `criar-superadmin` manual. Tudo idempotente peça por
# peça: rodar de novo só completa o que faltar (ex.: um Superadmin criado à mão antes continua único).

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
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.banco_dados import AsyncSessionLocal, Base
from app.configuracoes import configuracoes
from app.modelos.CategoriaChamado import CategoriaChamado
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

# Engine ADMINISTRATIVO (item F08-01) — dono do schema/tabelas, usado só por este script para DDL
# (dropar/criar schema, criar tabelas, criar o papel restrito e aplicar RLS/grants). `AsyncSessionLocal`
# (importado de app.banco_dados) continua ligado ao papel RESTRITO — o mesmo que a API usa — e segue
# reservado para semear dados e para `verificar-rls` provar o isolamento com a credencial real.
engine_admin = create_async_engine(configuracoes.DATABASE_URL_ADMIN, echo=configuracoes.DEBUG)

# Sessões administrativas (F08-01): usadas pelas operações deste script que legitimamente cruzam
# tenants — bootstrap de Empresa/Superadmin, seed e limpeza de demonstração. Sob o papel restrito
# (AsyncSessionLocal) essas escritas seriam bloqueadas pela RLS, porque nenhuma delas representa uma
# requisição real da API escopada a um único `app.empresa_id`.
AsyncSessionLocalAdmin = async_sessionmaker(engine_admin, expire_on_commit=False)

# Só letras/números/underscore, começando por letra ou underscore — o nome do papel restrito vem de
# DATABASE_URL (configurável via APP_DB_USER) e é interpolado em DDL (CREATE ROLE/GRANT), que não
# aceita parâmetros de identificador; validar aqui evita que um valor malformado gere SQL inválido.
IDENTIFICADOR_PAPEL_VALIDO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


# Escapa um literal de string para uso dentro de DDL (dobra aspas simples) — necessário porque
# CREATE ROLE/ALTER ROLE ... PASSWORD exige um literal na sintaxe, sem suporte a bind parameters.
def _escapar_literal_sql(valor: str) -> str:
    return valor.replace("'", "''")


# Lê o papel e a senha que a API usa (DATABASE_URL) — é esse papel que precisa existir no Postgres
# com privilégios restritos para o isolamento multi-tenant valer de fato (F08-01).
def _credenciais_papel_app() -> tuple[str, str]:
    url = make_url(configuracoes.DATABASE_URL)
    if not url.username or url.password is None:
        raise SystemExit(
            "DATABASE_URL precisa incluir usuário e senha do papel restrito da API (ver "
            "backend/.env.example)."
        )
    if not IDENTIFICADOR_PAPEL_VALIDO.match(url.username):
        raise SystemExit(
            f"Usuário de DATABASE_URL inválido como nome de papel do Postgres: {url.username!r}. "
            "Use apenas letras, números e _ (começando por letra ou _)."
        )
    return url.username, url.password


# Garante que o papel restrito da API existe no Postgres, com a senha atual de DATABASE_URL e sem
# nenhum privilégio capaz de ignorar RLS — e concede só o necessário para operar as tabelas do
# schema. Idempotente: pode rodar de novo (ex.: depois de trocar a senha) sem duplicar nada.
# Precisa rodar DEPOIS de `criar_tabelas()` (as tabelas precisam existir para "ALL TABLES" e "ALL
# SEQUENCES" alcançarem algo) e via `engine_admin` (só o dono do schema pode criar papéis e conceder
# privilégios sobre objetos que não são dele).
async def garantir_papel_app() -> None:
    papel, senha = _credenciais_papel_app()
    senha_escapada = _escapar_literal_sql(senha)

    async with engine_admin.begin() as conn:
        await conn.execute(text(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{papel}') THEN
                    CREATE ROLE "{papel}" LOGIN PASSWORD '{senha_escapada}'
                        NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOREPLICATION;
                ELSE
                    ALTER ROLE "{papel}" WITH LOGIN PASSWORD '{senha_escapada}'
                        NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOREPLICATION;
                END IF;
            END
            $$;
            """
        ))
        await conn.execute(text(f'GRANT USAGE ON SCHEMA public TO "{papel}"'))
        await conn.execute(text(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "{papel}"'))
        await conn.execute(text(f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "{papel}"'))


# ---------------------------------------------------------------------------
# Dados de demonstração (usados pelo subcomando `semear`)
# ---------------------------------------------------------------------------

# Todos os usuários de demonstração usam esta senha; e-mails ficam no domínio DOMINIO_DEMO,
# que também serve de marcador de idempotência do seed.
# Atualizada no item M1 para cumprir a política de senha (mínimo 15 caracteres — OWASP sem MFA):
# a senha antiga "Senha123" (8) ficaria abaixo do mínimo que a própria API passou a exigir.
#Perfil	Nome	Usuário				Empresa
#Superadmin	Superadmin Demo	superadmin@facilichat.dev	Iugo Performance (criado por `semear`, sem CNPJ real)
#Gestor	Gestor Demo	admin@facilichat.dev		1ª Empresa (criada por `criar-empresa`, nome livre)
#Supervisor	Roberto Supervisor	supervisor@demo.facilichat.dev	1ª Empresa
#Cliente	Ana Costa	ana@demo.facilichat.dev	1ª Empresa
#Cliente	Carlos Lima	carlos@demo.facilichat.dev	1ª Empresa
#Cliente	João Souza	joao@demo.facilichat.dev	1ª Empresa
#Cliente	Maria Silva	maria@demo.facilichat.dev	1ª Empresa
#Gestor	Gestora Horizonte	gestora.horizonte@demo.facilichat.dev	Horizonte Facilities (2ª Empresa, criada por `semear`)
#Supervisor	Marcos Andrade	marcos.andrade@demo.facilichat.dev	Horizonte Facilities
#Supervisor	Patricia Nunes	patricia.nunes@demo.facilichat.dev	Horizonte Facilities
#Supervisor	Diego Ramos	diego.ramos@demo.facilichat.dev	Horizonte Facilities
#Cliente	Fernanda Alves	fernanda.alves@demo.facilichat.dev	Horizonte Facilities
#Cliente	Ricardo Teixeira	ricardo.teixeira@demo.facilichat.dev	Horizonte Facilities
#Cliente	Juliana Martins	juliana.martins@demo.facilichat.dev	Horizonte Facilities



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
# 2ª Empresa de demonstração — mesmo domínio DOMINIO_DEMO, tenant diferente. Existe para dar
# visualização com MAIS de um supervisor por Empresa (o tenant principal acima só tem um), o que
# páginas como "Desempenho por supervisor" e "Supervisores" precisam para mostrar comparação real
# entre pessoas — não só um card sozinho.
# ---------------------------------------------------------------------------

EMPRESA2_NOME = "Horizonte Facilities"
EMPRESA2_CNPJ = "23.456.789/0001-01"
EMPRESA2_GESTOR_NOME = "Gestora Horizonte"
EMPRESA2_GESTOR_EMAIL = f"gestora.horizonte{DOMINIO_DEMO}"

# Três supervisores com desempenho deliberadamente desigual (ver CHAMADOS_EMPRESA2): um só com
# chamados concluídos, um misto, um com chamados parados/críticos — para o painel do Gestor
# renderizar estados diferentes (bom desempenho, atenção, gargalo) sem precisar de dados reais.
SUPERVISORES_EMPRESA2 = [
    {"Nome": "Marcos Andrade",  "Email": f"marcos.andrade{DOMINIO_DEMO}"},
    {"Nome": "Patricia Nunes",  "Email": f"patricia.nunes{DOMINIO_DEMO}"},
    {"Nome": "Diego Ramos",     "Email": f"diego.ramos{DOMINIO_DEMO}"},
]

CLIENTES_EMPRESA2 = [
    {"Nome": "Fernanda Alves",   "Email": f"fernanda.alves{DOMINIO_DEMO}",  "Condominio": "Ed. Torres do Parque"},
    {"Nome": "Ricardo Teixeira", "Email": f"ricardo.teixeira{DOMINIO_DEMO}", "Condominio": "Cond. Villa Bela"},
    {"Nome": "Juliana Martins",  "Email": f"juliana.martins{DOMINIO_DEMO}",  "Condominio": "Res. Monte Azul"},
]

# Índice de "supervisor" aqui aponta para SUPERVISORES_EMPRESA2 (0, 1 ou 2) — diferente do tenant
# principal, que só usa True/False porque tem um único supervisor (ver _resolver_supervisor).
CHAMADOS_EMPRESA2 = [
    # Marcos (0): os 3 concluídos — supervisor de alta performance.
    {
        "cliente": 0, "fila": ChamadoFila.Operacional, "categoria": "Elétrica",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Concluido,
        "dias": 5, "supervisor": 0,
        "resumo": "Troca das lâmpadas queimadas do hall de entrada do bloco A.",
        "chat": [
            (AutorTipo.Cliente, "As lâmpadas do hall de entrada queimaram, dá para trocar?"),
            (AutorTipo.Supervisor, "Vou passar lá hoje ainda com a equipe de manutenção."),
            (AutorTipo.Sistema, "Seu chamado foi concluído. Qualquer coisa, estamos por aqui."),
        ],
    },
    {
        "cliente": 1, "fila": ChamadoFila.Operacional, "categoria": "Pintura",
        "prioridade": ChamadoPrioridade.Baixa, "status": ChamadoStatus.Concluido,
        "dias": 9, "supervisor": 0,
        "resumo": "Repintura da fachada lateral do bloco B, descascando há meses.",
        "chat": [
            (AutorTipo.Cliente, "A fachada lateral está descascando, podemos programar a repintura?"),
            (AutorTipo.Supervisor, "Já orçamos e a equipe começa na próxima semana."),
            (AutorTipo.Sistema, "Seu chamado foi concluído. Qualquer coisa, estamos por aqui."),
        ],
    },
    {
        "cliente": 2, "fila": ChamadoFila.Operacional, "categoria": "Jardinagem",
        "prioridade": ChamadoPrioridade.Baixa, "status": ChamadoStatus.Concluido,
        "dias": 3, "supervisor": 0,
        "resumo": "Poda das árvores próximas ao playground, galhos baixos demais.",
        "chat": [
            (AutorTipo.Cliente, "Os galhos perto do playground estão baixos, dá risco para as crianças."),
            (AutorTipo.Supervisor, "Podamos hoje de manhã, antes do horário de uso do playground."),
            (AutorTipo.Sistema, "Seu chamado foi concluído. Qualquer coisa, estamos por aqui."),
        ],
    },
    # Patricia (1): mix — desempenho médio (1 concluído, 1 recebido, 1 crítico em andamento).
    {
        "cliente": 0, "fila": ChamadoFila.Operacional, "categoria": "Hidráulica",
        "prioridade": ChamadoPrioridade.Critica, "status": ChamadoStatus.EmAndamento,
        "dias": 0, "supervisor": 1,
        "resumo": "Vazamento na caixa d'água do bloco A, pressão caindo nos apartamentos altos.",
        "chat": [
            (AutorTipo.Cliente, "A água está fraca nos andares altos, acho que tem vazamento na caixa d'água."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
            (AutorTipo.Supervisor, "Confirmado, o encanador está subindo para a caixa d'água agora."),
        ],
    },
    {
        "cliente": 1, "fila": ChamadoFila.Financeiro, "categoria": "Cobrança",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Recebido,
        "dias": 2, "supervisor": 1,
        "resumo": "Taxa extra no boleto deste mês que o morador não reconhece.",
        "chat": [
            (AutorTipo.Cliente, "Tem uma taxa extra no meu boleto que eu não sei o que é."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
        ],
    },
    {
        "cliente": 2, "fila": ChamadoFila.RH, "categoria": "Escala",
        "prioridade": ChamadoPrioridade.Media, "status": ChamadoStatus.Concluido,
        "dias": 6, "supervisor": 1,
        "resumo": "Ajuste da escala de plantão da portaria no feriado.",
        "chat": [
            (AutorTipo.Cliente, "Como fica o plantão da portaria no feriado?"),
            (AutorTipo.Supervisor, "Já ajustei a escala e confirmei com a equipe."),
            (AutorTipo.Sistema, "Seu chamado foi concluído. Qualquer coisa, estamos por aqui."),
        ],
    },
    # Diego (2): nenhum concluído — supervisor em estado de atenção/gargalo (chamados parados).
    {
        "cliente": 0, "fila": ChamadoFila.Operacional, "categoria": "Elevador",
        "prioridade": ChamadoPrioridade.Critica, "status": ChamadoStatus.EmAndamento,
        "dias": 4, "supervisor": 2,
        "resumo": "Elevador social do bloco C fazendo ruído forte e parando entre andares.",
        "chat": [
            (AutorTipo.Cliente, "O elevador social está fazendo um barulho estranho e parou entre andares de novo."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
            (AutorTipo.Supervisor, "Chamei a manutenção do elevador, aguardando confirmação da visita."),
        ],
    },
    {
        "cliente": 1, "fila": ChamadoFila.Operacional, "categoria": "Portaria",
        "prioridade": ChamadoPrioridade.Alta, "status": ChamadoStatus.Recebido,
        "dias": 3, "supervisor": 2,
        "resumo": "Câmera da portaria principal fora do ar desde ontem.",
        "chat": [
            (AutorTipo.Cliente, "A câmera da portaria principal está fora do ar desde ontem, isso é sério."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
        ],
    },
    {
        "cliente": 2, "fila": ChamadoFila.Operacional, "categoria": "Segurança",
        "prioridade": ChamadoPrioridade.Alta, "status": ChamadoStatus.EmAndamento,
        "dias": 5, "supervisor": 2,
        "resumo": "Cerca elétrica do muro dos fundos desarmada há dias.",
        "chat": [
            (AutorTipo.Cliente, "A cerca elétrica dos fundos está desarmada, isso é uma brecha de segurança."),
            (AutorTipo.Sistema, "Recebemos sua solicitação. Ela está registrada e já foi encaminhada à equipe."),
            (AutorTipo.Supervisor, "Vou verificar o disjuntor da cerca ainda hoje."),
        ],
    },
]


# ---------------------------------------------------------------------------
# Helpers de schema e RLS
# ---------------------------------------------------------------------------

# Cria todas as tabelas/colunas a partir dos modelos atuais (idempotente — não recria o existente).
# Usa o engine ADMINISTRATIVO (F08-01): CREATE TABLE exige posse/privilégio de CREATE no schema, que
# o papel restrito da API deliberadamente não tem.
async def criar_tabelas() -> None:
    async with engine_admin.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Lê app/rls.sql e executa cada comando isoladamente (asyncpg não aceita múltiplos statements por
# chamada). O SQL usa DROP POLICY IF EXISTS, então é idempotente. Usa o engine ADMINISTRATIVO
# (F08-01): ALTER TABLE ... ENABLE/FORCE ROW LEVEL SECURITY e CREATE POLICY exigem ser o dono da
# tabela (ou superusuário) — privilégio que o papel restrito da API não tem.
async def aplicar_rls() -> None:
    with open(CAMINHO_RLS_SQL, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    script_sem_comentarios = re.sub(r"(?m)^\s*--.*$", "", script_sql)
    async with engine_admin.begin() as conn:
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


# Busca uma Categoria do catálogo do tenant pelo nome (case-insensitive) ou a cria.
async def _obter_ou_criar_categoria(db, empresa_id, nome):
    resultado = await db.execute(
        select(CategoriaChamado).where(
            CategoriaChamado.EmpresaID == empresa_id,
            func.lower(CategoriaChamado.Nome) == nome.lower(),
        )
    )
    categoria = resultado.scalar_one_or_none()
    if categoria:
        return categoria

    categoria = CategoriaChamado(EmpresaID=empresa_id, Nome=nome)
    db.add(categoria)
    await db.flush()
    return categoria


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


# Busca uma Empresa de demonstração pelo nome ou a cria junto com o próprio Gestor — mesma lógica de
# `criar-empresa`, mas idempotente (usada pelo seed para a 2ª Empresa, que ninguém cria à mão).
async def _obter_ou_criar_empresa_demo(db, nome, cnpj, gestor_nome, gestor_email):
    resultado = await db.execute(select(Empresa).where(Empresa.Nome == nome))
    empresa = resultado.scalar_one_or_none()
    if empresa:
        return empresa

    empresa = Empresa(Nome=nome, CNPJ=cnpj, Status=EmpresaStatus.Ativa)
    db.add(empresa)
    await db.flush()  # empresa.ID preenchido antes de criar o Gestor que o referencia

    gestor = Usuario(
        EmpresaID=empresa.ID,
        Nome=gestor_nome,
        Email=gestor_email,
        SenhaHash=pwd.hash(SENHA_PADRAO),
        Funcao=UsuarioFuncao.Gestor,
    )
    db.add(gestor)
    await db.flush()
    print(f"2ª Empresa de demonstração criada: {nome} ({cnpj}) — Gestor: {gestor_email}")
    return empresa


# Resolve qual supervisor (se algum) fica em `Chamado.SupervisorID` e autor das mensagens de chat.
# `indice` aceita True (compatibilidade com o tenant principal, que só tem 1 supervisor → índice 0),
# um inteiro (tenant com vários supervisores, ver CHAMADOS_EMPRESA2) ou False/None (sem atribuição).
def _resolver_supervisor(indice, supervisores):
    if not indice and indice != 0:
        return None
    return supervisores[0 if indice is True else indice]


# Popula um tenant (Empresa) com clientes, supervisores e chamados/chat de demonstração. Extraído
# para ser reaproveitado por mais de uma Empresa no seed (tenant principal + 2ª Empresa de demo) sem
# duplicar a lógica de criação de chamado e histórico de chat.
async def _semear_tenant(db, empresa_id, clientes_def, supervisores_def, chamados_def):
    supervisores = [
        await _obter_ou_criar_usuario(db, empresa_id, s["Nome"], s["Email"], UsuarioFuncao.Supervisor)
        for s in supervisores_def
    ]
    clientes = [
        await _obter_ou_criar_usuario(db, empresa_id, c["Nome"], c["Email"], UsuarioFuncao.Cliente, c["Condominio"])
        for c in clientes_def
    ]

    agora = agoraUtc()

    # Cria cada chamado com data de abertura escalonada e o histórico de chat correspondente.
    for item in chamados_def:
        categoria = await _obter_ou_criar_categoria(db, empresa_id, item["categoria"])
        aberto_em = agora - timedelta(days=item["dias"], hours=2)
        supervisor = _resolver_supervisor(item["supervisor"], supervisores)
        chamado = Chamado(
            EmpresaID=empresa_id,
            ClienteID=clientes[item["cliente"]].ID,
            SupervisorID=supervisor.ID if supervisor else None,
            Fila=item["fila"],
            CategoriaID=categoria.ID,
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
                autor_id = supervisor.ID  # só há mensagem de Supervisor quando ele está atribuído
            else:
                autor_id = None
            db.add(Mensagem(
                EmpresaID=empresa_id,
                ChamadoID=chamado.ID,
                AutorID=autor_id,
                AutorTipo=autor_tipo,
                Conteudo=conteudo,
                Criacao=aberto_em + timedelta(minutes=15 * (i + 1)),
            ))

    return clientes, supervisores


# Diz se o tenant já tem chamados de demonstração (Cliente com e-mail no DOMINIO_DEMO) — critério de
# idempotência por Empresa, para o seed poder completar só o que falta em vez de tudo ou nada.
async def _chamados_demo_existem(db, empresa_id) -> bool:
    resultado = await db.execute(
        select(func.count(Chamado.ID))
        .join(Usuario, Usuario.ID == Chamado.ClienteID)
        .where(Usuario.Email.like(f"%{DOMINIO_DEMO}"), Chamado.EmpresaID == empresa_id)
    )
    return (resultado.scalar() or 0) > 0


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

        categoria = CategoriaChamado(EmpresaID=empresa_id, Nome=f"Teste RLS {rotulo}")
        session.add(categoria)
        await session.flush()

        chamado = Chamado(
            EmpresaID=empresa_id,
            ClienteID=usuario.ID,
            Fila=ChamadoFila.Operacional,
            CategoriaID=categoria.ID,
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


# Confirma a camada do app: mesmo com dois tenants, queries por EmpresaID retornam só o bloco
# pedido. Usa a sessão ADMINISTRATIVA de propósito — o objetivo é testar a trava PRIMÁRIA (filtro
# explícito por EmpresaID) isolada da RLS; com o papel restrito, a RLS mascararia qualquer resultado
# sem `app.empresa_id` definido, e o teste deixaria de provar o que se propõe a provar.
async def _validar_filtros_aplicacao(empresa_id, esperado_cond, esperado_user, esperado_chamado):
    async with AsyncSessionLocalAdmin() as session:
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


# Confirma o comportamento fail-closed da política (F08-01, aceite explícito): sem `app.empresa_id`
# definido na sessão, nenhuma linha das tabelas tenant é visível — nem as de outros tenants criados
# neste mesmo teste. Usa AsyncSessionLocal (papel restrito da API) sem passar por `_sessao_tenant`,
# que sempre define a variável — aqui o ponto é justamente testar a ausência dela.
async def _validar_bloqueio_sem_tenant() -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(text("RESET app.empresa_id"))
        condominios = (await session.execute(select(Condominio.ID))).scalars().all()
        usuarios = (await session.execute(select(Usuario.ID))).scalars().all()
        chamados = (await session.execute(select(Chamado.ID))).scalars().all()

    assert condominios == [], f"Sem app.empresa_id, Condominios deveria estar vazio: {condominios}"
    assert usuarios == [], f"Sem app.empresa_id, Usuarios deveria estar vazio: {usuarios}"
    assert chamados == [], f"Sem app.empresa_id, Chamados deveria estar vazio: {chamados}"


# Remove os dados temporários no mesmo tenant que os criou (respeitando a RLS durante a limpeza).
async def _limpar_dados_tenant(empresa_id: uuid.UUID) -> None:
    async with _sessao_tenant(empresa_id) as session:
        await session.execute(delete(Chamado).where(Chamado.EmpresaID == empresa_id))
        await session.execute(delete(CategoriaChamado).where(CategoriaChamado.EmpresaID == empresa_id))
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
    # Todo o DDL de reset roda no engine ADMINISTRATIVO (F08-01) — o papel restrito da API não tem
    # (e não deve ter) privilégio para dropar/criar schema.
    async with engine_admin.begin() as conn:
        # DROP SCHEMA ... CASCADE remove tudo que pertence ao schema (inclusive os tipos ENUM criados
        # pelo SQLAlchemy); recriar deixa o banco limpo para o create_all reconstruir do zero.
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await criar_tabelas()
    # Recria as tabelas zera todos os grants do schema anterior — reconceder ao papel restrito
    # antes de aplicar as políticas de RLS.
    await garantir_papel_app()
    await aplicar_rls()
    print("Banco resetado: schema recriado, papel restrito garantido e RLS aplicada.")

    if args.semear:
        await _semear()


# `criar-empresa` — bootstrap da primeira Empresa (tenant) + primeiro Gestor, numa única transação
# (se o Gestor falhar, a Empresa também não é persistida — evita tenant órfão). É o ponto de entrada
# do sistema, já que o cadastro público fica fechado e /usuarios/equipe exige um Gestor autenticado.
# Usa a sessão ADMINISTRATIVA (F08-01): é um bootstrap fora de qualquer tenant ainda existente — sob
# o papel restrito, a RLS bloquearia o INSERT em "Usuarios" por não haver `app.empresa_id` definido.
async def cmd_criar_empresa(args) -> None:
    await criar_tabelas()  # garante que as tabelas existem (idempotente)

    async with AsyncSessionLocalAdmin() as db:
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

# Credenciais do Superadmin padrão criado automaticamente por `semear` — mesma convenção de senha
# dos demais usuários de demonstração (SENHA_PADRAO). Quem precisar de credenciais diferentes usa
# `criar-superadmin` diretamente, que aceita nome/e-mail/senha customizados.
SUPERADMIN_NOME_PADRAO = "Superadmin Demo"
SUPERADMIN_EMAIL_PADRAO = "superadmin@facilichat.dev"


# Bootstrap do Superadmin (Iugo Performance) dentro de uma sessão/transação já aberta pelo chamador
# — não abre sessão nem comita, para poder compor com `_semear` (que faz tudo numa única transação)
# e também com `cmd_criar_superadmin` (que abre sua própria sessão e comita sozinho).
#
# Por que existe: `POST /plataforma/empresas` exige um Superadmin já autenticado (`exigirSuperadmin`
# em rotas/Plataforma.py), e nada no backend criava o primeiro — um ovo-e-galinha que travava o
# acesso ao painel de plataforma.
#
# Idempotente: pode rodar de novo (inclusive dentro do `semear`) sem duplicar nada.
async def _bootstrap_superadmin(db, nome, email, senha, empresa_nome, cnpj) -> None:
    # --- Empresa da plataforma: reutiliza se já existir -------------------------------------
    resultado = await db.execute(select(Empresa).where(Empresa.Nome == empresa_nome))
    empresa = resultado.scalar_one_or_none()

    if empresa is None:
        empresa = Empresa(Nome=empresa_nome, CNPJ=cnpj, Status=EmpresaStatus.Ativa, EhPlataforma=True)
        db.add(empresa)
        await db.flush()  # empresa.ID preenchido antes de o Usuario referenciá-lo
        print(f"Empresa da plataforma criada: {empresa_nome} ({cnpj})")
    else:
        # Empresa suspensa faz `obterUsuarioAtual` responder 403 — o Superadmin ficaria trancado
        # para fora da própria plataforma. Reativar é a única saída sensata aqui.
        if empresa.Status == EmpresaStatus.Suspensa:
            empresa.Status = EmpresaStatus.Ativa
            print(f"Empresa da plataforma reativada: {empresa.Nome}")
        # Corrige instalações que rodaram este bootstrap antes do campo existir (ambiente gravado
        # sem o flag) — reutilizar a Empresa da Iugo sempre a marca como plataforma.
        if not empresa.EhPlataforma:
            empresa.EhPlataforma = True
            print("Empresa da plataforma marcada como EhPlataforma=True (correção)")

    # --- Usuário Superadmin ------------------------------------------------------------------
    resultado = await db.execute(select(Usuario).where(Usuario.Email == email))
    usuario = resultado.scalar_one_or_none()

    if usuario is not None:
        # Já é Superadmin: nada a fazer. É o caminho da idempotência (rodar 2x é seguro).
        if usuario.Funcao == UsuarioFuncao.Superadmin:
            print(f"Superadmin já existia, nada a fazer: {email}")
            return

        # NÃO promover um usuário existente. Um comando de bootstrap que transforma qualquer
        # conta em Superadmin é escalonamento de privilégio disfarçado — quem tiver acesso ao
        # shell promoveria o próprio Cliente. Falha alto e explícito.
        raise SystemExit(
            f"ERRO: o e-mail {email} já pertence a um usuário com perfil "
            f"{usuario.Funcao.value}. Este comando não promove usuários existentes a "
            f"Superadmin. Use outro e-mail."
        )

    superadmin = Usuario(
        EmpresaID=empresa.ID,
        Nome=nome,
        Email=email,
        SenhaHash=pwd.hash(senha),  # argon2, mesmo hasher das rotas
        Funcao=UsuarioFuncao.Superadmin,
    )
    db.add(superadmin)
    print(f"Superadmin criado com sucesso: {email} (Empresa: {empresa_nome})")


# `criar-superadmin` — comando avulso para provisionar um Superadmin com credenciais customizadas
# (ex.: produção, com `--cnpj` real). Abre sua própria sessão/transação em torno de `_bootstrap_superadmin`.
# Sessão ADMINISTRATIVA (F08-01): o Superadmin não pertence a um tenant comum, e o bootstrap
# recorrente da Empresa da plataforma não é uma requisição real da API escopada por `app.empresa_id`.
async def cmd_criar_superadmin(args) -> None:
    await criar_tabelas()  # garante que as tabelas existem (idempotente)

    async with AsyncSessionLocalAdmin() as db:
        await _bootstrap_superadmin(db, args.nome, args.email, args.senha, args.empresa_nome, args.cnpj)
        await db.commit()


# `semear` — entrega a base de testes completa: tenant principal (clientes/supervisor/chamados),
# 2ª Empresa de demonstração com 3 supervisores (melhor visualização de comparação entre eles) e o
# Superadmin padrão da plataforma. Idempotente peça por peça — rodar de novo só completa o que
# faltar, nunca duplica (cada bloco checa a própria condição antes de agir). Sessão ADMINISTRATIVA
# (F08-01): semeia DOIS tenants na mesma execução, o que a RLS do papel restrito impediria — não é
# uma simulação de requisição real da API, que sempre opera dentro de um único `app.empresa_id`.
async def _semear() -> None:
    # Guarda de ambiente (item S10): usuários demo nascem com SENHA_PADRAO, previsível e igual em
    # toda instalação — inaceitável em produção. Falha cedo, sem sequer tocar no banco, em vez de
    # confiar em alguém lembrar de não rodar este comando lá.
    if configuracoes.AMBIENTE == "producao":
        print("Recusado: AMBIENTE=producao. `semear` só roda em dev/staging (ver docs/setup.md).")
        sys.exit(1)

    await criar_tabelas()

    async with AsyncSessionLocalAdmin() as db:
        # --- Tenant principal: reaproveita a Empresa criada por `criar-empresa` -------------
        resultado_empresa = await db.execute(
            select(Empresa).where(Empresa.EhPlataforma.is_(False)).order_by(Empresa.Criacao).limit(1)
        )
        empresa = resultado_empresa.scalar_one_or_none()
        if not empresa:
            print("Nenhuma Empresa encontrada — rode `criar-empresa` antes de semear.")
            return

        if await _chamados_demo_existem(db, empresa.ID):
            print(f"Tenant principal ({empresa.Nome}) já tem chamados demo — pulando (idempotente).")
        else:
            await _semear_tenant(db, empresa.ID, CLIENTES, [SUPERVISOR], CHAMADOS)
            print(f"Tenant principal semeado: {len(CLIENTES)} clientes, 1 supervisor e {len(CHAMADOS)} chamados.")

        # --- 2ª Empresa de demonstração: cria o próprio tenant + Gestor se não existir --------
        empresa2 = await _obter_ou_criar_empresa_demo(
            db, EMPRESA2_NOME, EMPRESA2_CNPJ, EMPRESA2_GESTOR_NOME, EMPRESA2_GESTOR_EMAIL
        )
        if await _chamados_demo_existem(db, empresa2.ID):
            print(f"2ª Empresa ({empresa2.Nome}) já tem chamados demo — pulando (idempotente).")
        else:
            await _semear_tenant(db, empresa2.ID, CLIENTES_EMPRESA2, SUPERVISORES_EMPRESA2, CHAMADOS_EMPRESA2)
            print(
                f"2ª Empresa semeada: {len(CLIENTES_EMPRESA2)} clientes, "
                f"{len(SUPERVISORES_EMPRESA2)} supervisores e {len(CHAMADOS_EMPRESA2)} chamados."
            )

        # --- Superadmin padrão da plataforma --------------------------------------------------
        await _bootstrap_superadmin(
            db, SUPERADMIN_NOME_PADRAO, SUPERADMIN_EMAIL_PADRAO, SENHA_PADRAO,
            EMPRESA_PLATAFORMA_NOME, EMPRESA_PLATAFORMA_CNPJ_PADRAO,
        )

        await db.commit()

    print(f"Login dos clientes/supervisores/gestores demo: <email>{DOMINIO_DEMO} / senha: {SENHA_PADRAO}")
    print(f"Login do Superadmin: {SUPERADMIN_EMAIL_PADRAO} / senha: {SENHA_PADRAO}")


async def cmd_semear(args) -> None:
    await _semear()


# `limpar-demo` — apaga os usuários de demonstração (marcados pelo domínio DOMINIO_DEMO) e tudo que
# depende deles (chamados, mensagens, refresh tokens, sessões revogadas). Item S10: existe para dar
# um jeito documentado de rotacionar/remover os dados de seed em ambientes compartilhados (ex.:
# staging), sem precisar resetar o banco inteiro. Idempotente: rodar sem usuários demo não faz nada.
# Sessão ADMINISTRATIVA (F08-01): apaga usuários demo de QUALQUER tenant numa só passada — a RLS do
# papel restrito, escopada a um único `app.empresa_id`, não permitiria esse alcance cross-tenant.
async def _limpar_demo() -> None:
    async with AsyncSessionLocalAdmin() as db:
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


# `aplicar-rls` — garante o papel restrito da API (F08-01) e (re)aplica só as políticas de
# app/rls.sql (útil após mexer no arquivo de políticas ou trocar a senha em DATABASE_URL, sem
# precisar resetar o banco inteiro).
async def cmd_aplicar_rls(args) -> None:
    await garantir_papel_app()
    await aplicar_rls()
    print("Papel restrito garantido e políticas de RLS aplicadas com sucesso.")


# `verificar-rls` — cria duas Empresas temporárias, grava dados em cada tenant e confirma que cada
# sessão só enxerga os próprios registros (filtros do app + RLS do Postgres), além do bloqueio
# fail-closed sem `app.empresa_id`. Usa AsyncSessionLocal (DATABASE_URL) para provar o isolamento
# com a MESMA credencial que a API usa — não o papel administrativo. Limpa tudo ao final.
#
# Item F08-01 (aceite explícito): reprova — não pula — se o papel conectado ignora RLS
# (superuser/bypassrls), porque nesse caso a validação de RLS não provaria nada.
async def cmd_verificar_rls(args) -> None:
    if await _papel_ignora_rls():
        raise SystemExit(
            "REPROVADO: o papel conectado via DATABASE_URL ignora RLS (é superuser ou tem "
            "BYPASSRLS). A API deve conectar com o papel restrito criado por "
            "`gerenciar_banco.py reset`/`aplicar-rls` — ajuste DATABASE_URL antes de verificar."
        )

    tag = uuid.uuid4().hex[:8]
    empresa_a_id: uuid.UUID | None = None
    empresa_b_id: uuid.UUID | None = None

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
        await _validar_visibilidade_tenant(empresa_a_id, cond_a, user_a, chamado_a)
        await _validar_visibilidade_tenant(empresa_b_id, cond_b, user_b, chamado_b)
        await _validar_bloqueio_sem_tenant()
        print(
            "OK: filtros por EmpresaID, RLS e bloqueio fail-closed sem app.empresa_id validados "
            "para Condominios, Usuarios e Chamados."
        )
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
