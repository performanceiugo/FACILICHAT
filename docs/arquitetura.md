# FaciliChat — Arquitetura do Sistema

> Documento técnico para desenvolvedores e manutenções futuras.

---

## Visão geral da arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    CLIENTES                         │
│   Navegador Web (Admin)    Celular (iOS / Android)  │
└───────────────┬─────────────────────┬───────────────┘
                │ HTTPS               │ HTTPS
        ┌───────▼─────────┐   ┌───────▼─────────┐
        │  Next.js (Web)  │   │  Expo (Mobile)  │
        │  frontend/web/  │   │ frontend/mobile/ │
        └───────┬─────────┘   └───────┬──────────┘
                │ REST API             │ REST API
                └──────────┬───────────┘
                           │
                  ┌────────▼────────┐
                  │   FastAPI       │
                  │  backend/app/   │
                  └────────┬────────┘
                           │ SQLAlchemy async
                  ┌────────▼────────┐
                  │   PostgreSQL    │
                  │  (Docker)       │
                  └─────────────────┘
```

---

## Tecnologias utilizadas

### Backend
| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12+ | Linguagem do servidor |
| FastAPI | 0.138 | Framework web (API REST) |
| SQLAlchemy | 2.0 | ORM assíncrono (banco de dados) |
| asyncpg | 0.31 | Driver PostgreSQL assíncrono |
| Alembic | 1.18 | Migrações de banco de dados |
| python-jose | 3.5 | Geração e validação de JWT |
| pwdlib | 0.3 | Hash de senhas (argon2) |
| Anthropic SDK | 0.111 | Integração com IA da Anthropic |
| pydantic-settings | 2.14 | Configuração via variáveis de ambiente |

### Frontend Web
| Tecnologia | Versão | Função |
|---|---|---|
| Next.js | 15 | Framework React com App Router |
| React | 19 | Biblioteca de interface |
| TypeScript | 5 | Tipagem estática |
| CSS Modules | — | Estilos escopados por componente |

### Frontend Mobile
| Tecnologia | Versão | Função |
|---|---|---|
| Expo | 53 | Plataforma React Native |
| Expo Router | 4 | Navegação baseada em arquivos |
| React Native | 0.79 | Framework mobile nativo |
| expo-secure-store | 14 | Armazenamento seguro do token JWT |
| TypeScript | 5 | Tipagem estática |

### Infraestrutura
| Tecnologia | Função |
|---|---|
| Docker + Docker Compose | Banco de dados PostgreSQL em container |
| PostgreSQL 16 | Banco de dados relacional |

---

## Estrutura de pastas

```
FACILICHAT/
├── CLAUDE.md                    ← instruções para o agente de IA
├── docker-compose.yml           ← banco de dados em Docker
├── docs/                        ← documentação do projeto
│   ├── visao-geral.md
│   ├── arquitetura.md           ← este arquivo
│   ├── tecnico-backend.md
│   ├── tecnico-frontend.md
│   └── changelog.md
│
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py              ← entrada da aplicação
│       ├── configuracoes.py     ← variáveis de ambiente
│       ├── banco_dados.py       ← conexão e sessão do banco
│       ├── modelos/             ← tabelas do banco de dados
│       │   ├── Usuarios.py
│       │   ├── Chamados.py
│       │   └── Mensagens.py
│       └── rotas/               ← endpoints da API
│           ├── Autenticacao.py
│           ├── Usuarios.py
│           └── Chamados.py
│
├── frontend/
│   ├── web/                     ← painel administrativo (Next.js)
│   │   └── src/
│   │       ├── types/index.ts   ← tipos TypeScript
│   │       ├── lib/api.ts       ← cliente HTTP
│   │       ├── lib/auth.ts      ← gerenciamento de sessão
│   │       └── app/
│   │           ├── (auth)/login/
│   │           └── (painel)/chamados/
│   │
│   └── mobile/                  ← app celular (Expo)
│       ├── lib/
│       │   ├── types.ts
│       │   ├── api.ts
│       │   └── auth.ts
│       └── app/
│           ├── (auth)/login.tsx
│           └── (tabs)/
│               ├── chamados.tsx
│               └── perfil.tsx
```

---

## Fluxo de autenticação

```
1. Usuário envia email + senha → POST /autenticacao/login
2. Backend valida credenciais e retorna JWT (token)
3. Frontend armazena o token:
   - Web: localStorage do navegador
   - Mobile: expo-secure-store (armazenamento criptografado)
4. Todas as requisições seguintes enviam o token no header:
   Authorization: Bearer <token>
5. Token expira em 8 horas (configurável via JWT_EXPIRE_MINUTES)
```

---

## Variáveis de ambiente necessárias

### Backend (arquivo `backend/.env`)
```
DATABASE_URL=postgresql+asyncpg://facilichat:facilichat123@localhost:5432/facilichat_db
JWT_SECRET=sua_chave_secreta_aqui
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
```

### Frontend Web (arquivo `frontend/web/.env`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Frontend Mobile (arquivo `frontend/mobile/.env`)
```
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

---

*Última atualização: 25 de junho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
