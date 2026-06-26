# FaciliChat — Histórico de Alterações

> Registro de tudo que foi desenvolvido ou alterado no sistema, em ordem cronológica.
> Atualizado automaticamente a cada alteração pelo agente Claude Code.

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
