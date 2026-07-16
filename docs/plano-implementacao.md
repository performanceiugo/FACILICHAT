# FaciliChat — Plano de Implementação

> **Como usar este arquivo:**
> Antes de qualquer sessão de desenvolvimento, leia este arquivo inteiro.
> Marque os itens conforme o progresso usando os status abaixo.
> Nunca implemente um item sem antes atualizar este arquivo.
>
> **Status possíveis:**
> - `[ ]` — Na fila (não iniciado)
> - `[~]` — Em andamento (iniciado mas não concluído)
> - `[x]` — Concluído e funcionando

---

## Fonte canônica de execução

> Este arquivo é o registro canônico por fase, status e `CU:` do ClickUp.
> `docs/implementation/README.md` indexa somente as especificações detalhadas que complementam
> itens deste plano; não mantém status paralelo nem um mapa separado de `CU:`.

---

## 🔗 Integração com o ClickUp (fonte da verdade dupla: este `.md` + o board)

> Este plano está **espelhado** num board do ClickUp. Cada **fase** é uma **tarefa-pai** e cada
> **item** é uma **subtarefa**, com barra de progresso automática.
>
> **Local do board:** Operações Internas › FaciliChat - Desenvolvimento › **Roadmap de Implementação**
> **`list_id`:** `901114027434`
>
> **Como cada item carrega seu ID:** ao lado de cada item há o seu **`CU:`** (ID da subtarefa no
> ClickUp) e, no título de cada fase, o `CU:` da tarefa-pai. **Este arquivo é a fonte da verdade dos
> IDs** — não existe arquivo de mapa separado.
>
> **Como fechar/atualizar uma tarefa:** ao mudar o status de um item aqui (`[ ]`→`[~]`→`[x]`), mova a
> subtarefa daquele `CU:` para o status equivalente no ClickUp via MCP do ClickUp. O hook
> `.claude/hooks/plano-clickup-reminder.js` lembra disso sempre que este arquivo é editado.
>
> **Vocabulário de status do board:** `📋 backlog` ou `🎯 planejado` = `[ ]` · `🚧 em andamento` = `[~]` ·
> `👀 em revisão` = em revisão · `⛔ bloqueada` = bloqueada · `✅ concluída` = `[x]` ·
> `📦 arquivada` = arquivada.
>
> **Regra de ouro:** o `CU:` ao lado de cada item é a chave. Nunca buscar tarefa por nome; sempre pelo `CU:`.

---

## Regras obrigatórias para toda implementação

1. **Todo bloco de código deve ter comentário.** Sem exceção. Funções, classes, rotas, hooks, estados, constantes de mapeamento — todos com comentário explicando o propósito.
2. **Consultar este arquivo antes de implementar qualquer coisa.** Verificar se o item já está marcado `[x]` ou `[~]`.
3. **Atualizar este arquivo ao concluir cada item.** Mudar `[ ]` para `[~]` ao iniciar, e para `[x]` ao concluir.
4. **Sincronizar o ClickUp** movendo a subtarefa do `CU:` correspondente para o status equivalente.
5. **Atualizar `docs/changelog.md`** com cada entrega.
6. **Manter tipos TypeScript sincronizados** com os modelos Python após toda alteração de schema.
7. **Detalhar novas fases antes de registrá-las.** Apresentar a proposta ao usuário e aplicar
   `docs/implementation/modelo-detalhamento-fase.md` antes de criar/alterar ClickUp e planejamento.
8. **Testes de fase são disparados pelo usuário.** Preparar testes, dados e comandos, mas não rodar
   teste, suite, build, smoke ou validação visual sem comando explícito para a fase/conjunto; até lá,
   registrar `testes preparados — aguardando disparo do usuário` e não marcar como validado.

---

## 🧭 Infraestrutura de acompanhamento — Integração ClickUp

> Rastreio da própria montagem do board ClickUp (Regra de Ouro: nada fora do plano). Não toca código de produto.

| Status | Item |
|--------|------|
| `[x]` | Espelhar o roadmap num board do ClickUp (`list_id 901114027434`) — tarefa-pai por fase, subtarefa por item |
| `[x]` | Sincronizar o progresso já feito (Fases 0.6/0.7 e item M3) do código para o board |
| `[x]` | Completar o board com as fases de discovery (4.5, 5.5, 11), "Adiados" e itens extras das fases 0.6/1/3/4/5 |
| `[x]` | Unificar os `CU:` no `plano-implementacao.md` canônico e apagar o mirror `plano-implementacao_1_clickup.md` |
| `[x]` | Corrigir o hook `plano-clickup-reminder.js` (sem dependência de mapa) e registrá-lo em `.claude/settings.json` |
| `[x]` | Criar uma camada local `.codex/` com skills/checklists equivalentes às do Claude para uso por referência dentro do repositório |
| `[x]` | Documentar o fluxo do Codex neste ambiente: leitura obrigatória do `CLAUDE.md`, limites de sandbox/rede e ausência atual de MCP do ClickUp nesta sessão |
| `[x]` | Adicionar scripts locais do Codex para diagnóstico do ambiente e lembrete operacional de sincronização manual do ClickUp |
| `[ ]` | Habilitar no ambiente do Codex uma integração nativa de ClickUp equivalente à sessão do Claude (depende de instalação/autenticação fora do repositório) |
| `[ ]` | Commitar os artefatos da integração (hook, settings, plano unificado, changelog) |

---

## 🗺️ Mapa das fases (visão rápida)

| Fase | Tema | Tarefa-pai (CU) | Status |
|------|------|-----------------|--------|
| 0 | Infraestrutura e base | `868k60uxe` | ✅ Concluída |
| 0.5 | Correções do levantamento (bugs, segurança e melhorias) | `868k60uzw` / `868k60v1m` | ✅ Concluída (15/07/2026) — críticos, segurança (S1–S17), altos, médios (M1–M13), baixos (B1–B7), docs (D1–D8) e versões (V1–V6) fechados |
| 0.6 | Alinhamento de domínio com o branding | `868k60vdy` | 🟡 Núcleo e tickets irmãos concluídos; regras/refinos na fila · **PRIORITÁRIO** |
| 0.7 | Fundação SaaS Multi-Tenant | `868k60vfm` | ✅ Concluída |
| 0.8 | Consolidação pós-auditoria: segurança, sessão e validação | `868kd1jc1` | 🚧 Em andamento (F08-01 concluído; F08-02 em diante na fila) · executar antes da Fase 1 |
| 1 | Chat (base do produto) | `868k60vny` | ⬜ Na fila |
| 1.5 | Fundação Multicanal — WhatsApp como porta de entrada | `868kb75yf` | ⬜ Na fila · **NOVA (10/07/2026)** |
| 2 | Criar chamado e detalhe (cliente) | `868k60vvt` | ⬜ Na fila |
| 3 | Fila e operação do supervisor (mobile) | `868k60vx4` | ⬜ Na fila |
| 4 | Dashboard do gestor (web) | `868k60w16` | ✅ Concluída · backend, frontend e manutenção operacional (categorias/equipe) fechados e validados visualmente pelo usuário em 15/07/2026 |
| 4.1 | Desempenho e escala para produção | `868kcuvv8` | ⬜ Na fila · executar após a conclusão visual da Fase 4 e antes da produção |
| 4.5 | Catálogo de Serviços e Parceiros | `868k7vr0g` | ⬜ Na fila · **NOVA (discovery)** |
| 5 | IA (classificação, roteamento e narração) | `868k60w34` | ⬜ Na fila |
| 5.5 | Governança e guardrails da IA | `868k7vr1c` | ⬜ Na fila · **NOVA (discovery)** |
| 6 | Alertas comerciais e propostas | `868k60w41` | ⬜ Na fila |
| 7 | Gestão de Empresas e Condomínios (telas/CRUD) | `868k60wgx` | ⬜ Na fila |
| 8 | MVP 02: Visitas Técnicas | `868k60whw` | ⬜ Na fila |
| 9 | Upload de arquivos | `868k60wn5` | ⬜ Na fila |
| 10 | Notificações push | `868k60wpb` | ⬜ Na fila |
| 11 | Experiência do Funcionário (canal único, voz/foto, sensor de campo) | `868k7vr1k` | ⬜ Na fila · **NOVA (discovery)** |
| 12 | Finalização do desenvolvimento e preparação para produção | `868kd1jc8` | 🎯 Planejada · executar após as fases funcionais |
| — | Adiados (pós-MVP): privacidade por tópico, integração ERP | `868k7vr1q` | ⬜ Registrado |

> **Ordem recomendada de desenvolvimento:** **0.6 → 0.7 → 0.8 → 1 → 1.5 (inbound) → 2–4 → 4.1 → 4.5 → 5 → 5.5 → 6 → 7 → 8–11 → 12**,
> encaixando as correções pendentes da Fase 0.5 conforme a área que for tocada. As Fases 0.6, 0.7 e
> 0.8 são fundação/consolidação e vêm antes das features. As Fases 4.5, 5.5 e 11 saíram do material de discovery (jornadas +
> How Might We + Governança de IA em `docs/FaciliChat-Regras/`) revisado em 02/07/2026. A Fase 1.5
> (10/07/2026) entra logo após a base de mensagens da Fase 1 e antes da IA; o **bloco outbound** dela
> (respostas/templates/envio ativo) fica para **depois da Fase 5/5.5**. A Fase 0.8 consolida a base
> antes das features; a Fase 12 transforma o ambiente final em candidato a produção. O detalhe de
> cada fase está na Parte 2 e em `docs/implementation/`.

> **⚠️ Convenção de nomes (ler antes de modelar qualquer coisa desta revisão):** os documentos de
> discovery usam **personas e exemplos ilustrativos** (nomes de pessoas, de serviços, de parceiros,
> valores). **Nada disso vira nome fixo, enum ou constante no código.** Personas mapeiam apenas aos 7
> **perfis** já canônicos (`UsuarioFuncao`); serviços, parceiros, regras de RH/Financeiro, categorias e
> similares são **dados configuráveis por Empresa, armazenados no banco** (linhas de tabela), nunca
> hard-coded. Só são "fixos" no código os enums já definidos nos invariantes do `CLAUDE.md`.

---
---

# PARTE 1 — ✅ Concluído

> Tudo o que já está implementado e funcionando. Não reimplementar; ler o código existente antes de mexer.

## Fase 0 — Infraestrutura e base · CU: `868k60uxe`

| Status | CU | Item |
|--------|----|------|
| `[x]` | `868k60uxr` | Auth JWT (login, token, middleware `obterUsuarioAtual`) |
| `[x]` | `868k60uxu` | Modelo `Usuario` com enum `UsuarioFuncao` (Cliente/Supervisor/Funcionario/Gerente) |
| `[x]` | `868k60uy1` | Modelo `Chamado` com enums de Fila, Status e Prioridade |
| `[x]` | `868k60uy4` | Modelo `Mensagem` com `AutorTipo` (hoje: Cliente/Supervisor/Funcionario/IA/Sistema) |
| `[x]` | `868k60uya` | Rotas: POST `/usuarios/`, GET `/usuarios/eu` |
| `[x]` | `868k60uyf` | Rotas: POST `/chamados/`, GET `/chamados/`, PATCH `/chamados/{id}/status` |
| `[x]` | `868k60uym` | Conexão assíncrona PostgreSQL via SQLAlchemy + asyncpg |
| `[x]` | `868k60uyp` | Docker Compose com PostgreSQL 16 |
| `[x]` | `868k60uyx` | Frontend web: tela de login |
| `[x]` | `868k60uz4` | Frontend web: painel com lista de chamados (cards por status/prioridade) |
| `[x]` | `868k60uz9` | Frontend mobile: tela de login |
| `[x]` | `868k60uzb` | Frontend mobile: lista de chamados com pull-to-refresh |
| `[x]` | `868k60uzj` | Frontend mobile: tela de perfil com logout |
| `[x]` | `868k60uzm` | Comentários em todos os 27 arquivos existentes |
| `[x]` | `868k60uzn` | Documentação: `visao-geral.md`, `arquitetura.md`, `tecnico-backend.md`, `tecnico-frontend.md`, `setup.md`, `changelog.md` |

## Fase 0.5 — Correções já aplicadas (do levantamento de 27/06/2026) · CU: `868k60uzw`

> Itens do levantamento técnico que já foram corrigidos. Os pendentes do mesmo levantamento estão na Parte 2.

| Status | CU | ID | Problema | O que foi feito | Arquivo(s) |
|--------|----|----|----------|-----------------|-----------|
| `[x]` | `868k60v03` | C1 | Imports não batem com os nomes dos arquivos → `ModuleNotFoundError` | Padronizado: todos os imports qualificados pelo pacote (`from app.banco_dados import ...`) em 9 arquivos | `backend/app/main.py`, `banco_dados.py`, `modelos/*.py`, `rotas/*.py` |
| `[x]` | `868k60v05` | C2 | Não é um pacote Python — falta `__init__.py`; `uvicorn app.main:app` falha | Criado `backend/app/__init__.py` (marcador de pacote) | `backend/app/__init__.py` (novo) |
| `[x]` | `868k60v07` | C3 | Rotas `/painel/*` retornam 404 (route group `(painel)` não entra na URL) | Route group `(painel)` renomeado para pasta real `painel/` | `frontend/web/src/app/painel/**` |
| `[x]` | `868k60v0a` | C4 | `auth.ts` acessa `localStorage` sem guarda de `window` → quebra no SSR | Guarda `typeof window !== 'undefined'`; `painel/layout.tsx` lê sessão via estado em `useEffect` | `frontend/web/src/lib/auth.ts`, `frontend/web/src/app/painel/layout.tsx` |
| `[x]` | `868k60v0f` | C5 | `app.json` referencia assets inexistentes → build falha | Gerados placeholders branded; `backgroundColor` corrigida `#1a56db`→`#148AF5` | `frontend/mobile/assets/*.png` (novos), `frontend/mobile/app.json` |
| `[x]` | `868k60v0h` | C6 | Escalonamento de privilégio: `POST /usuarios/` público aceita `Funcao` do corpo | Cadastro público força `Funcao = Cliente`; criação privilegiada movida para `POST /usuarios/equipe` | `backend/app/rotas/Usuarios.py`, `backend/scripts/criar_gerente.py` (novo) |
| `[x]` | `868k60v0m` | C7 | `PATCH /chamados/{id}/status` sem autorização nem checagem de posse (IDOR) | Restrito a Supervisor/Gestor (403); estado terminal não reabre (409) | `backend/app/rotas/Chamados.py` |
| `[x]` | `868k60v15` | A2 | CORS não configurado → frontends no navegador não chamam a API | `CORSMiddleware` com origens explícitas de `CORS_ORIGINS`; sem `"*"` com credenciais | `backend/app/main.py`, `configuracoes.py` |
| `[x]` | `868k60v1a` | A9 | Web: `next@15.3.4` afetado pela CVE-2025-66478 (RCE crítico, CVSS 10.0) | Atualizado `next` e `eslint-config-next` para `15.3.6` | `frontend/web/package.json` |
| `[x]` | `868k60v1d` | D3 | Texto espúrio "oi" e "atualização em tempo real" enganoso | Removido "oi" e a data 2025→2026; texto ajustado para "pull-to-refresh" | `docs/visao-geral.md` |

---
---

# PARTE 2 — 🚧 Em desenvolvimento (na ordem recomendada)

## Fase 0.5 — Correções pendentes (do levantamento de 27/06/2026) · CU: `868k60v1m`

> **Como conduzir:** corrigir **um item por vez**. Ao iniciar, `[ ]` → `[~]`; ao concluir, `[~]` → `[x]`
> (mover a linha para a Parte 1) e registrar no `changelog.md`. Cada ID (ex.: `A1`) serve de referência na conversa.

### 🟠 Altos · CU: `868kb37kx`

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[x]` | `868k60v1q` | A1 | `obterUsuarioAtual` retorna 500 (não 401) em token malformado | Conversão de UUID dentro do try e captura `(PyJWTError, ValueError)` | `backend/app/rotas/Autenticacao.py` |
| `[x]` | `868k60v1x` | A3 | Web e mobile sem tratamento de 401/token expirado | No cliente HTTP, ao receber 401 → `auth.sair()` + redirecionar para login | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[x]` | `868k60v29` | A4 | Proteção de rota só client-side com flash de conteúdo (web) | Usar `middleware.ts` do Next; renderizar `null`/loader enquanto não autenticado | `frontend/web/src/middleware.ts` (novo), `(painel)/layout.tsx`, `frontend/web/src/lib/auth.ts` |
| `[x]` | `868k60v2e` | A5 | Design system violado: cor `#1a56db` (deveria `#148AF5`) e fonte Geist (deveria Figtree) | **Web feito** (tokens completos do DS em `globals.css` + Figtree via `next/font`); mobile alinhado a tokens, Figtree e navegação do design system | `frontend/web/src/app/layout.tsx`, `globals.css`, `frontend/mobile/app/**`, `frontend/mobile/lib/theme.ts` |
| `[x]` | `868k60v2g` | A6 | API de mensagens (`api.mensagens.*`) aponta para rota inexistente no backend | Alinhar com a Fase 1 (criar rota) ou marcar como código futuro | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[x]` | `868k60v2k` | A7 | Link `/usuarios` no sidebar sem página correspondente → 404 | Criar a página ou esconder o link até existir | `frontend/web/src/components/painel/AdminShell.tsx` |
| `[x]` | `868k60v2r` | A8 | Mobile: React 18.3 / expo-router 4 incompatíveis com Expo SDK 53 | Rodar `npx expo install --fix`; alinhar React 19 / router 5 | `frontend/mobile/package.json`, `frontend/mobile/package-lock.json` |

### ✅ Segurança (levantamento de 08/07/2026) · CU: `868kb37me` — CONCLUÍDA em 15/07/2026 (S1–S17)

> Itens convertidos da revisão de segurança feita sobre backend, web, mobile, Docker e dependências.
> Como conduzir: corrigir **um `S*` por vez**, começando por `S1` e `S2`. `CU: a-criar` significa que a
> subtarefa ainda precisa ser criada no ClickUp antes de iniciar a implementação.
>
> **Ampliado em 09/07/2026** pela auditoria de autenticação/sessão (referências: OWASP Session
> Management / CSRF / XSS / Authentication Cheat Sheets e MDN Set-Cookie): novos itens `S14`–`S17` e
> escopo ampliado de `S6`/`S7` (e `B6`). Ordem recomendada para o bloco de sessão, respeitando
> dependências: `S16` e `S17` (baratos, independentes) → `S7` → `S6` → `S14` (com `B6` junto) → `S15`.
>
> **Fechada em 15/07/2026** com o `S11`. Únicas pendências remanescentes ficaram fora desta seção,
> deliberadamente deferidas para outros itens: correção das 13 vulnerabilidades moderadas do mobile
> → `V3` (bump major do Expo SDK); rate limit compartilhado (Redis) para multi-réplica → evolução do
> `S9`; resposta neutra no fluxo de convite/onboarding → evolução do `S3`; promover a CSP de
> `Report-Only` para enforce → nota do `S16`/`setup.md`.

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[x]` | `868kaa34a` | S1 | `npm audit` reportou vulnerabilidades atuais em `next@15.3.6` e `postcss` transitivo | Next/ESLint config atualizados para `15.5.20`; `postcss` forçado para `8.5.10` via `overrides`; `npm audit --json` e `npm run build` validados | `frontend/web/package.json`, `frontend/web/package-lock.json` |
| `[x]` | `868kaa359` | S2 | RLS existe, mas as rotas usam `obterBancoDados` puro; `SET LOCAL app.empresa_id` não é aplicado nas consultas normais | Rotas multi-tenant migradas para `obterBancoDadosComTenant`; tenant agora persiste por request com `set_config(...)` + `RESET`; `Condominios` entrou na RLS e foi criado verificador automatizado de isolamento | `backend/app/rotas/*.py`, `backend/app/rls.sql`, `backend/scripts/verificar_isolamento_tenant.py` |
| `[x]` | `868kaa363` | S3 | Cadastro público permite escolher qualquer `EmpresaID` no payload | Correção interina aplicada: cadastro público falha fechado por padrão e só aceita a Empresa configurada em `CADASTRO_PUBLICO_EMPRESA_ID` quando `CADASTRO_PUBLICO_HABILITADO=true`; convite/onboarding definitivo segue como evolução futura | `backend/app/rotas/Usuarios.py`, `backend/app/configuracoes.py`, `backend/.env.example`, `docs/setup.md`, `docs/tecnico-backend.md` |
| `[x]` | `868kaa36v` | S4 | Credenciais do Postgres fixas no `docker-compose.yml` e na `DATABASE_URL` do serviço backend | Credenciais movidas para `.env` da raiz (+ `.env.example`), com `${VAR:?}` fazendo o compose falhar cedo se faltarem; `DATABASE_URL` do backend montada a partir das mesmas variáveis; senha local rotacionada via `ALTER USER` preservando os dados; `setup.md` ganhou a seção "Produção — credenciais do banco por ambiente" (dev/staging/prod, papel não-superusuário para a RLS valer, TLS) | `docker-compose.yml`, `.env.example` (novo), `docs/setup.md`, `docs/arquitetura.md` |
| `[x]` | `868kaa37j` | S5 | Postgres publicado em `5432:5432`, abrindo o banco para o host/rede local | Porta presa em `127.0.0.1:5432:5432` para manter acesso local de dev sem expor o banco na rede | `docker-compose.yml`, `docs/setup.md` |
| `[x]` | `868kaa382` | S6 | JWT do web acessível a JavaScript em **dois** lugares: `localStorage` **e** cookie duplicado via `document.cookie` sem `HttpOnly`/`Secure` (e com `Max-Age` de 7 dias para um token de 8h); middleware do Next confia em cookies graváveis pelo cliente (`funcao=Superadmin` forjável — inócuo hoje porque o backend revalida, mas é camada falsa) | Migrar para cookie de sessão **emitido pelo backend** (`HttpOnly; Secure; SameSite=Lax`; `Max-Age` = validade real do token) + proteção **CSRF** (double-submit + validação de `Origin`/`Referer` — nunca só `SameSite`; cobre também o login CSRF do form-urlencoded); remover token do localStorage e o cookie JS; `POST /autenticacao/logout` limpa os cookies (revogação server-side é o `S14`); manter `SecureStore` no mobile (Bearer continua aceito). **Decisão de 09/07/2026 (usuário):** o painel passa a chamar a API pelo **proxy `/api/*` do Next** (absorve o `M6`), então o cookie é **first-party** e `allow_credentials` do CORS **permanece `False`** — ao contrário do que esta linha dizia antes. Motivo: com chamada direta, domínios web/API diferentes tornariam o cookie de terceira parte (`SameSite=None`), bloqueado por padrão no Safari. Middleware do Next apenas **checa a presença** do cookie (evita flash de conteúdo); autorização real segue no backend, e o `JWT_SECRET` não sai dele. Propriedades do cookie ficam configuráveis por ambiente (`COOKIE_SECURE`/`COOKIE_SAMESITE`/`COOKIE_DOMAIN`) | `frontend/web/src/lib/auth.ts`, `auth-storage.ts`, `api.ts`, `middleware.ts`, `next.config.ts`, `backend/app/rotas/Autenticacao.py`, `backend/app/servicos/csrf.py` (novo), `configuracoes.py`, `main.py` |
| `[x]` | `868kaa3ax` | S7 | Login e cadastro sem rate limit, lockout ou atraso progressivo; timing do login denuncia e-mail cadastrado (`pwd.verify` só roda quando o usuário existe) e o cadastro público responde "Email ja cadastrado" (enumeração) | Fechado em 09/07/2026 (verificação de código): rate limit em memória por IP/e-mail no login e signup público (`seguranca.py`, 5 tentativas/5min, bloqueio 15min), hash dummy no login uniformizando o timing e respostas neutras ("Email ou senha incorretos"; cadastro público não revela e-mail já cadastrado). Evoluções registradas para não se perder: rate limit compartilhado (Redis) para multi-réplica → endurecimento de produção do `S9`; resposta neutra no fluxo de convite/onboarding → quando ele existir (evolução do `S3`) | `backend/app/rotas/Autenticacao.py`, `backend/app/rotas/Usuarios.py`, `backend/app/servicos/seguranca.py` |
| `[x]` | `868kaa3c6` | S8 | FastAPI expõe `/docs`, `/redoc` e `/openapi.json` por padrão | Nova config `API_DOCS_HABILITADO` (default `true`); `false` zera `docs_url`/`redoc_url`/`openapi_url` no `FastAPI(...)`, então as rotas nem são registradas. Validado com `docker compose up -d --force-recreate` nos dois estados (200 ligado, 404 desligado) e revertido para dev ao final | `backend/app/main.py`, `backend/app/configuracoes.py`, `backend/.env.example`, `docs/deploy-producao.md` |
| `[x]` | `868kaa3cg` | S9 | Ambiente Docker roda backend com `--reload`, volume de código e configuração de dev; não existe compose de produção e o web (Next.js) só roda com `npm run dev` fora do Docker | Fechado em 10/07/2026: `docker-compose.prod.yml` (backend sem reload/bind mount como `appuser` não-root + `--proxy-headers`; web via build standalone do Next como `node` não-root; Caddy único serviço com portas públicas, TLS Let's Encrypt + HSTS via `deploy/Caddyfile`; Postgres sem `ports:`); `.env.prod.example`; backup diário `deploy/backup-banco.sh` (+ cópia externa rclone); runbook `docs/deploy-producao.md` completado (deploy em ~4 comandos). Validado localmente: build das 2 imagens, healthchecks `healthy`, `whoami` non-root, `GET /` 200, `/docs` 404, `/login` 200, `caddy validate` ok. Bug achado na validação: composes de dev/prod sem `name:` disputavam o mesmo projeto Docker (um recriava os containers do outro) — corrigido com `name: facilichat`/`facilichat_prod`. Pendência única: emissão real do certificado TLS exige VPS com DNS público (não testável localmente) | `docker-compose.prod.yml` (novo), `backend/Dockerfile`, `frontend/web/Dockerfile` (novo), `frontend/web/.dockerignore` (novo), `deploy/Caddyfile` (novo), `deploy/backup-banco.sh` (novo), `.env.prod.example` (novo), `docker-compose.yml`, `docs/deploy-producao.md` |
| `[x]` | `868kaa3ct` | S10 | Scripts de seed criam usuários demo com senha padrão `Senha123` | Nova config `AMBIENTE` (`dev`/`staging`/`producao`, default `dev`, validada); `semear` recusa rodar com `AMBIENTE=producao` (sai com erro, sem tocar no banco); `.env.prod.example` passa a exigir `AMBIENTE=producao`. Novo subcomando `limpar-demo` remove usuários demo + tudo que depende deles (chamados, mensagens, refresh tokens, sessões revogadas), para rotação/limpeza em staging. Validado de ponta a ponta: bloqueio confirmado com `AMBIENTE=producao` (exit 1, banco intacto); `limpar-demo` rodado de verdade (removeu 5 usuários/14 chamados), confirmado vazio via API, idempotência confirmada (2ª chamada não encontra nada), e `semear` restaurou os 12 chamados originais | `backend/app/configuracoes.py`, `backend/scripts/gerenciar_banco.py`, `.env.prod.example`, `backend/.env.example` |
| `[x]` | `868kaa3dh` | S11 | App mobile não tem lockfile, então `npm audit` não roda de forma reproduzível | Fechado em 15/07/2026: o lockfile (`package-lock.json`, `lockfileVersion: 3`) já existia, commitado como efeito colateral do `A8`. Criado `.github/workflows/auditoria-mobile.yml` (mesmo padrão do `S12`): `npm ci` + `npm audit --audit-level=high` em push/PR do `package.json`/lockfile do mobile + semanal + manual. `npm audit` local acusa 13 vulnerabilidades moderadas, todas transitivas do Expo SDK 53 (`postcss`, `uuid`/`xcode`) e só corrigíveis via `expo@57.0.6` (bump major) — tratadas como parte do `V3` (migração sequencial de SDK), não duplicadas aqui; limiar do CI é alta/crítica para não travar o pipeline nessas moderadas já conhecidas, mas pegar qualquer vulnerabilidade nova e mais grave. Validado: `npm audit --audit-level=high` com exit code 0 | `frontend/mobile/package-lock.json`, `.github/workflows/auditoria-mobile.yml` (novo), `docs/setup.md` |
| `[x]` | `868kaa3dz` | S12 | Dependências Python não têm auditoria automatizada no projeto | Baseline local executado com `pip-audit` (limpo após migração para `PyJWT`); automatizado em 10/07/2026: workflow `.github/workflows/auditoria-python.yml` (primeiro CI do projeto) roda `pip-audit` em push/PR que toque o `requirements.txt` + semanalmente (pega CVE nova sem commit) + manual; rotina local e resposta a vulnerabilidade documentadas no `setup.md` | `.github/workflows/auditoria-python.yml` (novo), `docs/setup.md`, `docs/tecnico-backend.md` |
| `[x]` | `868ka61e5` | S13 | Faltava guia de produção para o `JWT_SECRET` (como gerar por ambiente e cadastrar como secret no provedor/CI, sem passar pelo Git) | Seção "Produção — JWT_SECRET e secrets por ambiente" adicionada ao `docs/setup.md` (geração PowerShell/Python/openssl, cadastro em VPS/provedor gerenciado/GitHub Actions, aviso de rotação) | `docs/setup.md` |
| `[x]` | `868kahv64` | S14 | Nenhuma revogação de sessão server-side: logout só limpa o cliente; token roubado vale as 8h inteiras (sem `jti`/denylist; troca/reset de senha não revoga nada) | `POST /autenticacao/logout` revoga de verdade (denylist do `jti` + família de refresh). Fechado nesta sessão: `PATCH /usuarios/eu/senha` (exige senha atual, denylista o `jti` da sessão atual e revoga todas as famílias de refresh do usuário) e `PATCH /usuarios/{usuarioID}/funcao` (só Gestor, mesma Empresa; revoga todas as famílias de refresh do alvo). Validado com curl: senha errada (400), senha certa revoga a sessão atual (`401 "Sessão encerrada"` reusando o token antigo), login com senha antiga falha e com a nova funciona; troca de função de outro usuário revoga o refresh dele (`401` ao tentar `/autenticacao/atualizar`); 403 para não-Gestor; 404 para alvo inexistente/de outra Empresa. Consultado `verificar-seguranca` antes de implementar (OWASP Session Management + Authentication Cheat Sheets) — abordagem já alinhada, sem necessidade de mudar a regra | `backend/app/rotas/Autenticacao.py`, `backend/app/rotas/Usuarios.py`, `backend/app/servicos/refresh.py`, `backend/app/modelos/SessaoRevogada.py`, `backend/app/servicos/revogacao.py` |
| `[x]` | `868kahv6r` | S15 | Access token de 8h (`JWT_EXPIRE_MINUTES=480`) sem refresh token — janela longa para uso de token roubado (XSS/infostealer) | Access token encurtado para 15min (`JWT_EXPIRE_MINUTES=15`); refresh token opaco (`{ID}.{segredo}`, só o hash sha256 do segredo fica no banco) com rotação a cada uso e detecção de reuso por família (`RefreshTokens`, `app/servicos/refresh.py`) — reuso de um token já consumido revoga a família inteira. Web: cookie `refresh` `HttpOnly` (`REFRESH_TOKEN_EXPIRE_DIAS=30`) + retry transparente single-flight em `lib/api.ts` num 401. Mobile: `refresh_token` no SecureStore + mesmo retry via `POST /autenticacao/atualizar`. Logout revoga a família também (não só o access token do S14). Validado via curl (rotação em cadeia, reuso derrubando a família, logout revogando) e através do proxy real do Next (cookie+CSRF) | `backend/app/servicos/refresh.py` (novo), `backend/app/modelos/RefreshToken.py` (novo), `backend/app/rotas/Autenticacao.py`, `backend/app/servicos/sessao.py`, `backend/app/configuracoes.py`, `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts`, `lib/auth.ts` (mobile) |
| `[x]` | `868kahv8b` | S16 | Web sem CSP nem headers de segurança (`X-Content-Type-Options`, `frame-ancestors`, `Referrer-Policy`, HSTS em prod) — sem CSP, um XSS faz requisições autenticadas mesmo com cookie HttpOnly | `headers()` no `next.config.ts`: CSP em `Report-Only` (promover a enforce após observação — guia no `setup.md`), `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`; HSTS documentado para o proxy HTTPS de produção; validado com `next build` + `next start` (headers conferidos na resposta real, variantes dev/prod) | `frontend/web/next.config.ts`, `docs/setup.md`, `docs/tecnico-frontend.md` |
| `[x]` | `868kahvad` | S17 | CORS com `allow_credentials=True` sem a API usar cookies, e wildcards em `allow_methods`/`allow_headers` | `allow_credentials=False`; listas explícitas `CORS_METODOS_PERMITIDOS` (`GET, POST, PATCH, OPTIONS` — a API não expõe `PUT`/`DELETE`) e `CORS_HEADERS_PERMITIDOS` (`Authorization, Content-Type`); `configuracoes.py` não precisou mudar. Validado com preflights reais (método/header/origem indevidos → 400) e fluxo autenticado preservado. **Religar credentials é tarefa do `S6`, junto do CSRF** | `backend/app/main.py`, `docs/tecnico-backend.md` |

### 🔄 Atualização de versões (auditoria de 10/07/2026) · CU: `868kb37q9`

> Origem: auditoria de atualidade de dependências pedida pelo usuário e verificada contra o projeto
> real (nenhuma vulnerabilidade ativa hoje — `npm audit`/`pip-audit` limpos — mas versões atrasadas
> em graus variados). Skill de apoio para rodadas futuras: `/verificar-versoes`.

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[x]` | `868kb32ap` | V1 | Docker Engine 29.5.3 desatualizado; 29.6.1 traz correções de segurança do Engine | Fechado em 15/07/2026: Docker Desktop atualizado via `winget upgrade` (4.79.0→4.82.0), trazendo Engine 29.5.3→29.6.1 e Compose v5.1.4→v5.3.0. Containers do projeto (`facilichat_db`/`facilichat_backend`) caíram no reinício do daemon e foram religados com `docker compose up -d`, confirmados saudáveis | máquina local (fora do repositório) |
| `[x]` | `868kb32cg` | V2 | Web: `npm run lint` não roda automatizado (config interativa); `next lint` será removido no Next 16 | Fechado em 15/07/2026: `eslint.config.mjs` (flat config, `FlatCompat` traduzindo `next/core-web-vitals`/`next/typescript`) com `.next/out/build` ignorados; script `lint` trocado para `eslint .`; nova dependência `@eslint/eslintrc`. Validado: `npm run lint` roda sem interação (exit 0, só 4 warnings pré-existentes em `api.ts`), `tsc --noEmit` e `npm run build` limpos | `frontend/web/package.json`, `eslint.config.mjs` (novo) |
| `[x]` | `868kb32gb` | V3 | Mobile: Expo SDK 53 (4 SDKs atrás); `npm audit` acusa 13 vulnerabilidades moderadas transitivas cuja correção exige SDK 57 | Fechado em 15/07/2026: migração sequencial 53→54→55→56→57, com `expo-doctor`/`tsc --noEmit`/`expo export --platform android|ios` validados a cada etapa. Correções pontuais no caminho: `@types/react` alinhado ao React 19.1 (SDK 54); `app.json` migrou o `splash` legado para o plugin `expo-splash-screen` e `@react-navigation/native` (dependência direta não usada em nenhum lugar do código) foi removido — SDK 56 descontinuou o uso conjunto com `expo-router`. **Vulnerabilidades:** a cadeia `uuid@7.0.3 → xcode → @expo/config-plugins` persistia mesmo no SDK 57.0.6 (mais recente); confirmado que `xcode` só chama `uuid.v4()` sem `buf` (a função vulnerável real é `v3/v5/v6` com `buf` informado, nunca usada aqui) e que o projeto é 100% managed workflow (sem `ios/android` nativos, `xcode` nunca executa hoje) — risco prático nulo. Ainda assim, `overrides.uuid: ^11.1.1` foi adicionado ao `package.json` e zerou o `npm audit` (0 vulnerabilidades), sem regressão em nenhuma validação | `frontend/mobile/package.json`, `frontend/mobile/app.json`, `frontend/mobile/app/_layout.tsx` |
| `[x]` | `868kb32ph` | V4 | Sem `.nvmrc`/`.python-version`/`engines`; Docker/CI usam Node 22/Python 3.12 e as máquinas locais podem divergir | Fechado em 15/07/2026: `.nvmrc` (`24`) e `.python-version` (`3.12`) novos na raiz; `engines.node` em `frontend/web/package.json` e `frontend/mobile/package.json`. **Decisão do usuário:** subir Node para 24 (não manter 22), então `frontend/web/Dockerfile` e `.github/workflows/auditoria-mobile.yml` também foram atualizados de `node:22`→`node:24` para não ficar inconsistente com o pin | `.nvmrc` (novo), `.python-version` (novo), `frontend/web/package.json`, `frontend/mobile/package.json`, `frontend/web/Dockerfile`, `.github/workflows/auditoria-mobile.yml`, `docs/setup.md` |
| `[x]` | `868kb32v1` | V5 | Next.js 15.5.20 desatualizado (atual 16.2.10) — não urgente, ainda em Maintenance LTS e sem vulnerabilidades | Fechado em 15/07/2026: `next`/`eslint-config-next` para `16.2.10`; `middleware.ts`→`proxy.ts` (renomeado manualmente, codemod recusou rodar por git sujo de outra frente); ESLint migrado do shim `FlatCompat` para o flat config nativo do `eslint-config-next` 16; Turbopack já padrão, sem mudança de script. **Regressão encontrada e corrigida:** regras novas do `eslint-plugin-react-hooks` v6 (via `eslint-config-next` 16) acusaram 5 erros em 4 arquivos com padrões antigos válidos — corrigidos (não rebaixados) por decisão do usuário. Validado com `npm run lint`/`tsc --noEmit`/`npm run build` limpos e smoke test real (`next start`: redirect 307 para `/login` + headers do S16 intactos) | `frontend/web/package.json`, `package-lock.json`, `eslint.config.mjs`, `src/proxy.ts` (novo, era `src/middleware.ts`), `src/lib/useAtualizacaoPeriodica.ts`, `src/components/painel/AdminShell.tsx`, `src/app/painel/chamados/page.tsx`, `src/app/painel/visao-geral/page.tsx`, `src/app/plataforma/empresas/page.tsx`, `tsconfig.json`, `docs/tecnico-frontend.md` |
| `[x]` | `868kb32wc` | V6 | Backend: 11 pacotes Python com versões menores mais novas (FastAPI, Uvicorn, SDK Anthropic, Alembic, AnyIO etc.), sem vulnerabilidade conhecida | Fechado em 15/07/2026: 10 dos 11 pacotes atualizados (`alembic` 1.18.4→1.18.5, `anthropic` 0.111.0→0.116.0, `anyio` 4.14.0→4.14.2, `cffi` 2.0.0→2.1.0, `click` 8.4.1→8.4.2, `fastapi` 0.138.0→0.139.0, `greenlet` 3.5.2→3.5.3, `jiter` 0.15.0→0.16.0, `typing_extensions` 4.15.0→4.16.0, `uvicorn` 0.49.0→0.51.0); `pydantic_core` mantido em `2.46.4` — `pydantic` 2.13.4 (já a versão mais nova) fixa essa dependência exata, upgrade isolado quebraria a resolução (`pip install` confirmado com `ResolutionImpossible`). Sem suíte de testes automatizada no backend (já documentado); validado via `docker compose build`, reset+reseed e checagem manual pela API (login, `/categorias/`, `/chamados/`, `/usuarios/equipe`, `/relatorios/visao-geral`, 401 anônimo) e `verificar-rls` OK | `backend/requirements.txt` |

### 🟡 Médios · CU: `868kb37nf`

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[x]` | `868k60v2w` | M1 | Falta validação Pydantic de tamanho/força (senha sem `min_length`) | Fechado em 15/07/2026 (consultado `verificar-seguranca`/OWASP antes): senha com `min_length=15` (**decisão do usuário** — OWASP recomenda 15 sem MFA; era 8 no `SenhaAlterar` do S14) e `max_length=128`, sem regras de composição, em `UsuarioCriar`, `SenhaAlterar.SenhaNova` e `PrimeiroGestorCriar` (`SenhaAtual` só com teto); `max_length` nos campos livres (`Nome`/`Condominio` 120, `Telefone` 20, `Categoria` 80 + `min_length=1`, `Resumo` 2000, `CNPJ` 20). Senha demo rotacionada para `FaciliChat2026Demo` (seed + Gestor Demo via API + docs/skills). Validado com curl: 422 em PT nos casos curto/longo/vazio, troca de senha real e logins com as senhas novas ok | `backend/app/rotas/Usuarios.py`, `Chamados.py`, `Plataforma.py`, `backend/scripts/gerenciar_banco.py`, `docs/setup.md` |
| `[x]` | `868k60v30` | M2 | `IntegrityError` no cadastro não tratado (corrida TOCTOU no check de email) | Fechado em 15/07/2026: `IntegrityError` capturado no commit de `_persistirUsuario` → rollback + 400 com a **mesma resposta neutra do S7** (específica reabriria enumeração de e-mail); mesmo tratamento em `POST /plataforma/empresas` (CNPJ no `flush`, e-mail do gestor no `commit` — mensagens específicas lá, rota só de Superadmin; rollback não deixa Empresa órfã). Validado com 4 curls paralelos (1×200, 3×400, nenhum 500) e teste determinístico no container forçando a corrida exata (barreira após os pre-checks: B recebeu 400 neutro da constraint) | `backend/app/rotas/Usuarios.py`, `backend/app/rotas/Plataforma.py` |
| `[x]` | `868k60v33` | M3 | Magic strings `"Gerente"/"Supervisor"` em vez do enum | Comparar com `UsuarioFuncao.Gestor`/`.Supervisor` (corrigido junto da Fase 0.6) | `backend/app/rotas/Chamados.py` |
| `[x]` | `868k60v3c` | M4 | `echo=True` fixo no engine (loga todo SQL em produção) | `echo=configuracoes.DEBUG` com `DEBUG=false` por padrão (env documentada no `.env.example` e `setup.md`) | `backend/app/banco_dados.py`, `configuracoes.py` |
| `[x]` | `868k60vam` | M5 | `Config` (Pydantic v1), `datetime.utcnow` deprecado e colunas `DateTime` naive | `SettingsConfigDict` no `configuracoes.py`; `agoraUtc()` (novo `app/tempo.py`) + `DateTime(timezone=True)` em todos os modelos, rotas e seed; migração `scripts/aplicar_m5_timestamptz.py` converte banco de dev existente preservando dados; validado com login/criação/atualização de chamado reais | `backend/app/modelos/*.py`, `rotas/*.py`, `configuracoes.py`, `app/tempo.py`, `scripts/` |
| `[x]` | `868k60vay` | M6 | Web: rewrite/proxy em `next.config.ts` configurado mas nunca usado | **Estratégia decidida em 09/07/2026: usar o proxy.** O painel chama `/api/*` (mesma origem do Next), tornando o cookie de sessão first-party; base URL centralizada em `api.ts`. Exigiu `skipTrailingSlashRedirect` + rewrite que preserva a barra final (senão o `fetch` seguiria um 307 do FastAPI para fora do proxy). Implementado e fechado **dentro do `S6`** | `frontend/web/next.config.ts`, `lib/api.ts` |
| `[x]` | `868k60vb1` | M7 | Web: `Record<string,string>` em vez dos enums; `err: any`; `erro.detail` não tipado | Fechado em 15/07/2026: `STATUS_LABEL`/`STATUS_COR` → `Record<ChamadoStatus, string>` e `PRIORIDADE_COR` → `Record<ChamadoPrioridade, string>`; `catch` com `err: unknown` + `instanceof Error` e mensagem PT. O `erro.detail` já tinha sido normalizado pelo M12 (`extrairDetail` em `lib/api.ts`), sem mudança adicional lá. Regra dos mapas tipados registrada no `tecnico-frontend.md` (enums da seção "Tipos compartilhados" corrigidos junto — citavam 4 perfis/3 filas). Validado com `tsc --noEmit` | `frontend/web/src/app/painel/chamados/page.tsx`, `docs/tecnico-frontend.md` |
| `[x]` | `868k60vb3` | M8 | Web: `token()` duplicado entre `api.ts` e `auth.ts` | Fechado em 15/07/2026 como obsoleto: o refactor do S6 (sessão via cookie `HttpOnly`) já removeu `token()` dos dois arquivos — `auth.ts` não guarda mais token nenhum e `api.ts` não injeta `Authorization`; não havia duplicação a corrigir | `frontend/web/src/lib/api.ts`, `frontend/web/src/lib/auth.ts` |
| `[x]` | `868k60vbb` | M9 | Web: arquivos CSS sem nenhum comentário (viola regra do `CLAUDE.md`) | Fechado em 15/07/2026: `globals.css` e `supervisores.module.css` já tinham cabeçalho e comentários de bloco; adicionado cabeçalho + comentário por bloco lógico em `login.module.css`, `chamados.module.css`, `empresas.module.css` e `visao-geral.module.css` (só comentários — nenhuma classe/valor alterado, confirmado via `git diff`) | `frontend/web/src/app/**/*.css` |
| `[x]` | `868k60vbj` | M10 | Mobile: `chamados.tsx`/`perfil.tsx` sem `catch` → erros engolidos | Adicionar `catch` com estado de erro e botão "Tentar novamente" | `frontend/mobile/app/(tabs)/chamados.tsx`, `frontend/mobile/app/(tabs)/perfil.tsx` |
| `[x]` | `868k60vbz` | M11 | Mobile: paleta fora dos tokens; Figtree não carregada | Substituir pelos tokens Ink; carregar Figtree via `expo-font` | `frontend/mobile/app/**`, `frontend/mobile/lib/theme.ts`, `frontend/mobile/app/_layout.tsx` |
| `[x]` | `868kcn4wu` | M13 | Balões de validação nativa do HTML5 (`required`, `type="email"`) aparecem no idioma do navegador (inglês) no login e no cadastro de Empresas — complemento do M12, que só cobriu erros vindos da API | Fechado em 15/07/2026: handlers reutilizáveis em `lib/validacao.ts` — `aoInvalidarCampo` (`onInvalid` → `setCustomValidity` em PT por motivo) e `limparValidacaoCustomizada` (`onInput` limpa para o navegador revalidar) — aplicados no login e no cadastro de Empresas, mantendo a validação nativa. Regra para telas novas documentada no `tecnico-frontend.md`. Validado com `tsc --noEmit` e Playwright lendo `validationMessage` na página real (e-mail sem `@`, campos vazios, destrava ao digitar) | `frontend/web/src/lib/validacao.ts` (novo), `frontend/web/src/app/(auth)/login/page.tsx`, `frontend/web/src/app/plataforma/empresas/page.tsx` |
| `[x]` | `868kakk65` | M12 | Mensagens de erro em inglês vazam ao usuário: 422 do Pydantic (`Field required` etc., com `detail` em lista que o front exibe como `[object Object]`) e falha de rede do fetch (`Failed to fetch`) | Handler de `RequestValidationError` no backend traduz os tipos comuns para PT e devolve `detail` como string; web/mobile ganharam `extrairDetail` (string/lista) e `fetchOuErroDeConexao` (falha de rede → mensagem PT); validado com curl (422/401 em PT) e `tsc --noEmit` nos dois fronts | `backend/app/main.py`, `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |

### 🟢 Baixos · CU: `868kb37nt`

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[x]` | `868k60vc3` | B1 | Raios de canto fora da escala (cards 10/12 em vez de 8; inputs 10) | Cards web ajustados para `--r-sm`/8px e mobile centralizado em `theme.radius.card/control` | web e mobile (CSS/estilos) |
| `[x]` | `868k60vca` | B2 | `useEffect` de fetch sem cleanup/AbortController (web e mobile) | Fechado em 15/07/2026: `painel/chamados/page.tsx` e `painel/visao-geral/page.tsx` já tinham guarda de montagem (`montadoRef`/`ativoRef`); adicionada a mesma guarda em `plataforma/empresas/page.tsx` (web) e em `(tabs)/chamados.tsx`/`(tabs)/perfil.tsx` (mobile) — nenhum `setState` roda mais após a tela desmontar. Convenção documentada no `tecnico-frontend.md` para telas novas. Validado com `tsc --noEmit` nos dois fronts | `frontend/web/src/app/plataforma/empresas/page.tsx`, `frontend/mobile/app/(tabs)/chamados.tsx`, `frontend/mobile/app/(tabs)/perfil.tsx`, `docs/tecnico-frontend.md` |
| `[x]` | `868k60vck` | B3 | Web: faltam `error.tsx` e `not-found.tsx` | Fechado em 15/07/2026: `app/error.tsx` (boundary global client-side, botão "Tentar novamente" via `reset()`, erro só no `console.error`) e `app/not-found.tsx` (404 com link "Voltar ao início"), em PT e nos tokens do design system (`app/erro.module.css` compartilhado, padrão visual do card de login). Validado com `tsc --noEmit` e Playwright no dev server real: 404 em desktop/mobile e boundary exercitado por rota temporária que lança exceção (removida após a captura) | `frontend/web/src/app/error.tsx`, `not-found.tsx`, `erro.module.css` (novos) |
| `[x]` | `868k60vct` | B4 | Mobile: tabs sem ícones (Line Awesome) | Adicionar `tabBarIcon` às abas | `frontend/mobile/app/(tabs)/_layout.tsx` |
| `[x]` | `868k60vcx` | B5 | A11y: foco de teclado removido; navegação sem ARIA; estados sem `aria-live` | Fechado em 15/07/2026: `:focus-visible` global no `globals.css` (anel 2px em `--border-focus`, qualquer elemento focável; removido o local redundante do `erro.module.css`); sidebar com `aria-label`/`aria-current="page"`/ícones `aria-hidden`; carregando com `role="status"` e erros com `role="alert"` (aria-live implícito) em chamados, visão geral, login e empresas (supervisores já conforme). Convenções registradas no `tecnico-frontend.md`. Validado com `tsc --noEmit` e Playwright real: Tab mostra outline `2px solid #148AF5` em botão e links, senha errada dispara o `role="alert"`, nav autenticada expõe o ARIA | `frontend/web/src/app/globals.css`, `erro.module.css`, `components/painel/AdminShell.tsx`, páginas de chamados/visão geral/login/empresas |
| `[x]` | `868k60vd4` | B6 | Backend: JWT sem `iat/iss/aud/jti`; hasher duplicado (achado um 4º ponto em `Plataforma.py` além dos 3 do levantamento original); `@app.on_event` deprecado | Claims `iat/iss/aud/jti` no token (`criarToken`) e validadas no decode (`_decodificarToken`, com `issuer`/`audience`); hasher centralizado em `app/servicos/hasher.py` e reaproveitado por `Autenticacao.py`, `Usuarios.py`, `Plataforma.py` e `gerenciar_banco.py`; `@app.on_event("startup")` migrado para `lifespan`. Validado com `import app.main`, reset+seed do banco e `verificar-rls` | `backend/app/servicos/hasher.py` (novo), `backend/app/rotas/Autenticacao.py`, `Usuarios.py`, `Plataforma.py`, `backend/app/main.py`, `backend/scripts/gerenciar_banco.py` |
| `[x]` | `868k7vx0v` | B7 | Painel web (desktop do Gestor) não validado em navegador mobile (breakpoints, tabelas largas) | Validado com Playwright (Chromium) em viewport mobile (390×844) e desktop (1440×900), autenticado como Gestor Demo: `/painel/chamados`, `/painel/supervisores` e `/painel/visao-geral` sem overflow horizontal, sidebar colapsa para o topo em mobile, cards empilham em coluna única, sem erros de console | `frontend/web/src/app/painel/**` |
| `[x]` | `868kcv8we` | B8 | `middleware.ts` ainda redirecionava para `/painel/chamados` após login (usuário reportou tela em branco ao abrir `localhost:3000` com sessão ativa) — o ajuste anterior só tinha corrigido o `router.push` do formulário de login, não o redirect server-side | Fechado em 15/07/2026: os dois redirects do `middleware.ts` (login já autenticado; `/plataforma` para não-Superadmin) e o guard client-side de `/plataforma/empresas` agora apontam para `/painel/visao-geral` | `frontend/web/src/middleware.ts`, `frontend/web/src/app/plataforma/empresas/page.tsx` |
| `[x]` | `868kcvg5c` | B9 | Mobile: `app/_layout.tsx` carrega as fontes Figtree com um `require(...)` de caminho que não existe no pacote (`@expo-google-fonts/figtree/Figtree_400Regular.ttf`), quebrando qualquer bundle real (Android/iOS). **Origem:** achado em 15/07/2026 durante a migração V3 do Expo SDK, ao validar com `expo export --platform android` — nunca tinha sido pego porque `expo-doctor` não bundla o JS e o app nunca fora validado com build real | Fechado em 15/07/2026: caminhos corrigidos para a subpasta real de cada peso (`400Regular/`, `600SemiBold/`, `700Bold/`), mantendo as mesmas chaves de família (`Figtree`, `Figtree-SemiBold`, `Figtree-Bold`) usadas em `theme.ts`. Validado com `expo export --platform android` (bundle e os 3 `.ttf` presentes nos assets) e `tsc --noEmit` | `frontend/mobile/app/_layout.tsx` |

### Revisão de layouts web/mobile — 09/07/2026

| Status | Ordem | Etapa | Arquivo(s) |
|--------|-------|-------|------------|
| `[x]` | 1 | Mapear fontes de design, tokens, telas, navegação e estilos globais existentes | `docs/FaciliChat-Regras/`, `docs/tecnico-frontend.md`, `frontend/web/src/app/globals.css`, `frontend/mobile/lib/theme.ts` |
| `[x]` | 2 | Padronizar raios, estados de botão e breakpoints das telas web existentes | `frontend/web/src/app/**/*.css`, `frontend/web/src/components/**/*.css` |
| `[x]` | 3 | Remover cores, tamanhos e espaçamentos soltos das telas mobile já existentes | `frontend/mobile/app/**`, `frontend/mobile/lib/theme.ts` |
| `[~]` | 4 | Validar visualmente em navegador desktop/mobile e em Expo após build/typecheck | web validado (Playwright, ver B7); falta Expo (emulador/dispositivo) |

### 📄 Documentação (divergências com o código real) · CU: `868kb37p9`

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[x]` | `868k60vdg` | D1 | Divergência de enums: doc cita `AutorTipo: Humano/IA/Sistema` mas código usa `Cliente/Supervisor/Funcionario/IA/Sistema` | Fechado em 15/07/2026: as duas ocorrências no plano (item da Fase 0 e notas rápidas) sincronizadas com o enum real; `tecnico-backend.md` já estava correto no `AutorTipo`, mas a tabela de `Funcao` (4 perfis com "Gerente") e as permissões de chamados foram atualizadas para os 7 perfis com `Gestor` | `plano-implementacao.md`, `tecnico-backend.md` |
| `[x]` | `868k60vdm` | D2 | Datas inconsistentes no `changelog.md` (mistura 2025/2026) | Fechado em 15/07/2026: versões `0.1.0`/`0.2.0`/`0.3.0`/`0.3.1` corrigidas de 2025 para junho de 2026 (typo entre entradas do mesmo período); mantido o "07/2025" da nota de WhatsApp por ser data externa real da política da Meta | `docs/changelog.md` |
| `[x]` | `868k60vdp` | D4 | `tecnico-backend.md` documenta `uvicorn app.main:app` que falha pelos imports | Fechado em 15/07/2026: "Como rodar" reescrito — caminho padrão é `docker compose up -d` (Postgres + API, como o compose faz hoje) e o `uvicorn` direto virou alternativa com `docker compose up -d db`; o comando funciona desde o `C2` (`__init__.py`) | `docs/tecnico-backend.md` |
| `[x]` | `868kaa3f2` | D5 | `visao-geral.md` está desatualizado: diz que o código ainda tem 4 perfis/"Gerente" e só 3 filas, mas o código já tem 7 perfis e fila `Comercial` | Fechado em 15/07/2026: reescrito para o estado real (7 perfis implementados, 4 filas com Comercial, multi-tenant/Superadmin entregues, KPIs reais, tickets irmãos, segurança atual); próximos passos só com o que falta e tabela de estado separando feito de planejado | `docs/visao-geral.md` |
| `[x]` | `868kaa3fz` | D6 | `arquitetura.md` afirma que `obterTenantAtual` é injetada em todas as rotas, mas a revisão mostrou rotas usando `obterBancoDados` puro | `arquitetura.md` atualizado junto do `S2`, descrevendo a dependência tenant-aware real (`obterBancoDadosComTenant`) | `docs/arquitetura.md`, `backend/app/rotas/*.py` |
| `[x]` | `868kaa3ga` | D7 | Notas rápidas do plano mantêm `AutorTipo mensagem: Humano/IA/Sistema`, divergindo do código atual (`Cliente/Supervisor/Funcionario/IA/Sistema`) | Fechado em 15/07/2026 junto do D1: a regra canônica confirmada é a do código (o enum diferencia os papéis humanos para rastreabilidade da autoria — tese anti-amnésia); notas rápidas sincronizadas | `docs/plano-implementacao.md`, `docs/tecnico-backend.md` |
| `[x]` | `868kaa3h4` | D8 | Resultado da validação dos HTMLs de branding ainda não existe como checklist explícito de aceite | Fechado em 15/07/2026: criada a seção "Checklist de aceite do branding (item D8)" no `arquitetura.md`, com critérios verificáveis por eixo (design system, anti-amnésia, multi-tenant, IA ancorada, visita técnica, jornadas) e nota de status por eixo; o aceite é reavaliado a cada entrega que toque o eixo | `docs/arquitetura.md` |

---

## Fase 0.6 — Alinhamento de domínio com o branding 📐 [PRIORITÁRIO] · CU: `868k60vdy`

> **Origem:** revisão dos documentos comerciais em `docs/FaciliChat-Regras/` em 27/06/2026. Termos
> canônicos do branding: a empresa cliente que compra é a **Empresa** (conservadora/facilities, ex.:
> "Cefram"); os clientes dela são **Condomínios** (síndicos); a plataforma é operada pela Iugo
> Performance como **Superadmin**.

### Papéis de usuário — o branding define 7 perfis
Hoje o enum `UsuarioFuncao` tem 4 (Cliente, Supervisor, Funcionario, **Gerente**). O branding define 7:
**Cliente, Funcionário, Supervisor, RH, Financeiro, Gestor, Superadmin**.

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60ve3` | Renomear `Gerente` → **`Gestor`** no enum e em todo o código (rotas, comparações, JWT, `isGerente`→`isGestor`, scripts) | `backend/app/modelos/Usuarios.py`, `rotas/*.py`, `frontend/**` |
| `[x]` | `868k60ve6` | Adicionar perfis **`RH`** e **`Financeiro`** ao `UsuarioFuncao` | `backend/app/modelos/Usuarios.py` + tipos do front |
| `[x]` | `868k60ve8` | Adicionar **`Superadmin`** (a Iugo Performance — ver Fase 0.7) | `backend/app/modelos/Usuarios.py` |
| `[x]` | `868k60vec` | Manter **`Funcionário` como perfil único** (sem subtipos) — decisão de produto do branding | — |

### Filas / roteamento
| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60vee` | Adicionar fila **`Comercial`** (contratos/propostas, roteada ao Gestor) ao `ChamadoFila` | `backend/app/modelos/Chamados.py` + tipos do front |

### Regras de negócio do branding a incorporar
| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60vem` | **Tickets irmãos:** uma mensagem pode gerar 2+ chamados simultâneos (ex.: atestado → RH valida + Supervisor cobre o posto) | `backend/app/rotas/Chamados.py`, `backend/app/servicos/chamados.py` |
| `[x]` | `868k7vrt2` | **Modelar o vínculo dos tickets irmãos:** campo de agrupamento no `Chamado` (`GrupoOrigemID`) que liga chamados nascidos do mesmo aviso | `backend/app/modelos/Chamados.py` |
| `[x]` | `868k60veu` | **Cliente = Condomínio/contrato** com um responsável (síndico): evoluir campo texto `Condominio` para entidade (Fase 7) | `backend/app/modelos/`, `backend/app/rotas/Usuarios.py`, `backend/scripts/aplicar_fase_06_condominios.py`, `backend/scripts/semear_chamados.py` |

### Refinos da Visita Técnica (MVP02) conforme o branding
> Refinos reclassificados para a **Fase 8 — MVP 02: Visitas Técnicas**, onde a entidade/rotas de
> visita serão implementadas de fato. No ClickUp, as subtarefas antigas dessa realocação (3 de
> visita + 1 de IA, que ficaram órfãs sob a Fase 0.6) foram **arquivadas e recriadas sob as fases
> corretas em 09/07/2026** — os `CU:` das Fases 5 e 8 já apontam para as novas.

---

## Fase 0.7 — Fundação SaaS Multi-Tenant 🏢 [PRIORITÁRIO — antes das features] · CU: `868k60vfm`

> **Decisão de arquitetura (27/06/2026):** banco **compartilhado** + coluna `EmpresaID` (o "tenant_id")
> em **todas** as tabelas + **Row-Level Security (RLS)** do PostgreSQL + o tenant viaja no **JWT**.
> Hierarquia: **Empresa (tenant) → Condomínios → Usuários e Chamados**. **Regra de ouro:** todo dado
> pertence a uma Empresa e **toda consulta é filtrada por ela**.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60vft` | Modelo `Empresa` (tenant): `Nome`, `CNPJ`, `Status` (Ativa/Suspensa), `Criacao` | `backend/app/modelos/Empresa.py` (novo) |
| `[x]` | `868k60vg4` | Adicionar `EmpresaID` (FK, NOT NULL) em `Usuario`, `Chamado`, `Mensagem` | `backend/app/modelos/*.py` |
| `[x]` | `868k60vgm` | Incluir o `EmpresaID` no payload do JWT no login | `backend/app/rotas/Autenticacao.py` |
| `[x]` | `868k60vhk` | Dependência `obterTenantAtual` + `obterBancoDadosComTenant` para RLS | `backend/app/rotas/Autenticacao.py` |
| `[x]` | `868k60vjt` | **Todas** as queries filtram por `EmpresaID` do usuário logado | `backend/app/rotas/*.py` |
| `[x]` | `868k60vjw` | Row-Level Security (RLS) no PostgreSQL (defesa em profundidade) | `backend/app/rls.sql`, `backend/scripts/aplicar_rls.py` (novos) |
| `[x]` | `868k60vk6` | Papéis por tenant (o **Gestor** é gestor **da sua** Empresa, não global) | `backend/app/rotas/Usuarios.py`, `Chamados.py` |
| `[x]` | `868k60vkz` | Nível **Superadmin da plataforma** (Iugo): cadastrar/suspender Empresas e criar o 1º Gestor | `backend/app/rotas/Plataforma.py` (novo) |
| `[x]` | `868k60vn1` | `scripts/criar_empresa.py` — cria Empresa + 1º Gestor juntos (substitui `criar_gerente.py`, removido) | `backend/scripts/` |
| `[x]` | `868kaqxyt` | **Bootstrap do 1º Superadmin (Iugo Performance)** — subcomando `criar-superadmin` no `gerenciar_banco.py`, idempotente, que cria/reutiliza a Empresa da Iugo e o usuário Superadmin. Fecha o ovo-e-galinha: `POST /plataforma/empresas` exige um Superadmin autenticado, mas nada criava o primeiro (não existia **nenhuma** atribuição `Funcao = Superadmin` no backend). Recusa-se a promover usuário existente, para o bootstrap não virar escalonamento de privilégio. Descoberto em 09/07/2026 | `backend/scripts/gerenciar_banco.py`, `docs/setup.md`, `docs/deploy-producao.md` |
| `[x]` | `868kar8pq` | **Bug:** a Empresa que hospeda o Superadmin (`Iugo Performance`, criada pelo `criar-superadmin`) é gravada como uma linha comum em `Empresas`, sem marcação — `GET /plataforma/empresas` lista todas sem filtro, então a Iugo aparece misturada na lista de tenants do painel do Superadmin (e pode ser suspensa por engano, trancando os Superadmins pra fora). Corrigido com o flag `Empresa.EhPlataforma` (marcado pelo `criar-superadmin`), filtrado em `listarEmpresas` e bloqueado (400) em `atualizarStatusEmpresa`. Banco de dev resetado e validado via curl: listagem só mostra tenants reais, tentativa de suspender a Iugo é recusada | `backend/app/modelos/Empresa.py`, `backend/app/rotas/Plataforma.py`, `backend/scripts/gerenciar_banco.py` |

### Frontend (web e mobile)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60vn7` | Tenant vem do token; Empresa (ID e nome) guardados em `auth.ts`; exibição no cabeçalho fica para o `AdminShell` | `frontend/web/src/lib/auth.ts` |
| `[x]` | `868k60vnh` | Área de **Superadmin** (web) para gerenciar Empresas | `frontend/web/src/app/plataforma/empresas/page.tsx` (novo) |
| `[x]` | `868k60vnp` | Tipos: `EmpresaID`/`empresa_nome` em `Usuario`/`Chamado`/`TokenResposta` (web); mobile só sincronizou `UsuarioFuncao`/`ChamadoFila` | `frontend/web/src/types/index.ts` |

---

## Fase 0.8 — Consolidação pós-auditoria 🔒 [antes das features] · CU: `868kd1jc1`

> **Por que existe:** a revisão das fases concluídas encontrou lacunas nos limites entre o papel do
> banco, o ciclo de sessão e a validação. A fase corrige o que sustenta o desenvolvimento corrente e
> direciona preparação exclusiva de produção para a Fase 12. Especificação completa, evidências,
> riscos e aceite: `docs/implementation/09-fase-08-consolidacao.md`.

> **Ordem obrigatória:** RLS/papéis → destinação dos itens → logout mobile → usuário inativo →
> concorrência do refresh → suíte sob demanda → cancelamento/reabertura e comunicação.

| Status | CU | ID | Item | Decisão e critério principal |
|--------|----|----|------|------------------------------|
| `[x]` | `868kd1jtu` | F08-01 | **Tornar o RLS efetivo com papéis corretos de banco** | Separar papel administrativo do papel restrito da API. Como o banco atual é local/descartável, alterar `rls.sql`, resetar e repopular por `gerenciar_banco.py`; provar isolamento com a credencial real da aplicação. Upgrade sem perda fica para F12. |
| `[ ]` | `868kd1juf` | F08-02 | **Registrar a destinação de migrações e escopos complementares** | Alembic/upgrade sem perda → F12-01/02; Redis → F12-03; privacidade sensível/RH por tópico → Adiados (`868k7vrgk`); Empresa/Condomínio → Fase 7. Item documental, sem código. |
| `[ ]` | `868kd1juu` | F08-03 | **Fazer o logout mobile revogar a sessão no backend** | Chamar `/autenticacao/logout` com access+refresh antes da limpeza local; saída offline continua possível; reutilização online dos tokens deve falhar. |
| `[ ]` | `868kd1jvc` | F08-04 | **Impedir acesso de usuário inativo em toda a sessão** | Bloquear login, refresh e access já emitido; revisar dependências tenant-only; reativação exige novo login e nunca restaura sessões antigas. |
| `[ ]` | `868kd1jvr` | F08-05 | **Tornar a rotação de refresh segura sob concorrência real** | Single-flight já existe nos clientes, mas não cobre abas/instâncias/retries. Tornar consumo atômico no backend sem gerar dois sucessores nem revogar uma sessão legítima por corrida. |
| `[ ]` | `868kd1jwg` | F08-06 | **Criar suíte automatizada executável sob solicitação** | Organizar testes por fase/domínio e CI manual. Agentes preparam testes/comandos, mas nenhuma execução de teste/build/smoke/visual ocorre sem o usuário disparar explicitamente a fase/conjunto. |
| `[ ]` | `868kd1jwx` | F08-07 | **Implementar cancelamento, reabertura e continuidade do responsável** | Decisão aprovada em 16/07/2026: Gestor cancela qualquer chamado do tenant; Supervisor só o atribuído; RH/Financeiro só suas filas; motivo obrigatório; Cliente reabre o próprio Cancelado para Recebido, preservando responsável e criando novo ciclo SLA. Concluído não cancela/reabre. Detalhe: `docs/implementation/11-fase-08-07-cancelamento-reabertura.md`. |

### F08-07 — subfases obrigatórias

> **Decisão formal:** `docs/decisoes/ADR-001-cancelamento-reabertura-chamados.md`. O código atual já
> possui o enum `Cancelado` e a reatribuição backend (`CU: 868kcv8dp`), mas ainda não implementa o
> contrato abaixo por completo. Não confundir regra aprovada com entrega concluída.

| Status | CU | ID | Entrega | Aceite principal |
|--------|----|----|---------|------------------|
| `[ ]` | `868kd2du1` | F08-07A | Regras, matriz de permissões e transições | Contrato único para papel, fila, atribuição, estado e erros; Concluído ≠ Cancelado |
| `[ ]` | `868kd2dua` | F08-07B | Histórico estruturado de status, responsável e ciclos de SLA | Evento append-only com RLS; status+histórico atômicos; reatribuições e ciclos reconstruíveis |
| `[ ]` | `868kd2dug` | F08-07C | Backend de cancelamento | `POST /chamados/{id}/cancelar`; motivo 10–1000; matriz de autorização; PATCH genérico não contorna regra |
| `[ ]` | `868kd2dum` | F08-07D | Backend de reabertura | Somente Cliente solicitante; Cancelado→Recebido; mesmo ticket/responsável atual; novo ciclo SLA |
| `[ ]` | `868kd2dut` | F08-07E | Interfaces internas de cancelamento | Ação/modal acessível só para papel, fila, atribuição e estado permitidos |
| `[ ]` | `868kd2dvc` | F08-07F | Interfaces do Cliente para motivo e reabertura | Motivo sem nota interna; explicação obrigatória; Concluído orienta novo chamado |
| `[ ]` | `868kd2dw0` | F08-07G | Evento, narração segura da IA e mensagem no chat | Uma mensagem factual por evento; IA não inventa; fallback determinístico obrigatório |
| `[ ]` | `868kd2dw9` | F08-07H | SLA, relatórios e indicadores | Cancelado não conta como Concluído; reabertura reativa e cria ciclo; métricas/denominadores documentados |
| `[ ]` | `868kd2dwg` | F08-07I | Outbox e notificações idempotentes | Falha externa não desfaz status; retry não duplica; tenant/destino corretos |
| `[ ]` | `868kd2dwt` | F08-07J | Reatribuição de Supervisor na interface do Gestor | Reutiliza backend `868kcv8dp`; troca explícita, auditada e sem transferência silenciosa |
| `[ ]` | `868kd2dx0` | F08-07K | Testes, matriz de aceite e documentação | Testes preparados por subfase; execução somente após comando explícito do usuário |

### Limites explícitos da Fase 0.8

- Não implantar Alembic nem migração de produção agora.
- Não exigir preservação dos dados do banco local atual.
- Não implementar Redis antes da preparação multi-réplica.
- Não antecipar privacidade sensível/RH por tópico nem funcionalidades da Fase 7.
- Não permitir que IA decida cancelamento ou invente motivo/prazo/promessa.
- Não transformar a regressão completa nem os testes de fase em execução automática: o usuário
  dispara explicitamente cada fase/conjunto; até lá registrar “testes preparados — aguardando disparo”.

---

## Fase 1 — Chat (base do produto) · CU: `868k60vny`

> Desbloqueia o produto. Implementar **logo após** a consolidação da Fase 0.8. Especificação
> executável: `docs/implementation/12-fase-01-chat.md`; decisão aprovada:
> `docs/decisoes/ADR-002-chat-presenca-confirmacao.md`.

### Resultado e decisões aprovadas

- Histórico persistente/paginado, envio idempotente, leitura/não lidas, WebSocket recuperável,
  digitação e presença online real; central web e chat mobile resiliente.
- Gestor participa de todos os chamados do tenant; Supervisor também participa de todos, como ponte
  entre solicitante e áreas, sem ganhar cancelamento/reatribuição indevidos; RH/Financeiro tratam
  suas filas; Cliente/Funcionário os próprios; Superadmin não lê conteúdo operacional automaticamente.
- Supervisor/Gestor solicitam conclusão com resumo; Cliente decide em `AguardandoConfirmacao`.
  Aprovação conclui; recusa justificada volta a Em andamento, mesmo responsável/ciclo SLA.
- Lembretes configuráveis por Empresa, defaults 24h/48h/72h, snapshot por janela e sem conclusão
  automática. SLA operacional pausa; espera e tempo total permanecem auditáveis.
- Texto funciona nesta fase; tipos Audio/Imagem/Video/Documento são preparados, mas upload real
  depende da auditoria/implementação da Fase 9.

### Ordem obrigatória das subfases

`F01-A → B → C → D → E → F → G → H/I → J → K → L`

| Status | CU | Subfase | Entrega/gate de aceite |
|--------|----|---------|------------------------|
| `[ ]` | `868kd35hy` | F01-A — Contrato e permissões | Matriz papel×tenant×fila×solicitante×estado; leitura, envio e ações separados; HTTP/WS usam a mesma autoridade |
| `[ ]` | `868kd35kj` | F01-B — Persistência/autoria | AutorTipo completo, UTC, tipo/origem, idempotência, constraints, índices/cursor e seed; banco local descartável |
| `[ ]` | `868k60vpu`, `868k60vq1`, `868k60vrq` | F01-C — API | GET paginado + POST idempotente; autoria/tenant derivados; schemas/versionamento/erros PT; commit antes do evento |
| `[ ]` | `868k7vrte` | F01-D — Recebido | Chamado e confirmação Sistema atômicos; nenhuma dependência de IA; tickets irmãos preservados |
| `[ ]` | `868kd35m7` | F01-E — Confirmação e SLA | `AguardandoConfirmacao`, aprovação/recusa, configuração 24/48/72, scheduler idempotente, pausa/retomada do mesmo ciclo |
| `[ ]` | `868k60vrt` | F01-F — Tempo real | WS autenticado, eventos versionados, heartbeat, proxy, sessão/revogação e recovery HTTP; sem gravação direta pelo socket |
| `[ ]` | `868kd35n1` | F01-G — Leitura/presença | Não lidas monotônicas, multi-dispositivo, online real até última conexão, offline após 60s, digitação temporária |
| `[ ]` | `868k60vtc`, `868k60vt2`, `868k60vt8`, `868k60vun` | F01-H — Web | Central lista+thread responsiva/acessível, busca/badges, retry idempotente, presença e configuração do Gestor |
| `[ ]` | `868k60vvh`, `868k60vv3`, `868k60vv8`, `868k60vvm`, `868k60vvp` | F01-I — Mobile | Tipos alinhados, FlatList/paginação, offline/reconexão, navegação segura, presença e confirmação |
| `[ ]` | `868k7vrtu` | F01-J — Mídia | Contrato Texto/Áudio/Imagem/Vídeo/Documento sem exibir controles não funcionais; execução real vai à Fase 9 |
| `[ ]` | `868kd35p0` | F01-K — Integrações | Serviço/evento único para WhatsApp, IA, status, visitas, mídia e push; outbox quando externo |
| `[ ]` | `868kd35pv`, `868k60vrz`, `868k60vv2` | F01-L — QA/docs | Matriz requisito→teste→evidência, seed multi-tenant/perfis/estados, comandos e documentação completa |

### Contratos essenciais

- `GET/POST /chamados/{id}/mensagens`; cursor `Criacao+ID`, limite controlado e
  `ChaveIdempotencia` obrigatória no envio.
- `GET /conversas` e `POST /chamados/{id}/leitura`; contador por usuário/chamado sem retrocesso.
- `POST /chamados/{id}/solicitar-conclusao|confirmar-conclusao|recusar-conclusao|retirar-conclusao`.
- `GET/PATCH /configuracoes/confirmacao-chamado`, somente Gestor e validação
  `0 < primeiro < segundo < escalonamento`.
- `WS /ws/chamados/{id}`: eventos mensagem/digitação/presença, autenticação segura, heartbeat e
  reconexão que consulta HTTP. Token nunca vai na query string.

### Fora do escopo com destino obrigatório

- Upload/download/scan/compactação de mídia → Fase 9 (`868k60wn5`).
- WhatsApp/lembretes externos → Fase 1.5/MO8 (`868kd2e33`); push → Fase 10 (`868k60wpb`).
- IA/triagem/narração → Fases 5/5.5; visita → Fase 8; canal do Funcionário → Fase 11.
- Privacidade por assunto sensível continua evolução futura; não contradizer a decisão de Supervisor
  amplo no MVP.
- Broker/pubsub para presença/WS multi-réplica e Alembic/upgrade sem perda → Fase 12.

### Testes

Cada subfase prepara matriz, dados e comandos. **Não executar** teste, suite, build, smoke, export,
reset/seed de banco ou validação visual até o usuário disparar a Fase 1/conjunto. Ao implementar,
registrar `testes preparados — aguardando disparo do usuário`; nenhum `[ ]` vira validado por haver
teste escrito.

---

## Fase 1.5 — Fundação Multicanal: WhatsApp como porta de entrada 🆕 · CU: `868kb75yf`

> **Origem:** decisão de produto de 10/07/2026, já prevista no material comercial
> (`FaciliChat-Apresentacao.html`: "o WhatsApp vira um canal, nunca o dono dos seus dados").
> **Princípio arquitetural:** o WhatsApp é um **adaptador de entrada**. O núcleo (Mensagem, Chamado,
> tickets irmãos, IA, auditoria, isolamento por Empresa) permanece independente do canal.
> Fluxo: `WhatsApp / App / Web → entrada normalizada → Mensagem → Chamado(s) → operação FaciliChat`.
>
> **Posição:** o bloco inbound roda logo **após a Fase 1** (depende da base de mensagens) e **antes
> da Fase 5** (a IA passa a rotear mensagens de qualquer canal). O bloco outbound fica para **depois
> da Fase 5/5.5**. Dependências registradas no ClickUp: Fase 1.5 ← Fase 1 (`868k60vny`); MC10 ←
> Fase 9 (`868k60wn5`); Fase 5 (`868k60w34`) ← Fase 1.5; Outbound ← Inbound + Fase 5.
>
> **Referências técnicas confirmadas em 10/07/2026 (Meta WhatsApp Cloud API):** webhook com
> verificação GET (`hub.challenge`/verify token) e eventos POST assinados com `X-Hub-Signature-256`
> (HMAC-SHA256 do corpo bruto com o App Secret); entrega **at-least-once** — duplicatas são condição
> normal (dedup por `wamid` obrigatório; retries por até 7 dias); responder 200 rápido e processar
> assíncrono; mídia baixada via Graph API com URL efêmera; janela de atendimento de 24h (fora dela,
> só template aprovado); pricing por mensagem desde 07/2025 e mensagens de serviço passam a ser
> cobradas em 01/10/2026.
>
> **Invariantes preservados:** toda entidade nova tem `EmpresaID` + RLS; nada se perde (mensagem sem
> destino conhecido vai para triagem, nunca é descartada); evento duplicado não cria nada duplicado;
> números/templates são dados por Empresa (nunca hard-coded); o FaciliChat continua funcionando se a
> Meta cair (o canal para, o produto não).

### 📥 Bloco A — Inbound (MVP) · CU: `868kb76xr`

| Status | CU | ID | Item | Arquivo(s) |
|--------|----|----|------|-----------|
| `[ ]` | `868kb77b5` | MC1 | Enum `CanalOrigem` (App/Web/WhatsApp) em `Mensagem` e `Chamado` (derivado da 1ª mensagem); defaults preservam comportamento atual; tipos do front sincronizados | `backend/app/modelos/Mensagens.py`, `Chamados.py` |
| `[ ]` | `868kb77jm` | MC2 | Modelo `ContatoCanal` — vínculo (Canal, IdentificadorExterno E.164) ↔ Empresa/Usuário/Condomínio, com unicidade por tenant e RLS | `backend/app/modelos/ContatoCanal.py` (novo), `rls.sql` |
| `[ ]` | `868kb77m6` | MC3 | Correlação externa e idempotência: `MensagemExternaID` (wamid) **UNIQUE**, `ConversaExternaID`, `StatusExterno` (Recebido/Enviado/Entregue/Lido/Falhou) | `backend/app/modelos/MensagemCanal.py` (novo) |
| `[ ]` | `868kb77pw` | MC4 | Auditoria `EventosWebhook` (payload bruto + resultado), retenção **configurável** (política = decisão D4) | `backend/app/modelos/EventoWebhook.py` (novo) |
| `[ ]` | `868kb77rb` | MC5 | Camada de entrada normalizada: adaptador (payload Meta → DTO neutro) + núcleo neutro que reusa serviços existentes (incl. `montarChamadosIrmaos`); adaptador sem regra de negócio | `backend/app/servicos/canais.py`, `adaptadores/whatsapp.py` (novos) |
| `[ ]` | `868kb77u1` | MC6 | Webhook `GET /webhooks/whatsapp` (verificação) + `POST` (eventos) com 200 imediato e processamento assíncrono | `backend/app/rotas/WebhooksWhatsApp.py` (novo) |
| `[ ]` | `868kb77vb` | MC7 | Validação `X-Hub-Signature-256` (HMAC do corpo bruto, tempo constante; inválida → 403 + auditoria) | `backend/app/servicos/webhook_assinatura.py` (novo) |
| `[ ]` | `868kb77zj` | MC8 | Resolução segura de tenant/contato: `phone_number_id` → Empresa; `wa_id` → ContatoCanal; desconhecido segue política D2/D3 (**bloqueado pelas decisões MC-D**) | `backend/app/servicos/canais.py` |
| `[ ]` | `868kb781w` | MC9 | Criação/associação de chamado a partir da mensagem (conversa ativa anexa; sem chamado cria `Recebido`); compatível com tickets irmãos | `backend/app/servicos/canais.py` |
| `[ ]` | `868kb783m` | MC10 | Texto no MVP; áudio/imagem via Graph API (URL efêmera) — **depende da Fase 9** (`868k60wn5`); até lá, mídia fica pendente sem perder o evento | `backend/app/adaptadores/whatsapp.py` |
| `[ ]` | `868kb7855` | MC11 | Status externos (`statuses`: sent/delivered/read/failed) atualizam `MensagemCanal`; fora de ordem não regride estado | `backend/app/servicos/canais.py` |
| `[ ]` | `868kb786k` | MC12 | Testes de robustez: wamid duplicado, fora de ordem, assinatura inválida, tenant errado, payload malformado — nada duplica nem vaza entre Empresas | `backend/scripts/` (verificador) |
| `[ ]` | `868kb788v` | MC13 | Observabilidade + reprocessamento de evento falho a partir da auditoria (idempotente, seguro re-rodar) | `backend/app/servicos/canais.py`, logs |
| `[ ]` | `868kb78ar` | MC14 | Documentação: arquitetura multicanal, webhook, env vars Meta, setup de dev (número de teste) | `docs/arquitetura.md`, `tecnico-backend.md`, `setup.md` |

### 📤 Bloco B — Outbound (posterior — executar após a Fase 5/5.5) · CU: `868kb7701`

| Status | CU | ID | Item | Arquivo(s) |
|--------|----|----|------|-----------|
| `[ ]` | `868kb78gx` | MO1 | Resposta do atendente pelo WhatsApp na janela de 24h (free-form); custo: Meta cobra mensagens de serviço a partir de 01/10/2026 | backend |
| `[ ]` | `868kb78jn` | MO2 | Rastreio da janela de atendimento por conversa; painel indica quando só template é possível | backend + web |
| `[ ]` | `868kb78nd` | MO3 | Templates aprovados (utility/marketing/auth) geridos **por Empresa como dado no banco** | backend |
| `[ ]` | `868kb78qv` | MO4 | Mensagens iniciadas pela empresa + opt-in/opt-out persistido e honrado imediatamente | backend |
| `[ ]` | `868kb78v0` | MO5 | Onboarding/gestão de números (WABA, verificação, display name, tiers) — depende de D1/D5 | docs + ops |
| `[ ]` | `868kb78wq` | MO6 | Custos, limites e monitoramento de qualidade (quality rating, messaging limits, alertas) | backend |
| `[ ]` | `868kb78y9` | MO7 | Campanhas/recursos comerciais (futuro, se aprovado; liga com a Fase 6) | backend |
| `[ ]` | `868kd2e33` | MO8 | **Notificações transacionais do ciclo do chamado** — Recebido/Em andamento/Agendado/Aguardando confirmação/Concluído/Cancelado/Reaberto + lembretes/escalonamento F01-E; usa snapshot 24h/48h/72h, nunca conclui por silêncio; motivo/resumo/ação sem notas internas; janela ou template; outbox/idempotência/retry; falha não desfaz transição/SLA | `backend/app/servicos/canais.py`, histórico/outbox, templates por Empresa |

### ❓ Decisões pendentes de validação humana · CU: `868kb7937`

> Precisam de confirmação do usuário/comercial **antes do MC8** (que está bloqueado por elas no ClickUp):

| ID | Decisão | Afeta |
|----|---------|-------|
| D1 | Um número WhatsApp por Empresa vs número compartilhado da plataforma | MC8, MO5 |
| D2 | Contato desconhecido → pré-cadastro, chamado pendente ou fila de triagem | MC8, MC9 |
| D3 | Mesmo telefone representando 2+ condomínios → bot pergunta ou triagem humana | MC8 |
| D4 | Retenção do payload bruto (LGPD): 30/90 dias | MC4 |
| D5 | Meta Cloud API direta vs BSP (Twilio/360dialog/Infobip) | MC6, MO5 |
| D6 | **Parcialmente decidido em 16/07/2026:** notificações transacionais de status entram no escopo (MO8); respostas livres/campanhas continuam separadas e dependem das regras do outbound | fronteira A×B, MO8 |

---

## Fase 2 — Criar chamado e detalhe (cliente) · CU: `868k60vvt`

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vvx` | Validar que `POST /chamados/` retorna o chamado criado com ID para redirecionar | `backend/app/rotas/Chamados.py` |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vvz` | Botão "Novo chamado" abre modal com textarea (IA classifica no backend) | `frontend/web/src/app/(painel)/chamados/page.tsx` |

### Frontend Mobile

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vwa` | Tela "Novo chamado" — textarea livre, botão enviar, IA classifica no backend | `frontend/mobile/app/(tabs)/novo-chamado.tsx` (novo) |
| `[ ]` | `868k60vwk` | Adicionar aba "Novo" no tab navigator | `frontend/mobile/app/(tabs)/_layout.tsx` |
| `[ ]` | `868k60vx1` | Tela de detalhe do chamado — timeline vertical de status | `frontend/mobile/app/(tabs)/chamados/[id]/detalhe.tsx` (novo) |

---

## Fase 3 — Fila e operação do supervisor (mobile) · CU: `868k60vx4`

> Supervisor está em campo, no celular. Cada ação deve caber em menos de 30 segundos.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vxf` | `GET /chamados/?supervisor_id=me&ordenar=prazo` — lista filtrada para o supervisor logado | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k60vxk` | `PATCH /chamados/{id}/agendar` — salvar executor, data/hora, observação ao cliente | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k60vya` | Campo `NotaInterna` no modelo `Chamado` (nunca exposta ao cliente) | `backend/app/modelos/Chamados.py` |
| `[ ]` | `868k60vym` | `PATCH /chamados/{id}/concluir` — transição para Concluido + mensagem automática | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k7vru6` | **Solicitar conclusão em pouquíssimos toques** — Supervisor/Gestor informa resumo e entra em `AguardandoConfirmacao`; não marca Concluído diretamente; contrato F01-E | `frontend/mobile/app/(supervisor)/**` |
| `[ ]` | `868k7vruk` | **Aprovação do Cliente encerra o ticket** — Cliente confirma/recusa no chat; recusa justificada volta a Em andamento, mesmo responsável/ciclo SLA; defaults 24h/48h/72h sem auto-conclusão; distinto da Visita Técnica; implementação-base F01-E (`868kd35m7`) | `backend/app/modelos/Chamados.py`, rotas |
| `[ ]` | `868k7vrv2` | **Agenda do dia com prioridade visual sobre a fila** — ao abrir, o Supervisor vê primeiro as visitas de hoje, depois os tickets | `frontend/mobile/app/(supervisor)/**` |

### Frontend Mobile

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vzj` | Tela "Fila" do supervisor — abas: Todos / Atrasados / Aguardando / Agendados; ordenado por prazo | `frontend/mobile/app/(supervisor)/fila.tsx` (novo) |
| `[ ]` | `868k60vzp` | Badge vermelho em chamados com prazo estourado | (dentro da tela Fila) |
| `[ ]` | `868k60vzr` | Tela "Hoje" do supervisor — agenda do dia em ordem cronológica | `frontend/mobile/app/(supervisor)/hoje.tsx` (novo) |
| `[ ]` | `868k60w0b` | Tela "Ticket completo" — agendamento, observação ao cliente, nota interna oculta, botão Concluir | `frontend/mobile/app/(supervisor)/ticket/[id].tsx` (novo) |
| `[ ]` | `868k60w0v` | Navegação por abas do supervisor: Fila / Hoje / Perfil | `frontend/mobile/app/(supervisor)/_layout.tsx` (novo) |
| `[ ]` | `868k60w13` | Roteamento dinâmico por `Funcao` (Supervisor vs Cliente) | `frontend/mobile/app/(tabs)/_layout.tsx` ou `app/index.tsx` |

---

## Fase 4 — Dashboard do gestor (web) · CU: `868k60w16`

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60w1b` | `GET /relatorios/visao-geral` — total abertos, SLA estourado, 1ª resposta média, resolução média; exclusivo do Gestor, escopado por Empresa/RLS, médias em minutos e `null` sem amostra | `backend/app/rotas/Relatorios.py` (novo) |
| `[x]` | `868k60w1e` | `GET /relatorios/supervisores` — supervisores com abertos, atrasados, 1ª resposta média; exclusivo do Gestor, escopado por Empresa/RLS, inclui supervisores sem chamados e preserva `null` sem resposta registrada. Validado em 15/07/2026: rota/contrato presentes no OpenAPI, import real no contêiner e acesso anônimo rejeitado com 401 | `backend/app/rotas/Relatorios.py` |
| `[x]` | `868k60w1g` | `GET /chamados/?supervisor_id={id}` — fila de um supervisor específico, exclusiva do Gestor e restrita à mesma Empresa; mantém a listagem anterior quando o filtro não é enviado. Validado em 15/07/2026: supervisor válido retornou 7 chamados corretamente atribuídos (`200`), UUID inexistente retornou `404` e uso pelo Supervisor retornou `403` | `backend/app/rotas/Chamados.py` |
| `[x]` | `868k7vrvm` | **Alerta de gargalo "parado há tempo demais"** — `LimiteGargaloHoras` persistido por Empresa em configuração tenant-aware (padrão inicial 72h), com GET/PATCH exclusivos do Gestor; relatório lista chamados ativos cujo tempo parado é **derivado** de `Atualizacao`. Nova tabela compatível com instalações existentes via `create_all` e protegida por RLS. Validado em 15/07/2026: limite 72→24→72, gargalos 4→8, durações ≥ limite e valor inválido rejeitado com `422` | `backend/app/modelos/Empresa.py`, `backend/app/rotas/Relatorios.py`, `backend/app/rls.sql` |
| `[x]` | `868k7vrw8` | **Alerta de cobertura descoberta** — cobertura estruturada por Empresa (condomínio/posto, início/fim, funcionário e confirmação); Supervisor/Gestor registra e confirma; relatório exclusivo do Gestor lista turnos atuais/futuros sem funcionário confirmado. RLS aplicada e banco dev recriado com autorização do usuário. Validado em 15/07/2026: 2 descobertas, confirmação reduziu para 1, responsável/data persistidos, turno encerrado excluído e ambiente final resetado/limpo | `backend/app/modelos/CoberturaTurno.py` (novo), `backend/app/rotas/Coberturas.py` (novo), `backend/app/rotas/Relatorios.py`, `backend/app/rls.sql` |
| `[x]` | `868k7vrwh` | **Desempenho por supervisor com lastro** — relatório exclusivo do Gestor inclui todos os supervisores e deriva recebidos das atribuições, resolvidos de `Concluido`, parados de `Atualizacao` + limite configurável e taxa de resolução (`null` sem amostra). Validado em 15/07/2026: 7 recebidos, 2 resolvidos, taxa 28,57%; parados 3→5 ao alterar 72h→1h e limite restaurado | `backend/app/rotas/Relatorios.py` |
| `[x]` | `868kcv8dp` | `PATCH /chamados/{id}/supervisor` — atribui ou troca o supervisor responsável por um chamado existente; exclusivo do Gestor, supervisor precisa existir na mesma Empresa, `null` remove a atribuição. **Origem:** descoberto em 15/07/2026 ao popular o banco de demonstração com múltiplos supervisores — não existia nenhuma rota para isso (só inserção direta via script de seed). Validado em 15/07/2026: atribuição/remoção/reatribuição retornaram `200` com `SupervisorNome` correto; Supervisor tentando atribuir recebeu `403`; UUID de supervisor inexistente e chamado inexistente retornaram `404` | `backend/app/rotas/Chamados.py` |

### Backend — manutenção operacional do Gestor (categorias e equipe) 🆕

> **Origem:** discussão de planejamento de 15/07/2026 sobre como uma Empresa nova será implantada
> (categorias, equipe) e como o cliente fará manutenções depois (incluir/remover categoria,
> adicionar/remover supervisor). Nenhuma dessas operações existia até então — hoje o Superadmin só
> cria a Empresa + 1º Gestor (Fase 0.7), o tenant nasce vazio, `Categoria` é texto livre sem catálogo
> e não existe rota nenhuma para editar/desativar um usuário já criado. **Decisão de produto:** essa
> manutenção é autoatendimento do **Gestor** de cada Empresa (não tarefa manual do Superadmin por
> cliente); categoria vira **catálogo obrigatório por Empresa** (FK, não sugestão — inclui migrar as
> categorias já usadas nos chamados existentes); remover um membro da equipe é sempre **desativação,
> nunca exclusão** (tese anti-amnésia — preserva o histórico dos chamados já atendidos).

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868kcw5ft` | Modelo `CategoriaChamado` (`EmpresaID`, `Nome`, `Ativa`) — catálogo de categorias por Empresa. RLS aplicada (`app/rls.sql`) | `backend/app/modelos/CategoriaChamado.py` (novo) |
| `[x]` | `868kcw5gb` | CRUD de categorias (listar/criar/editar/ativar-desativar), exclusivo do Gestor, escopado por Empresa/RLS; desativar não afeta chamados já criados com aquela categoria. Validado em 15/07/2026: criar/duplicada (`400`)/ativar/desativar via curl | `backend/app/rotas/Categorias.py` (novo) |
| `[x]` | `868kcw5h9` | **Migração** `Chamado.Categoria` (texto livre) → `CategoriaID` (FK). **Decisão de 15/07/2026:** sem script incremental novo — `reset` + `criar-empresa` + `semear` recriaram o schema com o catálogo já povoado a partir das categorias do seed, consistente com a prática de não criar scripts `aplicar_fase_*` incrementais | `backend/app/modelos/Chamados.py`, `backend/scripts/gerenciar_banco.py` |
| `[x]` | `868kcw5mk` | `ChamadoCriar`/`ChamadoSaida` e rotas de chamado passam a exigir `CategoriaID` de uma categoria ativa da mesma Empresa (substitui o campo texto); resposta inclui o nome da categoria via join. Validado em 15/07/2026: criação com categoria ativa (`200`), inativa (`404`) e inexistente (`404`); `GET /chamados/`, `/irmaos`, `/gargalos` ajustados | `backend/app/rotas/Chamados.py`, `backend/app/rotas/Relatorios.py`, `backend/app/servicos/chamados.py` |
| `[x]` | `868kcw5nh` | `Usuario.Ativo` (novo campo, default `True`) + `PATCH /usuarios/{id}/status` (ativar/desativar), exclusivo do Gestor; usuário inativo não loga e não aparece para novas atribuições. Gestor não pode autodesativar (`400`). Validado em 15/07/2026 via curl | `backend/app/modelos/Usuarios.py`, `backend/app/rotas/Usuarios.py` |
| `[x]` | `868kcw5qk` | `GET /usuarios/equipe` (lista a equipe da Empresa, filtro por `Funcao`) e `PATCH /usuarios/{id}` (edita Nome/Telefone/Email) — exclusivos do Gestor. Validado em 15/07/2026: filtro por Supervisor, edição de telefone e `403` para não-Gestor | `backend/app/rotas/Usuarios.py` |
| `[x]` | `868kcw5v8` | Login (`POST /autenticacao/login`) nega acesso (401) a usuário `Ativo=False`; `PATCH /chamados/{id}/supervisor` só aceita supervisor ativo. Validado em 15/07/2026: supervisor desativado recebeu `401` no login e `404` na atribuição | `backend/app/rotas/Autenticacao.py`, `backend/app/rotas/Chamados.py` |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60w1k` | Página `/painel` redirecionada para `/painel/visao-geral` | `frontend/web/src/app/(painel)/page.tsx` |
| `[x]` | `868k60w1r` | Página `visao-geral` — cards de KPIs (abertos, SLA em risco, 1ª resposta, resolução) | `frontend/web/src/app/(painel)/visao-geral/page.tsx` (novo) |
| `[x]` | `868k60w1y` | Seção "Desempenho por supervisor" — tabela cruza carga, primeira resposta e desempenho com lastro por supervisor; exibe nome, abertos, resolvidos/recebidos e estado operacional, com acesso à equipe. Validado visualmente pelo usuário em 15/07/2026: Roberto Supervisor com 5 abertos, 2 de 7 resolvidos, primeira resposta de 34 min e estado "Precisa de atenção" | `frontend/web/src/app/painel/visao-geral/page.tsx`, `visao-geral.module.css`, `frontend/web/src/lib/api.ts`, `frontend/web/src/types/index.ts` |
| `[x]` | `868k60w26` | Seção "Volume por categoria" — categorias vêm **dos dados** (agregação real), não de lista fixa | (dentro de visao-geral) |
| `[x]` | `868k7vrwr` | **Hierarquia do painel: urgente → tendência → detalhe** — ação agora primeiro; tendência em 2º nível; detalhe sob demanda | (dentro de visao-geral) |
| `[x]` | `868k7vrx5` | **Painel "O que precisa da sua atenção"** — alertas críticos, atenções operacionais e oportunidades já roteadas à fila Comercial, sem atribuir detecção à IA; cada item abre e realça diretamente o chamado correspondente. Validado em 15/07/2026: TypeScript sem erros, 2 críticos e 5 atenções reais no banco local, destinos sem erro de runtime e aprovação visual do usuário | `frontend/web/src/app/painel/visao-geral/page.tsx`, `visao-geral.module.css`, `frontend/web/src/app/painel/chamados/page.tsx`, `chamados.module.css` |
| `[x]` | `868k60w2a` | Página `supervisores` — cards clicáveis com métricas reais; clique busca e expande a fila atribuída daquele supervisor, com estados isolados de carregamento/erro e cache por card. Validado em 15/07/2026: TypeScript sem erros, rota `200` sem erro de runtime e aprovação visual do usuário | `frontend/web/src/app/painel/supervisores/page.tsx`, `supervisores.module.css`, `frontend/web/src/lib/api.ts`, `frontend/web/src/types/index.ts` |
| `[x]` | `868k60w2j` | Página `tickets` — tabela com filtros: período, supervisor, status, categoria; busca por cliente. Validado em 15/07/2026: login como Gestor Demo via Playwright, 25 tickets renderizados sem erro de console, filtro de Status reduziu a lista de 25→10 corretamente | `frontend/web/src/app/(painel)/tickets/page.tsx` (novo) |
| `[x]` | `868k60w2w` | Adicionar links no sidebar: Visão geral / Supervisores / Todos os tickets / Alertas; Alertas aponta para a seção existente `#atencao`, sem antecipar a página comercial da Fase 6. Validado em 15/07/2026: TypeScript sem erros, destinos `200` e aprovação visual do usuário | `frontend/web/src/components/painel/AdminShell.tsx`, `frontend/web/src/app/painel/visao-geral/page.tsx` |
| `[x]` | `868kb4ga6` | **Atualização automática (polling)** — Visão geral e lista de Chamados refazem o fetch sozinhas a cada ~20s (estilo painel de BI), pausando quando a aba está em segundo plano; hook reutilizável, sem nova dependência (SWR/React Query ficam de fora por ora) | Hook `useAtualizacaoPeriodica` (setInterval de 20s + Page Visibility API); as duas páginas só reexibem "Carregando..."/erro na carga inicial — atualizações de fundo trocam os dados em silêncio e mantêm a última leitura boa se uma falhar. Validado com Playwright: criei um chamado via API enquanto a página estava aberta e sem dar reload — KPI "Chamados abertos" foi de 10→11 e o total da lista de 14→15, ambos sozinhos | `frontend/web/src/lib/useAtualizacaoPeriodica.ts` (novo), `frontend/web/src/app/painel/visao-geral/page.tsx`, `frontend/web/src/app/painel/chamados/page.tsx` |

### Frontend Web — manutenção operacional do Gestor (categorias e equipe) 🆕

> Ver origem/decisões na seção "Backend — manutenção operacional do Gestor" acima.

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868kcw5xj` | Página `/painel/categorias` — listar categorias da Empresa, criar, editar nome e ativar/desativar. Validado em 15/07/2026: TypeScript sem erros; Playwright cobriu criar/editar nome/ativar/desativar sem erro de console; aprovação visual do usuário | `frontend/web/src/app/painel/categorias/page.tsx` (novo), `categorias.module.css` (novo), `frontend/web/src/lib/api.ts`, `frontend/web/src/types/index.ts` |
| `[x]` | `868kcw5z1` | Página `/painel/equipe` — lista a equipe da Empresa, cria (reaproveita `POST /usuarios/equipe`), edita dados cadastrais e ativa/desativa (inclui adicionar/remover Supervisor); tela separada do dashboard de métricas em `/painel/supervisores` (que continua só leitura). Validado em 15/07/2026: TypeScript/lint sem novidade, Playwright cobriu contratar/editar/ativar-desativar e confirmou a trava de autodesativação do Gestor (mensagem inline), sem erro de console além do 400 esperado; aprovação visual do usuário | `frontend/web/src/app/painel/equipe/page.tsx` (novo), `equipe.module.css` (novo), `frontend/web/src/lib/api.ts`, `frontend/web/src/types/index.ts` |
| `[x]` | `868kcw619` | Adicionar links no sidebar: Categorias e Equipe (reorganizados a pedido do usuário num submenu recolhível "Ajustes"). Validado em 15/07/2026: TypeScript sem erros, Playwright confirmou navegação e destaque `aria-current`, sem erro de console; aprovação visual do usuário | `frontend/web/src/components/painel/AdminShell.tsx` |

---

## Fase 4.1 — Desempenho e escala para produção · CU: `868kcuvv8`

> **Momento de execução:** concluir primeiro a validação visual da Fase 4. Este pacote não bloqueia o
> MVP com o volume atual (12 chamados, 34 mensagens e 7 usuários), mas deve ser concluído e validado
> antes de escalar o ambiente de produção. Preservar em todas as otimizações o isolamento por
> `EmpresaID` e a proteção RLS já estabelecida.

| Status | CU | Item | Critério de aceite / Arquivo(s) provável(is) |
|--------|----|------|----------------------------------------------|
| `[ ]` | `868kcuw15` | **Índices para consultas multi-tenant e relacionamentos** — levantar os planos reais com `EXPLAIN (ANALYZE, BUFFERS)` e criar índices compostos iniciando por `EmpresaID`, combinados conforme os filtros/ordenações de chamados (`SupervisorID`, `Status`, `Atualizacao`, `PrazoSLA`) e mensagens (`ChamadoID`, `Criacao`/ordenação). Não criar índices isolados por suposição; validar custo de escrita e evitar redundâncias | Migração versionada, RLS preservada e planos comparativos registrados para consultas representativas do painel, listagem e thread de mensagens · `backend/alembic/**` ou mecanismo de migração adotado, modelos e documentação técnica |
| `[ ]` | `868kcuw1q` | **Paginação da listagem de chamados** — substituir o retorno integral por paginação estável, com limite máximo e ordenação determinística; manter filtros por tenant, supervisor, status, período, categoria e busca | Contrato retorna itens + metadados/cursor, não repete nem omite registros entre páginas em ordem estável, limita volume por requisição e mantém compatibilidade coordenada entre backend e web/mobile · `backend/app/rotas/Chamados.py`, schemas, clientes e tipos frontend |
| `[ ]` | `868kcuw24` | **Endpoint agregado do dashboard** — consolidar numa única leitura do frontend os dados necessários à visão geral e reutilizar agregações/CTEs quando relatórios percorrem as mesmas tabelas, sem mover cálculo registro a registro para Python | A atualização principal do dashboard usa 1 chamada, preserva os valores atuais e o escopo por Empresa/RLS; comparar SQL e tempo de resposta antes/depois · `backend/app/rotas/Relatorios.py`, `frontend/web/src/lib/api.ts`, `frontend/web/src/app/painel/visao-geral/page.tsx` |
| `[ ]` | `868kcuw2p` | **Polling eficiente e proteção contra atualizações simultâneas** — impedir uma nova atualização enquanto a anterior estiver em andamento, cancelar requisições obsoletas ao desmontar/trocar de contexto e evitar baixar toda a listagem apenas para atualizar indicadores | Nunca há duas atualizações equivalentes simultâneas por tela; polling segue suspenso em aba oculta, preserva a última leitura boa em falhas e não refaz a listagem completa quando só os KPIs precisam mudar · `frontend/web/src/lib/useAtualizacaoPeriodica.ts`, páginas do painel e cliente de API |
| `[ ]` | `868kcuw3b` | **Validação de escala antes da produção** — criar massa sintética multi-tenant e medir as rotas críticas com volume representativo, incluindo concorrência controlada | Cenário reproduzível com milhares de chamados/mensagens, sem dados reais; registrar p50/p95, taxa de erros, consultas lentas e evidência de isolamento entre tenants; definir orçamento de desempenho e impedir regressão relevante antes do go-live · scripts/testes de carga, `docs/deploy-producao.md`, documentação técnica |

---

## Fase 4.5 — Catálogo de Serviços e Parceiros 🆕 [discovery: Governança de IA] · CU: `868k7vr0g`

> **Origem:** documento de Governança de IA em `docs/FaciliChat-Regras/`. O **catálogo é a fonte da
> verdade comercial** de cada Empresa e o **portão obrigatório** que a IA consulta antes de sinalizar
> qualquer oportunidade (Fase 5). **Regra de modelagem:** serviços e parceiros são **dados por Empresa
> (linhas de tabela)**, nunca nomes fixos. **Não há campo de preço** — preço é decisão humana do Gestor.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vr66` | Modelo `Parceiro` (executor terceirizado): `EmpresaID`, `Nome`, `Contato` (opcional) | `backend/app/modelos/Parceiro.py` (novo) |
| `[ ]` | `868k7vr6h` | Modelo `CatalogoServico`: `EmpresaID`, `Nome`, `Tipo` (Proprio/Parceria), `ParceiroID` (opcional), `Oferece` (bool). **Sem preço** | `backend/app/modelos/CatalogoServico.py` (novo) |
| `[ ]` | `868k7vr6z` | CRUD do catálogo e de parceiros — escopado à Empresa; edição só do **Gestor** (e Superadmin no onboarding) | `backend/app/rotas/Catalogo.py` (novo) |

### Frontend Web (Gestor)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vr7n` | Tela "Catálogo de serviços" — listar/adicionar/editar/ativar-desativar serviço | `frontend/web/src/app/painel/catalogo/page.tsx` (novo) |
| `[ ]` | `868k7vr7y` | Tela "Parceiros" — listar/adicionar/editar parceiros | `frontend/web/src/app/painel/parceiros/page.tsx` (novo) |
| `[ ]` | `868k7vr8d` | Tipos TS `CatalogoServico`/`Parceiro` sincronizados com o backend | `frontend/web/src/types/index.ts` |

---

## Fase 5 — IA (classificação, roteamento e narração) · CU: `868k60w34`

> IA usa o SDK Anthropic já instalado. Nunca inventa prazos. Só narra campos estruturados.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60w36` | Serviço `ia_classificar(texto)` — retorna `Fila`, `Categoria`, `Prioridade` | `backend/app/servicos/ia.py` (novo) |
| `[ ]` | `868k60w38` | Ao criar chamado (`POST /chamados/`): chamar `ia_classificar` e preencher campos | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k60w3e` | Serviço de narração segura para **todas** as transições (Recebido/Em andamento/Agendado/Aguardando confirmação/Concluído/Cancelado/Reaberto), consumindo evento estruturado. IA não decide aprovação, prazos configurados ou SLA, não inventa motivo/promessa, não expõe nota interna nem fala pelo Supervisor; Cancelado nunca é serviço realizado; fallback obrigatório | `backend/app/servicos/ia.py`, histórico F01/F08-07 |
| `[ ]` | `868k60w3h` | Após commit da transição, criar exatamente uma mensagem automática ligada ao evento e disponibilizar saída para canais; retry/concor­rência não duplica; falha de IA/WhatsApp não desfaz status | `backend/app/rotas/Chamados.py`, serviços de histórico/outbox |
| `[ ]` | `868k7vrxw` | **Roteamento por intenção → fila correta**, incluindo **tickets irmãos** (um aviso → N chamados) usando o vínculo de grupo da Fase 0.6 | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | `868k60w3m` | Serviço `ia_detectar_oportunidade(mensagem)` — detecta intenção de serviço extra | `backend/app/servicos/ia.py` |
| `[ ]` | `868kahvau` | **Reforço do invariante da Fase 0.6:** IA detecta intenção de compra, mas **nunca inventa preço/prazo**; só sinaliza oportunidade ancorada em dados reais | `backend/app/servicos/ia.py` |
| `[ ]` | `868k7vryf` | **Portão do catálogo (obrigatório):** ao detectar intenção, consultar o `CatalogoServico` da Empresa. No catálogo → registra oportunidade; **fora → silêncio comercial** (só observação operacional) | `backend/app/servicos/ia.py` |
| `[ ]` | `868k7vryy` | Modelo `Oportunidade` (entidade própria): `EmpresaID`, `ChamadoID`, `ServicoID`, `Status` (Nova/Vista/PropostaConstruida/Rejeitada), `Criacao`. A IA **nunca cita preço** | `backend/app/modelos/Oportunidade.py` (novo) |

---

## Fase 5.5 — Governança e guardrails da IA 🆕 [discovery: Governança de IA] · CU: `868k7vr1c`

> **Origem:** documento de Governança de IA em `docs/FaciliChat-Regras/`. Formaliza **o que a IA pode e
> não pode fazer** como **camada verificável** (guardrails + validação de resposta + auditoria).
> Princípio fundador: **"geração ancorada"** — a IA só fala o que um humano cadastrou.

### Backend — guardrails e validação

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vraj` | **Matriz de permissões por perfil** (7 perfis × pode/não-pode) traduzida em guardrails aplicados **antes** de gerar cada resposta | `backend/app/servicos/ia_governanca.py` (novo) |
| `[ ]` | `868k7vray` | **Validação pós-geração** de toda resposta: não contém preço? só cita serviço do catálogo? não promete prazo não registrado? não responde regra de RH/Financeiro não cadastrada? não fala em nome de humano? | `backend/app/servicos/ia_governanca.py` |
| `[ ]` | `868k7vrbc` | **Log de auditoria de decisões da IA** — intenção detectada, consulta ao catálogo/base e ação tomada | `backend/app/modelos/IaAuditoria.py` (novo) |
| `[ ]` | `868k7vrbh` | Reforçar isolamento multi-tenant na IA — toda consulta filtrada por `EmpresaID` (nunca cruza Empresas) | `backend/app/servicos/ia*.py` |

### Backend — base de regras (RH / Financeiro)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vrc1` | Modelo `BaseRegra`: `EmpresaID`, `Area` (RH/Financeiro), `Chave`/`Pergunta`, `Resposta` — conhecimento **cadastrado por Empresa** | `backend/app/modelos/BaseRegra.py` (novo) |
| `[ ]` | `868k7vrcg` | IA **responde dúvida recorrente** só a partir da `BaseRegra`; **regra ausente → encaminha** para fila humana | `backend/app/servicos/ia.py` |
| `[ ]` | `868k7vrcn` | CRUD da base de regras — RH edita a sua, Financeiro a sua (escopado por Empresa e área) | `backend/app/rotas/Regras.py` (novo) |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vrd0` | Tela de "Base de regras" (RH e Financeiro) — cadastrar/editar perguntas e respostas recorrentes | `frontend/web/src/app/painel/regras/page.tsx` (novo) |

---

## Fase 6 — Alertas comerciais e propostas · CU: `868k60w41`

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60w47` | Modelo `Proposta`: `ChamadoID`, `OportunidadeID` (Fase 5), Titulo, Escopo, Prazo, Valor, Status (Rascunho/Enviada/Aprovada/Recusada). **`Valor` preenchido pelo Gestor** — a IA nunca o gera | `backend/app/modelos/Proposta.py` (novo) |
| `[ ]` | `868k60w4a` | `GET /propostas/alertas` — lista as `Oportunidade`s (Status=Nova) aguardando decisão/proposta | `backend/app/rotas/Propostas.py` (novo) |
| `[ ]` | `868k60w4e` | `POST /propostas/` — criar e enviar proposta no chat do cliente | `backend/app/rotas/Propostas.py` |
| `[ ]` | `868k60w4g` | `PATCH /propostas/{id}/status` — cliente aprova ou recusa | `backend/app/rotas/Propostas.py` |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60w4n` | Página `alertas` — cards de oportunidades; botão "Montar proposta" abre formulário | `frontend/web/src/app/(painel)/alertas/page.tsx` (novo) |
| `[ ]` | `868k60w4u` | Formulário de proposta: Título, Escopo, Prazo médio, Início previsto, Valor (R$), preview do cliente | (dentro de alertas ou modal) |

### Frontend Mobile (Cliente)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60w4x` | Componente de proposta no chat — card com título, escopo, prazo, valor, botões Aprovar/Recusar | `frontend/mobile/components/CardProposta.tsx` (novo) |

---

## Fase 7 — Gestão de Empresas e Condomínios (telas/CRUD) · CU: `868k60wgx`

> **Depende da Fase 0.7 (Fundação SaaS Multi-Tenant)**, que já cria a entidade `Empresa`, o `EmpresaID`
> em todas as tabelas, o escopo por tenant, a RLS e o tenant no JWT.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wh3` | Modelo `Condominio`: `Nome`, `Endereco`, `CNPJ`, **`EmpresaID`** | `backend/app/modelos/Condominio.py` (novo) |
| `[ ]` | `868k60wh7` | CRUD de condomínios — escopado à Empresa do Gestor | `backend/app/rotas/Condominios.py` (novo) |
| `[ ]` | `868k60whc` | CRUD de Empresas — somente Superadmin da plataforma | `backend/app/rotas/Plataforma.py` |
| `[ ]` | `868kd2e3h` | F07-SP1 — **Supervisor padrão por Condomínio** (`SupervisorPadraoID`) + atribuição automática em chamado individual/tickets irmãos. Supervisor ativo e do mesmo tenant; mudar padrão só afeta futuros; sem padrão válido o chamado nasce sem responsável e alerta o Gestor, nunca é perdido | `backend/app/modelos/Condominio.py`, `rotas/Condominios.py`, `rotas/Chamados.py`, RLS/histórico |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60whj` | Página `cadastros` — usuários e condomínios da empresa (só Gestor) | `frontend/web/src/app/painel/cadastros/page.tsx` (novo) |
| `[ ]` | `868k60whn` | Área de plataforma — gerenciar Empresas (Superadmin) | `frontend/web/src/app/(plataforma)/...` (novo) |
| `[ ]` | `868kd2e3w` | F07-SP2 — Configurar Supervisor padrão no cadastro do Condomínio; lista só ativos do tenant; explica que a mudança vale para novos chamados e direciona à reatribuição explícita dos abertos (`F08-07J`) | página/cliente API/tipos do cadastro de Condomínios |

---

## Fase 8 — MVP 02: Visitas Técnicas · CU: `868k60whw`

> Entidade separada do Chamado. Proativa (supervisor → cliente), não reativa.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wj5` | Modelo `VisitaTecnica`: SupervisorID, CondominioID, EmpresaID, DataHoraAgendada, HoraChegada, HoraSaida, Notas, Status, `ticket_id` opcional. **Duração deriva** de HoraSaida−HoraChegada | `backend/app/modelos/VisitaTecnica.py` (novo) |
| `[ ]` | `868kahvb2` | **Refino herdado da Fase 0.6:** `Duracao` **não é coluna** — derivar de `HoraSaida − HoraChegada` | `backend/app/modelos/VisitaTecnica.py` |
| `[ ]` | `868kahvbe` | **Refino herdado da Fase 0.6:** adicionar `ticket_id` **opcional** (vínculo a uma reclamação) | `backend/app/modelos/VisitaTecnica.py` |
| `[ ]` | `868k60wjj` | `POST /visitas/` — agendar visita | `backend/app/rotas/Visitas.py` (novo) |
| `[ ]` | `868k60wjq` | `PATCH /visitas/{id}/iniciar` — grava `HoraChegada` = agora | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wjv` | `PATCH /visitas/{id}/finalizar` — grava `HoraSaida`, muda status para Finalizada | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wk2` | Ao finalizar: IA narra relatório e posta `Mensagem` no chat do condomínio (AutorTipo = IA) | `backend/app/rotas/Visitas.py` + `servicos/ia.py` |
| `[ ]` | `868k60wk9` | Upload de fotos da visita | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wkf` | `GET /visitas/?condominio_id=` — histórico para o cliente | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wkn` | `GET /visitas/?supervisor_id=me` — agenda do supervisor | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868kahvbk` | **Refino herdado da Fase 0.6:** cliente **não aprova** a visita; só recebe/consulta as evidências e o relatório | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wkq` | IA detecta acordo de visita no chat e cria visita agendada automaticamente | `backend/app/servicos/ia.py` |

### Frontend Mobile (Supervisor)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wkv` | Tela "Visita em andamento" — cronômetro (HH:MM:SS), texto livre, galeria de fotos, botão "Finalizar visita" | `frontend/mobile/app/(supervisor)/visita/[id].tsx` (novo) |
| `[ ]` | `868k60wm6` | Tela "Agendar visita" — picker de condomínio, data/hora | `frontend/mobile/app/(supervisor)/visita/nova.tsx` (novo) |
| `[ ]` | `868k60wmf` | Visitas aparecem na tela "Hoje" do supervisor | `frontend/mobile/app/(supervisor)/hoje.tsx` |

### Frontend Mobile (Cliente)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wmm` | Aba "Visitas" no app do cliente — data, horário, duração, supervisor, observações, fotos | `frontend/mobile/app/(tabs)/visitas.tsx` (novo) |

### Frontend Web (Gestor)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wmu` | Página `visitas` no painel — tabela: cliente, supervisor, data, duração, status; filtro; badge "Não realizada" | `frontend/web/src/app/(painel)/visitas/page.tsx` (novo) |
| `[ ]` | `868k60wn0` | Adicionar "Visitas técnicas" no sidebar (Gestor e Supervisor) | `frontend/web/src/app/painel/layout.tsx` |

---

## Fase 9 — Upload de arquivos · CU: `868k60wn5`

> **Auditoria obrigatória antes de implementar:** confrontar novamente branding, código e contratos
> da F01-J. O escopo antigo de “foto” é insuficiente: revisar Áudio, Imagem, Vídeo e Documento/PDF,
> MIME real, limites, compressão, duração/miniatura, URLs temporárias, tenant, arquivo malicioso,
> retenção/exclusão, upload interrompido/idempotente, mídia efêmera do WhatsApp e celulares/dados
> limitados. Não mostrar controle antes do fluxo completo funcionar. Testes aguardam disparo do usuário.

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wnd` | Configurar storage (S3 ou MinIO local via Docker) | `backend/app/servicos/storage.py` (novo), `docker-compose.yml` |
| `[ ]` | `868k60wng` | Rota `POST /uploads/` — retorna URL do arquivo | `backend/app/rotas/Uploads.py` (novo) |
| `[ ]` | `868k60wnh` | Implementar mídia do chat conforme revisão F01-J: tipos aprovados, referência autorizada, metadados, download/stream e segurança por tenant | `backend/app/modelos/Mensagens.py`, rotas/serviços |
| `[ ]` | `868k60wnr` | Componentes web para upload/exibição dos tipos aprovados, com progresso, retry e acessibilidade | `frontend/web/src/components/` |
| `[ ]` | `868k60wnx` | Captura/seleção/exibição mobile dos tipos aprovados, considerando dados limitados e interrupção | `frontend/mobile/` |

---

## Fase 10 — Notificações push · CU: `868k60wpb`

> Push também entrega os lembretes da F01-E: primeiro/segundo ao Cliente e escalonamento ao
> Supervisor responsável/Gestor. Usa prazos já calculados no snapshot, nunca conclui por silêncio,
> não recalcula SLA e falha externa não altera o chamado. Evitar conteúdo sensível excessivo na
> tela bloqueada; deep link sempre revalida sessão/permissão. Testes aguardam disparo do usuário.

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wpt` | Integrar Expo Push Notifications no mobile | `frontend/mobile/lib/notificacoes.ts` (novo) |
| `[ ]` | `868k60wpx` | Backend envia push idempotente ao destinatário offline e nos lembretes/escalonamento F01-E | `backend/app/servicos/notificacoes.py` (novo) |
| `[ ]` | `868k60wq2` | Configurar tokens de dispositivo por usuário no banco | `backend/app/modelos/Usuarios.py` |

---

## Fase 11 — Experiência do Funcionário (canal único) 🆕 [discovery: Jornada do Funcionário] · CU: `868k7vr1k`

> **Origem:** jornada do Funcionário em `docs/FaciliChat-Regras/`. App **radicalmente simples** (celular
> simples, dados limitados, preferência por voz/foto): "se for mais difícil que o WhatsApp, ele não usa".
> **Reaproveita:** roteamento por intenção e tickets irmãos (Fase 5), voz/foto no chat (Fases 1 e 9),
> base de regras (Fase 5.5). **Funcionário é perfil único** (sem subtipos) — invariante do `CLAUDE.md`.

### Frontend Mobile (Funcionário)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vre5` | Canal único de comunicação com entrada mínima — um só campo que aceita **texto, voz e foto**; zero formulário obrigatório | `frontend/mobile/app/(funcionario)/**` (novo) |
| `[ ]` | `868k7vreg` | Confirmação "Recebido" visível imediatamente após enviar (reaproveita a Fase 1) | (dentro do canal) |
| `[ ]` | `868k7vren` | Navegação por abas do funcionário (roteamento dinâmico por `Funcao`, como o supervisor na Fase 3) | `frontend/mobile/app/(funcionario)/_layout.tsx` (novo) |

### Fluxos de aviso do Funcionário (backend + IA)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k7vrew` | **Atestado/falta → tickets irmãos** (RH valida + Supervisor cobre o posto) a partir de um único aviso | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | `868k7vrfc` | **Sensor de campo** — observação vira `Oportunidade` **via portão do catálogo** (Fase 5), sem transformar o funcionário em vendedor e sem preço | `backend/app/servicos/ia.py` |
| `[ ]` | `868k7vrfv` | **Reposição de insumo** — aviso simples vira chamado rastreável; detalhes estruturados nos bastidores (Integração ERP adiada) | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | `868k7vrg7` | **Dúvida pessoal** (holerite, vale) — roteada à fila individual correta; resposta automática pela `BaseRegra` (Fase 5.5) quando cadastrada | `backend/app/servicos/ia.py` |

> **Nota de modelagem:** os "tipos de aviso" acima são **classificações de intenção detectadas pela IA
> e/ou um campo `Tipo`/`Categoria` no chamado**, não telas/rotas fixas nem nomes hard-coded. A rota de
> origem é sempre o mesmo canal único.

---

## Fase 12 — Finalização do desenvolvimento e preparação para produção 🚀 · CU: `868kd1jc8`

> **Por que existe:** concentra controles indispensáveis ao go-live que causariam retrabalho durante
> o primeiro desenvolvimento. Não adiciona funcionalidades de negócio. Executar depois das fases
> funcionais, aproveitando a Fase 4.1 (escala), a Fase 0.8 e a regressão solicitada. Especificação:
> `docs/implementation/10-fase-12-finalizacao-producao.md`.

| Status | CU | ID | Item | Critério principal |
|--------|----|----|------|--------------------|
| `[ ]` | `868kd1k6v` | F12-01 | **Implantar Alembic e estabelecer migrações versionadas** | Baseline coerente; banco vazio e existente chegam ao `head`; RLS/grants entram nas revisões; produção deixa de depender de reset/`create_all`. |
| `[ ]` | `868kd1k7a` | F12-02 | **Validar atualização sem perda e papéis/RLS de produção** | Ensaio em cópia representativa, integridade preservada, papel da API sem bypass, backup e rollback/roll-forward comprovados. |
| `[ ]` | `868kd1k7e` | F12-03 | **Migrar estado efêmero para armazenamento compartilhado quando houver múltiplas réplicas** | Redis ou equivalente: rate limit sempre compartilhado; pubsub/salas/presença da Fase 1 compartilhados se a topologia tiver 2+ backends; TTL/atomicidade/falha documentados. |
| `[ ]` | `868kd1k7p` | F12-04 | **Fechar endurecimento de borda e configuração de produção** | TLS/DNS, cookies/origens reais, CSP aplicada, segredos, exposição e logs validados no ambiente candidato. |
| `[ ]` | `868kd1k7w` | F12-05 | **Implantar e ensaiar backup, restauração e recuperação** | RPO/RTO definidos; restauração real medida; integridade e RLS verificadas. |
| `[ ]` | `868kd1k82` | F12-06 | **Executar gate final de go-live e registrar decisão de publicação** | Evidências, riscos, responsáveis, implantação e rollback consolidados numa decisão explícita `go/no-go`, sem duplicar a Fase 4.1. |

### Fora do escopo da Fase 12

Novas funcionalidades de Empresa/Condomínio (Fase 7), privacidade sensível/RH por tópico (Adiados),
otimizações já atribuídas à Fase 4.1 e qualquer decisão de produto não aprovada.

---

## Adiados (pós-MVP) — registrados para não se perder · CU: `868k7vr1q`

> Decisões conscientes de **não fazer agora**, tiradas do material de discovery. **Não** entram no MVP.

| Status | CU | Item | Origem |
|--------|----|------|--------|
| `[ ]` | `868k7vrgk` | **Isolamento de privacidade por tópico** — restringir conteúdo sensível (atestado, folha, salário) por área/papel; hoje Supervisor/Gestor veem tudo | Jornadas Funcionário/Dono + HMW |
| `[ ]` | `868k7vrgw` | **Integração com ERP** — reposição de insumo (Fase 11) pode baixar estoque / gerar cobrança automaticamente. Modelar pensando nisso, sem implementar | Jornada do Funcionário |

---

## Notas de arquitetura para consulta rápida

```
Design tokens principais:
  Azul primário:  #148AF5   (hover: #0E72D4,  fundo: #EAF4FE)
  Ink (texto):    #17171A / #34363D / #646874
  Fundos:         #F7F9FA (página) / #FFFFFF (card)
  Bordas:         #E7ECEF / #C1CCD3
  Sucesso:        #1FAE68  bg #E7F6EE
  Atenção:        #F0961E  bg #FEF4E6
  Erro/Crítico:   #E5484D  bg #FDECEC
  Raios:          8px card, 12px modal, 999px badge/pílula
  Fonte:          Figtree (sans-serif geométrica)
  Ícones:         Line Awesome  (18–24px, estilo linha)

Multi-tenant (SaaS): Empresa (tenant) → Condomínios → Usuários/Chamados
                     Toda tabela tem EmpresaID; toda query filtra por ele; RLS no Postgres.
                     O tenant viaja no JWT. Papéis são por empresa (não globais).
Superadmin:          Nível da plataforma (Iugo Performance) — cadastra/suspende Empresas.
Perfis de usuário:    Cliente | Funcionário | Supervisor | RH | Financeiro | Gestor | Superadmin
Filas de chamado:     Operacional | RH | Financeiro | Comercial
Status de chamado:    Recebido | EmAndamento | Agendado | Concluido | Cancelado
Prioridades:          Baixa | Media | Alta | Critica
Status de visita:     Agendada | EmAndamento | Finalizada | RelatorioEnviado
AutorTipo mensagem:   Cliente | Supervisor | Funcionario | IA | Sistema
Tipo de mensagem:     Texto | Audio | Imagem  (voz/foto valem igual a texto — Fases 1/9)

Entidades novas (discovery, ainda não implementadas):
  CatalogoServico:   por Empresa — Nome, Tipo(Proprio/Parceria), ParceiroID, Oferece  (SEM preço)  [Fase 4.5]
  Parceiro:          por Empresa — Nome, Contato                                                    [Fase 4.5]
  Oportunidade:      por Empresa — ChamadoID, ServicoID, Status(Nova/Vista/PropostaConstruida/...)  [Fase 5]
  BaseRegra:         por Empresa — Area(RH/Financeiro), Chave, Resposta                             [Fase 5.5]
  IaAuditoria:       log de decisões da IA (intenção, consulta, ação)                               [Fase 5.5]
  Proposta:          ChamadoID, OportunidadeID, ... , Valor (preenchido pelo Gestor)                [Fase 6]

Regra da IA (geração ancorada — só fala o que um humano cadastrou):
  - Nunca inventa preço nem prazo; só narra campos estruturados (status, datas, responsável).
  - Nunca oferece serviço fora do catálogo da Empresa (portão obrigatório).
  - Nunca responde regra de RH/Financeiro não cadastrada (encaminha em vez de inventar).
  - Nunca fala em nome de um humano; nunca cruza dados entre Empresas.

Nomes de personas/serviços/parceiros dos docs de discovery são EXEMPLOS — viram DADOS no banco,
nunca nome fixo/enum/constante no código.

ClickUp board: Operações Internas › FaciliChat - Desenvolvimento › Roadmap de Implementação
               list_id 901114027434. Cada item carrega seu CU: (subtarefa); a fase carrega o CU: da pai.
               Fechar/mover tarefa = mover o CU: para o status equivalente via MCP do ClickUp.
```

---

*Mantido por: Claude Code — atualizar a cada sessão de desenvolvimento (arquivo + ClickUp).*
