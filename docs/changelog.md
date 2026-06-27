# FaciliChat — Histórico de Alterações

> Registro de tudo que foi desenvolvido ou alterado no sistema, em ordem cronológica.
> Atualizado automaticamente a cada alteração pelo agente Claude Code.

---

## [0.6.2] — 27 de junho de 2026

### Processo / governança
- **Trava de segurança de produto** — adicionada a seção "🔒 TRAVA DE SEGURANÇA — invariantes do produto" no topo do `CLAUDE.md` (lida por qualquer sessão do Claude Code no repositório). Ela define a fonte da verdade (`docs/FaciliChat-Regras/`) e os invariantes que **não podem ser alterados sem confirmação explícita do usuário**: SaaS multi-tenant (Empresa/Condomínios/Superadmin), os 7 perfis, a regra da IA (nunca inventa preço/prazo), estados do ticket, visita técnica como entidade irmã, tickets irmãos, design system fixo e o princípio anti-amnésia. Antes de qualquer mudança de funcionamento/regra, é obrigatório validar contra esses invariantes.
- **Nova skill `/validar-regras`** (`.claude/skills/validar-regras/SKILL.md`) — checklist invocável que percorre os invariantes acima e instrui a **parar e pedir confirmação** caso a mudança quebre alguma regra definida.

---

## [0.6.1] — 27 de junho de 2026

### Revisão e alinhamento com o branding
- **Revisão dos documentos comerciais** (`docs/FaciliChat-Regras/`: apresentação, personas, design system, MVP02) revelou divergências entre o código/docs e o produto definido pelo comercial. Correções de documentação:
  - **Tenant renomeado de "Administradora" para "Empresa"** em todos os docs e na memória. O termo do branding para quem compra o sistema é a **conservadora/empresa de facilities** (ex.: "Cefram"); os clientes dela são os **Condomínios**. "Administradora" no branding é um papel de cliente, então o termo anterior conflitava.
  - **Enquadramento do produto corrigido** em `visao-geral.md`: o FaciliChat é para **empresas de facilities atenderem seus clientes (condomínios)**, não para "gestão de condomínios".
  - **Perfis alinhados ao branding (7):** Cliente, Funcionário, Supervisor, **RH**, **Financeiro**, **Gestor** (não "Gerente"), **Superadmin** (Iugo Performance). Tabela de perfis da `visao-geral.md` atualizada.
- **`docs/plano-implementacao.md` — nova Fase 0.6 (Alinhamento de domínio com o branding)** com itens de migração de código: renomear `Gerente→Gestor`, adicionar `RH`/`Financeiro`/`Superadmin`, adicionar fila `Comercial`, "tickets irmãos" (uma mensagem → 2 chamados), Cliente = Condomínio/contrato, e refinos da Visita Técnica (duração derivada, `ticket_id` opcional, cliente não aprova).
- **`docs/plano-implementacao.md` reorganizado** para melhor visão: adicionado um **🗺️ Mapa das fases** (status de cada fase de relance) e o conteúdo dividido em **Parte 1 — ✅ Concluído** (Fase 0 + correções já aplicadas) e **Parte 2 — 🚧 Em desenvolvimento** (na ordem recomendada). Apenas reorganização — itens e status preservados.
- **Nota:** o código ainda usa "Gerente" e 4 perfis; as mudanças de código estão registradas como itens `[ ]` na Fase 0.6, não foram aplicadas nesta entrega (apenas documentação).

---

## [0.6.0] — 27 de junho de 2026

### Decisão de arquitetura
- **FaciliChat definido como SaaS multi-tenant** — o produto será vendido para várias **Empresas** (empresas que gerem condomínios), cada uma com dados totalmente isolados. Hierarquia: **Empresa (tenant) → Condomínios → Usuários/Chamados**. Estratégia escolhida: **banco compartilhado + coluna `EmpresaID` em todas as tabelas + Row-Level Security (RLS) no PostgreSQL + tenant no JWT**. Nenhuma mudança de código nesta entrega — apenas documentação do plano a partir de agora.

### Documentação
- **`docs/plano-implementacao.md`** — criada a **Fase 0.7 — Fundação SaaS Multi-Tenant** (prioritária, antes das features), com checklist de backend e frontend; a antiga "Fase 7 — Condomínios e multi-tenant" foi reescrita como "Gestão de Empresas e Condomínios (telas/CRUD)", dependente da 0.7; notas de arquitetura do rodapé atualizadas com o conceito de tenant/Superadmin.
- **`docs/arquitetura.md`** — nova seção "Arquitetura Multi-Tenant (SaaS)" (hierarquia, estratégia de isolamento, RLS, regra de ouro); fluxo de autenticação atualizado para incluir o `EmpresaID` no JWT.
- **`docs/tecnico-backend.md`** — nova seção "Multi-tenancy (SaaS)" com as convenções de `EmpresaID`, escopo por dependência, RLS, Superadmin e bootstrap; item adicionado em "Pendente".
- **`docs/tecnico-frontend.md`** — nova seção sobre o impacto do multi-tenant no front (tenant vem do token, exibir Empresa atual, área de Superadmin, tipos a adicionar).
- **`docs/setup.md`** — aviso de que o onboarding passará a criar Empresa + 1º Gerente juntos.
- **`docs/visao-geral.md`** — adicionado o item "Plataforma multi-empresa (SaaS)" nos próximos passos. **D3 corrigido**: removido o texto espúrio "oi", data 2025→2026 e troca de "atualização em tempo real" por "pull-to-refresh".

---

## [0.5.4] — 27 de junho de 2026

### Segurança
- **A9 — Next.js atualizado para corrigir a CVE-2025-66478** — o `npm install` da web acusou que `next@15.3.4` está afetado por uma vulnerabilidade crítica (RCE no protocolo RSC do App Router, CVSS 10.0). Atualizados `next` e `eslint-config-next` de `15.3.4` para `15.3.6` (patch da própria linha 15.3.x, mantém React 19). Dev server reiniciado e validado (`/login` e `/painel/chamados` → 200). A app nunca esteve online, então não foi necessário rotacionar segredos. Arquivo: `frontend/web/package.json`.

### Corrigido
- **C5 — Assets faltantes do mobile** — criados os arquivos `icon.png`, `splash.png` e `adaptive-icon.png` em `frontend/mobile/assets/` (1024×1024, "F" branco sobre a cor primária `#148AF5`), que o `app.json` referenciava mas não existiam — o build do Expo quebrava. As `backgroundColor` do splash e do adaptiveIcon também foram corrigidas de `#1a56db` para `#148AF5` (design system). Os placeholders podem ser substituídos pela arte final depois. Arquivos: `frontend/mobile/assets/*.png` (novos), `frontend/mobile/app.json`.

---

## [0.5.3] — 27 de junho de 2026

### Corrigido
- **C3 — Rotas `/painel/*` davam 404** — o route group `(painel)` (parênteses são omitidos da URL pelo Next.js) foi renomeado para a pasta real `painel/`. Agora as URLs `/painel/chamados` etc., que o código de navegação já usava, existem de fato. Login → painel funciona. Arquivos: `frontend/web/src/app/painel/**`.
- **C4 — `auth.ts` quebrava no SSR** — adicionada guarda `typeof window !== 'undefined'` em todos os métodos que acessam `localStorage`. O `painel/layout.tsx` passou a ler a sessão via estado (`useEffect`) e só renderiza o painel após validar a autenticação, eliminando o "flash" de conteúdo protegido (melhora parcial do A4). Arquivos: `frontend/web/src/lib/auth.ts`, `frontend/web/src/app/painel/layout.tsx`.

### Adicionado (infraestrutura)
- **Backend conteinerizado** — novos `backend/Dockerfile` (Python 3.12-slim) e `backend/.dockerignore`; o `docker-compose.yml` ganhou o serviço `backend` (com `depends_on` + healthcheck do Postgres, volume do código para hot-reload e `DATABASE_URL` apontando para o serviço `db`). Agora `docker compose up --build` sobe API + banco juntos, sem instalar Python localmente. Validado de ponta a ponta: criação do 1º Gerente, cadastro público (vira Cliente), bloqueios 403 de C6/C7 e fluxo de chamado.
- **`backend/scripts/criar_gerente.py`** — ajustado para inserir a raiz do backend no `sys.path`, permitindo rodar `python scripts/criar_gerente.py` direto (inclusive via `docker compose exec`).

---

## [0.5.2] — 27 de junho de 2026

### Segurança
- **C6 — Escalonamento de privilégio no cadastro corrigido** — `POST /usuarios/` (cadastro público) agora **sempre** cria usuário com função `Cliente`; o campo `Funcao` foi removido do schema público. A criação de perfis privilegiados passou para a nova rota protegida **`POST /usuarios/equipe`**, que exige um usuário autenticado com função `Gerente` (retorna 403 caso contrário). Arquivo: `backend/app/rotas/Usuarios.py`.
- **C7 — Autorização no `PATCH /chamados/{id}/status` (IDOR) corrigida** — alterar status agora é permitido apenas a `Supervisor` e `Gerente` (403 para os demais), impedindo que um Cliente altere chamados de qualquer um. Adicionada também regra de negócio: chamado em estado terminal (`Concluido`/`Cancelado`) não pode ser reaberto (409). Arquivo: `backend/app/rotas/Chamados.py`.

### Adicionado
- **CORS (A2)** — registrado `CORSMiddleware` em `main.py` com origens explícitas (sem `"*"` junto de credenciais), configuráveis pela nova variável `CORS_ORIGINS` (padrão: `http://localhost:3000,http://127.0.0.1:3000`). Sem isso, os frontends no navegador não conseguiam chamar a API. Arquivos: `backend/app/main.py`, `backend/app/configuracoes.py`, `backend/.env.example`.
- **`backend/scripts/criar_gerente.py` (novo)** — script de bootstrap para criar o primeiro usuário `Gerente`, necessário porque o cadastro público virou Cliente-only (C6). Uso: `python scripts/criar_gerente.py "Nome" email senha`.

### Documentação
- **`docs/setup.md` atualizado** — detalhada cada variável do `.env` (incluindo `CORS_ORIGINS` e como gerar `JWT_SECRET`); **corrigido** o passo de banco de dados, que mandava rodar `alembic upgrade head` (Alembic não está configurado) — as tabelas são criadas automaticamente no startup via `create_all`; adicionado passo para criar o primeiro Gerente.

---

## [0.5.1] — 27 de junho de 2026

### Corrigido
- **Imports do backend (C1 + C2)** — todos os imports dos 9 arquivos Python passaram a ser qualificados pelo pacote `app` (ex: `from app.banco_dados import Base`, `from app.modelos.Usuarios import Usuario`, `from app.rotas.Autenticacao import obterUsuarioAtual`). Antes usavam nomes que não correspondiam aos arquivos reais (`from BancoDados`, `from Modelos`, `from Rotas`, `from Configuracoes`), causando `ModuleNotFoundError` e impedindo a API de iniciar. Arquivos: `main.py`, `banco_dados.py`, `modelos/__init__.py`, `modelos/Usuarios.py`, `modelos/Chamados.py`, `modelos/Mensagens.py`, `rotas/Autenticacao.py`, `rotas/Usuarios.py`, `rotas/Chamados.py`.
- **`backend/app/__init__.py` (novo)** — criado o marcador de pacote Python que faltava, permitindo executar a aplicação com `uvicorn app.main:app` a partir de `backend/` (conforme já documentado em `tecnico-backend.md`).

---

## [0.5.0] — 27 de junho de 2026

### Adicionado
- **`docs/plano-implementacao.md` — Fase 0.5 (Correções prioritárias)** — incorporado ao backlog o levantamento técnico completo realizado em 27/06/2026 (análise de backend, frontend web, mobile e documentação). A nova seção lista os problemas encontrados como itens rastreáveis e numerados por ID (C1–C7 críticos, A1–A8 altos, M1–M11 médios, B1–B6 baixos, D1–D4 de documentação), ordenados por severidade. Os críticos vêm primeiro porque, no estado atual, o app não sobe (imports do backend quebrados) nem navega (rotas `/painel/*` em 404). A correção será conduzida um item por vez.

### Configuração
- **`.claude/settings.json` (novo)** — definido o modelo padrão do projeto como Sonnet 4.6 (`"model": "sonnet"`), adequado a tarefas de rotina; a troca para Opus passa a ser feita manualmente por sessão quando necessário.

---

## [0.4.0] — 26 de junho de 2026

### Adicionado
- **`docs/plano-implementacao.md`** — backlog completo de desenvolvimento organizado em 10 fases (Fase 0 a Fase 10), com status rastreável por item (`[ ]` na fila, `[~]` em andamento, `[x]` concluído). Inclui os tokens de design system, regras de negócio e notas de arquitetura para consulta rápida durante o desenvolvimento.
- **`CLAUDE.md` atualizado** — adicionadas regras obrigatórias: (1) verificar `plano-implementacao.md` antes de qualquer implementação para evitar duplicações; (2) todo bloco de código deve ter comentário sem exceção; (3) atualizar o plano e o changelog ao concluir cada item. Adicionados também os tokens de design visual como referência permanente.

---

## [0.3.3] — 26 de junho de 2026

### Melhorado
- **Comentários em todo o código-fonte** — adicionados comentários explicativos em todos os 27 arquivos do projeto (10 Python no backend, 8 TypeScript/TSX no frontend web, 9 TypeScript/TSX no frontend mobile). Cada arquivo recebeu:
  - Comentário de cabeçalho descrevendo a responsabilidade do arquivo
  - Comentários inline em cada bloco lógico (enums, classes, funções, rotas, hooks, estados)
  - Explicações de decisões não óbvias (ex: por que `expire_on_commit=False`, por que form-urlencoded no login, diferença SecureStore vs localStorage)
  - Indicação de cores em constantes de estilo e valores de configuração

---

## [0.3.2] — 25 de junho de 2026

### Corrigido
- **`backend/.env` movido** — arquivo de configuração estava em `backend/app/.env` (local errado); movido para `backend/.env`, onde o `configuracoes.py` realmente o procura ao iniciar com `uvicorn` a partir de `backend/`
- **`frontend/mobile/lib/types.ts`** — adicionada interface `ChamadoCriar` que existia no web mas estava ausente no mobile
- **`frontend/mobile/lib/api.ts`** — tipo corrigido em `chamados.criar()` de `object` para `ChamadoCriar`; adicionado método `chamados.atualizarStatus()` em paridade com o web
- **`frontend/mobile/lib/auth.ts`** — adicionados métodos `isGerente()` e `isSupervisor()` (assíncronos, via `expo-secure-store`), em paridade com o web
- **`.gitignore`** — adicionadas entradas `node_modules/`, `.next/` e `.expo/` que estavam ausentes

---

## [0.3.1] — 25 de junho de 2025

### Adicionado
- **`docs/setup.md`** — guia completo de configuração do ambiente para novos desenvolvedores (WSL 2, Docker, Python venv, Alembic, frontend web e mobile, tabela de solução de problemas)

---

## [0.3.0] — 25 de junho de 2025

### Adicionado
- **Frontend Web (Next.js 15)** — estrutura inicial completa:
  - Tela de login com validação e tratamento de erro
  - Painel administrativo com sidebar de navegação
  - Listagem de chamados com cores por prioridade e status
  - Cliente HTTP com autenticação JWT automática
  - Gerenciamento de sessão via localStorage
  - Proteção de rotas (redireciona para login se não autenticado)
  - Variáveis CSS globais para identidade visual

- **Frontend Mobile (Expo + React Native)** — estrutura inicial completa:
  - Tela de login nativa (iOS e Android)
  - Redirecionamento automático baseado em autenticação
  - Lista de chamados com pull-to-refresh
  - Tela de perfil com botão de logout
  - Armazenamento seguro do token JWT via `expo-secure-store`
  - Navegação por abas com Expo Router

- **Documentação** (`docs/`):
  - `visao-geral.md` — documento para donos da empresa
  - `arquitetura.md` — estrutura técnica e tecnologias
  - `tecnico-backend.md` — backend, modelos, rotas e como rodar
  - `tecnico-frontend.md` — web e mobile, padrões e como expandir
  - `changelog.md` — este arquivo

- **`CLAUDE.md`** — instruções para o agente de IA manter a documentação atualizada a cada alteração

---

## [0.2.0] — Junho de 2025

### Adicionado
- **Backend FastAPI** — estrutura inicial completa:
  - Modelo `Usuario` com funcoes: Cliente, Supervisor, Funcionario, Gerente
  - Modelo `Chamado` com fila (Operacional/RH/Financeiro), status, prioridade e SLA
  - Modelo `Mensagem` com suporte a AutorTipo IA e Sistema (preparado para IA)
  - Rota `POST /autenticacao/login` — login com JWT
  - Rota `POST /usuarios/` — criação de usuário
  - Rota `GET /usuarios/eu` — perfil do usuário logado
  - Rota `POST /chamados/` — abertura de chamado
  - Rota `GET /chamados/` — listagem (filtro por perfil automático)
  - Rota `PATCH /chamados/{id}/status` — atualização de status
  - Configuração via variáveis de ambiente (pydantic-settings)
  - Conexão assíncrona com PostgreSQL (SQLAlchemy + asyncpg)

- **Docker Compose** — banco PostgreSQL 16 em container

---

## [0.1.0] — Junho de 2025

### Adicionado
- Estrutura inicial do repositório
- Configuração de arquivos Git (`.gitignore`, `.gitattributes`)
- Arquivo `requirements.txt` com todas as dependências do backend

---

*Mantido por: Claude Code (agente de desenvolvimento)*
