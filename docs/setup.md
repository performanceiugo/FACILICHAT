# FaciliChat — Setup de Desenvolvimento (caminho rápido)

> Para colocar o projeto rodando na sua máquina em ~5 minutos, com Docker.
>
> - Prefere rodar o Python sem Docker (WSL/venv)? → [`docs/setup-manual.md`](setup-manual.md)
> - Vai publicar em staging/produção? → [`docs/deploy-producao.md`](deploy-producao.md)

---

## Pré-requisitos

- **Docker Desktop** instalado e rodando (Windows/Mac/Linux)
- **Node.js 24** (para o frontend web) — versão travada no `.nvmrc` da raiz; se usar `nvm`, rode `nvm use` no repositório
- **Git**

> O repositório fixa as versões oficiais de desenvolvimento em arquivos de pinagem na raiz:
> `.nvmrc` (Node 24, mesma major do Docker/CI) e `.python-version` (Python 3.12, mesma versão do
> `backend/Dockerfile`). Ferramentas como `nvm`/`pyenv` os detectam automaticamente.

---

## Passo 1 — Criar os dois `.env` (uma vez)

```bash
# .env da RAIZ: credenciais do Postgres (lido pelo docker-compose.yml)
cp .env.example .env
# edite .env e defina POSTGRES_PASSWORD e APP_DB_PASSWORD aleatórias (senhas diferentes):
#   python -c "import secrets; print(secrets.token_hex(24))"

# .env do BACKEND: configuração da aplicação
cp backend/.env.example backend/.env
# edite backend/.env e gere um JWT_SECRET:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
# (ANTHROPIC_API_KEY pode ficar como placeholder — a IA ainda não é usada)
```

> **Dois papéis de banco (item F08-01):** `POSTGRES_USER`/`POSTGRES_PASSWORD` (raiz) são o papel
> **administrativo** — dono do schema, usado só por `gerenciar_banco.py` para DDL (reset, criar
> tabelas, aplicar RLS/grants). `APP_DB_USER`/`APP_DB_PASSWORD` (raiz) são o papel **restrito** que a
> própria API usa em tempo de execução — sem `SUPERUSER`/`BYPASSRLS`/posse das tabelas. O compose
> cria as duas URLs (`DATABASE_URL` e `DATABASE_URL_ADMIN`) a partir dessas variáveis; rodando fora
> do Docker, defina as duas em `backend/.env` (ver tabela abaixo).

> **Dois arquivos, papéis diferentes:** o da **raiz** guarda só as credenciais do Postgres;
> o de **`backend/`** guarda a configuração da aplicação. Ambos estão no `.gitignore`.
> Se o `.env` da raiz não existir, `docker compose up` falha dizendo qual variável falta,
> em vez de subir o banco com senha padrão.

### Variáveis do `backend/.env` (referência)

| Variável | Para que serve | Observação |
|---|---|---|
| `DATABASE_URL` | Conexão da **API** com o Postgres — papel RESTRITO (item F08-01) | Em Docker o compose monta sozinho a partir de `APP_DB_USER`/`APP_DB_PASSWORD`. Fora do Docker, aponte para o papel restrito criado por `gerenciar_banco.py reset`/`aplicar-rls` — nunca o superusuário. Manter o driver `+asyncpg`. |
| `DATABASE_URL_ADMIN` | Conexão **administrativa** usada só por `gerenciar_banco.py` (DDL) | Em Docker o compose monta sozinho a partir de `POSTGRES_USER`/`POSTGRES_PASSWORD`. Fora do Docker, use o superusuário do seu Postgres local. A API em si nunca lê esta variável em tempo de execução. |
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

# base de testes completa (idempotente): clientes/supervisor/chamados/chat na Empresa acima,
# + uma 2ª Empresa de demonstração com 3 supervisores, + o Superadmin padrão da plataforma
docker compose exec backend python scripts/gerenciar_banco.py semear

# remove os dados de demonstração acima (idempotente) — útil para rotacionar/limpar em staging
docker compose exec backend python scripts/gerenciar_banco.py limpar-demo

# se precisar de um Superadmin com credenciais customizadas (ex.: produção, com --cnpj real) em vez
# do padrão criado por `semear`. Idempotente.
docker compose exec backend python scripts/gerenciar_banco.py criar-superadmin "Superadmin Iugo" superadmin@iugo.com.br SenhaForte123

# se precisar zerar o banco de dev (dropa tudo, recria, cria/atualiza o papel restrito da API e
# aplica RLS):
docker compose exec backend python scripts/gerenciar_banco.py reset
```

> **Ambiente já existente antes do item F08-01:** se seu `.env` da raiz ainda não tem
> `APP_DB_USER`/`APP_DB_PASSWORD`, adicione-os (ver `.env.example`) e rode
> `docker compose up -d --build` seguido de `reset --semear` — o papel restrito da API só passa a
> existir depois do primeiro `reset` após esta mudança.

Depois, o Gestor cria o resto da equipe logado no painel (`POST /usuarios/equipe`).

> **Por que existe o `criar-superadmin`:** `POST /plataforma/empresas` exige um Superadmin
> autenticado, mas nada criava o primeiro — ovo e galinha. O comando cria a Empresa
> `Iugo Performance` (o schema exige que todo usuário tenha uma Empresa) e o Superadmin dentro dela.
> Ele **não promove** um usuário existente: se o e-mail já existir com outro perfil, aborta.
> Em produção, passe o CNPJ real com `--cnpj` — o padrão é um placeholder de dev. Em dev/staging,
> `semear` já chama essa mesma lógica internamente com credenciais padrão — só rode este comando à
> parte se precisar de um e-mail/senha diferente.

> **`semear` nunca roda em produção (item S10):** os usuários de demonstração nascem com a mesma
> senha padrão (`FaciliChat2026Demo`) em toda instalação — inaceitável fora de dev/staging. O comando recusa
> rodar (sai com erro, sem tocar no banco) quando `AMBIENTE=producao` no `.env` — ver
> `.env.prod.example`. Em staging, se os dados demo precisarem ser rotacionados/removidos, use
> `limpar-demo` (apaga os usuários demo e tudo que depende deles — chamados, mensagens, sessões).

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

## Auditoria de dependências Python (`pip-audit`)

As dependências do backend são auditadas de duas formas (item `S12` do plano):

- **Automática (CI):** o workflow `.github/workflows/auditoria-python.yml` roda o `pip-audit`
  contra `backend/requirements.txt` em todo push/PR que altere o arquivo **e toda segunda-feira**
  (pega CVE publicada depois do último commit). Vulnerabilidade conhecida = workflow vermelho.
- **Local (antes de mudar dependência):**

```bash
python -m pip install pip-audit          # uma vez
python -m pip_audit -r backend/requirements.txt
```

**Quando a auditoria acusar vulnerabilidade:**
1. Veja no relatório qual pacote/versão e o aviso (`PYSEC-*`/`CVE-*`) — ele indica a versão corrigida.
2. Atualize a versão fixada no `backend/requirements.txt` (ou troque o pacote, como foi feito com
   `python-jose` → `PyJWT`) e rode a auditoria de novo até ficar limpa.
3. Reconstrua o container (`docker compose up --build -d`) e valide a API.
4. Registre a correção no `docs/changelog.md`.

---

## Auditoria de dependências do mobile (`npm audit`)

O app mobile (`frontend/mobile`) tem lockfile versionado (`package-lock.json`, `lockfileVersion: 3`),
então o `npm audit` roda de forma reprodutível (item `S11` do plano):

- **Automática (CI):** o workflow `.github/workflows/auditoria-mobile.yml` roda `npm ci` + `npm audit
  --audit-level=high` em todo push/PR que altere `frontend/mobile/package.json` ou o lockfile **e
  toda segunda-feira**. O limiar ficou em **alta/crítica** — não moderada — enquanto o projeto estava
  preso ao Expo SDK 53 com 13 vulnerabilidades moderadas conhecidas; a correção exigia o bump major
  de SDK feito no item `V3` (migração sequencial 53→54→55→56→57, concluída em 15/07/2026).
- **Estado atual (pós-`V3`, SDK 57):** `npm audit` está **limpo (0 vulnerabilidades)**. A cadeia
  `uuid@7.0.3 → xcode → @expo/config-plugins` persistia mesmo no SDK 57.0.6 (mais recente
  disponível), mas foi neutralizada com `overrides.uuid: "^11.1.1"` no `package.json` — mesmo padrão
  já usado para o `postcss` no web (`S1`). Antes de aplicar o override, confirmamos que o risco real
  já era nulo: a falha do `uuid` só afeta as funções `v3/v5/v6` quando chamadas com um `buf` próprio,
  e o `xcode` só usa `uuid.v4()` sem argumentos; além disso o projeto é managed workflow (sem pastas
  `ios`/`android` nativas), então esse trecho do `xcode` nem chega a executar hoje.
- **Local (antes de mudar dependência):**

```bash
cd frontend/mobile
npm audit                 # relatório completo — hoje deve vir limpo
npm audit --audit-level=high   # mesmo filtro do CI
```

**Quando a auditoria acusar vulnerabilidade alta/crítica:**
1. Veja no relatório qual pacote/versão e o aviso (`GHSA-*`/`CVE-*`) — ele indica a versão corrigida.
2. Se a correção não exigir bump major do Expo SDK, atualize a dependência (`npx expo install --fix`
   quando for pacote do ecossistema Expo) e rode a auditoria de novo.
3. Se for uma dependência transitiva de uma ferramenta do próprio Expo (como o caso do `uuid`/`xcode`
   acima) e o `npm audit fix --force` sugerir rebaixar o `expo` para uma versão muito antiga, **não
   aceite cegamente** — investigue se a função vulnerável é realmente alcançada pelo código que a usa
   (ver exemplo acima) e considere um `overrides` específico no `package.json` antes de rebaixar
   qualquer coisa.
4. Registre a correção no `docs/changelog.md`.

---

## Solução de problemas comuns

| Problema | Causa | Solução |
|---|---|---|
| `docker compose up` falha pedindo variável | `.env` da raiz não existe | Passo 1 |
| API não sobe, erro de `JWT_SECRET` | Placeholder/chave curta no `backend/.env` | Gerar chave com o comando do Passo 1 |
| Erro de conexão com banco | Container não está rodando | `docker compose up -d` |
| Web não fala com a API (CORS/rede) | `.env.local` ausente ou URL errada | Passo 4; conferir `CORS_ORIGINS` no `backend/.env` |
| Login com contas demo falha | Banco sem seed | `gerenciar_banco.py semear` (senha demo: `FaciliChat2026Demo`) |

---

*Mantido por: Claude Code (agente de desenvolvimento)*
