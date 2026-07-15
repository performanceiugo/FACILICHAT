---
name: subir-projeto
description: Sobe o FaciliChat completo para análise em funcionamento (Postgres + API FastAPI via Docker, semeia o primeiro Gestor, sobe o web Next.js e abre no navegador para inspeção). Use quando o usuário pedir para "rodar", "subir", "ligar" ou "colocar o projeto no ar" para ver funcionando.
---

# Subir o FaciliChat para análise em funcionamento

Runbook determinístico para colocar o projeto no ar de ponta a ponta e validar visualmente.
Execute os passos **em ordem**. Em cada passo, se algo falhar, PARE, explique o erro ao usuário
e proponha a correção — não avance com um serviço quebrado.

Arquitetura (ver `docs/arquitetura.md`):
- **db** (Postgres 16) + **backend** (FastAPI/Uvicorn) sobem juntos via `docker-compose.yml` na raiz.
- **frontend/web** (Next.js 15) roda localmente com `npm run dev` (porta 3000).
- **frontend/mobile** (Expo) fica **fora** deste fluxo — precisa de emulador/dispositivo. Só mencione
  como opcional; não tente subir a menos que o usuário peça.

Portas: API `8000`, Web `3000`, Postgres `5432`.

---

## Passo 1 — Pré-voo (ferramentas e Docker)

1. Confirme Docker: `docker compose version`.
2. Verifique se o **daemon** está no ar: `docker ps`.
   - Se falhar com "cannot find the file"/"daemon is not running", o **Docker Desktop está fechado**.
     Tente iniciá-lo (Windows):
     `powershell -Command "Start-Process 'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'"`
     e então aguarde em loop até `docker ps` responder (pode levar 30–90s). Faça polling curto
     (rode `docker ps` a cada ~5s, até ~24 tentativas). Se não subir, PARE e peça ao usuário para
     abrir o Docker Desktop manualmente.
3. Confirme Node para o web: `node --version` (precisa existir).

## Passo 2 — Variáveis de ambiente

1. **Backend** — `backend/.env` deve existir (já existe no repo). Leia e verifique
   `ANTHROPIC_API_KEY`: se estiver com placeholder (`sua-chave-aqui`/`sk-ant-...`), **avise** que a
   IA (detecção de intenção) não funcionará, mas o resto da aplicação sobe normalmente. Não bloqueie
   por isso. Nunca commite o `.env`.
2. **Web** — se `frontend/web/.env.local` não existir, crie-o copiando de `.env.example`
   (conteúdo: `NEXT_PUBLIC_API_URL=http://localhost:8000`). Isso aponta o front para a API local.

## Passo 3 — Subir banco + API (Docker)

Da **raiz do repositório** (`D:/ProjetoDEV/FACILICHAT`):

```
docker compose up -d --build
```

Isso sobe `facilichat_db` e `facilichat_backend`. O compose já espera o Postgres ficar saudável
(healthcheck) antes de subir a API, e o backend cria as tabelas no startup (`Base.metadata.create_all`).

Aguarde a API responder — faça polling em `http://localhost:8000/` até obter
`{"mensagem":"FaciliChat online!"}` (ex.: `curl -s http://localhost:8000/`). Se demorar,
inspecione `docker compose logs backend --tail 50`.

## Passo 4 — Semear a primeira Empresa e o primeiro Gestor (idempotente)

O sistema é multi-tenant (Fase 0.7): todo usuário pertence a uma Empresa. O cadastro público cria
apenas Cliente; perfis privilegiados exigem um gestor já autenticado. Logo, a primeira Empresa e seu
primeiro Gestor precisam ser criados fora da API, pelo script — rode-o **dentro do container** (assim
reusa as dependências já instaladas, sem depender do Python local):

```
docker compose exec backend python scripts/gerenciar_banco.py criar-empresa "Cefram Demo" 12.345.678/0001-90 "Gestor Demo" admin@facilichat.dev FaciliChat2026Demo
```

- Se retornar sucesso, guarde as credenciais para o relatório final.
- Se falhar por e-mail/CNPJ já existente (violação de unicidade), **isso é esperado** em execuções
  repetidas — significa que a Empresa/Gestor já foram semeados. Trate como sucesso e siga.

## Passo 5 — Subir o web (Next.js)

De `frontend/web`, rode o dev server **em background** (não bloqueie a sessão):

```
npm run dev
```

(Se `node_modules` não existir, rode `npm install` antes.) Aguarde a linha "Ready"/porta 3000.
Faça polling em `http://localhost:3000` até responder.

## Passo 6 — Abrir no navegador e validar

Use as ferramentas do Chrome (`mcp__claude-in-chrome__*` — carregue via ToolSearch o conjunto core
antes de usar). Faça:

1. `tabs_context_mcp` e abra uma **nova aba** (não reutilize abas do usuário).
2. Navegue para **`http://localhost:8000/docs`** (Swagger) — confirme que a API subiu e liste as
   rotas. Screenshot.
3. Navegue para **`http://localhost:3000`** — a tela de login do painel do gestor. Screenshot.
4. Faça login com `admin@facilichat.dev` / `FaciliChat2026Demo` e confirme que o painel de chamados
   carrega. Se der erro de CORS/conexão, verifique `CORS_ORIGINS` no backend e `NEXT_PUBLIC_API_URL`
   no web. Screenshot do painel autenticado.

## Passo 7 — Relatório final ao usuário

Entregue um resumo curto:
- ✅ Serviços no ar e URLs clicáveis: API `http://localhost:8000` (docs em `/docs`),
  Web `http://localhost:3000`.
- 🔑 Credenciais de acesso semeadas (Gestor Demo).
- 📋 O que você observou funcionando (login, painel, rotas) e qualquer aviso (ex.: IA sem chave).
- 🛑 Como derrubar: `docker compose down` (para db+API; use `down -v` para zerar o banco) e encerrar
  o processo do web (Ctrl+C / matar o background do `npm run dev`).

---

## Notas operacionais
- **Reexecução:** o fluxo é idempotente. Rodar de novo apenas reconecta; o seed detecta gestor já
  existente; `docker compose up -d` não duplica containers.
- **Zerar tudo:** `docker compose down -v` remove o volume `pgdata` (perde os dados do banco).
- **Logs:** `docker compose logs -f backend` para a API; a saída do `npm run dev` para o web.
- **Antes de qualquer alteração de código** durante a análise, respeite a trava do `CLAUDE.md` e a
  skill `/validar-regras`. Este runbook só **sobe** o projeto; não altera regra de negócio.
