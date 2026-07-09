# FaciliChat — Setup de Desenvolvimento (caminho rápido)

> Para colocar o projeto rodando na sua máquina em ~5 minutos, com Docker.
>
> - Prefere rodar o Python sem Docker (WSL/venv)? → [`docs/setup-manual.md`](setup-manual.md)
> - Vai publicar em staging/produção? → [`docs/deploy-producao.md`](deploy-producao.md)

---

## Pré-requisitos

- **Docker Desktop** instalado e rodando (Windows/Mac/Linux)
- **Node.js 20+** (para o frontend web)
- **Git**

---

## Passo 1 — Criar os dois `.env` (uma vez)

```bash
# .env da RAIZ: credenciais do Postgres (lido pelo docker-compose.yml)
cp .env.example .env
# edite .env e defina uma POSTGRES_PASSWORD aleatória:
#   python -c "import secrets; print(secrets.token_hex(24))"

# .env do BACKEND: configuração da aplicação
cp backend/.env.example backend/.env
# edite backend/.env e gere um JWT_SECRET:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
# (ANTHROPIC_API_KEY pode ficar como placeholder — a IA ainda não é usada)
```

> **Dois arquivos, papéis diferentes:** o da **raiz** guarda só as credenciais do Postgres;
> o de **`backend/`** guarda a configuração da aplicação. Ambos estão no `.gitignore`.
> Se o `.env` da raiz não existir, `docker compose up` falha dizendo qual variável falta,
> em vez de subir o banco com senha padrão.

### Variáveis do `backend/.env` (referência)

| Variável | Para que serve | Observação |
|---|---|---|
| `DATABASE_URL` | Conexão com o Postgres | Usada só quando o backend roda **fora** do Docker (o compose monta a URL sozinho). Usuário/senha/banco devem bater com o `.env` da raiz. Manter o driver `+asyncpg`. |
| `JWT_SECRET` | Assina/valida os tokens de login | Chave aleatória forte, mínimo 32 bytes — o backend recusa placeholder/curta na subida. **Nunca** commite. Se mudar, todos os logins caem. |
| `JWT_EXPIRE_MINUTES` | Validade do token (minutos) | Padrão 480 (8h). |
| `ANTHROPIC_API_KEY` | Funcionalidades de IA (Fase 5) | Ainda **não é usada**, mas é obrigatória para a app subir. Placeholder serve. |
| `CORS_ORIGINS` | Frontends autorizados a chamar a API pelo navegador | Lista separada por vírgula. O middleware CSRF também valida `Origin` contra ela. |
| `CADASTRO_PUBLICO_HABILITADO` | Liga/desliga `POST /usuarios/` sem autenticação | Padrão seguro: `false`. `true` só em dev/onboarding assistido. |
| `CADASTRO_PUBLICO_EMPRESA_ID` | Empresa única autorizada a receber cadastro público | Obrigatória quando o cadastro público está habilitado. |
| `COOKIE_SECURE` / `COOKIE_SAMESITE` / `COOKIE_DOMAIN` | Atributos do cookie de sessão do painel web | Em dev: `COOKIE_SECURE=false` (roda em http). Produção: ver `deploy-producao.md`. |
| `DEBUG` | Liga o `echo` do SQLAlchemy (loga todo SQL) | Padrão `false`. `true` só para depurar queries em dev. |

---

## Passo 2 — Subir banco + API

```bash
docker compose up --build -d

# conferir que está no ar
docker compose ps                  # backend e db devem estar "Up"
curl http://localhost:8000/        # -> {"mensagem":"FaciliChat online!"}
```

Swagger em **`http://localhost:8000/docs`**.

> Dentro dos containers o host do banco é `db` (não `localhost`) — o compose já monta a
> `DATABASE_URL` correta. A porta 5432 fica exposta só em `127.0.0.1`, para ferramentas locais.
> O código do backend é montado no container: alterações em `.py` recarregam sozinhas (`--reload`).

---

## Passo 3 — Criar a primeira Empresa + Gestor (e dados demo)

O sistema é multi-tenant: todo usuário pertence a uma Empresa, e o cadastro público fica fechado
por padrão. O bootstrap é pelo CLI do banco (ver "Scripts do banco" em `docs/tecnico-backend.md`):

```bash
docker compose exec backend python scripts/gerenciar_banco.py criar-empresa "Nome da Empresa" "12.345.678/0001-90" "Nome do Gestor" gestor@exemplo.com SenhaForte123

# opcional: clientes, chamados e chat de demonstração (idempotente)
docker compose exec backend python scripts/gerenciar_banco.py semear

# Superadmin da plataforma (Iugo) — dá acesso a /plataforma/empresas. Idempotente.
docker compose exec backend python scripts/gerenciar_banco.py criar-superadmin "Superadmin Iugo" superadmin@iugo.com.br SenhaForte123

# se precisar zerar o banco de dev (dropa tudo, recria e aplica RLS):
docker compose exec backend python scripts/gerenciar_banco.py reset
```

Depois, o Gestor cria o resto da equipe logado no painel (`POST /usuarios/equipe`).

> **Por que existe o `criar-superadmin`:** `POST /plataforma/empresas` exige um Superadmin
> autenticado, mas nada criava o primeiro — ovo e galinha. O comando cria a Empresa
> `Iugo Performance` (o schema exige que todo usuário tenha uma Empresa) e o Superadmin dentro dela.
> Ele **não promove** um usuário existente: se o e-mail já existir com outro perfil, aborta.
> Em produção, passe o CNPJ real com `--cnpj` — o padrão é um placeholder de dev.

---

## Passo 4 — Rodar o frontend web

```bash
cd frontend/web
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000 (só na primeira vez)
npm install                  # só na primeira vez
npm run dev
```

Acesse **`http://localhost:3000`**.

> **Mobile (opcional):** `cd frontend/mobile && npm install && npx expo start` e escaneie o QR Code
> com o app Expo Go. Em dispositivo físico, defina `EXPO_PUBLIC_API_URL` com o IP da sua máquina.

---

## Comandos do dia a dia

```bash
docker compose up -d               # subir banco + API
docker compose logs -f backend     # acompanhar logs da API
docker compose down                # parar (mantém os dados no volume; down -v apaga)
docker compose up --build -d       # reconstruir após mudar dependências Python
cd frontend/web && npm run dev     # web
```

> ⚠️ Não rode `npm run build` do web com o `npm run dev` ativo — os dois compartilham a pasta
> `.next/` e o build sai corrompido (detalhes em `docs/tecnico-frontend.md`).

---

## Solução de problemas comuns

| Problema | Causa | Solução |
|---|---|---|
| `docker compose up` falha pedindo variável | `.env` da raiz não existe | Passo 1 |
| API não sobe, erro de `JWT_SECRET` | Placeholder/chave curta no `backend/.env` | Gerar chave com o comando do Passo 1 |
| Erro de conexão com banco | Container não está rodando | `docker compose up -d` |
| Web não fala com a API (CORS/rede) | `.env.local` ausente ou URL errada | Passo 4; conferir `CORS_ORIGINS` no `backend/.env` |
| Login com contas demo falha | Banco sem seed | `gerenciar_banco.py semear` (senha demo: `Senha123`) |

---

*Mantido por: Claude Code (agente de desenvolvimento)*
