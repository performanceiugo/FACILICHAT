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

## Fase 0 — Infraestrutura e base (já concluída)

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

---

## Fase 0.5 — Correções prioritárias (levantamento de bugs e melhorias)

> **Origem:** levantamento técnico realizado em 27/06/2026 (análise completa de backend, web, mobile e docs).
> **Como conduzir:** corrigir **um item por vez**, de cima para baixo. Ao iniciar um item, mudar `[ ]` → `[~]`;
> ao concluir, `[~]` → `[x]` e registrar no `changelog.md`. Cada ID (ex: `C1`) serve para referência na conversa.
> Os **Críticos** vêm primeiro porque, no estado atual, o app não sobe nem navega.

### 🔴 Críticos — impedem o app de rodar

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[x]` | C1 | Imports não batem com os nomes dos arquivos (`from BancoDados` vs `banco_dados.py`, `Modelos`, `Rotas`, `Configuracoes`) → `ModuleNotFoundError` | Padronizado: todos os imports qualificados pelo pacote (`from app.banco_dados import ...`) em 9 arquivos | `backend/app/main.py`, `banco_dados.py`, `modelos/*.py`, `rotas/*.py` |
| `[x]` | C2 | Não é um pacote Python — falta `__init__.py`; `uvicorn app.main:app` falha | Criado `backend/app/__init__.py` (marcador de pacote) — habilita os imports qualificados do C1 | `backend/app/__init__.py` (novo) |
| `[x]` | C3 | Rotas `/painel/*` retornam 404 (route group `(painel)` não entra na URL) | Route group `(painel)` renomeado para pasta real `painel/` (via `git mv`) — as URLs `/painel/...` que o código já usava passaram a existir; zero mudança de navegação | `frontend/web/src/app/painel/**` |
| `[x]` | C4 | `auth.ts` acessa `localStorage` sem guarda de `window` → quebra no SSR / hydration mismatch | Adicionada guarda `typeof window !== 'undefined'` em todos os métodos; `painel/layout.tsx` agora lê a sessão via estado em `useEffect` e só renderiza após validar (remove flash — melhora parcial do A4) | `frontend/web/src/lib/auth.ts`, `frontend/web/src/app/painel/layout.tsx` |
| `[x]` | C5 | `app.json` referencia assets inexistentes (`icon.png`, `splash.png`, `adaptive-icon.png`) → build falha | Gerados placeholders branded (1024×1024, "F" branco na cor #148AF5) em `assets/`; `backgroundColor` do splash/adaptiveIcon corrigida `#1a56db`→`#148AF5`. Arte real pode substituir depois | `frontend/mobile/assets/*.png` (novos), `frontend/mobile/app.json` |
| `[x]` | C6 | Escalonamento de privilégio: `POST /usuarios/` é público e aceita `Funcao` do corpo → qualquer um vira Gerente | Cadastro público agora força `Funcao = Cliente`; criação privilegiada movida para `POST /usuarios/equipe` (só Gerente). Bootstrap do 1º Gerente via `backend/scripts/criar_gerente.py` | `backend/app/rotas/Usuarios.py`, `backend/scripts/criar_gerente.py` (novo) |
| `[x]` | C7 | `PATCH /chamados/{id}/status` sem autorização nem checagem de posse (IDOR) | Restrito a Supervisor/Gerente (403 caso contrário); chamado em estado terminal (Concluído/Cancelado) não pode ser reaberto (409) | `backend/app/rotas/Chamados.py` |

### 🟠 Altos

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | A1 | `obterUsuarioAtual` retorna 500 (não 401) em token malformado (`uuid.UUID()` fora do try/except) | Mover conversão para dentro do try e capturar `(JWTError, ValueError)` | `backend/app/rotas/Autenticacao.py` |
| `[x]` | A2 | CORS não configurado → frontends no navegador não chamam a API | Adicionado `CORSMiddleware` com origens explícitas vindas de `CORS_ORIGINS` (config/.env); sem `"*"` junto de credenciais | `backend/app/main.py`, `configuracoes.py` |
| `[ ]` | A3 | Web e mobile sem tratamento de 401/token expirado (usuário fica preso) | No cliente HTTP, ao receber 401 → `auth.sair()` + redirecionar para login | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[ ]` | A4 | Proteção de rota só client-side com flash de conteúdo (web) | Usar `middleware.ts` do Next; renderizar `null`/loader enquanto não autenticado | `frontend/web/src/middleware.ts` (novo), `(painel)/layout.tsx` |
| `[ ]` | A5 | Design system violado: cor primária `#1a56db` (deveria `#148AF5`) e fonte Geist (deveria Figtree) | Substituir tokens de cor e trocar fonte para Figtree (web e mobile) | `frontend/web/src/app/layout.tsx`, `globals.css`; `frontend/mobile/app/**` |
| `[ ]` | A6 | API de mensagens (`api.mensagens.*`) aponta para rota inexistente no backend | Alinhar com a Fase 1 (criar rota) ou marcar como código futuro até existir | `frontend/web/src/lib/api.ts`, `frontend/mobile/lib/api.ts` |
| `[ ]` | A7 | Link `/usuarios` no sidebar sem página correspondente → 404 | Criar a página ou esconder o link até existir | `frontend/web/src/app/(painel)/layout.tsx` |
| `[ ]` | A8 | Mobile: React 18.3 / expo-router 4 incompatíveis com Expo SDK 53 | Rodar `npx expo install --fix`; alinhar React 19 / router 5; adicionar `react-dom`/`react-native-web` | `frontend/mobile/package.json` |
| `[x]` | A9 | Web: `next@15.3.4` afetado pela CVE-2025-66478 (RCE crítico no RSC, CVSS 10.0) — descoberto no `npm install` | Atualizado `next` e `eslint-config-next` para `15.3.6` (patch da linha 15.3.x); dev server reiniciado e validado | `frontend/web/package.json` |

### 🟡 Médios

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | M1 | Falta validação Pydantic de tamanho/força (senha sem `min_length`; campos sem `max_length` → 500 em overflow) | Adicionar `Field(max_length=...)` alinhado às colunas e `min_length` na senha | `backend/app/rotas/Usuarios.py`, `Chamados.py` |
| `[ ]` | M2 | `IntegrityError` no cadastro não tratado (corrida TOCTOU no check de email) | Capturar `IntegrityError` e retornar 400, confiando na constraint `unique` | `backend/app/rotas/Usuarios.py` |
| `[ ]` | M3 | Magic strings `"Gerente"/"Supervisor"` em vez do enum `UsuarioFuncao` | Comparar com `UsuarioFuncao.Gerente`/`.Supervisor` | `backend/app/rotas/Chamados.py` |
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

### 📄 Documentação (divergências com o código real)

| Status | ID | Problema | Correção | Arquivo(s) |
|--------|----|----------|----------|-----------|
| `[ ]` | D1 | Divergência de enums: doc cita `AutorTipo: Humano/IA/Sistema` mas código usa `Cliente/Supervisor/Funcionario/IA/Sistema` | Padronizar doc com o código (ou vice-versa, definir fonte de verdade) | `plano-implementacao.md`, `tecnico-backend.md` |
| `[ ]` | D2 | Datas inconsistentes no `changelog.md` (mistura 2025/2026) | Padronizar para o calendário correto | `docs/changelog.md` |
| `[ ]` | D3 | Texto espúrio "oi" e "atualização em tempo real" enganoso | Remover "oi"; ajustar texto para "pull-to-refresh" | `docs/visao-geral.md` |
| `[ ]` | D4 | `tecnico-backend.md` documenta `uvicorn app.main:app` que falha pelos imports (resolver junto de C1/C2) | Atualizar comando de execução após corrigir imports | `docs/tecnico-backend.md` |

---

## Fase 1 — Chat (base do produto)

> Desbloqueia o produto inteiro. Implementar antes de qualquer outra fase.

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Rotas de mensagens: `GET /chamados/{id}/mensagens` e `POST /chamados/{id}/mensagens` | `backend/app/rotas/Mensagens.py` (novo) |
| `[ ]` | Schemas Pydantic: `MensagemCriar` e `MensagemSaida` | `backend/app/rotas/Mensagens.py` |
| `[ ]` | Registrar router `/mensagens` no `main.py` | `backend/app/main.py` |
| `[ ]` | WebSocket por chamado: `GET /ws/chamados/{id}` — broadcast para participantes | `backend/app/rotas/WebSocket.py` (novo) |
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

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Página `/painel` redirecionada para `/painel/visao-geral` | `frontend/web/src/app/(painel)/page.tsx` |
| `[ ]` | Página `visao-geral` — cards de KPIs (abertos, SLA em risco, 1ª resposta, resolução) | `frontend/web/src/app/(painel)/visao-geral/page.tsx` (novo) |
| `[ ]` | Seção "Desempenho por supervisor" — tabela com nome, abertos, 1ª resposta, estado (vermelho/verde) | (dentro de visao-geral) |
| `[ ]` | Seção "Volume por categoria" — Limpeza, Portaria, Jardinagem, Serviço extra, Reclamação | (dentro de visao-geral) |
| `[ ]` | Página `supervisores` — cards clicáveis; clique expande a fila daquele supervisor | `frontend/web/src/app/(painel)/supervisores/page.tsx` (novo) |
| `[ ]` | Página `tickets` — tabela completa com filtros: período, supervisor, status, categoria; busca por cliente | `frontend/web/src/app/(painel)/tickets/page.tsx` (novo) |
| `[ ]` | Adicionar links no sidebar: Visão geral / Supervisores / Todos os tickets / Alertas | `frontend/web/src/app/(painel)/layout.tsx` |

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
| `[ ]` | Serviço `ia_detectar_oportunidade(mensagem)` — detecta intenção de serviço extra | `backend/app/servicos/ia.py` |
| `[ ]` | Se oportunidade detectada: criar alerta comercial (campo `AlertaComercial` no Chamado ou tabela separada) | `backend/app/modelos/` |

---

## Fase 6 — Alertas comerciais e propostas

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `Proposta`: campos ChamadoID, Titulo, Escopo, Prazo, Valor, Status (Rascunho/Enviada/Aprovada/Recusada) | `backend/app/modelos/Proposta.py` (novo) |
| `[ ]` | `GET /propostas/alertas` — oportunidades detectadas aguardando proposta | `backend/app/rotas/Propostas.py` (novo) |
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

## Fase 7 — Condomínios e multi-tenant

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `Condominio`: nome, endereço, CNPJ | `backend/app/modelos/Condominio.py` (novo) |
| `[ ]` | Adicionar `CondominioID` em `Usuario` e `Chamado` | `backend/app/modelos/Usuarios.py`, `Chamados.py` |
| `[ ]` | Filtros de listagem respeitam `CondominioID` do usuário logado | `backend/app/rotas/Chamados.py` |
| `[ ]` | Rotas de gestão de condomínios (CRUD básico para o Gerente) | `backend/app/rotas/Condominios.py` (novo) |

### Frontend Web

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Página `cadastros` — listar/criar usuários e condomínios (só visível para Gerente) | `frontend/web/src/app/(painel)/cadastros/page.tsx` (novo) |

---

## Fase 8 — MVP 02: Visitas Técnicas

> Entidade separada do Chamado. Proativa (supervisor → cliente), não reativa.

### Backend

| Status | Item | Arquivo(s) |
|--------|------|-----------|
| `[ ]` | Modelo `VisitaTecnica`: SupervisorID, CondominioID, DataHoraAgendada, HoraChegada, HoraSaida, Duracao, Notas, Status (Agendada/EmAndamento/Finalizada/RelatorioEnviado) | `backend/app/modelos/VisitaTecnica.py` (novo) |
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
| `[ ]` | Adicionar "Visitas técnicas" no sidebar (visível para Gerente e Supervisor) | `frontend/web/src/app/(painel)/layout.tsx` |

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

Perfis de usuário:    Cliente | Supervisor | Funcionario | Gerente
Filas de chamado:     Operacional | RH | Financeiro | Comercial
Status de chamado:    Recebido | EmAndamento | Agendado | Concluido | Cancelado
Prioridades:          Baixa | Media | Alta | Critica
Status de visita:     Agendada | EmAndamento | Finalizada | RelatorioEnviado
AutorTipo mensagem:   Humano | IA | Sistema

Regra da IA: só narra campos estruturados já definidos (status, datas, responsável).
             Nunca inventa prazos nem fala em nome de um supervisor.
```

---

*Mantido por: Claude Code — atualizar a cada sessão de desenvolvimento*
