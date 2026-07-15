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

## Arquitetura Multi-Tenant (SaaS)

> **Decisão de 27/06/2026:** o FaciliChat é um **SaaS multi-tenant**. O produto é vendido para várias
> **Empresas** (conservadoras/facilities, ex.: "Cefram"), e cada uma enxerga **apenas os seus próprios
> dados**, isolada das demais. Os clientes de uma Empresa são os **Condomínios** que ela atende.

### Hierarquia de dados

```
Superadmin da plataforma (Iugo Performance)
   └── Empresa (TENANT)        ← a conservadora/facilities que assina o FaciliChat
          └── Condomínios       ← os clientes da Empresa (cada um com um síndico)
                 └── Usuários (Cliente/Funcionário/Supervisor/RH/Financeiro/Gestor) e Chamados
```

> Observação: o **código atual** ainda usa o perfil "Gerente" (em vez de "Gestor") e tem apenas 4
> perfis; a migração para os 7 perfis do branding está na Fase 0.6 do `plano-implementacao.md`.

### Estratégia de isolamento: banco compartilhado + `EmpresaID`

- **Um único banco** PostgreSQL para todos os tenants (mais econômico de operar nesta fase).
- **Toda tabela** tem a coluna `EmpresaID` (o "tenant_id"), FK e `NOT NULL`.
- **Toda consulta sensível a tenant** é filtrada por `EmpresaID` — implementado por uma dependência
  de sessão tenant-aware no FastAPI (`obterBancoDadosComTenant`, que extrai o tenant do JWT via
  `obterTenantAtual`) aplicada nas rotas de negócio multi-tenant.
- **Row-Level Security (RLS)** do PostgreSQL como **segunda trava** (defesa em profundidade): mesmo
  que uma query esqueça o filtro, o banco bloqueia o acesso cruzado entre tenants.
- O **tenant viaja dentro do JWT** — não é enviado pelo frontend, evitando adulteração.
- **Papéis são por tenant:** um `Gestor` é gestor *da sua* Empresa, nunca global.

> Alternativas consideradas e descartadas por ora: **schema por tenant** e **banco por tenant** —
> dão isolamento físico maior, mas custam mais e são mais complexas de migrar/manter.

### Regra de ouro

**Todo dado pertence a uma Empresa; toda leitura e escrita é escopada por ela.** Cada nova
tabela/rota deve nascer com `EmpresaID` — ver `docs/plano-implementacao.md`, Fase 0.7.

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
| PyJWT | 2.13 | Geração e validação de JWT HS256 |
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
│       │   ├── Empresa.py           ← Empresa + configuração operacional 1:1 por tenant
│       │   ├── Chamados.py
│       │   ├── CoberturaTurno.py     ← posto/turno e confirmação de responsável por tenant
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
   → o token carrega: id do usuário (sub), função e, no modelo multi-tenant,
     o EmpresaID (tenant) — usado para escopar todas as consultas
3. Frontend armazena o token:
   - Web: localStorage do navegador
   - Mobile: expo-secure-store (armazenamento criptografado)
4. Todas as requisições seguintes enviam o token no header:
   Authorization: Bearer <token>
5. O backend extrai o tenant do token e filtra os dados por Empresa
6. Token expira em 8 horas (configurável via JWT_EXPIRE_MINUTES)
```

---

## Variáveis de ambiente necessárias

### Raiz do projeto (arquivo `.env`) — credenciais do Postgres do `docker-compose.yml`
```
POSTGRES_USER=facilichat
POSTGRES_PASSWORD=<senha aleatória, uma por ambiente>
POSTGRES_DB=facilichat_db
```

### Backend (arquivo `backend/.env`)
```
DATABASE_URL=postgresql+asyncpg://facilichat:<mesma senha do .env da raiz>@localhost:5432/facilichat_db
JWT_SECRET=sua_chave_secreta_aqui
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
```

> Nenhum dos dois `.env` é versionado. O compose monta a `DATABASE_URL` dos containers a partir das
> variáveis `POSTGRES_*`, então a senha existe em um único lugar. Regras de produção em
> `docs/deploy-producao.md`.

### Frontend Web (arquivo `frontend/web/.env`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Frontend Mobile (arquivo `frontend/mobile/.env`)
```
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

---

## Checklist de aceite do branding (item D8)

> Resultado da validação dos HTMLs comerciais de `docs/FaciliChat-Regras/` convertido em critérios
> de aceite verificáveis, por eixo. Qualquer entrega nova deve continuar passando em todos os
> itens do(s) eixo(s) que ela toca — em caso de conflito, a fonte da verdade é o material do
> comercial (e a Trava de Segurança do `CLAUDE.md`).

### Eixo 1 — Design system
- [ ] Toda cor, raio, espaçamento e fonte da UI vem dos tokens (`globals.css` no web, `lib/theme.ts` no mobile) — nunca valores hardcoded
- [ ] Azul primário #148AF5, texto nas escalas Ink, Figtree como fonte, ícones de linha (Line Awesome ou equivalente inline)
- [ ] Interface discreta: hospeda a marca do cliente e nunca compete com ela
- [ ] Linguagem das telas simples e sem jargão técnico

### Eixo 2 — Anti-amnésia (tese central)
- [ ] Nada que o cliente pede se perde: toda solicitação vira registro rastreável (chamado)
- [ ] Uma mensagem pode gerar 2+ chamados (tickets irmãos via `GrupoOrigemID`) sem perder o vínculo de origem
- [ ] Histórico completo consultável (mensagens, mudanças de status, autoria — incluindo IA/Sistema)

### Eixo 3 — Multi-tenant
- [ ] Toda tabela tem `EmpresaID`; toda query é escopada por ele; RLS ativo no Postgres
- [ ] O tenant viaja no JWT; papéis valem por Empresa (não globais)
- [ ] 7 perfis: Cliente, Funcionário (único, sem subtipos), Supervisor, RH, Financeiro, Gestor, Superadmin
- [ ] Superadmin (Iugo) opera a plataforma; Empresas são criadas/suspensas só por ele

### Eixo 4 — IA ancorada (inegociável)
- [ ] A IA nunca inventa preço nem prazo; só narra campos estruturados (status, datas, responsável)
- [ ] Nunca oferece serviço fora do catálogo da Empresa; nunca responde regra de RH/Financeiro não cadastrada (encaminha)
- [ ] Nunca responde em nome de um supervisor; mensagens da IA são identificáveis (`AutorTipo.IA`)
- [ ] Decisões da IA são auditáveis (log de intenção/consulta/ação — `IaAuditoria`, Fase 5.5)

### Eixo 5 — Visita técnica (MVP02)
- [ ] Visita é entidade irmã do ticket (não um tipo de ticket)
- [ ] Proativa (supervisor→cliente), com tempo cronometrado; duração **derivada**, nunca armazenada
- [ ] O cliente não aprova a visita — só recebe/consulta a prova

### Eixo 6 — Jornadas (chat é o palco, ticket é o bastidor)
- [ ] O cliente interage por conversa; o ticket organiza o trabalho nos bastidores
- [ ] Estados do ticket no MVP: Recebido, Em andamento, Agendado, Concluído (+ Cancelado)
- [ ] Filas roteiam ao papel certo: Operacional→Supervisor, RH→RH, Financeiro→Financeiro, Comercial→Gestor
- [ ] Cliente vê só os próprios chamados; equipe vê conforme o papel

> Status em 15/07/2026: eixos 1, 2 (parcial — chat pendente), 3 e 6 (parcial — chat pendente) já
> têm implementação conferível no código; eixos 4 e 5 valem como critério de aceite para as fases
> futuras (IA nas Fases 5/5.5, visitas na Fase 8). As caixas ficam vazias de propósito: o aceite
> é reavaliado a cada entrega, não marcado uma vez.

---

*Última atualização: 15 de julho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
