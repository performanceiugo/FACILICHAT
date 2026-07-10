-- Consultas genericas para explorar o banco local do FaciliChat (uso manual, fora da API).
-- Nao e executado por nenhum script/CI; serve de referencia para quem quiser rodar SELECTs
-- direto no Postgres de desenvolvimento (DBeaver, TablePlus, pgAdmin ou psql).
--
-- CONEXAO (Postgres do docker-compose.yml, valores lidos do .env da raiz):
--   Host:     localhost
--   Porta:    5432
--   Banco:    facilichat_db
--   Usuario:  facilichat
--   Senha:    ver .env da raiz (chave POSTGRES_PASSWORD) — nao repetida aqui por seguranca
--
-- Via linha de comando (psql precisa estar instalado local, ou use dentro do container):
--   psql "postgresql://facilichat:<SENHA_DO_.ENV>@localhost:5432/facilichat_db"
--
-- Sem psql local, rode direto dentro do container do banco (nao precisa senha na mao):
--   docker compose exec db psql -U facilichat -d facilichat_db
--
-- Em cliente grafico (DBeaver, TablePlus, pgAdmin etc.): usar os mesmos host/porta/banco/usuario
-- acima, com a senha do .env.
--
-- NOTA: o usuario "facilichat" e o superusuario do container Postgres (criado pelo proprio
-- docker-compose) — conectar com ele enxerga TODAS as Empresas, ignorando a RLS por tenant que
-- a API aplica nas rotas (isso e esperado para consulta manual/administrativa, nao e um bug).
--
-- ============================================================

-- Lista todas as tabelas do schema publico
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Estrutura de colunas de uma tabela especifica (troque 'Usuarios' pela tabela desejada)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'Usuarios'
ORDER BY ordinal_position;

-- ============================================================
-- Consultas genericas por tabela (todas as tabelas reais do projeto)
-- ============================================================

-- Empresas (tenants do SaaS)
SELECT * FROM "Empresas" ORDER BY "CriadoEm" DESC LIMIT 50;

-- Usuarios (Cliente, Funcionario, Supervisor, RH, Financeiro, Gestor, Superadmin)
SELECT "ID", "EmpresaID", "Nome", "Email", "Funcao", "CondominioID"
FROM "Usuarios"
ORDER BY "Nome"
LIMIT 100;

-- Condominios (clientes de uma Empresa)
SELECT * FROM "Condominios" ORDER BY "Nome" LIMIT 100;

-- Chamados (tickets) — com filtro opcional por Empresa/Status/Prioridade
SELECT "ID", "EmpresaID", "Titulo", "Fila", "Status", "Prioridade", "CriadoEm"
FROM "Chamados"
ORDER BY "CriadoEm" DESC
LIMIT 100;
-- Exemplo com filtro:
-- WHERE "Status" = 'Recebido' AND "Prioridade" = 'Critica'

-- Mensagens de um Chamado especifico (troque o UUID abaixo)
SELECT "ID", "ChamadoID", "AutorTipo", "Conteudo", "CriadoEm"
FROM "Mensagens"
WHERE "ChamadoID" = '00000000-0000-0000-0000-000000000000'
ORDER BY "CriadoEm";

-- Sessoes revogadas (denylist do logout — item S14)
SELECT * FROM "SessoesRevogadas" ORDER BY "ExpiraEm" DESC LIMIT 50;

-- Refresh tokens ativos por usuario (nao mostra o segredo, so o hash — item S15)
SELECT "ID", "UsuarioID", "FamiliaID", "CriadoEm", "ExpiraEm", "RevogadoEm"
FROM "RefreshTokens"
WHERE "RevogadoEm" IS NULL
ORDER BY "CriadoEm" DESC
LIMIT 50;

-- ============================================================
-- Extras uteis
-- ============================================================

-- Contagem de chamados por Empresa e Status (visao rapida do volume)
SELECT "EmpresaID", "Status", COUNT(*) AS total
FROM "Chamados"
GROUP BY "EmpresaID", "Status"
ORDER BY "EmpresaID", total DESC;

-- Ver as policies de RLS ativas (para conferir o isolamento multi-tenant)
SELECT schemaname, tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public';
