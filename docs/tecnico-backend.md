# FaciliChat — Documentação Técnica: Backend

---

## Como rodar o backend

O caminho padrão é o Docker Compose — ele sobe o Postgres **e** a API juntos (o serviço `backend`
roda `uvicorn` com `--reload` dentro do container, com o código local montado como volume):

```bash
# na raiz do repositório (exige .env da raiz e backend/.env — ver docs/setup.md)
docker compose up -d
```

Alternativa sem Docker para a API (o banco continua vindo do compose) — funciona desde a criação
do `backend/app/__init__.py` (item C2), que tornou `app` um pacote importável:

```bash
docker compose up -d db          # só o Postgres
cd backend
pip install -r requirements.txt
cp .env.example .env             # editar os valores (DATABASE_URL aponta para localhost)
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
| Funcao | Enum | Cliente / Funcionario / Supervisor / RH / Financeiro / Gestor / Superadmin |
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

### `CoberturasTurno` — Cobertura operacional estruturada

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador da cobertura |
| EmpresaID | UUID → Empresas | Tenant, com RLS forçada |
| CondominioID | UUID → Condominios | Contrato/local atendido |
| Posto / Turno | String | Identificação operacional do período |
| Inicio / Fim | DateTime | Janela real da cobertura |
| ResponsavelID | UUID → Usuarios | Funcionário confirmado; nulo enquanto descoberta |
| ConfirmadaEm | DateTime | Momento da confirmação; nulo enquanto descoberta |

---

## Rotas da API

### Autenticação — `/autenticacao`

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| POST | `/autenticacao/login` | Login com email e senha, retorna access + refresh token | Não |
| POST | `/autenticacao/atualizar` | Troca um refresh token válido por um access token novo (item S15) | Refresh token (cookie ou corpo) |
| POST | `/autenticacao/logout` | Revoga a sessão de verdade: denylist do `jti` do access token (S14) + família do refresh token (S15) | Opcional |

**Resposta do login e de `/autenticacao/atualizar`** (mesmo formato — item S15):
```json
{
  "token_acesso": "eyJ...",
  "tipo_token": "bearer",
  "refresh_token": "5f2c...-uuid.segredo-opaco",
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
| PATCH | `/usuarios/eu/senha` | Troca a própria senha (exige `SenhaAtual`); revoga **todas** as sessões do usuário — denylist do `jti` atual + todas as famílias de refresh (item S14) | Sim | Qualquer perfil |
| PATCH | `/usuarios/{usuarioID}/funcao` | Muda a função de outro usuário da mesma Empresa; revoga todas as famílias de refresh do usuário-alvo (item S14) | Sim | Apenas Gestor (403 caso contrário); 404 se o alvo não existir ou for de outra Empresa |

> **Primeiro Gestor:** como o cadastro público fica fechado por padrão e `/usuarios/equipe` exige um Gestor, a primeira Empresa + primeiro Gestor são criados por `python scripts/gerenciar_banco.py criar-empresa ...` (ver a seção "Scripts do banco" abaixo e `docs/setup.md`).

### Chamados — `/chamados`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/chamados/` | Abrir novo chamado | Sim | Qualquer perfil |
| POST | `/chamados/irmaos` | Abrir 2+ chamados simultâneos ligados pelo mesmo `GrupoOrigemID` | Sim | Qualquer perfil |
| GET | `/chamados/` | Listar chamados; aceita `supervisor_id={UUID}` para retornar somente a fila atribuída a um supervisor da mesma Empresa | Sim | Sem filtro: Cliente vê só os seus e Supervisor/Gestor vê todos. Com `supervisor_id`: apenas Gestor; 404 para supervisor inexistente, de outro tenant ou com outro perfil |
| PATCH | `/chamados/{id}/status` | Atualizar status | Sim | Apenas Supervisor/Gestor (403 caso contrário); chamado finalizado não reabre (409) |

### Relatórios — `/relatorios`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| GET | `/relatorios/visao-geral` | Total de chamados abertos, SLA vencido, primeira resposta média e resolução média; tempos em minutos e `null` quando não há amostra | Sim | Apenas Gestor; dados filtrados pela Empresa do token e protegidos por RLS |
| GET | `/relatorios/supervisores` | Lista todos os supervisores da Empresa com chamados abertos, atrasados e primeira resposta média; inclui supervisores sem chamados e usa `null` quando não há resposta | Sim | Apenas Gestor; chamados e mensagens filtrados pela Empresa do token e protegidos por RLS |
| GET | `/relatorios/configuracao-gargalo` | Retorna o limite efetivo de horas sem atualização (padrão inicial 72h) | Sim | Apenas Gestor; configuração da Empresa do token |
| PATCH | `/relatorios/configuracao-gargalo` | Persiste `LimiteGargaloHoras` entre 1 e 720 horas | Sim | Apenas Gestor; escrita isolada por Empresa/RLS |
| GET | `/relatorios/gargalos` | Chamados ativos parados além do limite; `TempoParadoHoras` é derivado de `Atualizacao` | Sim | Apenas Gestor; chamados e configuração da Empresa do token |
| GET | `/relatorios/coberturas-descobertas` | Coberturas atuais/futuras sem Funcionário e confirmação | Sim | Apenas Gestor; Empresa do token/RLS |
| GET | `/relatorios/desempenho-supervisores` | Recebidos, resolvidos, parados e taxa de resolução por supervisor; inclui zero amostra | Sim | Apenas Gestor; Empresa do token/RLS |

### Coberturas — `/coberturas`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/coberturas/` | Registra condomínio/posto/turno e janela ainda descoberta | Sim | Supervisor ou Gestor |
| GET | `/coberturas/` | Lista a escala estruturada da Empresa | Sim | Supervisor ou Gestor |
| PATCH | `/coberturas/{id}/confirmar` | Confirma um usuário com perfil Funcionário do mesmo tenant | Sim | Supervisor ou Gestor |

A primeira resposta por supervisor só considera a primeira mensagem do próprio supervisor
atribuído ao chamado, posterior à abertura. Respostas de outro usuário ou mensagens de sistema/IA
não entram na média. Os valores são calculados no PostgreSQL e arredondados apenas na resposta.

`EmpresaConfiguracoes` guarda parâmetros operacionais por tenant em uma tabela 1:1 com Empresa.
Ela foi separada de `Empresas` para que `create_all` consiga adicioná-la a bancos existentes sem
reset enquanto Alembic está pendente. A tabela possui `EmpresaID` como chave primária e política
RLS forçada; ausência de linha significa o padrão inicial de 72h, e o primeiro PATCH persiste a
escolha do Gestor.

---

## Segurança

- Senhas armazenadas com hash **argon2** via `pwdlib` (nunca em texto puro); hasher centralizado
  em `app/servicos/hasher.py` (item B6) — reaproveitado por todas as rotas e scripts que hasheiam
  senha, em vez de instanciado de forma duplicada
- **Política de senha e limites de entrada (item M1):** senha com **mínimo de 15 caracteres**
  (OWASP Authentication Cheat Sheet para aplicação **sem MFA** — decisão do usuário em 15/07/2026)
  e **máximo de 128** (≥ 64 para permitir passphrases e teto contra DoS de senha longa no argon2),
  **sem regras de composição** (maiúscula/número/símbolo não são exigidos — OWASP) e aceitando
  qualquer caractere. Vale para `UsuarioCriar`/`UsuarioCriarEquipe`, `SenhaAlterar.SenhaNova` e
  `PrimeiroGestorCriar` (rota da plataforma); `SenhaAtual` só tem teto (senhas antigas podem ser
  mais curtas e ainda precisam ser conferidas). Campos de texto livres ganharam `max_length`
  (`Nome`/`Condominio` 120, `Telefone` 20, `Categoria` 80 com mínimo 1, `Resumo` 2000, `CNPJ` 20)
  como defesa contra payloads abusivos; os 422 saem em português via o handler do M12. A senha demo
  do seed passou a ser `FaciliChat2026Demo` (a antiga `Senha123` ficaria abaixo do mínimo da API).
- JWT assinado com `HS256` e chave secreta configurável. Claims: `sub` (usuário), `funcao`,
  `empresa_id`, `iat`/`exp` (emissão/expiração), `iss`/`aud` (`JWT_ISSUER`/`JWT_AUDIENCE`,
  validados no decode) e `jti` (ID único do token — item B6/S14)
- **Access token curto + refresh rotativo (item S15):** access token válido por **15 minutos**
  (`JWT_EXPIRE_MINUTES`) — a sessão "longa" vem do **refresh token**, não do access token. Refresh
  token opaco no formato `"{ID}.{segredo}"` (`RefreshTokens`, `app/servicos/refresh.py`): o `ID` é
  a chave primária (lookup indexado) e só o **hash sha256** do segredo fica no banco, como uma
  senha. Válido por `REFRESH_TOKEN_EXPIRE_DIAS` (padrão 30), sessão "deslizante" — cada rotação
  renova a janela. **Rotação com detecção de reuso por família:** todo refresh nascido do mesmo
  login compartilha um `FamiliaID`; cada uso em `POST /autenticacao/atualizar` consome o token e
  gera o próximo elo da mesma família; reusar um token já consumido é tratado como furto/replay e
  **revoga a família inteira** (não só o token reusado). `RefreshTokens` fica fora da RLS pelo
  mesmo motivo do `SessoesRevogadas` do S14 (checagem roda antes de `app.empresa_id` ser setado).
- **Duas formas de sessão convivem** (item S6), resolvidas por `obterTokenDaRequisicao`:
  o **painel web** usa o cookie `sessao` (`HttpOnly`, emitido pelo backend no login, `Max-Age`
  igual à validade do token); o **app mobile** usa `Authorization: Bearer` com o token no
  `SecureStore`. O header tem precedência sobre o cookie.
- **CSRF** (`app/servicos/csrf.py`, middleware): em `POST`/`PUT`/`PATCH`/`DELETE` valida
  `Origin`/`Referer` contra `CORS_ORIGINS` e, quando a credencial é o cookie, exige o
  double-submit (`X-CSRF-Token` == cookie `csrf_token`, comparado em tempo constante).
  Requisições com `Bearer` pulam o double-submit: um header não é credencial ambiente, então
  não há superfície de CSRF. `SameSite` sozinho **não** basta (OWASP).
- `POST /autenticacao/logout` revoga a sessão de verdade (itens S14/S15): decodifica o access
  token recebido (cookie ou `Bearer`) e registra o seu `jti` numa denylist (tabela
  `SessoesRevogadas`, `app/servicos/revogacao.py`) — além disso, localiza e revoga a **família
  inteira** do refresh token (`app/servicos/refresh.revogarFamilia`), então nem uma cópia do
  access nem do refresh (roubados antes do logout) continuam funcionando. `obterUsuarioAtual` e
  `obterTenantAtual` checam a denylist do access token a cada requisição autenticada. Ambas as
  tabelas (`SessoesRevogadas`, `RefreshTokens`) ficam deliberadamente fora da RLS (a checagem roda
  antes de `app.empresa_id` ser setado; com RLS a query veria sempre zero linhas).
- **Revogação em troca de senha e mudança de função (item S14, fechado):** `PATCH
  /usuarios/eu/senha` exige a senha atual (OWASP Authentication Cheat Sheet) e, ao trocar,
  denylista o `jti` da sessão atual **e** revoga todas as famílias de refresh do usuário
  (`app/servicos/refresh.revogarTodasFamiliasDoUsuario`) — forçando novo login em todos os
  dispositivos, incluindo o que fez a troca. `PATCH /usuarios/{usuarioID}/funcao` (só Gestor, mesma
  Empresa) revoga todas as famílias de refresh do usuário-alvo ao mudar sua função — o access
  token que o alvo já tem em mãos continua válido até expirar (no máximo 15min, janela curta do
  S15), porque não há como localizar o `jti` de um dispositivo que não é o da requisição atual.
  Segue a recomendação da OWASP Session Management Cheat Sheet de invalidar sessões em troca de
  senha e em mudança de privilégio.
- Cookie configurável por ambiente: `COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_DOMAIN`
  (defaults seguros; `SameSite=none` sem `Secure` falha na subida)
- Dependência `obterUsuarioAtual` protege automaticamente qualquer rota que a use
- Login e cadastro público têm rate limit simples por IP/e-mail; login usa hash dummy quando o e-mail não existe para reduzir enumeração por timing
- **Corrida TOCTOU no cadastro (item M2):** o check prévio de e-mail duplicado não é atômico — duas
  requisições simultâneas podem passar juntas por ele. A constraint `UNIQUE` do banco é a fonte da
  verdade: o `IntegrityError` do commit é capturado e vira **400 com a mesma resposta neutra do
  check prévio** (S7 — resposta específica reabriria a enumeração de e-mail). O mesmo tratamento
  cobre a rota da plataforma (`POST /plataforma/empresas`): CNPJ no `flush` e e-mail do gestor no
  `commit`, com rollback desfazendo a Empresa junto (nunca fica Empresa órfã sem o primeiro Gestor);
  lá as mensagens podem ser específicas porque a rota é exclusiva do Superadmin
- **CORS** restrito às origens em `CORS_ORIGINS` (config/.env), sem `"*"` em nenhum eixo (item S17):
  métodos limitados aos que a API expõe (`GET, POST, PATCH, OPTIONS`) e headers a `Authorization` e
  `Content-Type`. `allow_credentials=False` — a autenticação é por header `Bearer`, nenhum cliente
  envia cookies. Religar credentials é tarefa do **S6**, e só junto da proteção CSRF.
  > Ao criar uma rota com um verbo novo (ex.: `DELETE`), adicione-o a `CORS_METODOS_PERMITIDOS`
  > em `app/main.py` — senão o preflight do navegador reprova a chamada.
- **Cadastro público fechado por padrão**; quando habilitado, só aceita a Empresa configurada e cria Cliente. Perfis privilegiados só via `/usuarios/equipe` (Gestor)
- **Alteração de status de chamado** restrita a Supervisor/Gerente (evita IDOR)
- **Docs da API configuráveis por ambiente (item S8):** `API_DOCS_HABILITADO` (default `true`)
  controla `docs_url`/`redoc_url`/`openapi_url` na instância `FastAPI(...)` (`main.py`). Com
  `false`, o FastAPI nem registra `/docs`, `/redoc` ou `/openapi.json` — não gera o schema, não é
  só uma UI escondida. Ligado em dev, desligado em produção (`docs/deploy-producao.md`).
- **Auditoria automatizada de dependências (item S12):** o workflow
  `.github/workflows/auditoria-python.yml` roda `pip-audit -r backend/requirements.txt` em todo
  push/PR que altere o arquivo e semanalmente (segunda 09:00 UTC) — CVE nova em versão já fixada
  derruba o CI mesmo sem commit. Rotina local e o que fazer quando acusar vulnerabilidade:
  seção "Auditoria de dependências Python" do `docs/setup.md`.
- **Imagem de produção endurecida (item S9):** `backend/Dockerfile` roda como usuário não-root
  (`appuser`, via `useradd --system`) — a mesma imagem serve dev e produção; só o
  `docker-compose.prod.yml` muda o comando (sem `--reload`, com `--proxy-headers` atrás do Caddy) e
  remove o bind mount do código. Passo a passo completo de deploy: `docs/deploy-producao.md`.

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
| `criar-empresa "<Nome>" <CNPJ> "<Gestor>" <email> <senha>` | Cria a 1ª Empresa (tenant) + o 1º Gestor numa transação só. **Não** é idempotente. |
| `criar-superadmin "<Nome>" <email> <senha> [--empresa-nome N] [--cnpj C]` | Cria a Empresa `Iugo Performance` (se faltar) + o 1º **Superadmin** da plataforma. **Idempotente.** Aborta se o e-mail já pertence a outro perfil — nunca promove usuário existente. |
| `semear` | Popula clientes, supervisor, chamados e chat de demonstração na 1ª Empresa (idempotente). **Recusa rodar se `AMBIENTE=producao`** (item S10) — usuários demo nascem com senha padrão, inaceitável fora de dev/staging. |
| `limpar-demo` | Remove os usuários de demonstração (marcados pelo domínio `DOMINIO_DEMO`) e tudo que depende deles — chamados, mensagens, refresh tokens, sessões revogadas (idempotente). Item S10: rotação/limpeza dos dados demo em ambientes compartilhados (staging). |
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
  para cadastrar/suspender Empresas e criar o 1º Gestor de cada uma. Dois bootstraps distintos:
  - `gerenciar_banco.py criar-superadmin ...` → cria o **Superadmin** (e a Empresa da Iugo).
  - `gerenciar_banco.py criar-empresa ...` → cria uma **Empresa cliente** + o 1º Gestor dela.

  > **Nuance de modelo:** conceitualmente a Iugo está *acima* dos tenants, mas o schema exige
  > `Usuario.EmpresaID NOT NULL` (`modelos/Usuarios.py:32`). Por isso a Iugo existe como uma linha
  > em `Empresas`, marcada com `EhPlataforma=True` — a única diferença de uma Empresa-cliente
  > comum. `listarEmpresas` filtra `EhPlataforma=False`, então a Iugo **não aparece** na lista de
  > tenants do painel (bug reportado pelo usuário em 09/07/2026, corrigido no mesmo dia:
  > `Empresa.EhPlataforma`, `Plataforma.listarEmpresas`, `Plataforma.atualizarStatusEmpresa`).
  > `atualizarStatusEmpresa` recusa (400) mudar o status desta Empresa mesmo se alguém chamar a
  > API direto — suspendê-la trancaria todos os Superadmins fora da própria plataforma. A
  > autorização de rota não depende do flag: `exigirSuperadmin` olha só a `Funcao`, e a tabela
  > `Empresas` está fora da RLS, então qualquer Superadmin enxerga (nas queries que quiserem) todos
  > os tenants.

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
