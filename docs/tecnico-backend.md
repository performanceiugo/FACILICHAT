# FaciliChat — Documentação Técnica: Backend

---

## Como rodar o backend

```bash
# 1. Subir o banco de dados
docker compose up -d

# 2. Instalar dependências Python
cd backend
pip install -r requirements.txt

# 3. Criar arquivo .env (copiar do exemplo)
cp .env.example .env
# (editar os valores no .env)

# 4. Rodar o servidor (a partir de backend/)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000/docs` — documentação automática da API (Swagger UI)

---

## Modelos de banco de dados

### `Usuarios` — Tabela de usuários

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador único |
| Nome | String(120) | Nome completo |
| Email | String(120) | Email único (login) |
| SenhaHash | String(255) | Senha em hash argon2 |
| Funcao | Enum | Cliente / Supervisor / Funcionario / Gerente |
| Telefone | String(20) | Opcional |
| Condominio | String(120) | Nome do condomínio, opcional |
| Criacao | DateTime | Data de cadastro |

### `Chamados` — Tabela de chamados/solicitações

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador único |
| EmpresaID | UUID → Empresas | Tenant do chamado |
| ClienteID | UUID → Usuarios | Quem abriu o chamado |
| GrupoOrigemID | UUID | Opcional; agrupa tickets irmãos nascidos do mesmo aviso/mensagem |
| SupervisorID | UUID → Usuarios | Supervisor atribuído (opcional) |
| Fila | Enum | Operacional / RH / Financeiro / Comercial |
| Categoria | String(80) | Ex: "Vazamento", "Folha de Pagamento" |
| Status | Enum | Recebido / EmAndamento / Agendado / Concluido / Cancelado |
| Prioridade | Enum | Baixa / Media / Alta / Critica |
| Resumo | Text | Descrição do problema (opcional) |
| PrazoSLA | DateTime | Prazo de atendimento (opcional) |
| Criacao | DateTime | Data de abertura |
| Atualizacao | DateTime | Última atualização |

### `Mensagens` — Tabela de mensagens do chat

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador único |
| ChamadoID | UUID → Chamados | A qual chamado pertence |
| AutorID | UUID → Usuarios | Quem enviou (null se for IA/Sistema) |
| AutorTipo | Enum | Cliente / Supervisor / Funcionario / IA / Sistema |
| Conteudo | Text | Texto da mensagem |
| Anexo | String(500) | URL do arquivo anexado (opcional) |
| Criacao | DateTime | Data/hora do envio |

---

## Rotas da API

### Autenticação — `/autenticacao`

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| POST | `/autenticacao/login` | Login com email e senha, retorna JWT | Não |

**Resposta do login:**
```json
{
  "token_acesso": "eyJ...",
  "tipo_token": "bearer",
  "funcao": "Cliente",
  "nome": "João Silva"
}
```

### Usuários — `/usuarios`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/usuarios/` | Cadastro público controlado — fechado por padrão; quando habilitado, cria **sempre** um Cliente na Empresa liberada por `CADASTRO_PUBLICO_EMPRESA_ID` | Não | Pública controlada |
| POST | `/usuarios/equipe` | Criar usuário com função definida (Supervisor/Funcionario/RH/Financeiro/Gestor) | Sim | Apenas Gestor (403 caso contrário) |
| GET | `/usuarios/eu` | Retorna dados do usuário logado | Sim | Qualquer perfil |

> **Primeiro Gestor:** como o cadastro público fica fechado por padrão e `/usuarios/equipe` exige um Gestor, a primeira Empresa + primeiro Gestor são criados por `python scripts/gerenciar_banco.py criar-empresa ...` (ver a seção "Scripts do banco" abaixo e `docs/setup.md`).

### Chamados — `/chamados`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/chamados/` | Abrir novo chamado | Sim | Qualquer perfil |
| POST | `/chamados/irmaos` | Abrir 2+ chamados simultâneos ligados pelo mesmo `GrupoOrigemID` | Sim | Qualquer perfil |
| GET | `/chamados/` | Listar chamados | Sim | Cliente vê só os seus; Supervisor/Gerente vê todos |
| PATCH | `/chamados/{id}/status` | Atualizar status | Sim | Apenas Supervisor/Gerente (403 caso contrário); chamado finalizado não reabre (409) |

---

## Segurança

- Senhas armazenadas com hash **argon2** via `pwdlib` (nunca em texto puro)
- JWT assinado com `HS256` e chave secreta configurável
- Token válido por **8 horas** (configurável via `JWT_EXPIRE_MINUTES`)
- Dependência `obterUsuarioAtual` protege automaticamente qualquer rota que a use
- Login e cadastro público têm rate limit simples por IP/e-mail; login usa hash dummy quando o e-mail não existe para reduzir enumeração por timing
- **CORS** restrito às origens em `CORS_ORIGINS` (config/.env) — sem `"*"` junto de credenciais
- **Cadastro público fechado por padrão**; quando habilitado, só aceita a Empresa configurada e cria Cliente. Perfis privilegiados só via `/usuarios/equipe` (Gestor)
- **Alteração de status de chamado** restrita a Supervisor/Gerente (evita IDOR)

## Data/hora — sempre UTC timezone-aware (M5)

- Todas as colunas de data/hora usam `DateTime(timezone=True)` (`timestamptz` no Postgres) e os
  defaults/gravações usam **`agoraUtc()` de `app/tempo.py`** — nunca `datetime.utcnow()` (deprecado
  e naive) nem `datetime.now()` (hora local).
- Se o schema mudar, em dev basta recriar o banco com `python scripts/gerenciar_banco.py reset`
  (ver abaixo) — não há migrações incrementais a rodar.

## Scripts do banco (desenvolvimento)

Há **um único** ponto de entrada para tudo relacionado ao banco de dev: `backend/scripts/gerenciar_banco.py`.
Rode a partir de `backend/` ou via `docker compose exec backend python scripts/gerenciar_banco.py <cmd>`.

| Comando | O que faz |
|---|---|
| `reset [--semear]` | Dropa o schema inteiro, recria as tabelas (a partir dos modelos) e aplica a RLS. Com `--semear`, também popula os dados de demonstração. É o jeito correto de aplicar mudança de schema em dev. |
| `criar-empresa "<Nome>" <CNPJ> "<Gestor>" <email> <senha>` | Cria a 1ª Empresa (tenant) + o 1º Gestor numa transação só. |
| `semear` | Popula clientes, supervisor, chamados e chat de demonstração na 1ª Empresa (idempotente). |
| `aplicar-rls` | (Re)aplica só as políticas de `app/rls.sql`. |
| `verificar-rls` | Testa o isolamento multi-tenant (filtros por `EmpresaID` + RLS do Postgres). |

Fluxo do zero: `reset` → `criar-empresa ...` → `semear`.

> **Por que não há mais migrações incrementais:** como não há Alembic e o banco de dev não tem dados
> de produção a preservar, `Base.metadata.create_all` já reconstrói o schema completo a partir dos
> modelos. Os antigos scripts `aplicar_fase_06_*` e `aplicar_m5_timestamptz` foram removidos — o
> `reset` os substitui.
>
> **Atenção:** rodar `reset` com a API no ar invalida o cache de prepared statements do pool; a
> primeira requisição seguinte pode responder um 500 transitório (`InvalidCachedStatementError`) que
> o SQLAlchemy se auto-corrige na sequência. Para evitar o soluço, rode
> `docker compose restart backend` após o `reset`.
- A API passa a responder datas com sufixo `Z` (ex.: `2026-07-09T15:52:34Z`); `new Date(...)` no
  front interpreta corretamente.

## Erros para o usuário — sempre em português (M12)

Todo corpo de erro da API sai como `{"detail": "<mensagem em português>"}` (string única):

- Os `HTTPException` das rotas já são escritos em PT ("Email ou senha incorretos" etc.).
- Os erros de **validação automática do Pydantic** (422), que por padrão saem em inglês e em
  formato de lista, passam por um handler global de `RequestValidationError` no `main.py` que
  traduz os tipos comuns (`missing`, `uuid_parsing`, e-mail inválido, etc.) e junta tudo numa
  única string — ex.: `"O campo 'Email' deve ser um e-mail válido"`.
- Ao criar rotas novas, **escreva o `detail` em português**; tipos de validação ainda não mapeados
  caem no genérico "tem um valor inválido" (adicione ao mapa `TRADUCAO_ERROS_VALIDACAO` se preciso).
- Nos clientes web/mobile, `lib/api.ts` normaliza o `detail` (string ou lista) e converte falha de
  rede do `fetch` em "Não foi possível conectar ao servidor..." — nunca "Failed to fetch".

---

## Multi-tenancy (SaaS) — a implementar (Fase 0.7, prioritária)

O FaciliChat será um **SaaS multi-tenant**: cada **Empresa** (a conservadora/facilities cliente) tem
seus dados isolados; os clientes de uma Empresa são os **Condomínios** que ela atende. Convenções que
valerão para **todo** o backend a partir desta fase:

- **Entidade `Empresa`** (o tenant), com `Nome`, `CNPJ`, `Status`.
- **Coluna `EmpresaID`** (FK, `NOT NULL`) em **todas** as tabelas: `Usuario`, `Condominio`,
  `Chamado`, `Mensagem` e qualquer modelo futuro.
- **Tenant no JWT:** o `criarToken` passa a incluir o `EmpresaID`; a dependência
  `obterTenantAtual` extrai esse valor do token e é injetada em todas as rotas.
- **Escopo obrigatório:** **toda** query (`select`, `update`, `delete`) filtra por
  `EmpresaID` do usuário logado. Nenhuma rota retorna dados de outro tenant.
- **Row-Level Security (RLS)** no PostgreSQL como segunda trava (defesa em profundidade).
- **Papéis por tenant:** `Gestor`/`Supervisor`/etc. valem dentro da sua Empresa.
- **Superadmin da plataforma (Iugo Performance):** nível acima dos tenants (rotas em `Plataforma.py`)
  para cadastrar/suspender Empresas e criar o 1º Gestor de cada uma. O bootstrap é feito por
  `python scripts/gerenciar_banco.py criar-empresa ...` (cria Empresa + 1º Gestor juntos).

> **Perfis (branding):** o produto define 7 perfis — Cliente, Funcionário, Supervisor, **RH**,
> **Financeiro**, **Gestor**, **Superadmin**. O código atual tem 4 (Cliente, Supervisor, Funcionario,
> **Gerente**); a renomeação `Gerente→Gestor` e a inclusão de RH/Financeiro/Superadmin estão na
> **Fase 0.6** do plano. As tabelas de rotas abaixo refletem o estado **atual** do código.

> Detalhamento e checklist completo em `docs/plano-implementacao.md` (Fase 0.7). Visão de
> arquitetura em `docs/arquitetura.md` (seção "Arquitetura Multi-Tenant (SaaS)").

---

## Pendente de implementação

- [ ] **Fundação Multi-Tenant (Fase 0.7) — prioritária** (ver seção acima)
- [ ] Rotas de Mensagens (`/mensagens/{chamadoID}`)
- [ ] Integração com Anthropic (triagem automática de chamados por IA)
- [ ] Configuração do Alembic para migrações versionadas
- [ ] Rota para listar/buscar usuários (para Gerentes)
- [ ] Atribuição de supervisor a um chamado
- [ ] Filtros na listagem de chamados (por status, fila, prioridade)

---

*Última atualização: 27 de junho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
