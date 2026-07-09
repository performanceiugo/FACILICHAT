# FaciliChat — Setup Manual (sem Docker para o backend)

> Caminho alternativo ao [`docs/setup.md`](setup.md): roda o Python direto no WSL, com venv.
> Use apenas se tiver um motivo para não usar o backend em container (ex.: depurar com breakpoints
> no processo local). O banco continua no Docker.

---

## Passo 1 — Habilitar Docker no WSL 2

O Docker precisa ser integrado ao WSL para funcionar no terminal Linux.

1. Abra o **Docker Desktop** no Windows
2. Vá em **Settings → Resources → WSL Integration**
3. Ative **"Enable integration with my default WSL distro"**
4. Clique em **Apply & Restart**

Verifique no terminal WSL:

```bash
docker --version
```

---

## Passo 2 — Instalar Python no WSL

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
python3 --version
```

---

## Passo 3 — Clonar o repositório (se ainda não tiver)

```bash
cd ~
git clone <url-do-repositorio> facilichat
cd facilichat
```

> Se já clonou no Windows, o projeto estará disponível em `/mnt/c/` ou `/mnt/d/` no WSL.
> Exemplo: `cd "/mnt/d/ProjetoDEV/FACILICHAT"`

---

## Passo 4 — Criar o ambiente virtual Python

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

O terminal mostra `(.venv)` no início da linha quando está ativo. Para reativar em sessões
futuras, rode `source .venv/bin/activate` na raiz do projeto.

---

## Passo 5 — Instalar dependências do backend

```bash
pip install -r backend/requirements.txt
```

---

## Passo 6 — Criar os arquivos `.env`

São os mesmos dois `.env` do caminho Docker — siga o **Passo 1 do `setup.md`** (lá está a tabela
com todas as variáveis). A única diferença no caminho manual: a `DATABASE_URL` do `backend/.env`
**é usada de verdade** (aponta para `localhost`) e a senha nela precisa ser a mesma
`POSTGRES_PASSWORD` do `.env` da raiz:

```env
DATABASE_URL=postgresql+asyncpg://facilichat:<a-mesma-POSTGRES_PASSWORD-do-.env-da-raiz>@localhost:5432/facilichat_db
```

---

## Passo 7 — Subir o banco de dados

Na raiz do projeto:

```bash
docker compose up -d db     # sobe só o Postgres
docker ps                   # facilichat_db deve estar "Up"
```

---

## Passo 8 — Rodar o backend (cria as tabelas automaticamente)

> **Como as tabelas são criadas hoje:** o backend executa `Base.metadata.create_all` no startup —
> as tabelas nascem sozinhas na primeira subida. **Não há Alembic** configurado; não rode
> `alembic upgrade head`. Para recriar o schema após mudança nos modelos, use
> `python scripts/gerenciar_banco.py reset` (ver `docs/tecnico-backend.md`).

```bash
cd backend
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

> Na primeira execução, observe no log a mensagem "Banco de dados conectado!".

---

## Passo 9 — Criar a primeira Empresa + Gestor

Igual ao caminho Docker, mas rodando o CLI direto (com o venv ativo, a partir de `backend/`):

```bash
python scripts/gerenciar_banco.py criar-empresa "Nome da Empresa" "00.000.000/0001-00" "Nome do Gestor" gestor@exemplo.com SenhaForte123

# opcional: dados de demonstração
python scripts/gerenciar_banco.py semear
```

---

## Passo 10 — Rodar o frontend web (opcional)

Outro terminal:

```bash
cd "/mnt/d/ProjetoDEV/FACILICHAT/frontend/web"
npm install
npm run dev
```

Acesse `http://localhost:3000`.

---

## Passo 11 — Rodar o frontend mobile (opcional)

Requer Node.js no WSL (`sudo apt install -y nodejs npm`):

```bash
cd "/mnt/d/ProjetoDEV/FACILICHAT/frontend/mobile"
npm install
npx expo start
```

Escaneie o QR Code com o aplicativo **Expo Go** no celular.

---

## Resumo dos comandos do dia a dia (caminho manual)

```bash
cd "/mnt/d/ProjetoDEV/FACILICHAT"
source .venv/bin/activate
docker compose up -d db
cd backend && uvicorn app.main:app --reload
```

---

## Solução de problemas comuns (caminho manual)

| Problema | Causa | Solução |
|---|---|---|
| `docker: command not found` | Integração WSL não ativada | Refazer o Passo 1 |
| `No such file or directory` com caminho `D:\` | Sintaxe Windows no WSL | Usar `/mnt/d/` em vez de `D:\` |
| `ModuleNotFoundError` ao rodar uvicorn | Venv não ativado | `source .venv/bin/activate` |
| Erro de autenticação no banco | Senha da `DATABASE_URL` diferente da do `.env` da raiz | Alinhar as duas (Passo 6) |

---

*Mantido por: Claude Code (agente de desenvolvimento)*
