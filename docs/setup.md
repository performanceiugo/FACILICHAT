# FaciliChat — Guia de Configuração do Ambiente

> Para desenvolvedores que vão rodar o projeto pela primeira vez.

---

## Pré-requisitos

- Windows 10/11 com WSL 2 instalado (distribuição Ubuntu recomendada)
- Docker Desktop instalado no Windows
- Git instalado no WSL

---

## Passo 1 — Habilitar Docker no WSL 2

O Docker precisa ser integrado ao WSL para funcionar no terminal Linux.

1. Abra o **Docker Desktop** no Windows
2. Vá em **Settings → Resources → WSL Integration**
3. Ative **"Enable integration with my default WSL distro"**
4. Clique em **Apply & Restart**

Verifique se funcionou no terminal WSL:

```bash
docker --version
```

---

## Passo 2 — Instalar Python no WSL

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

Verifique:

```bash
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

O terminal vai mostrar `(.venv)` no início da linha quando estiver ativo.

> Para reativar em sessões futuras, sempre rode `source .venv/bin/activate` na raiz do projeto.

---

## Passo 5 — Instalar dependências do backend

```bash
pip install -r backend/requirements.txt
```

---

## Passo 6 — Criar o arquivo `.env`

Copie o exemplo e edite com os valores reais:

```bash
cp backend/.env.example backend/.env
```

Abra `backend/.env` e preencha:

```env
DATABASE_URL=postgresql+asyncpg://facilichat:facilichat123@localhost:5432/facilichat_db
JWT_SECRET=coloque-aqui-uma-chave-aleatoria-longa
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

> A `ANTHROPIC_API_KEY` é necessária para as funcionalidades de IA. Para rodar o sistema sem IA, use qualquer valor como placeholder.

---

## Passo 7 — Subir o banco de dados

Na raiz do projeto:

```bash
docker compose up -d
```

Verifique se o container subiu:

```bash
docker ps
```

Você deve ver o container `facilichat_db` com status `Up`.

---

## Passo 8 — Configurar e rodar as migrações (Alembic)

> **Atenção:** este passo cria as tabelas no banco. Execute apenas uma vez na primeira configuração, ou quando houver novas migrações.

```bash
cd backend
alembic upgrade head
```

---

## Passo 9 — Rodar o backend

```bash
cd backend
uvicorn app.main:app --reload
```

O servidor estará disponível em:

- API: `http://localhost:8000`
- Documentação interativa (Swagger): `http://localhost:8000/docs`
- Documentação alternativa (Redoc): `http://localhost:8000/redoc`

---

## Passo 10 — Rodar o frontend web (opcional)

Abra outro terminal WSL:

```bash
cd "/mnt/d/ProjetoDEV/FACILICHAT/frontend/web"
npm install
npm run dev
```

Acesse: `http://localhost:3000`

---

## Passo 11 — Rodar o frontend mobile (opcional)

Requer Node.js instalado no WSL:

```bash
sudo apt install -y nodejs npm
```

```bash
cd "/mnt/d/ProjetoDEV/FACILICHAT/frontend/mobile"
npm install
npx expo start
```

Escaneie o QR Code com o aplicativo **Expo Go** no celular.

---

## Resumo dos comandos do dia a dia

Depois da configuração inicial, para rodar o projeto basta:

```bash
# 1. Entrar na pasta do projeto
cd "/mnt/d/ProjetoDEV/FACILICHAT"

# 2. Ativar o ambiente virtual
source .venv/bin/activate

# 3. Garantir que o banco está rodando
docker compose up -d

# 4. Rodar o backend
cd backend && uvicorn app.main:app --reload
```

---

## Solução de problemas comuns

| Problema | Causa | Solução |
|---|---|---|
| `docker: command not found` | Integração WSL não ativada | Refazer o Passo 1 |
| `No such file or directory` ao usar caminho `D:\` | Sintaxe Windows no WSL | Usar `/mnt/d/` em vez de `D:\` |
| `ModuleNotFoundError` ao rodar uvicorn | Venv não ativado | Rodar `source .venv/bin/activate` |
| Erro de conexão com banco | Container não está rodando | Rodar `docker compose up -d` |
| `ANTHROPIC_API_KEY` inválida | Placeholder no `.env` | Substituir pela chave real em `backend/.env` |

---

*Mantido por: Claude Code (agente de desenvolvimento)*
