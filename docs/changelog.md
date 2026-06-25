# FaciliChat — Histórico de Alterações

> Registro de tudo que foi desenvolvido ou alterado no sistema, em ordem cronológica.
> Atualizado automaticamente a cada alteração pelo agente Claude Code.

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
