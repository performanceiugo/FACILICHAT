-- Row-Level Security (RLS) do Postgres — trava SECUNDÁRIA de isolamento multi-tenant (Fase 0.7).
-- O filtro por EmpresaID já é feito em cada rota (trava primária); RLS existe como defesa em
-- profundidade caso uma query futura esqueça o filtro por Empresa.
--
-- Funciona lendo a variável de sessão `app.empresa_id`, que a aplicação define por requisição em
-- `rotas.Autenticacao.obterBancoDadosComTenant` via `set_config('app.empresa_id', '<uuid>', false)`
-- antes de rodar
-- qualquer query. Sem essa variável setada, current_setting(...) retorna vazio e nenhuma linha passa
-- (fail-closed).
--
-- Aplicar com: python scripts/gerenciar_banco.py aplicar-rls (idempotente — pode rodar de novo sem erro)

-- FORCE é necessário porque a aplicação conecta como dono das tabelas — sem FORCE, o Postgres
-- isenta o dono da tabela da política por padrão, e a trava não valeria nada.

ALTER TABLE "Usuarios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Usuarios" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Usuarios";
CREATE POLICY tenant_isolamento ON "Usuarios"
    USING ("EmpresaID" = current_setting('app.empresa_id', true)::uuid);

ALTER TABLE "Chamados" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Chamados" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Chamados";
CREATE POLICY tenant_isolamento ON "Chamados"
    USING ("EmpresaID" = current_setting('app.empresa_id', true)::uuid);

ALTER TABLE "Mensagens" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Mensagens" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Mensagens";
CREATE POLICY tenant_isolamento ON "Mensagens"
    USING ("EmpresaID" = current_setting('app.empresa_id', true)::uuid);

ALTER TABLE "Condominios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Condominios" FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolamento ON "Condominios";
CREATE POLICY tenant_isolamento ON "Condominios"
    USING ("EmpresaID" = current_setting('app.empresa_id', true)::uuid);
