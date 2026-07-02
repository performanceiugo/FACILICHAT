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

## Regras obrigatórias para toda implementação

1. **Todo bloco de código deve ter comentário.** Sem exceção. Funções, classes, rotas, hooks, estados, constantes de mapeamento — todos com comentário explicando o propósito.
2. **Consultar este arquivo antes de implementar qualquer coisa.** Verificar se o item já está marcado `[x]` ou `[~]`.
3. **Atualizar este arquivo ao concluir cada item.** Mudar `[ ]` para `[~]` ao iniciar, e para `[x]` ao concluir.
4. **Atualizar `docs/changelog.md`** com cada entrega.
5. **Manter tipos TypeScript sincronizados** com os modelos Python após toda alteração de schema.

---

## 🗺️ Mapa das fases (visão rápida)

| Fase | Tema | Status |
|------|------|--------|
| 0 | Infraestrutura e base | ✅ Concluída |
| 0.5 | Correções do levantamento (bugs e melhorias) | 🟡 Críticos concluídos; altos/médios/baixos/docs na fila |
| 0.6 | Alinhamento de domínio com o branding | ⬜ Na fila · **PRIORITÁRIO** |
| 0.7 | Fundação SaaS Multi-Tenant | ⬜ Na fila · **PRIORITÁRIO** |
| 1 | Chat (base do produto) | ⬜ Na fila |
| 2 | Criar chamado e detalhe (cliente) | ⬜ Na fila |
| 3 | Fila e operação do supervisor (mobile) | ⬜ Na fila |
| 4 | Dashboard do gestor (web) | ⬜ Na fila |
| 4.5 | Catálogo de Serviços e Parceiros | ⬜ Na fila · **NOVA (discovery)** |
| 5 | IA (classificação, roteamento e narração) | ⬜ Na fila |
| 5.5 | Governança e guardrails da IA | ⬜ Na fila · **NOVA (discovery)** |
| 6 | Alertas comerciais e propostas | ⬜ Na fila |
| 7 | Gestão de Empresas e Condomínios (telas/CRUD) | ⬜ Na fila |
| 8 | MVP 02: Visitas Técnicas | ⬜ Na fila |
| 9 | Upload de arquivos | ⬜ Na fila |
| 10 | Notificações push | ⬜ Na fila |
| 11 | Experiência do Funcionário (canal único, voz/foto, sensor de campo) | ⬜ Na fila · **NOVA (discovery)** |
| — | Adiados (pós-MVP): privacidade por tópico, integração ERP | ⬜ Registrado |

> **Ordem recomendada de desenvolvimento:** **0.6 → 0.7 → 1–4 → 4.5 → 5 → 5.5 → 6 → 7 → 8–11**,
> encaixando as correções pendentes da Fase 0.5 conforme a área que for tocada. As Fases 0.6 e 0.7 são
> fundação e vêm antes das features. As Fases 4.5, 5.5 e 11 saíram do material de discovery (jornadas +
> How Might We + Governança de IA em `docs/FaciliChat-Regras/`) revisado em 02/07/2026. O detalhe de
> cada fase está na Parte 2.

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

## Fase 0 — Infraestrutura e base

| Status | Item |
|--------|------|
| `[x]` | Auth JWT (login, token, middleware `obterUsuarioAtual`) |
| `[x]` | Modelo `Usuario` com enum `UsuarioFuncao` (Cliente/Supervisor/Funcionario/Gerente) |
| `[x]` | Modelo `Chamado` com enums de Fila, Status e Prioridade |
| `[x]` | Modelo `Mensagem` com `AutorTipo` (Humano/IA/Sistema) |
| `[x]` | Rotas: POST `/usuarios/`, GET `/usuarios/eu` |
| `[x]` | Rotas: POST `/chamados/`, GET `/chamados/`, PATCH `/chamados/{id}/status` |
| `[x]` | Conexão assíncrona PostgreSQL via SQLAlchemy + asyncpg |
| `[x]` | Docker Compose com PostgreSQL 16 |
| `[x]` | Frontend web: tela de login |
| `[x]` | Frontend web: painel com lista de chamados (cards por status/prioridade) |
| `[x]` | Frontend mobile: tela de login |
| `[x]` | Frontend mobile: lista de chamados com pull-to-refresh |
| `[x]` | Frontend mobile: tela de perfil com logout |
| `[x]` | Comentários em todos os 27 arquivos existentes |
| `[x]` | Documentação: `visao-geral.md`, `arquitetura.md`, `tecnico-backend.md`, `tecnico-frontend.md`, `setup.md`, `changelog.md` |

## Fase 0.5 — Correções já aplicadas (do levantamento de 27/06/2026)

> Itens do levantamento técnico que já foram corrigidos. Os pendentes do mesmo levantamento estão na Parte 2.

| Status | ID | Problema | O que foi feito | Arquivo(s) |
|--------|----|----------|-----------------|-----------|
| `[x]` | C1 | Imports não batem com os nomes dos arquivos (`from BancoDados` vs `banco_dados.py`, `Modelos`, `Rotas`, `Configuracoes`) → `ModuleNotFoundError` | Padronizado: todos os imports qualificados pelo pacote (`from app.banco_dados import ...`) em 9 arquivos | `backend/app/main.py`, `banco_dados.py`, `modelos/*.py`, `rotas/*.py` |
| `[x]` | C2 | Não é um pacote Python — falta `__init__.py`; `uvicorn app.main:app` falha | Criado `backend/app/__init__.py` (marcador de pacote) — habilita os imports qualificados do C1 | `backend/app/__init__.py` (novo) |
| `[x]` | C3 | Rotas `/painel/*` retornam 404 (route group `(painel)` não entra na URL) | Route group `(painel)` renomeado para pasta real `painel/` (via `git mv`) — as URLs `/painel/...` que o código já usava passaram a existir; zero mudança de navegação | `frontend/web/src/app/painel/**` |
| `[x]` | C4 | `auth.ts` acessa `localStorage` sem guarda de `window` → quebra no SSR / hydration mismatch | Adicionada guarda `typeof window !== 'undefined'` em todos os métodos; `painel/layout.tsx` agora lê a sessão via estado em `useEffect` e só renderiza após validar (remove flash — melhora parcial do A4) | `frontend/web/src/lib/auth.ts`, `frontend/web/src/app/painel/layout.tsx` |
| `[x]` | C5 | `app.json` referencia assets inexistentes (`icon.png`, `splash.png`, `adaptive-icon.png`) → build falha | Gerados placeholders branded (1024×1024, "F" branco na cor #148AF5) em `assets/`; `backgroundColor` do splash/adaptiveIcon corrigida `#1a56db`→`#148AF5`. Arte real pode substituir depois | `frontend/mobile/assets/*.png` (novos), `frontend/mobile/app.json` |
| `[x]` | C6 | Escalonamento de privilégio: `POST /usuarios/` é público e aceita `Funcao` do corpo → qualquer um vira Gerente | Cadastro público agora força `Funcao = Cliente`; criação privilegiada movida para `POST /usuarios/equipe` (só Gerente). Bootstrap do 1º Gerente via `backend/scripts/criar_gerente.py` | `backend/app/rotas/Usuarios.py`, `backend/scripts/criar_gerente.py` (novo) |
| `[x]` | C7 | `PATCH /chamados/{id}/status` sem autorização nem checagem de posse (IDOR) | Restrito a Supervisor/Gerente (403 caso contrário); chamado em estado terminal (Concluído/Cancelado) não pode ser reaberto (409) | `backend/app/rotas/Chamados.py` |
| `[x]` | A2 | CORS não configurado → frontends no navegador não chamam a API | Adicionado `CORSMiddleware` com origens explícitas vindas de `CORS_ORIGINS` (config/.env); sem `"*"` junto de credenciais | `backend/app/main.py`, `configuracoes.py` |
| `[x]` | A9 | Web: `next@15.3.4` afetado pela CVE-2025-66478 (RCE crítico no RSC, CVSS 10.0) — descoberto no `npm install` | Atualizado `next` e `eslint-config-next` para `15.3.6` (patch da linha 15.3.x); dev server reiniciado e validado | `frontend/web/package.json` |
| `[x]` | D3 | Texto espúrio "oi" e "atualização em tempo real" enganoso | Removido "oi" e a data 2025→2026; texto ajustado para "pull-to-refresh" | `docs/visao-geral.md` |

---
---

# PARTE 2 — 🚧 Em desenvolvimento (na ordem recomendada)

## Fase 0.5 — Correções pendentes (do levantamento de 27/06/2026)

> **Como conduzir:** corrigir **um item por vez**. Ao iniciar, mudar `[ ]` → `[~]`; ao concluir, `[~]` → `[x]`
> (mover a linha para a Parte 1) e registrar no `changelog.md`. Cada ID (ex.: `A1`) serve de referência na conversa.
> Os críticos (C1–C7) já estão concluídos (Parte 1).

### 🟠 Altos

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | A1 | `obterUsuarioAtual` retorna 500 (não 401) em token malformado (`uuid.UUID()` fora do try/except) | Mover conversão para dentro do try e capturar `(JWTError, ValueError)` | `backend/app/rotas/Autenticacao.py` |
| `[ ]` | A3 | Web e mobile sem tratamento de 401/token expirado (usuário fica preso) | No cliente HTTP, ao receber 401 → `auth.sair()` + redirecionar para login | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[ ]` | A4 | Proteção de rota só client-side com flash de conteúdo (web) | Usar `middleware.ts` do Next; renderizar `null`/loader enquanto não autenticado | `frontend/web/src/middleware.ts` (novo), `(painel)/layout.tsx` |
| `[ ]` | A5 | Design system violado: cor primária `#1a56db` (deveria `#148AF5`) e fonte Geist (deveria Figtree) | Substituir tokens de cor e trocar fonte para Figtree (web e mobile) | `frontend/web/src/app/layout.tsx`, `globals.css`; `frontend/mobile/app/**` |
| `[ ]` | A6 | API de mensagens (`api.mensagens.*`) aponta para rota inexistente no backend | Alinhar com a Fase 1 (criar rota) ou marcar como código futuro até existir | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[ ]` | A7 | Link `/usuarios` no sidebar sem página correspondente → 404 | Criar a página ou esconder o link até existir | `frontend/web/src/app/(painel)/layout.tsx` |
| `[ ]` | A8 | Mobile: React 18.3 / expo-router 4 incompatíveis com Expo SDK 53 | Rodar `npx expo install --fix`; alinhar React 19 / router 5; adicionar `react-dom`/`react-native-web` | `frontend/mobile/package.json` |

### 🟡 Médios

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | M1 | Falta validação Pydantic de tamanho/força (senha sem `min_length`; campos sem `max_length` → 500 em overflow) | Adicionar `Field(max_length=...)` alinhado às colunas e `min_length` na senha | `backend/app/rotas/Usuarios.py`, `Chamados.py` |
| `[ ]` | M2 | `IntegrityError` no cadastro não tratado (corrida TOCTOU no check de email) | Capturar `IntegrityError` e retornar 400, confiando na constraint `unique` | `backend/app/rotas/Usuarios.py` |
| `[x]` | M3 | Magic strings `"Gerente"/"Supervisor"` em vez do enum `UsuarioFuncao` | Comparar com `UsuarioFuncao.Gestor`/`.Supervisor` (corrigido junto da Fase 0.6, já usando o nome novo `Gestor`) | `backend/app/rotas/Chamados.py` |
| `[ ]` | M4 | `echo=True` fixo no engine (loga todo SQL em produção) | Tornar configurável via env (`echo=configuracoes.DEBUG`) | `backend/app/banco_dados.py` |
| `[ ]` | M5 | `Config` (Pydantic v1), `datetime.utcnow` deprecado e colunas `DateTime` naive | Migrar para `ConfigDict`; usar `datetime.now(timezone.utc)` + `DateTime(timezone=True)` | `backend/app/modelos/*.py`, `rotas/*.py`, `configuracoes.py` |
| `[ ]` | M6 | Web: rewrite/proxy em `next.config.ts` configurado mas nunca usado (depende de CORS aberto) | Escolher estratégia (usar `/api/...` via rewrite ou remover) e centralizar base URL | `frontend/web/next.config.ts`, `lib/api.ts` |
| `[ ]` | M7 | Web: `Record<string,string>` em vez dos enums; `err: any` em catch; `erro.detail` não tipado (quebra em 422) | Tipar com `Record<ChamadoStatus, ...>`; normalizar `detail` array/string; `err instanceof Error` | `frontend/web/src/app/(painel)/chamados/page.tsx`, `lib/api.ts` |
| `[ ]` | M8 | Web: `token()` duplicado entre `api.ts` e `auth.ts` (duas fontes de verdade) | `api.ts` importa e usa `auth.token()` | `frontend/web/src/lib/api.ts` |
| `[ ]` | M9 | Web: arquivos CSS sem nenhum comentário (viola regra do `CLAUDE.md`) | Adicionar cabeçalho e comentar blocos (especialmente `:root` de tokens) | `frontend/web/src/app/**/*.css` |
| `[ ]` | M10 | Mobile: `chamados.tsx`/`perfil.tsx` sem `catch` → erros engolidos silenciosamente | Adicionar `catch` com estado de erro e botão "Tentar novamente" | `frontend/mobile/app/(tabs)/chamados.tsx`, `perfil.tsx` |
| `[ ]` | M11 | Mobile: paleta de cinzas/feedback fora dos tokens; Figtree não carregada | Substituir pelos tokens Ink; carregar Figtree via `expo-font` | `frontend/mobile/app/**` |

### 🟢 Baixos

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | B1 | Raios de canto fora da escala (cards 10/12 em vez de 8; inputs 10) | Padronizar 8px em cards, conforme design system | web e mobile (CSS/estilos) |
| `[ ]` | B2 | `useEffect` de fetch sem cleanup/AbortController (web e mobile) | Adicionar `AbortController`/flag de montagem no cleanup | `chamados/page.tsx` (web), telas mobile |
| `[ ]` | B3 | Web: faltam `error.tsx` e `not-found.tsx` (sem fallback de erro) | Criar `app/error.tsx` e `app/not-found.tsx` | `frontend/web/src/app/` |
| `[ ]` | B4 | Mobile: tabs sem ícones (Line Awesome) | Adicionar `tabBarIcon` às abas | `frontend/mobile/app/(tabs)/_layout.tsx` |
| `[ ]` | B5 | A11y: foco de teclado removido (web); navegação sem `aria-label`/`aria-current`; estados sem `aria-live` | Usar `:focus-visible` com anel de foco; adicionar atributos ARIA | `frontend/web/src/app/**` |
| `[ ]` | B6 | Backend: JWT sem `iat/iss/aud`; hasher de senha duplicado; `@app.on_event` deprecado | Adicionar claims; centralizar hasher; migrar para `lifespan` | `backend/app/rotas/Autenticacao.py`, `Usuarios.py`, `main.py` |
| `[ ]` | B7 | Painel web (Next.js, pensado para desktop do Gestor) ainda não foi validado em navegador mobile (breakpoints, sidebar, tabelas largas) | Analisar no futuro o enquadramento responsivo do painel web em telas de navegador mobile e ajustar CSS/layout onde necessário | `frontend/web/src/app/painel/**` |

### 📄 Documentação (divergências com o código real)

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | D1 | Divergência de enums: doc cita `AutorTipo: Humano/IA/Sistema` mas código usa `Cliente/Supervisor/Funcionario/IA/Sistema` | Padronizar doc com o código (ou vice-versa, definir fonte de verdade) | `plano-implementacao.md`, `tecnico-backend.md` |
| `[ ]` | D2 | Datas inconsistentes no `changelog.md` (mistura 2025/2026) | Padronizar para o calendário correto | `docs/changelog.md` |
| `[ ]` | D4 | `tecnico-backend.md` documenta `uvicorn app.main:app` que falha pelos imports (resolver junto de C1/C2) | Atualizar comando de execução após corrigir imports | `docs/tecnico-backend.md` |

---

## Fase 0.6 — Alinhamento de domínio com o branding 📐 [PRIORITÁRIO]

> **Origem:** revisão dos documentos comerciais em `docs/FaciliChat-Regras/` (apresentação, personas,
> design system, MVP02) em 27/06/2026. O modelo de domínio do código divergia do produto definido pelo
> comercial. Estes itens alinham o domínio **antes** de construir as features. Termos canônicos do
> branding: a empresa cliente que compra é a **Empresa** (conservadora/facilities, ex.: "Cefram"); os
> clientes dela são **Condomínios** (representados por síndicos); a plataforma é operada pela Iugo
> Performance como **Superadmin**.

### Papéis de usuário — o branding define 7 perfis
Hoje o enum `UsuarioFuncao` tem 4 (Cliente, Supervisor, Funcionario, **Gerente**). O branding define 7:
**Cliente, Funcionário, Supervisor, RH, Financeiro, Gestor, Superadmin**.

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[x]` | Renomear `Gerente` → **`Gestor`** no enum e em todo o código (rotas, comparações, claim do JWT, frontend `isGerente`→`isGestor`, scripts) | `backend/app/modelos/Usuarios.py`, `rotas/*.py`, `frontend/**` |
| `[x]` | Adicionar perfis **`RH`** e **`Financeiro`** ao `UsuarioFuncao` (back-office, com filas próprias) | `backend/app/modelos/Usuarios.py` + tipos do front |
| `[x]` | Adicionar **`Superadmin`** (a Iugo Performance, que opera a plataforma — ver Fase 0.7) | `backend/app/modelos/Usuarios.py` |
| `[x]` | Manter **`Funcionário` como perfil único** (sem subtipos: limpeza/portaria/zelador têm a mesma experiência) — decisão de produto do branding | — |

### Filas / roteamento
| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[x]` | Adicionar fila **`Comercial`** (contratos/propostas, roteada ao Gestor) ao `ChamadoFila` | `backend/app/modelos/Chamados.py` + tipos do front |

### Regras de negócio do branding a incorporar
| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | **Tickets irmãos:** uma mensagem pode gerar 2+ chamados simultâneos (ex.: atestado → RH valida + Supervisor cobre o posto), sem o usuário precisar saber das filas | modelo/serviço de chamados + IA |
| `[ ]` | **Modelar o vínculo dos tickets irmãos:** campo de agrupamento no `Chamado` (ex.: `GrupoOrigemID`/`AvisoOrigemID`) que liga chamados nascidos do mesmo aviso humano — permite a cada área ver só a sua fatia e o Gestor ver o conjunto | `backend/app/modelos/Chamados.py` |
| `[ ]` | **Cliente = Condomínio/contrato** com um responsável (síndico): evoluir o campo texto `Condominio` para entidade (detalhado na Fase 7) | `backend/app/modelos/` |
| `[ ]` | **IA detecta intenção de compra, nunca inventa preço/prazo** (invariante inegociável do branding) — já previsto na Fase 5; reforçar | `backend/app/servicos/ia.py` |

### Refinos da Visita Técnica (MVP02) conforme o branding
| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | `Duracao` **não é coluna** — derivar de `finalizada_em − iniciada_em` | `backend/app/modelos/VisitaTecnica.py` |
| `[ ]` | Adicionar `ticket_id` **opcional** (vínculo a uma reclamação) | `backend/app/modelos/VisitaTecnica.py` |
| `[ ]` | Cliente **não aprova** a visita (só recebe/consulta a prova) — diferente do chamado | rotas de visita |

---

## Fase 0.7 — Fundação SaaS Multi-Tenant 🏢 [PRIORITÁRIO — antes das features]

> **Decisão de arquitetura (27/06/2026):** o FaciliChat será um **SaaS multi-tenant**. Cada cliente do
> negócio é uma **Empresa** (conservadora/facilities que atende condomínios), e os dados de uma empresa
> ficam **totalmente isolados** das demais. Hierarquia:
> **Empresa (tenant) → Condomínios → Usuários e Chamados**.
>
> **Estratégia escolhida:** banco de dados **compartilhado** + coluna `EmpresaID` (o "tenant_id")
> em **todas** as tabelas + **Row-Level Security (RLS)** do PostgreSQL como trava extra + o tenant viaja
> dentro do **JWT**. É a abordagem mais econômica e simples de operar nesta fase (alternativas: schema
> por tenant ou banco por tenant — mais caras/complexas, descartadas por ora).
>
> **Regra de ouro:** todo dado pertence a uma Empresa e **toda consulta é filtrada por ela**.
> Por isso esta fundação vem **antes** das features grandes (Fases 1–6): cada nova tabela/rota já nasce
> com o tenant correto, evitando retrabalho caro depois.

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[x]` | Modelo `Empresa` (tenant): `Nome`, `CNPJ`, `Status` (Ativa/Suspensa), `Criacao` | `backend/app/modelos/Empresa.py` (novo) |
| `[x]` | Adicionar `EmpresaID` (FK, NOT NULL) em `Usuario`, `Chamado`, `Mensagem` — `Condominio` recebe o campo já ao nascer na Fase 7 | `backend/app/modelos/*.py` |
| `[x]` | Incluir o `EmpresaID` no payload do JWT no login | `backend/app/rotas/Autenticacao.py` |
| `[x]` | Dependência `obterTenantAtual` — extrai o tenant do token; e `obterBancoDadosComTenant` para RLS | `backend/app/rotas/Autenticacao.py` |
| `[x]` | **Todas** as queries filtram por `EmpresaID` do usuário logado (chamados, usuários, etc.) | `backend/app/rotas/*.py` |
| `[x]` | Row-Level Security (RLS) no PostgreSQL como segunda trava (defesa em profundidade) | `backend/app/rls.sql`, `backend/scripts/aplicar_rls.py` (novos) |
| `[x]` | Papéis por tenant (o **Gestor** é gestor **da sua** Empresa, não global) | `backend/app/rotas/Usuarios.py`, `Chamados.py` |
| `[ ]` | Nível **Superadmin da plataforma** (Iugo Performance): cadastrar/suspender Empresas e criar o 1º Gestor de cada uma | `backend/app/rotas/Plataforma.py` (novo) — **fora de escopo desta entrega** (script `criar_empresa.py` cobre o bootstrap; UI/rotas de Superadmin ficam para quando houver demanda) |
| `[x]` | `scripts/criar_empresa.py` — cria Empresa + 1º Gestor juntos (substitui `criar_gerente.py`, removido) | `backend/scripts/` |

### Frontend (web e mobile)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[x]` | Tenant vem do token (o front não envia); Empresa (ID e nome) guardados em `auth.ts`, exibição no cabeçalho fica para o `AdminShell` (painel do gestor) | `frontend/web/src/lib/auth.ts` |
| `[ ]` | Área de **Superadmin** (web) para gerenciar Empresas (separada do painel da empresa) | `frontend/web/src/app/(plataforma)/...` (novo) — **fora de escopo desta entrega**, ver nota acima |
| `[x]` | Tipos: `EmpresaID`/`empresa_nome` adicionados a `Usuario`/`Chamado`/`TokenResposta` (web). Mobile só sincronizou `UsuarioFuncao`/`ChamadoFila` (Fase 0.6) — sem UI multi-tenant no mobile, fora do escopo desta entrega | `frontend/web/src/types/index.ts` |

---

## Fase 1 — Chat (base do produto)

> Desbloqueia o produto. Implementar **logo após** a Fundação Multi-Tenant (Fase 0.7).

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Rotas de mensagens: `GET /chamados/{id}/mensagens` e `POST /chamados/{id}/mensagens` | `backend/app/rotas/Mensagens.py` (novo) |
| `[ ]` | Schemas Pydantic: `MensagemCriar` e `MensagemSaida` | `backend/app/rotas/Mensagens.py` |
| `[ ]` | Registrar router `/mensagens` no `main.py` | `backend/app/main.py` |
| `[ ]` | WebSocket por chamado: `GET /ws/chamados/{id}` — broadcast para participantes | `backend/app/rotas/WebSocket.py` (novo) |
| `[ ]` | **Confirmação automática "Recebido"** ao abrir chamado — mensagem de sistema imediata (jornada do Cliente e do Funcionário: certeza de ter sido ouvido antes de qualquer atraso) | `backend/app/rotas/Chamados.py`/`Mensagens.py` |
| `[ ]` | **Mensagens de voz e foto como primeira classe** — `Mensagem` aceita `Tipo` (Texto/Audio/Imagem) e conteúdo de mídia; entrada por voz/foto vale igual a texto (baixa intimidade digital do Funcionário). Storage detalhado na Fase 9 | `backend/app/modelos/Mensagens.py` + rotas |
| `[ ]` | Atualizar `docs/tecnico-backend.md` com as novas rotas | `docs/tecnico-backend.md` |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Adicionar `api.mensagens.listar(chamadoId)` e `api.mensagens.enviar(chamadoId, texto)` | `frontend/web/src/lib/api.ts` |
| `[ ]` | Componente `BolhaMensagem` (recebida ← branca/esquerda, enviada → azul/direita, sistema → pílula central) | `frontend/web/src/components/BolhaMensagem.tsx` (novo) |
| `[ ]` | Página `/painel/chamados/[id]` — thread de chat com input de envio | `frontend/web/src/app/(painel)/chamados/[id]/page.tsx` (novo) |
| `[ ]` | Hook `useWebSocket(chamadoId)` para mensagens em tempo real | `frontend/web/src/lib/useWebSocket.ts` (novo) |
| `[ ]` | Atualizar `docs/tecnico-frontend.md` | `docs/tecnico-frontend.md` |

### Frontend Mobile

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Adicionar `api.mensagens.listar` e `api.mensagens.enviar` | `frontend/mobile/lib/api.ts` |
| `[ ]` | Tipo `Mensagem` já existe — verificar se `MensagemCriar` precisa ser adicionado | `frontend/mobile/lib/types.ts` |
| `[ ]` | Tela de chat por chamado com FlatList de bolhas + TextInput + botão enviar | `frontend/mobile/app/(tabs)/chamados/[id].tsx` (novo) |
| `[ ]` | Conectar WebSocket nativo no mobile | `frontend/mobile/lib/useWebSocket.ts` (novo) |
| `[ ]` | Toque no card de chamado navega para a tela de chat | `frontend/mobile/app/(tabs)/chamados.tsx` |

---

## Fase 2 — Criar chamado e detalhe (cliente)

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Validar que `POST /chamados/` retorna o chamado criado com ID para redirecionar | `backend/app/rotas/Chamados.py` |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Botão "Novo chamado" abre modal com textarea (IA classifica no backend) | `frontend/web/src/app/(painel)/chamados/page.tsx` |

### Frontend Mobile

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Tela "Novo chamado" — textarea livre, botão enviar, IA classifica no backend | `frontend/mobile/app/(tabs)/novo-chamado.tsx` (novo) |
| `[ ]` | Adicionar aba "Novo" no tab navigator | `frontend/mobile/app/(tabs)/_layout.tsx` |
| `[ ]` | Tela de detalhe do chamado — timeline vertical de status (Recebido → Em Andamento → Agendado → Concluído) | `frontend/mobile/app/(tabs)/chamados/[id]/detalhe.tsx` (novo) |

---

## Fase 3 — Fila e operação do supervisor (mobile)

> Supervisor está em campo, no celular. Cada ação deve caber em menos de 30 segundos.

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | `GET /chamados/?supervisor_id=me&ordenar=prazo` — lista filtrada para o supervisor logado | `backend/app/rotas/Chamados.py` |
| `[ ]` | `PATCH /chamados/{id}/agendar` — salvar executor, data/hora, observação ao cliente | `backend/app/rotas/Chamados.py` |
| `[ ]` | Campo `NotaInterna` no modelo `Chamado` (nunca exposta ao cliente) | `backend/app/modelos/Chamados.py` |
| `[ ]` | `PATCH /chamados/{id}/concluir` — transição para Concluido + dispara mensagem automática | `backend/app/rotas/Chamados.py` |
| `[ ]` | **Fechamento em pouquíssimos toques** (jornada do Supervisor: "concluir precisa ser mais leve que mandar um WhatsApp") — revisar UX de conclusão para caber em 1–2 toques | `frontend/mobile/app/(supervisor)/**` |
| `[ ]` | **Aprovação do cliente encerra o ticket** — o Cliente aprova a conclusão no chat (campo `AprovadoEm` no `Chamado`); distinto da Visita Técnica, que o cliente **não** aprova | `backend/app/modelos/Chamados.py`, rotas |
| `[ ]` | **Agenda do dia com prioridade visual sobre a fila** — ao abrir o app, o Supervisor vê primeiro onde precisa estar (visitas de hoje) e depois o que precisa resolver (tickets) | `frontend/mobile/app/(supervisor)/**` |

### Frontend Mobile

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Tela "Fila" do supervisor — abas: Todos / Atrasados / Aguardando / Agendados; ordenado por prazo | `frontend/mobile/app/(supervisor)/fila.tsx` (novo) |
| `[ ]` | Badge vermelho em chamados com prazo estourado | (dentro da tela Fila) |
| `[ ]` | Tela "Hoje" do supervisor — agenda do dia em ordem cronológica | `frontend/mobile/app/(supervisor)/hoje.tsx` (novo) |
| `[ ]` | Tela "Ticket completo" — campo de agendamento (executor + data/hora), observação ao cliente, nota interna oculta, botão Concluir com confirmação | `frontend/mobile/app/(supervisor)/ticket/[id].tsx` (novo) |
| `[ ]` | Navegação por abas do supervisor: Fila / Hoje / Perfil | `frontend/mobile/app/(supervisor)/_layout.tsx` (novo) |
| `[ ]` | Roteamento dinâmico: se `Funcao === Supervisor`, mostrar tabs do supervisor; se `Cliente`, tabs do cliente | `frontend/mobile/app/(tabs)/_layout.tsx` ou `app/index.tsx` |

---

## Fase 4 — Dashboard do gestor (web)

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | `GET /relatorios/visao-geral` — retorna: total abertos, SLA estourado, 1ª resposta média, resolução média | `backend/app/rotas/Relatorios.py` (novo) |
| `[ ]` | `GET /relatorios/supervisores` — lista supervisores com: abertos, atrasados, 1ª resposta média | `backend/app/rotas/Relatorios.py` |
| `[ ]` | `GET /chamados/?supervisor_id={id}` — fila de um supervisor específico (para o gestor ver) | `backend/app/rotas/Chamados.py` |
| `[ ]` | **Alerta de gargalo "parado há tempo demais"** — chamado sem movimentação acima de um limite (o limite é **configurável por Empresa**, ex.: guardado como campo/config do tenant; **não** hard-coded) sobe como alerta no painel do Gestor. "Tempo parado" é **derivado** de `Atualizacao`, não coluna | `backend/app/rotas/Relatorios.py` |
| `[ ]` | **Alerta de cobertura descoberta** — posto/turno sem responsável confirmado vira alerta de atenção | `backend/app/rotas/Relatorios.py` |
| `[ ]` | **Desempenho por supervisor com lastro** — métrica derivada do fechamento de chamados (recebidos/resolvidos/parados por supervisor e por fila), não de impressão | `backend/app/rotas/Relatorios.py` |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Página `/painel` redirecionada para `/painel/visao-geral` | `frontend/web/src/app/(painel)/page.tsx` |
| `[ ]` | Página `visao-geral` — cards de KPIs (abertos, SLA em risco, 1ª resposta, resolução) | `frontend/web/src/app/(painel)/visao-geral/page.tsx` (novo) |
| `[ ]` | Seção "Desempenho por supervisor" — tabela com nome, abertos, 1ª resposta, estado (vermelho/verde) | (dentro de visao-geral) |
| `[ ]` | Seção "Volume por categoria" — categorias vêm **dos dados** (agregação das categorias reais dos chamados da Empresa), não de uma lista fixa no código | (dentro de visao-geral) |
| `[ ]` | **Hierarquia do painel: urgente → tendência → detalhe** — o que exige ação agora aparece primeiro; tendência em segundo nível; detalhe sob demanda (evita "parede de números") | (dentro de visao-geral) |
| `[ ]` | **Painel "O que precisa da sua atenção"** — lista de alertas (crítico / atenção / oportunidade) com atalho do alerta direto para o chamado/conversa (sem garimpo) | (dentro de visao-geral) |
| `[ ]` | Página `supervisores` — cards clicáveis; clique expande a fila daquele supervisor | `frontend/web/src/app/(painel)/supervisores/page.tsx` (novo) |
| `[ ]` | Página `tickets` — tabela completa com filtros: período, supervisor, status, categoria; busca por cliente | `frontend/web/src/app/(painel)/tickets/page.tsx` (novo) |
| `[ ]` | Adicionar links no sidebar: Visão geral / Supervisores / Todos os tickets / Alertas | `frontend/web/src/app/(painel)/layout.tsx` |

---

## Fase 4.5 — Catálogo de Serviços e Parceiros 🆕 [discovery: Governança de IA]

> **Origem:** documento de Governança de IA em `docs/FaciliChat-Regras/`. O **catálogo é a fonte da
> verdade comercial** de cada Empresa e o **portão obrigatório** que a IA consulta antes de sinalizar
> qualquer oportunidade (Fase 5). Sem catálogo, a IA não tem o que oferecer.
>
> **Regra de modelagem:** serviços e parceiros são **dados por Empresa (linhas de tabela)**, nunca
> nomes fixos no código. **Não há campo de preço** — preço é decisão humana do Gestor (invariante da IA).

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `Parceiro` (executor terceirizado): `EmpresaID`, `Nome`, `Contato` (opcional) | `backend/app/modelos/Parceiro.py` (novo) |
| `[ ]` | Modelo `CatalogoServico`: `EmpresaID`, `Nome`, `Tipo` (Proprio/Parceria), `ParceiroID` (opcional, só se Parceria), `Oferece` (bool). **Sem campo de valor/preço** | `backend/app/modelos/CatalogoServico.py` (novo) |
| `[ ]` | CRUD do catálogo e de parceiros — escopado à Empresa; edição só do **Gestor** (e Superadmin no onboarding) | `backend/app/rotas/Catalogo.py` (novo) |

### Frontend Web (Gestor)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Tela "Catálogo de serviços" — listar/adicionar/editar/ativar-desativar serviço (nome, tipo próprio/parceria, parceiro, oferece) | `frontend/web/src/app/painel/catalogo/page.tsx` (novo) |
| `[ ]` | Tela "Parceiros" — listar/adicionar/editar parceiros | `frontend/web/src/app/painel/parceiros/page.tsx` (novo) |
| `[ ]` | Tipos TS `CatalogoServico`/`Parceiro` sincronizados com o backend | `frontend/web/src/types/index.ts` |

---

## Fase 5 — IA (classificação, roteamento e narração)

> IA usa o SDK Anthropic já instalado. Nunca inventa prazos. Só narra campos estruturados.

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Serviço `ia_classificar(texto)` — retorna `Fila`, `Categoria`, `Prioridade` | `backend/app/servicos/ia.py` (novo) |
| `[ ]` | Ao criar chamado (`POST /chamados/`): chamar `ia_classificar` e preencher campos automaticamente | `backend/app/rotas/Chamados.py` |
| `[ ]` | Serviço `ia_narrar_status(chamado)` — gera mensagem de sistema quando status muda | `backend/app/servicos/ia.py` |
| `[ ]` | Ao atualizar status: criar `Mensagem` automática com `AutorTipo = IA` | `backend/app/rotas/Chamados.py` |
| `[ ]` | **Roteamento por intenção → fila correta**, incluindo **tickets irmãos** (um aviso → N chamados em filas distintas) usando o vínculo de grupo da Fase 0.6 | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | Serviço `ia_detectar_oportunidade(mensagem)` — detecta intenção de serviço extra | `backend/app/servicos/ia.py` |
| `[ ]` | **Portão do catálogo (obrigatório):** ao detectar intenção, a IA **consulta o `CatalogoServico` da Empresa** (Fase 4.5). Serviço no catálogo → registra oportunidade; **fora do catálogo → silêncio comercial** (registra só como observação operacional para a supervisão, não oferece nada ao cliente) | `backend/app/servicos/ia.py` |
| `[ ]` | Modelo `Oportunidade` (entidade própria, não campo no Chamado): `EmpresaID`, `ChamadoID`, `ServicoID`, `Status` (Nova/Vista/PropostaConstruida/Rejeitada), `Criacao`. A IA **nunca cita preço** — só sinaliza | `backend/app/modelos/Oportunidade.py` (novo) |

---

## Fase 5.5 — Governança e guardrails da IA 🆕 [discovery: Governança de IA]

> **Origem:** documento de Governança de IA em `docs/FaciliChat-Regras/`. Formaliza **o que a IA pode e
> não pode fazer** — não como instrução solta no prompt, mas como **camada verificável** (guardrails +
> validação de resposta + auditoria). Princípio fundador: **"geração ancorada"** — a IA só fala o que um
> humano cadastrou (campo de ticket, regra na base, serviço no catálogo).

### Backend — guardrails e validação

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | **Matriz de permissões por perfil** (7 perfis × pode/não-pode) traduzida em guardrails aplicados **antes** de gerar cada resposta | `backend/app/servicos/ia_governanca.py` (novo) |
| `[ ]` | **Validação pós-geração** de toda resposta da IA antes de enviar: não contém preço? só cita serviço do catálogo? não promete prazo não registrado? não responde regra de RH/Financeiro não cadastrada? não fala em nome de humano? | `backend/app/servicos/ia_governanca.py` |
| `[ ]` | **Log de auditoria de decisões da IA** — registra intenção detectada, consulta ao catálogo/base e ação tomada (rastreabilidade e confiança) | `backend/app/modelos/IaAuditoria.py` (novo) |
| `[ ]` | Reforçar isolamento multi-tenant na IA — toda consulta da IA filtrada por `EmpresaID` (nunca cruza Empresas) | `backend/app/servicos/ia*.py` |

### Backend — base de regras (RH / Financeiro)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `BaseRegra`: `EmpresaID`, `Area` (RH/Financeiro), `Chave`/`Pergunta`, `Resposta` — conhecimento **cadastrado por Empresa**, nunca hard-coded | `backend/app/modelos/BaseRegra.py` (novo) |
| `[ ]` | IA **responde dúvida recorrente** (ex.: 2ª via de holerite, vale) só a partir da `BaseRegra`; **regra ausente → encaminha** para a fila humana em vez de inventar | `backend/app/servicos/ia.py` |
| `[ ]` | CRUD da base de regras — RH edita a sua, Financeiro a sua (escopado por Empresa e por área) | `backend/app/rotas/Regras.py` (novo) |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Tela de "Base de regras" (RH e Financeiro) — cadastrar/editar perguntas e respostas recorrentes | `frontend/web/src/app/painel/regras/page.tsx` (novo) |

---

## Fase 6 — Alertas comerciais e propostas

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `Proposta`: campos ChamadoID, `OportunidadeID` (vínculo à `Oportunidade` da Fase 5), Titulo, Escopo, Prazo, Valor, Status (Rascunho/Enviada/Aprovada/Recusada). **O `Valor` é preenchido pelo Gestor** — a IA nunca o gera | `backend/app/modelos/Proposta.py` (novo) |
| `[ ]` | `GET /propostas/alertas` — lista as `Oportunidade`s (Status=Nova) aguardando decisão/proposta do Gestor | `backend/app/rotas/Propostas.py` (novo) |
| `[ ]` | `POST /propostas/` — criar e enviar proposta no chat do cliente | `backend/app/rotas/Propostas.py` |
| `[ ]` | `PATCH /propostas/{id}/status` — cliente aprova ou recusa | `backend/app/rotas/Propostas.py` |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Página `alertas` — cards de oportunidades; botão "Montar proposta" abre formulário | `frontend/web/src/app/(painel)/alertas/page.tsx` (novo) |
| `[ ]` | Formulário de proposta: Título, Escopo (textarea), Prazo médio, Início previsto, Valor (R$), preview de como o cliente vai ver | (dentro de alertas ou modal) |

### Frontend Mobile (Cliente)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Componente de proposta no chat — card com título, escopo, prazo, valor, botões Aprovar/Recusar | `frontend/mobile/components/CardProposta.tsx` (novo) |

---

## Fase 7 — Gestão de Empresas e Condomínios (telas/CRUD)

> **Depende da Fase 0.7 (Fundação SaaS Multi-Tenant)**, que já cria a entidade `Empresa`, o
> `EmpresaID` em todas as tabelas, o escopo por tenant, a RLS e o tenant no JWT. Esta fase
> entrega as **telas e rotas de gestão** que usam aquela fundação. (O `CondominioID` em `Usuario`/
> `Chamado` e o isolamento por tenant já terão sido feitos na 0.7.)

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `Condominio`: `Nome`, `Endereco`, `CNPJ`, **`EmpresaID`** | `backend/app/modelos/Condominio.py` (novo) |
| `[ ]` | CRUD de condomínios — escopado à Empresa do Gestor | `backend/app/rotas/Condominios.py` (novo) |
| `[ ]` | CRUD de Empresas — somente Superadmin da plataforma | `backend/app/rotas/Plataforma.py` |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Página `cadastros` — usuários e condomínios da empresa (só Gestor) | `frontend/web/src/app/painel/cadastros/page.tsx` (novo) |
| `[ ]` | Área de plataforma — gerenciar Empresas (Superadmin) | `frontend/web/src/app/(plataforma)/...` (novo) |

---

## Fase 8 — MVP 02: Visitas Técnicas

> Entidade separada do Chamado. Proativa (supervisor → cliente), não reativa.

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `VisitaTecnica`: SupervisorID, CondominioID, EmpresaID, DataHoraAgendada, HoraChegada, HoraSaida, Notas, Status (Agendada/EmAndamento/Finalizada/RelatorioEnviado), `ticket_id` opcional. **Duração deriva** de HoraSaida−HoraChegada (não é coluna) | `backend/app/modelos/VisitaTecnica.py` (novo) |
| `[ ]` | `POST /visitas/` — agendar visita | `backend/app/rotas/Visitas.py` (novo) |
| `[ ]` | `PATCH /visitas/{id}/iniciar` — grava `HoraChegada` = agora | `backend/app/rotas/Visitas.py` |
| `[ ]` | `PATCH /visitas/{id}/finalizar` — grava `HoraSaida`, calcula `Duracao`, muda status para Finalizada | `backend/app/rotas/Visitas.py` |
| `[ ]` | Ao finalizar: IA narra relatório e posta `Mensagem` no chat do condomínio (AutorTipo = IA) | `backend/app/rotas/Visitas.py` + `servicos/ia.py` |
| `[ ]` | Upload de fotos da visita | `backend/app/rotas/Visitas.py` |
| `[ ]` | `GET /visitas/?condominio_id=` — histórico para o cliente | `backend/app/rotas/Visitas.py` |
| `[ ]` | `GET /visitas/?supervisor_id=me` — agenda do supervisor | `backend/app/rotas/Visitas.py` |
| `[ ]` | IA detecta acordo de visita no chat e cria visita agendada automaticamente | `backend/app/servicos/ia.py` |

### Frontend Mobile (Supervisor)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Tela "Visita em andamento" — cronômetro no topo (HH:MM:SS), campo de texto livre, galeria de fotos (botão adicionar empilha abaixo do texto), botão "Finalizar visita" | `frontend/mobile/app/(supervisor)/visita/[id].tsx` (novo) |
| `[ ]` | Tela "Agendar visita" — picker de condomínio, data/hora | `frontend/mobile/app/(supervisor)/visita/nova.tsx` (novo) |
| `[ ]` | Visitas aparecem na tela "Hoje" do supervisor | `frontend/mobile/app/(supervisor)/hoje.tsx` |

### Frontend Mobile (Cliente)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Aba "Visitas" no app do cliente — lista com data, horário, duração, supervisor, observações, fotos | `frontend/mobile/app/(tabs)/visitas.tsx` (novo) |

### Frontend Web (Gestor)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Página `visitas` no painel — tabela: cliente, supervisor, data, duração, status; filtro por supervisor; badge "Não realizada" em vermelho | `frontend/web/src/app/(painel)/visitas/page.tsx` (novo) |
| `[ ]` | Adicionar "Visitas técnicas" no sidebar (visível para Gestor e Supervisor) | `frontend/web/src/app/painel/layout.tsx` |

---

## Fase 9 — Upload de arquivos

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Configurar storage (S3 ou MinIO local via Docker) | `backend/app/servicos/storage.py` (novo), `docker-compose.yml` |
| `[ ]` | Rota `POST /uploads/` — retorna URL do arquivo | `backend/app/rotas/Uploads.py` (novo) |
| `[ ]` | Suporte a envio de fotos no chat (mensagens com `tipo = imagem`) | `backend/app/modelos/Mensagens.py`, rotas |
| `[ ]` | Componente de upload de imagem no chat web | `frontend/web/src/components/` |
| `[ ]` | Upload de imagem no chat mobile via `expo-image-picker` | `frontend/mobile/` |

---

## Fase 10 — Notificações push

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Integrar Expo Push Notifications no mobile | `frontend/mobile/lib/notificacoes.ts` (novo) |
| `[ ]` | Backend envia push ao criar mensagem para o destinatário offline | `backend/app/servicos/notificacoes.py` (novo) |
| `[ ]` | Configurar tokens de dispositivo por usuário no banco | `backend/app/modelos/Usuarios.py` |

---

## Fase 11 — Experiência do Funcionário (canal único) 🆕 [discovery: Jornada do Funcionário]

> **Origem:** jornada do Funcionário em `docs/FaciliChat-Regras/`. Hoje o perfil Funcionário quase não
> existe no produto. A jornada exige um app **radicalmente simples** (celular simples, dados limitados,
> preferência por voz/foto): "se for mais difícil que o WhatsApp, ele não usa".
>
> **Reaproveita:** roteamento por intenção e tickets irmãos (Fase 5), voz/foto no chat (Fases 1 e 9),
> base de regras e resposta automática (Fase 5.5). Esta fase é a **experiência do Funcionário** montada
> sobre essas fundações. **Funcionário é perfil único** (sem subtipos) — invariante do `CLAUDE.md`.

### Frontend Mobile (Funcionário)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Canal único de comunicação com entrada mínima — um só campo que aceita **texto, voz e foto**; zero formulário obrigatório | `frontend/mobile/app/(funcionario)/**` (novo) |
| `[ ]` | Confirmação "Recebido" visível imediatamente após enviar (reaproveita a Fase 1) | (dentro do canal) |
| `[ ]` | Navegação por abas do funcionário (roteamento dinâmico por `Funcao`, como o supervisor na Fase 3) | `frontend/mobile/app/(funcionario)/_layout.tsx` (novo) |

### Fluxos de aviso do Funcionário (backend + IA)

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | **Atestado/falta → tickets irmãos** (RH valida + Supervisor cobre o posto) a partir de um único aviso | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | **Sensor de campo** — observação do funcionário vira `Oportunidade` **via portão do catálogo** (Fase 5), sem transformar o funcionário em vendedor e sem preço | `backend/app/servicos/ia.py` |
| `[ ]` | **Reposição de insumo** — aviso simples ("está acabando") vira chamado rastreável para a área responsável; detalhes (item/quantidade) estruturados nos bastidores, não pedidos ao funcionário. (Integração ERP fica adiada — ver "Adiados") | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | **Dúvida pessoal** (holerite, vale) — roteada à fila individual correta; resposta automática pela `BaseRegra` (Fase 5.5) quando cadastrada | `backend/app/servicos/ia.py` |

> **Nota de modelagem:** os "tipos de aviso" acima (atestado/falta, sensor de campo, reposição, dúvida
> pessoal) são **classificações de intenção detectadas pela IA e/ou um campo `Tipo`/`Categoria` no
> chamado**, não telas/rotas fixas nem nomes hard-coded. A rota de origem é sempre o mesmo canal único.

---

## Adiados (pós-MVP) — registrados para não se perder

> Decisões conscientes de **não fazer agora**, tiradas do material de discovery. Ficam registradas para
> não sumirem; **não** entram no MVP.

| Status | Item | Origem |
|--------|------|--------|
| `[ ]` | **Isolamento de privacidade por tópico** — hoje o Supervisor/Gestor enxergam todas as conversas. Restringir conteúdo sensível (atestado, folha, salário) por área/papel é evolução futura, a validar com usuários reais | Jornadas Funcionário/Dono + HMW |
| `[ ]` | **Integração com ERP** — a reposição de insumo (Fase 11) pode, no futuro, baixar estoque / gerar reposição / cobrança automaticamente. Modelar já pensando nisso, sem implementar | Jornada do Funcionário |

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
Perfis de usuário:    Cliente | Funcionário | Supervisor | RH | Financeiro | Gestor  (dentro de uma Empresa)
                     [código atual ainda usa "Gerente" e só 4 perfis; migração na Fase 0.6]
Filas de chamado:     Operacional | RH | Financeiro | Comercial
Status de chamado:    Recebido | EmAndamento | Agendado | Concluido | Cancelado
Prioridades:          Baixa | Media | Alta | Critica
Status de visita:     Agendada | EmAndamento | Finalizada | RelatorioEnviado
AutorTipo mensagem:   Humano | IA | Sistema
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
```

---

*Mantido por: Claude Code — atualizar a cada sessão de desenvolvimento*
