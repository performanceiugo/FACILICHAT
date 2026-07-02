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
> **Vocabulário de status do board:** `📋 backlog` = `[ ]` · `🚧 em andamento` = `[~]` ·
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
| `[ ]` | Commitar os artefatos da integração (hook, settings, plano unificado, changelog) |

---

## 🗺️ Mapa das fases (visão rápida)

| Fase | Tema | Tarefa-pai (CU) | Status |
|------|------|-----------------|--------|
| 0 | Infraestrutura e base | `868k60uxe` | ✅ Concluída |
| 0.5 | Correções do levantamento (bugs e melhorias) | `868k60uzw` / `868k60v1m` | 🟡 Críticos concluídos; altos/médios/baixos/docs na fila |
| 0.6 | Alinhamento de domínio com o branding | `868k60vdy` | 🟡 Núcleo (7 perfis/fila) concluído; regras/refinos na fila · **PRIORITÁRIO** |
| 0.7 | Fundação SaaS Multi-Tenant | `868k60vfm` | 🟡 Fundação concluída; Superadmin da plataforma na fila · **PRIORITÁRIO** |
| 1 | Chat (base do produto) | `868k60vny` | ⬜ Na fila |
| 2 | Criar chamado e detalhe (cliente) | `868k60vvt` | ⬜ Na fila |
| 3 | Fila e operação do supervisor (mobile) | `868k60vx4` | ⬜ Na fila |
| 4 | Dashboard do gestor (web) | `868k60w16` | ⬜ Na fila |
| 4.5 | Catálogo de Serviços e Parceiros | `868k7vr0g` | ⬜ Na fila · **NOVA (discovery)** |
| 5 | IA (classificação, roteamento e narração) | `868k60w34` | ⬜ Na fila |
| 5.5 | Governança e guardrails da IA | `868k7vr1c` | ⬜ Na fila · **NOVA (discovery)** |
| 6 | Alertas comerciais e propostas | `868k60w41` | ⬜ Na fila |
| 7 | Gestão de Empresas e Condomínios (telas/CRUD) | `868k60wgx` | ⬜ Na fila |
| 8 | MVP 02: Visitas Técnicas | `868k60whw` | ⬜ Na fila |
| 9 | Upload de arquivos | `868k60wn5` | ⬜ Na fila |
| 10 | Notificações push | `868k60wpb` | ⬜ Na fila |
| 11 | Experiência do Funcionário (canal único, voz/foto, sensor de campo) | `868k7vr1k` | ⬜ Na fila · **NOVA (discovery)** |
| — | Adiados (pós-MVP): privacidade por tópico, integração ERP | `868k7vr1q` | ⬜ Registrado |

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

## Fase 0 — Infraestrutura e base · CU: `868k60uxe`

| Status | CU | Item |
|--------|----|------|
| `[x]` | `868k60uxr` | Auth JWT (login, token, middleware `obterUsuarioAtual`) |
| `[x]` | `868k60uxu` | Modelo `Usuario` com enum `UsuarioFuncao` (Cliente/Supervisor/Funcionario/Gerente) |
| `[x]` | `868k60uy1` | Modelo `Chamado` com enums de Fila, Status e Prioridade |
| `[x]` | `868k60uy4` | Modelo `Mensagem` com `AutorTipo` (Humano/IA/Sistema) |
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

### 🟠 Altos

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[ ]` | `868k60v1q` | A1 | `obterUsuarioAtual` retorna 500 (não 401) em token malformado | Mover conversão para dentro do try e capturar `(JWTError, ValueError)` | `backend/app/rotas/Autenticacao.py` |
| `[ ]` | `868k60v1x` | A3 | Web e mobile sem tratamento de 401/token expirado | No cliente HTTP, ao receber 401 → `auth.sair()` + redirecionar para login | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[ ]` | `868k60v29` | A4 | Proteção de rota só client-side com flash de conteúdo (web) | Usar `middleware.ts` do Next; renderizar `null`/loader enquanto não autenticado | `frontend/web/src/middleware.ts` (novo), `(painel)/layout.tsx` |
| `[ ]` | `868k60v2e` | A5 | Design system violado: cor `#1a56db` (deveria `#148AF5`) e fonte Geist (deveria Figtree) | Substituir tokens de cor e trocar fonte para Figtree (web e mobile) | `frontend/web/src/app/layout.tsx`, `globals.css`; `frontend/mobile/app/**` |
| `[ ]` | `868k60v2g` | A6 | API de mensagens (`api.mensagens.*`) aponta para rota inexistente no backend | Alinhar com a Fase 1 (criar rota) ou marcar como código futuro | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[ ]` | `868k60v2k` | A7 | Link `/usuarios` no sidebar sem página correspondente → 404 | Criar a página ou esconder o link até existir | `frontend/web/src/app/(painel)/layout.tsx` |
| `[ ]` | `868k60v2r` | A8 | Mobile: React 18.3 / expo-router 4 incompatíveis com Expo SDK 53 | Rodar `npx expo install --fix`; alinhar React 19 / router 5 | `frontend/mobile/package.json` |

### 🟡 Médios

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[ ]` | `868k60v2w` | M1 | Falta validação Pydantic de tamanho/força (senha sem `min_length`) | Adicionar `Field(max_length=...)` e `min_length` na senha | `backend/app/rotas/Usuarios.py`, `Chamados.py` |
| `[ ]` | `868k60v30` | M2 | `IntegrityError` no cadastro não tratado (corrida TOCTOU no check de email) | Capturar `IntegrityError` e retornar 400 | `backend/app/rotas/Usuarios.py` |
| `[x]` | `868k60v33` | M3 | Magic strings `"Gerente"/"Supervisor"` em vez do enum | Comparar com `UsuarioFuncao.Gestor`/`.Supervisor` (corrigido junto da Fase 0.6) | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k60v3c` | M4 | `echo=True` fixo no engine (loga todo SQL em produção) | Tornar configurável via env (`echo=configuracoes.DEBUG`) | `backend/app/banco_dados.py` |
| `[ ]` | `868k60vam` | M5 | `Config` (Pydantic v1), `datetime.utcnow` deprecado e colunas `DateTime` naive | Migrar para `ConfigDict`; `datetime.now(timezone.utc)` + `DateTime(timezone=True)` | `backend/app/modelos/*.py`, `rotas/*.py`, `configuracoes.py` |
| `[ ]` | `868k60vay` | M6 | Web: rewrite/proxy em `next.config.ts` configurado mas nunca usado | Escolher estratégia e centralizar base URL | `frontend/web/next.config.ts`, `lib/api.ts` |
| `[ ]` | `868k60vb1` | M7 | Web: `Record<string,string>` em vez dos enums; `err: any`; `erro.detail` não tipado | Tipar com `Record<ChamadoStatus, ...>`; normalizar `detail`; `err instanceof Error` | `frontend/web/src/app/(painel)/chamados/page.tsx`, `lib/api.ts` |
| `[ ]` | `868k60vb3` | M8 | Web: `token()` duplicado entre `api.ts` e `auth.ts` | `api.ts` importa e usa `auth.token()` | `frontend/web/src/lib/api.ts` |
| `[ ]` | `868k60vbb` | M9 | Web: arquivos CSS sem nenhum comentário (viola regra do `CLAUDE.md`) | Adicionar cabeçalho e comentar blocos (especialmente `:root` de tokens) | `frontend/web/src/app/**/*.css` |
| `[ ]` | `868k60vbj` | M10 | Mobile: `chamados.tsx`/`perfil.tsx` sem `catch` → erros engolidos | Adicionar `catch` com estado de erro e botão "Tentar novamente" | `frontend/mobile/app/(tabs)/chamados.tsx`, `perfil.tsx` |
| `[ ]` | `868k60vbz` | M11 | Mobile: paleta fora dos tokens; Figtree não carregada | Substituir pelos tokens Ink; carregar Figtree via `expo-font` | `frontend/mobile/app/**` |

### 🟢 Baixos

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[ ]` | `868k60vc3` | B1 | Raios de canto fora da escala (cards 10/12 em vez de 8; inputs 10) | Padronizar 8px em cards | web e mobile (CSS/estilos) |
| `[ ]` | `868k60vca` | B2 | `useEffect` de fetch sem cleanup/AbortController (web e mobile) | Adicionar `AbortController`/flag de montagem no cleanup | `chamados/page.tsx` (web), telas mobile |
| `[ ]` | `868k60vck` | B3 | Web: faltam `error.tsx` e `not-found.tsx` | Criar `app/error.tsx` e `app/not-found.tsx` | `frontend/web/src/app/` |
| `[ ]` | `868k60vct` | B4 | Mobile: tabs sem ícones (Line Awesome) | Adicionar `tabBarIcon` às abas | `frontend/mobile/app/(tabs)/_layout.tsx` |
| `[ ]` | `868k60vcx` | B5 | A11y: foco de teclado removido; navegação sem ARIA; estados sem `aria-live` | `:focus-visible` com anel de foco; adicionar atributos ARIA | `frontend/web/src/app/**` |
| `[ ]` | `868k60vd4` | B6 | Backend: JWT sem `iat/iss/aud`; hasher duplicado; `@app.on_event` deprecado | Adicionar claims; centralizar hasher; migrar para `lifespan` | `backend/app/rotas/Autenticacao.py`, `Usuarios.py`, `main.py` |
| `[ ]` | `868k7vx0v` | B7 | Painel web (desktop do Gestor) não validado em navegador mobile (breakpoints, tabelas largas) | Analisar o enquadramento responsivo do painel web em telas de navegador mobile e ajustar CSS/layout | `frontend/web/src/app/painel/**` |

### 📄 Documentação (divergências com o código real)

| Status | CU | ID | Problema | Correção | Arquivo(s) |
|--------|----|----|----------|----------|-----------|
| `[ ]` | `868k60vdg` | D1 | Divergência de enums: doc cita `AutorTipo: Humano/IA/Sistema` mas código usa `Cliente/Supervisor/Funcionario/IA/Sistema` | Padronizar doc com o código | `plano-implementacao.md`, `tecnico-backend.md` |
| `[ ]` | `868k60vdm` | D2 | Datas inconsistentes no `changelog.md` (mistura 2025/2026) | Padronizar para o calendário correto | `docs/changelog.md` |
| `[ ]` | `868k60vdp` | D4 | `tecnico-backend.md` documenta `uvicorn app.main:app` que falha pelos imports | Atualizar comando de execução após corrigir imports | `docs/tecnico-backend.md` |

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
| `[ ]` | `868k60vem` | **Tickets irmãos:** uma mensagem pode gerar 2+ chamados simultâneos (ex.: atestado → RH valida + Supervisor cobre o posto) | modelo/serviço de chamados + IA |
| `[ ]` | `868k7vrt2` | **Modelar o vínculo dos tickets irmãos:** campo de agrupamento no `Chamado` (`GrupoOrigemID`/`AvisoOrigemID`) que liga chamados nascidos do mesmo aviso | `backend/app/modelos/Chamados.py` |
| `[ ]` | `868k60veu` | **Cliente = Condomínio/contrato** com um responsável (síndico): evoluir campo texto `Condominio` para entidade (Fase 7) | `backend/app/modelos/` |
| `[ ]` | `868k60vf2` | **IA detecta intenção de compra, nunca inventa preço/prazo** (invariante) — reforçar | `backend/app/servicos/ia.py` |

### Refinos da Visita Técnica (MVP02) conforme o branding
| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vf7` | `Duracao` **não é coluna** — derivar de `finalizada_em − iniciada_em` | `backend/app/modelos/VisitaTecnica.py` |
| `[ ]` | `868k60vfc` | Adicionar `ticket_id` **opcional** (vínculo a uma reclamação) | `backend/app/modelos/VisitaTecnica.py` |
| `[ ]` | `868k60vfg` | Cliente **não aprova** a visita (só recebe/consulta a prova) | rotas de visita |

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
| `[ ]` | `868k60vkz` | Nível **Superadmin da plataforma** (Iugo): cadastrar/suspender Empresas e criar o 1º Gestor — **fora de escopo desta entrega** (bootstrap via `criar_empresa.py`) | `backend/app/rotas/Plataforma.py` (novo) |
| `[x]` | `868k60vn1` | `scripts/criar_empresa.py` — cria Empresa + 1º Gestor juntos (substitui `criar_gerente.py`, removido) | `backend/scripts/` |

### Frontend (web e mobile)

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[x]` | `868k60vn7` | Tenant vem do token; Empresa (ID e nome) guardados em `auth.ts`; exibição no cabeçalho fica para o `AdminShell` | `frontend/web/src/lib/auth.ts` |
| `[ ]` | `868k60vnh` | Área de **Superadmin** (web) para gerenciar Empresas — **fora de escopo desta entrega** | `frontend/web/src/app/(plataforma)/...` (novo) |
| `[x]` | `868k60vnp` | Tipos: `EmpresaID`/`empresa_nome` em `Usuario`/`Chamado`/`TokenResposta` (web); mobile só sincronizou `UsuarioFuncao`/`ChamadoFila` | `frontend/web/src/types/index.ts` |

---

## Fase 1 — Chat (base do produto) · CU: `868k60vny`

> Desbloqueia o produto. Implementar **logo após** a Fundação Multi-Tenant (Fase 0.7).

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vpu` | Rotas de mensagens: `GET /chamados/{id}/mensagens` e `POST /chamados/{id}/mensagens` | `backend/app/rotas/Mensagens.py` (novo) |
| `[ ]` | `868k60vq1` | Schemas Pydantic: `MensagemCriar` e `MensagemSaida` | `backend/app/rotas/Mensagens.py` |
| `[ ]` | `868k60vrq` | Registrar router `/mensagens` no `main.py` | `backend/app/main.py` |
| `[ ]` | `868k60vrt` | WebSocket por chamado: `GET /ws/chamados/{id}` — broadcast para participantes | `backend/app/rotas/WebSocket.py` (novo) |
| `[ ]` | `868k7vrte` | **Confirmação automática "Recebido"** ao abrir chamado — mensagem de sistema imediata | `backend/app/rotas/Chamados.py`/`Mensagens.py` |
| `[ ]` | `868k7vrtu` | **Mensagens de voz e foto como primeira classe** — `Mensagem` aceita `Tipo` (Texto/Audio/Imagem). Storage na Fase 9 | `backend/app/modelos/Mensagens.py` + rotas |
| `[ ]` | `868k60vrz` | Atualizar `docs/tecnico-backend.md` com as novas rotas | `docs/tecnico-backend.md` |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vt2` | Adicionar `api.mensagens.listar(chamadoId)` e `api.mensagens.enviar(chamadoId, texto)` | `frontend/web/src/lib/api.ts` |
| `[ ]` | `868k60vt8` | Componente `BolhaMensagem` (recebida ← esquerda, enviada → azul/direita, sistema → pílula central) | `frontend/web/src/components/BolhaMensagem.tsx` (novo) |
| `[ ]` | `868k60vtc` | Página `/painel/chamados/[id]` — thread de chat com input de envio | `frontend/web/src/app/(painel)/chamados/[id]/page.tsx` (novo) |
| `[ ]` | `868k60vun` | Hook `useWebSocket(chamadoId)` para mensagens em tempo real | `frontend/web/src/lib/useWebSocket.ts` (novo) |
| `[ ]` | `868k60vv2` | Atualizar `docs/tecnico-frontend.md` | `docs/tecnico-frontend.md` |

### Frontend Mobile

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60vv3` | Adicionar `api.mensagens.listar` e `api.mensagens.enviar` | `frontend/mobile/lib/api.ts` |
| `[ ]` | `868k60vv8` | Tipo `Mensagem` já existe — verificar se `MensagemCriar` precisa ser adicionado | `frontend/mobile/lib/types.ts` |
| `[ ]` | `868k60vvh` | Tela de chat por chamado com FlatList de bolhas + TextInput + botão enviar | `frontend/mobile/app/(tabs)/chamados/[id].tsx` (novo) |
| `[ ]` | `868k60vvm` | Conectar WebSocket nativo no mobile | `frontend/mobile/lib/useWebSocket.ts` (novo) |
| `[ ]` | `868k60vvp` | Toque no card de chamado navega para a tela de chat | `frontend/mobile/app/(tabs)/chamados.tsx` |

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
| `[ ]` | `868k7vru6` | **Fechamento em pouquíssimos toques** — conclusão em 1–2 toques | `frontend/mobile/app/(supervisor)/**` |
| `[ ]` | `868k7vruk` | **Aprovação do cliente encerra o ticket** — Cliente aprova a conclusão no chat (campo `AprovadoEm`); distinto da Visita Técnica | `backend/app/modelos/Chamados.py`, rotas |
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
| `[ ]` | `868k60w1b` | `GET /relatorios/visao-geral` — total abertos, SLA estourado, 1ª resposta média, resolução média | `backend/app/rotas/Relatorios.py` (novo) |
| `[ ]` | `868k60w1e` | `GET /relatorios/supervisores` — supervisores com abertos, atrasados, 1ª resposta média | `backend/app/rotas/Relatorios.py` |
| `[ ]` | `868k60w1g` | `GET /chamados/?supervisor_id={id}` — fila de um supervisor específico (visão do gestor) | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k7vrvm` | **Alerta de gargalo "parado há tempo demais"** — limite **configurável por Empresa** (não hard-coded); "tempo parado" é **derivado** de `Atualizacao` | `backend/app/rotas/Relatorios.py` |
| `[ ]` | `868k7vrw8` | **Alerta de cobertura descoberta** — posto/turno sem responsável confirmado | `backend/app/rotas/Relatorios.py` |
| `[ ]` | `868k7vrwh` | **Desempenho por supervisor com lastro** — métrica derivada do fechamento (recebidos/resolvidos/parados) | `backend/app/rotas/Relatorios.py` |

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60w1k` | Página `/painel` redirecionada para `/painel/visao-geral` | `frontend/web/src/app/(painel)/page.tsx` |
| `[ ]` | `868k60w1r` | Página `visao-geral` — cards de KPIs (abertos, SLA em risco, 1ª resposta, resolução) | `frontend/web/src/app/(painel)/visao-geral/page.tsx` (novo) |
| `[ ]` | `868k60w1y` | Seção "Desempenho por supervisor" — tabela com nome, abertos, 1ª resposta, estado | (dentro de visao-geral) |
| `[ ]` | `868k60w26` | Seção "Volume por categoria" — categorias vêm **dos dados** (agregação real), não de lista fixa | (dentro de visao-geral) |
| `[ ]` | `868k7vrwr` | **Hierarquia do painel: urgente → tendência → detalhe** — ação agora primeiro; tendência em 2º nível; detalhe sob demanda | (dentro de visao-geral) |
| `[ ]` | `868k7vrx5` | **Painel "O que precisa da sua atenção"** — alertas (crítico/atenção/oportunidade) com atalho direto ao chamado | (dentro de visao-geral) |
| `[ ]` | `868k60w2a` | Página `supervisores` — cards clicáveis; clique expande a fila daquele supervisor | `frontend/web/src/app/(painel)/supervisores/page.tsx` (novo) |
| `[ ]` | `868k60w2j` | Página `tickets` — tabela com filtros: período, supervisor, status, categoria; busca por cliente | `frontend/web/src/app/(painel)/tickets/page.tsx` (novo) |
| `[ ]` | `868k60w2w` | Adicionar links no sidebar: Visão geral / Supervisores / Todos os tickets / Alertas | `frontend/web/src/app/(painel)/layout.tsx` |

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
| `[ ]` | `868k60w3e` | Serviço `ia_narrar_status(chamado)` — gera mensagem de sistema quando status muda | `backend/app/servicos/ia.py` |
| `[ ]` | `868k60w3h` | Ao atualizar status: criar `Mensagem` automática com `AutorTipo = IA` | `backend/app/rotas/Chamados.py` |
| `[ ]` | `868k7vrxw` | **Roteamento por intenção → fila correta**, incluindo **tickets irmãos** (um aviso → N chamados) usando o vínculo de grupo da Fase 0.6 | `backend/app/servicos/ia.py`, `rotas/Chamados.py` |
| `[ ]` | `868k60w3m` | Serviço `ia_detectar_oportunidade(mensagem)` — detecta intenção de serviço extra | `backend/app/servicos/ia.py` |
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

### Frontend Web

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60whj` | Página `cadastros` — usuários e condomínios da empresa (só Gestor) | `frontend/web/src/app/painel/cadastros/page.tsx` (novo) |
| `[ ]` | `868k60whn` | Área de plataforma — gerenciar Empresas (Superadmin) | `frontend/web/src/app/(plataforma)/...` (novo) |

---

## Fase 8 — MVP 02: Visitas Técnicas · CU: `868k60whw`

> Entidade separada do Chamado. Proativa (supervisor → cliente), não reativa.

### Backend

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wj5` | Modelo `VisitaTecnica`: SupervisorID, CondominioID, EmpresaID, DataHoraAgendada, HoraChegada, HoraSaida, Notas, Status, `ticket_id` opcional. **Duração deriva** de HoraSaida−HoraChegada | `backend/app/modelos/VisitaTecnica.py` (novo) |
| `[ ]` | `868k60wjj` | `POST /visitas/` — agendar visita | `backend/app/rotas/Visitas.py` (novo) |
| `[ ]` | `868k60wjq` | `PATCH /visitas/{id}/iniciar` — grava `HoraChegada` = agora | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wjv` | `PATCH /visitas/{id}/finalizar` — grava `HoraSaida`, muda status para Finalizada | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wk2` | Ao finalizar: IA narra relatório e posta `Mensagem` no chat do condomínio (AutorTipo = IA) | `backend/app/rotas/Visitas.py` + `servicos/ia.py` |
| `[ ]` | `868k60wk9` | Upload de fotos da visita | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wkf` | `GET /visitas/?condominio_id=` — histórico para o cliente | `backend/app/rotas/Visitas.py` |
| `[ ]` | `868k60wkn` | `GET /visitas/?supervisor_id=me` — agenda do supervisor | `backend/app/rotas/Visitas.py` |
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

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wnd` | Configurar storage (S3 ou MinIO local via Docker) | `backend/app/servicos/storage.py` (novo), `docker-compose.yml` |
| `[ ]` | `868k60wng` | Rota `POST /uploads/` — retorna URL do arquivo | `backend/app/rotas/Uploads.py` (novo) |
| `[ ]` | `868k60wnh` | Suporte a envio de fotos no chat (mensagens com `tipo = imagem`) | `backend/app/modelos/Mensagens.py`, rotas |
| `[ ]` | `868k60wnr` | Componente de upload de imagem no chat web | `frontend/web/src/components/` |
| `[ ]` | `868k60wnx` | Upload de imagem no chat mobile via `expo-image-picker` | `frontend/mobile/` |

---

## Fase 10 — Notificações push · CU: `868k60wpb`

| Status | CU | Item | Arquivo(s) |
|--------|----|------|-----------|
| `[ ]` | `868k60wpt` | Integrar Expo Push Notifications no mobile | `frontend/mobile/lib/notificacoes.ts` (novo) |
| `[ ]` | `868k60wpx` | Backend envia push ao criar mensagem para o destinatário offline | `backend/app/servicos/notificacoes.py` (novo) |
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
Perfis de usuário:    Cliente | Funcionário | Supervisor | RH | Financeiro | Gestor  (dentro de uma Empresa)
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

ClickUp board: Operações Internas › FaciliChat - Desenvolvimento › Roadmap de Implementação
               list_id 901114027434. Cada item carrega seu CU: (subtarefa); a fase carrega o CU: da pai.
               Fechar/mover tarefa = mover o CU: para o status equivalente via MCP do ClickUp.
```

---

*Mantido por: Claude Code — atualizar a cada sessão de desenvolvimento (arquivo + ClickUp).*
