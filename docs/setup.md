# FaciliChat — Guia de Configuração do Ambiente

> Para desenvolvedores que vão rodar o projeto pela primeira vez.

---

## Pré-requisitos

- Windows 10/11 com WSL 2 instalado (distribuição Ubuntu recomendada)
- Docker Desktop instalado no Windows
- Git instalado no WSL

---

## Opção A (recomendada) — Rodar o backend com Docker

Este é o caminho mais simples: **não precisa instalar Python nem as dependências** na sua máquina.
Sobe a API + o banco juntos, em containers. Requer apenas o **Docker Desktop** rodando.

```bash
# 1. Na raiz do projeto, criar o .env do backend (uma vez)
cp backend/.env.example backend/.env
# edite backend/.env e gere um JWT_SECRET (pode deixar ANTHROPIC_API_KEY como placeholder)

# 2. Subir API + banco (a primeira vez baixa a imagem e instala as dependências)
docker compose up --build -d

# 3. Conferir que está no ar
docker compose ps                 # backend e db devem estar "Up"
curl http://localhost:8000/        # -> {"mensagem":"FaciliChat online!"}
```

Acesse a documentação interativa em **`http://localhost:8000/docs`** (Swagger).

> **DATABASE_URL no Docker:** dentro dos containers o host do banco é `db` (não `localhost`).
> O `docker-compose.yml` já injeta a `DATABASE_URL` correta automaticamente — não precisa mexer no `.env`.

### Criar o primeiro Gerente (rodando dentro do container)

```bash
docker compose exec backend python scripts/criar_gerente.py "Nome do Gestor" gestor@exemplo.com SenhaForte123
```

### Comandos úteis do dia a dia (Docker)

```bash
docker compose up -d        # subir
docker compose logs -f backend   # acompanhar logs da API
docker compose down         # parar (mantém os dados do banco no volume)
docker compose up --build -d     # reconstruir após mudar dependências
```

> O código do backend é montado no container, então alterações em `.py` recarregam sozinhas (--reload).
> O **frontend web** (Next.js) ainda roda fora do Docker — veja os passos 10 em diante (requer Node.js).

---

## Opção B — Ambiente local manual (sem Docker para o backend)

Use esta opção se preferir rodar o Python direto no WSL.

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
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Detalhes de cada variável:

| Variável | Para que serve | Observação |
|---|---|---|
| `DATABASE_URL` | Conexão com o Postgres | Em dev, use exatamente o valor acima (bate com o `docker-compose.yml`). Mantenha o driver `+asyncpg`. |
| `JWT_SECRET` | Assina/valida os tokens de login | Gere uma chave aleatória forte (veja abaixo). **Nunca** commite. Se mudar, todos os logins caem. |
| `JWT_EXPIRE_MINUTES` | Validade do token (minutos) | Padrão 480 (8h). |
| `ANTHROPIC_API_KEY` | Funcionalidades de IA (Fase 5) | Ainda **não é usada** pelo código, mas é obrigatória para a app subir. Use um placeholder por enquanto. |
| `CORS_ORIGINS` | Quais frontends podem chamar a API pelo navegador | Lista separada por vírgula. Em produção, troque pelos domínios reais. |

Para gerar um `JWT_SECRET` forte (com o venv ativado):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

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

## Passo 8 — Rodar o backend (cria as tabelas automaticamente)

> **Como as tabelas são criadas hoje:** o backend executa `Base.metadata.create_all` no startup,
> ou seja, **as tabelas são criadas sozinhas na primeira vez que o servidor sobe**. Não há Alembic
> configurado ainda (migrações estão no backlog — `plano-implementacao.md`). Por isso **não** rode
> `alembic upgrade head`: o comando falharia, pois não existe configuração de Alembic no projeto.

```bash
cd backend
uvicorn app.main:app --reload
```

O servidor estará disponível em:

- API: `http://localhost:8000`
- Documentação interativa (Swagger): `http://localhost:8000/docs`
- Documentação alternativa (Redoc): `http://localhost:8000/redoc`

> Na primeira execução, observe no log a mensagem "Banco de dados conectado!" — sinal de que as tabelas foram criadas.

---

## Passo 9 — Criar o primeiro usuário Gerente

Por segurança, o cadastro público (`POST /usuarios/`) **sempre cria um Cliente**, e a criação de
perfis privilegiados (`POST /usuarios/equipe`) exige um **Gerente já autenticado**. Logo, o primeiro
Gerente precisa ser criado pelo script de bootstrap (rode uma única vez, com o backend já tendo subido
ao menos uma vez para as tabelas existirem):

```bash
cd backend
python scripts/criar_gerente.py "Nome do Gestor" gestor@exemplo.com SenhaForte123
```

Depois disso, faça login com esse Gerente para criar os demais usuários da equipe (Supervisores,
Funcionários e outros Gerentes) via `POST /usuarios/equipe`. Clientes podem se cadastrar sozinhos
pelo `POST /usuarios/`.

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
