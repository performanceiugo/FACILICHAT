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
> A porta do Postgres fica exposta apenas em `127.0.0.1:5432` para ferramentas locais de desenvolvimento;
> ela não deve ficar aberta em `0.0.0.0` na rede.

### Criar o primeiro Gerente (rodando dentro do container)

```bash
docker compose exec backend python scripts/criar_gerente.py "Nome do Gestor" gestor@exemplo.com SenhaForte123
```

> 🏢 **Mudança futura (SaaS multi-tenant — Fase 0.7):** quando a fundação multi-tenant entrar, o
> primeiro acesso deixará de ser "só criar um Gerente". Passará a ser **criar uma Empresa
> (tenant) + o seu primeiro Gestor juntos** — provavelmente via `scripts/criar_empresa.py`.
> Cada Empresa terá seus próprios usuários/condomínios/chamados, isolados das demais. Detalhes
> em `docs/plano-implementacao.md` (Fase 0.7) e `docs/arquitetura.md`.

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
CADASTRO_PUBLICO_HABILITADO=false
CADASTRO_PUBLICO_EMPRESA_ID=
```

Detalhes de cada variável:

| Variável | Para que serve | Observação |
|---|---|---|
| `DATABASE_URL` | Conexão com o Postgres | Em dev, use exatamente o valor acima (bate com o `docker-compose.yml`). Mantenha o driver `+asyncpg`. |
| `JWT_SECRET` | Assina/valida os tokens de login | Gere uma chave aleatória forte (veja abaixo). **Nunca** commite. Se mudar, todos os logins caem. |
| `JWT_EXPIRE_MINUTES` | Validade do token (minutos) | Padrão 480 (8h). |
| `ANTHROPIC_API_KEY` | Funcionalidades de IA (Fase 5) | Ainda **não é usada** pelo código, mas é obrigatória para a app subir. Use um placeholder por enquanto. |
| `CORS_ORIGINS` | Quais frontends podem chamar a API pelo navegador | Lista separada por vírgula. Em produção, troque pelos domínios reais. |
| `CADASTRO_PUBLICO_HABILITADO` | Liga/desliga `POST /usuarios/` sem autenticação | Padrão seguro: `false`. Use `true` só em dev/onboarding assistido. |
| `CADASTRO_PUBLICO_EMPRESA_ID` | Empresa única autorizada a receber cadastro público | Obrigatória quando `CADASTRO_PUBLICO_HABILITADO=true`; o `EmpresaID` do payload precisa bater exatamente com este valor. |

Para gerar um `JWT_SECRET` forte (com o venv ativado):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

O backend recusa `JWT_SECRET` curto, previsível ou placeholder na inicialização. Para HS256, use
um valor aleatório com pelo menos 32 bytes por ambiente; se ele mudar, todos os tokens existentes
deixam de ser válidos e os usuários precisam entrar novamente.

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

## Passo 9 — Criar o primeiro usuário Gestor

Por segurança, o cadastro público (`POST /usuarios/`) fica **desabilitado por padrão** e, quando
habilitado em dev/onboarding assistido, **sempre cria um Cliente** apenas para a Empresa definida em
`CADASTRO_PUBLICO_EMPRESA_ID`. A criação de perfis privilegiados (`POST /usuarios/equipe`) exige um
**Gestor já autenticado**. Logo, o primeiro Gestor precisa ser criado pelo script de bootstrap (rode
uma única vez, com o backend já tendo subido ao menos uma vez para as tabelas existirem):

```bash
cd backend
python scripts/criar_empresa.py "Nome da Empresa" "00.000.000/0001-00" "Nome do Gestor" gestor@exemplo.com SenhaForte123
```

Depois disso, faça login com esse Gestor para criar os demais usuários da equipe (Supervisores,
Funcionários, RH, Financeiro e outros Gestores) via `POST /usuarios/equipe`. Para liberar cadastro
público de Clientes em dev, defina `CADASTRO_PUBLICO_HABILITADO=true` e copie o ID da Empresa criada
para `CADASTRO_PUBLICO_EMPRESA_ID`.

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

## Produção — `JWT_SECRET` e secrets por ambiente

> Guia para quando o app for publicado (staging/produção). Em dev, o `backend/.env` local já resolve.
> **Regra central: o segredo nunca entra no código nem no Git** — ele vive apenas no `.env` local
> (dev) e no cofre de variáveis do ambiente onde a API roda (produção). Colar a chave em
> `configuracoes.py` ou em qualquer arquivo versionado é vazamento: se acontecer, gere outra.

### 1. Gerar uma chave forte (uma por ambiente)

Cada ambiente (dev, staging, produção) deve ter **sua própria chave** — assim, o vazamento de uma
não compromete as outras. Qualquer um dos comandos abaixo serve; copie a saída direto para o destino:

```powershell
# PowerShell (Windows, sem dependências)
$bytes = New-Object byte[] 64
[Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
[Convert]::ToBase64String($bytes)
```

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# openssl (Linux/Mac/Git Bash)
openssl rand -base64 64
```

O backend valida na inicialização: recusa segredo com menos de 32 bytes ou igual aos placeholders
conhecidos (ver `backend/app/configuracoes.py`).

### 2. Cadastrar como secret no ambiente de produção

"Cadastrar como secret" = informar o par `JWT_SECRET=<valor>` na área de variáveis de ambiente do
lugar onde a API vai rodar. O provedor injeta a variável no processo quando a API sobe — o valor
nunca passa pelo repositório.

| Onde a API roda | Como cadastrar |
|---|---|
| **VPS próprio com Docker Compose** (DigitalOcean, Hostinger, etc.) | Via SSH, criar `backend/.env` direto no servidor com a chave de produção e restringir leitura: `chmod 600 backend/.env`. O `env_file` do compose carrega igual ao dev. |
| **Render** | Painel do serviço → aba **Environment** → *Add Environment Variable* → `JWT_SECRET` + valor → Save. |
| **Railway** | Painel do serviço → aba **Variables** → *New Variable*. |
| **Fly.io** | Terminal: `fly secrets set JWT_SECRET=<valor>` (criptografa e reinicia o app). |
| **CI (GitHub Actions)** | Repositório → **Settings → Secrets and variables → Actions → New repository secret**. No workflow, usar `${{ secrets.JWT_SECRET }}` (o GitHub mascara o valor nos logs). |

> **Docker Desktop não é provedor de produção.** Ele roda containers **na sua máquina** (dev). A
> conta Docker (Docker Hub) serve para publicar **imagens** — e imagem também não pode conter
> secret, pois quem baixa a imagem enxerga tudo que foi copiado para dentro dela. Em produção, a
> imagem roda em um servidor/provedor, e é **lá** que o secret é cadastrado.

### 3. Rotação (trocar a chave)

Trocar o `JWT_SECRET` **invalida todos os tokens já emitidos** — todos os usuários logados caem e
precisam entrar de novo. Em produção, rotacione em horário de baixo uso. Rotacione imediatamente
sempre que houver suspeita de exposição (chave commitada, colada em chat, etc.).

---

## Produção — headers de segurança, CSP e HSTS (web) · item S16

O `frontend/web/next.config.ts` envia headers de segurança em **todas** as respostas do painel:
`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`,
`Permissions-Policy` e uma **Content Security Policy em modo Report-Only**.

### 1. CSP: fase de observação (Report-Only) → enforce

Hoje a política sai no header `Content-Security-Policy-Report-Only`: o navegador **só registra**
violações no console (aba Console do DevTools, mensagens `[Report Only]`), sem bloquear nada.
Isso permite validar a política com o app real antes de ativá-la.

Passos para promover a enforce, após um período de uso sem violações legítimas:

1. Navegar pelo painel inteiro (login, chamados, plataforma) com o DevTools aberto e confirmar
   que não aparecem violações `[Report Only]` causadas pelo próprio app.
2. Em `next.config.ts`, trocar a chave `Content-Security-Policy-Report-Only` por
   `Content-Security-Policy` (mesma política).
3. Evolução futura (junto do endurecimento): substituir `'unsafe-inline'` de `script-src` por
   nonces (middleware do Next), o que exige gerar a CSP por requisição.

> A origem da API entra no `connect-src` a partir de `NEXT_PUBLIC_API_URL` — em produção,
> **defina essa variável com a URL HTTPS real da API**, senão os `fetch` do painel viram violação.

### 2. HSTS (só no proxy HTTPS de produção)

`Strict-Transport-Security` **não** é enviado pelo Next de propósito: em dev o site roda em HTTP
e HSTS gravaria no navegador uma exigência de HTTPS para `localhost`. Configure no proxy/host
TLS de produção (nginx, Caddy, Cloudflare, Vercel etc.). Exemplo (nginx, dentro do bloco TLS):

```nginx
# Começar SEM includeSubDomains/preload; adicionar depois que todos os subdomínios tiverem TLS
add_header Strict-Transport-Security "max-age=31536000" always;
```

> Referências do item S16: OWASP XSS Prevention Cheat Sheet (CSP como defesa em profundidade) e
> MDN HTTP Headers. O CORS do backend (S17) e o cookie de sessão (S6) são itens separados do plano.

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
