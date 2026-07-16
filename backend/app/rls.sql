-- Row-Level Security (RLS) do Postgres — trava SECUNDÁRIA de isolamento multi-tenant (Fase 0.7).
-- O filtro por EmpresaID já é feito em cada rota (trava primária); RLS existe como defesa em
-- profundidade caso uma query futura esqueça o filtro por Empresa.
--
-- Funciona lendo a variável de sessão `app.empresa_id`, que a aplicação define por requisição em
-- `rotas.Autenticacao.obterBancoDadosComTenant` via `set_config('app.empresa_id', '<uuid>', false)`
-- antes de rodar qualquer query. Sem essa variável setada, current_setting(...) retorna NULL e
-- nenhuma linha passa (fail-closed). `NULLIF(..., '')` cobre outro caso real (item F08-01): numa
-- conexão reciclada do pool em que a variável foi setada e depois `RESET`, o valor "de reset" de um
-- GUC customizado é STRING VAZIA, não NULL — sem o NULLIF, o cast `::uuid` de '' geraria um ERRO
-- (500), não zero linhas. Com o NULLIF, tanto ausência quanto reset caem em NULL e a trava
-- permanece fail-closed sem lançar exceção.
--
-- Aplicar com: python scripts/gerenciar_banco.py aplicar-rls (idempotente — pode rodar de novo sem erro)
--
-- Pré-requisito (item F08-01): a aplicação precisa conectar com um papel RESTRITO, sem SUPERUSER
-- nem BYPASSRLS e sem ser dono das tabelas — nenhum desses dois privilégios pode ser contornado só
-- com política de RLS, mesmo com FORCE. `gerenciar_banco.py reset`/`aplicar-rls` criam/atualizam
-- esse papel (lido de DATABASE_URL) e concedem só o necessário antes de aplicar as políticas abaixo.

-- FORCE é necessário porque quem aplica este script (papel administrativo/dono das tabelas) não é
-- quem a aplicação usa em tempo de execução — sem FORCE, o Postgres isentaria o dono da tabela da
-- política por padrão, e a trava não valeria nada para quem conectasse como tal.

ALTER TABLE "Usuarios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Usuarios" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Usuarios";
CREATE POLICY tenant_isolamento ON "Usuarios"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);

ALTER TABLE "Chamados" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Chamados" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Chamados";
CREATE POLICY tenant_isolamento ON "Chamados"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);

ALTER TABLE "Mensagens" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Mensagens" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Mensagens";
CREATE POLICY tenant_isolamento ON "Mensagens"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);

ALTER TABLE "Condominios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Condominios" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Condominios";
CREATE POLICY tenant_isolamento ON "Condominios"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);

ALTER TABLE "EmpresaConfiguracoes" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "EmpresaConfiguracoes" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "EmpresaConfiguracoes";
CREATE POLICY tenant_isolamento ON "EmpresaConfiguracoes"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);

ALTER TABLE "CoberturasTurno" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "CoberturasTurno" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "CoberturasTurno";
CREATE POLICY tenant_isolamento ON "CoberturasTurno"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);

ALTER TABLE "CategoriasChamado" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "CategoriasChamado" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "CategoriasChamado";
CREATE POLICY tenant_isolamento ON "CategoriasChamado"
    USING ("EmpresaID" = NULLIF(current_setting('app.empresa_id', true), '')::uuid);
