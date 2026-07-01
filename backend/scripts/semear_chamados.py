# Script de seed de DADOS DE ANÁLISE — popula o banco com chamados realistas para inspeção visual.
#
# Por que existe: para analisar o produto em funcionamento (painel do gestor, filas, status, chat)
# é preciso ter chamados no banco. Este script cria clientes de demonstração, um supervisor e um
# conjunto variado de chamados cobrindo as 3 filas (Operacional, RH, Financeiro), todos os status
# (Recebido, EmAndamento, Agendado, Concluido, Cancelado) e as 4 prioridades, cada um com o histórico
# de chat (Mensagens) preenchido — o chat é o palco, o ticket é o bastidor.
#
# NÃO altera nenhuma regra de negócio: apenas insere dados usando os modelos/enums existentes.
#
# Como usar (dentro do container backend, com o Postgres no ar):
#   docker compose exec backend python scripts/semear_chamados.py
#
# É IDEMPOTENTE: se os chamados de demonstração já existirem, não duplica — apenas informa e sai.

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Garante que a raiz do backend (pasta-pai de scripts/) esteja no sys.path para achar o pacote `app`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from pwdlib import PasswordHash

from app.banco_dados import engine, Base, AsyncSessionLocal
from app.modelos.Empresa import Empresa
from app.modelos.Usuarios import Usuario, UsuarioFuncao
from app.modelos.Chamados import Chamado, ChamadoFila, ChamadoStatus, ChamadoPrioridade
from app.modelos.Mensagens import Mensagem, AutorTipo
import app.modelos  # importa todos os modelos para o create_all conhecer todas as tabelas

# Hasher de senha (mesmo argon2 das rotas de autenticação) — todos os clientes demo usam "Senha123".
pwd = PasswordHash.recommended()
SENHA_PADRAO = "Senha123"

# Marcador de idempotência: e-mails de demonstração ficam neste domínio.
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


# Busca um usuário pelo e-mail ou o cria com a função indicada (idempotente por e-mail único).
async def obter_ou_criar_usuario(db, empresa_id, nome, email, funcao, condominio=None):
    resultado = await db.execute(select(Usuario).where(Usuario.Email == email))
    usuario = resultado.scalar_one_or_none()
    if usuario:
        return usuario
    usuario = Usuario(
        EmpresaID=empresa_id,
        Nome=nome,
        Email=email,
        SenhaHash=pwd.hash(SENHA_PADRAO),
        Funcao=funcao,
        Condominio=condominio,
    )
    db.add(usuario)
    await db.flush()  # garante que o ID já esteja disponível para vincular aos chamados
    return usuario


async def main():
    # Garante que as tabelas existem (idempotente — não recria o que já existe).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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

        # Reaproveita a primeira Empresa já existente (criada por scripts/criar_empresa.py) —
        # este seed é multi-tenant-aware, mas não cria Empresa: pressupõe que o bootstrap já rodou.
        resultado_empresa = await db.execute(select(Empresa).order_by(Empresa.Criacao).limit(1))
        empresa = resultado_empresa.scalar_one_or_none()
        if not empresa:
            print("Nenhuma Empresa encontrada — rode scripts/criar_empresa.py antes de semear chamados.")
            return

        # Cria (ou reaproveita) o supervisor e os clientes de demonstração.
        supervisor = await obter_ou_criar_usuario(
            db, empresa.ID, SUPERVISOR["Nome"], SUPERVISOR["Email"], UsuarioFuncao.Supervisor
        )
        clientes = []
        for c in CLIENTES:
            clientes.append(await obter_ou_criar_usuario(
                db, empresa.ID, c["Nome"], c["Email"], UsuarioFuncao.Cliente, c["Condominio"]
            ))

        agora = datetime.utcnow()

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

    # Resumo no console para conferência rápida.
    print(f"Seed concluído: {len(CLIENTES)} clientes, 1 supervisor e {len(CHAMADOS)} chamados criados.")
    print(f"Login dos clientes demo: <email>{DOMINIO_DEMO} / senha: {SENHA_PADRAO}")


if __name__ == "__main__":
    asyncio.run(main())
