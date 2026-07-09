# FaciliChat — Runbook de Produção

> Passo-a-passo único "do servidor vazio ao app no ar". Consolida as regras de produção que antes
> viviam espalhadas no `setup.md` (itens S3/S4/S5/S6/S13/S16/S17 do plano).
>
> ⚠️ **Documento em construção proposital:** o produto ainda está em fase de fundação (sem chat,
> IA e storage) e o item **S9** do plano — compose de produção — ainda não foi executado. As seções
> marcadas com 🔜 dependem dele. O objetivo final é o deploy caber em ~4 comandos (ver "Processo-alvo").

---

## Processo-alvo (quando o S9 fechar)

```bash
git clone <repo> && cd FACILICHAT
cp .env.prod.example .env && nano .env    # preencher os secrets (seção 2)
docker compose -f docker-compose.prod.yml up -d --build
docker compose exec backend python scripts/gerenciar_banco.py criar-empresa ...
```

## O que já está pronto vs pendente

| Área | Status |
|---|---|
| Secrets fail-fast (`JWT_SECRET`, `POSTGRES_PASSWORD` obrigatórios na subida) | ✅ |
| Cookie de sessão HttpOnly + CSRF (S6) e CORS endurecido (S17) | ✅ |
| Headers de segurança + CSP Report-Only no web (S16) | ✅ |
| Cadastro público fechado por padrão (S3) | ✅ |
| Compose de produção (sem `--reload`/bind mount, usuário endurecido) | 🔜 S9 |
| Web (Next.js) containerizado + proxy TLS com HSTS | 🔜 S9 |
| Seeds demo bloqueados em produção | 🔜 S10 |
| `/docs`/`/redoc` desabilitados em produção | 🔜 S8 |
| Revogação de sessão server-side / refresh token | 🔜 S14/S15 |

---

## 1. Infraestrutura mínima

- **Servidor/provedor** para os containers (VPS com Docker Compose, Render, Railway, Fly.io...).
- **Banco gerenciado** (RDS, Neon, Supabase, Cloud SQL) ou servidor dedicado — **nunca** o
  container de dev do compose. Regras (item S4):
  - Uma senha por ambiente (staging ≠ produção ≠ dev).
  - **Usuário da aplicação não é superusuário** — crie um papel só com DML. Isso é o que faz a
    **RLS valer para a aplicação** (superusuário e dono da tabela a ignoram).
  - Banco não exposto à internet: só a rede privada da aplicação alcança a porta 5432.
  - TLS obrigatório na conexão (`?ssl=require` ou equivalente do provedor).
- **Proxy TLS** na frente de tudo (nginx, Caddy, Cloudflare, ou o TLS do provedor) — HTTPS em
  100% do tráfego.

## 2. Secrets por ambiente

**Regra central: segredo nunca entra no código nem no Git.** Vive no cofre de variáveis do
provedor (ou num `.env` criado direto no servidor, com `chmod 600`).

Gerar uma chave forte por ambiente (dev, staging e produção têm chaves **diferentes**):

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"     # JWT_SECRET
python -c "import secrets; print(secrets.token_hex(24))"         # senha do Postgres
# PowerShell: [Convert]::ToBase64String((1..64 | % { Get-Random -Max 256 }))
# openssl:    openssl rand -base64 64
```

Onde cadastrar:

| Onde a API roda | Como cadastrar |
|---|---|
| **VPS com Docker Compose** | Criar `backend/.env` direto no servidor via SSH e `chmod 600 backend/.env`. |
| **Render** | Painel do serviço → **Environment** → *Add Environment Variable*. |
| **Railway** | Painel do serviço → **Variables** → *New Variable*. |
| **Fly.io** | `fly secrets set JWT_SECRET=<valor>`. |
| **CI (GitHub Actions)** | **Settings → Secrets and variables → Actions**; usar `${{ secrets.X }}`. |

> **Docker Desktop não é provedor de produção** — roda containers na sua máquina. E imagem Docker
> não pode conter secret: quem baixa a imagem enxerga tudo dentro dela.

**Rotação:** trocar o `JWT_SECRET` invalida todos os tokens (todos os usuários caem) — rotacione
em horário de baixo uso, e imediatamente se houver suspeita de exposição. O backend recusa chave
com menos de 32 bytes ou igual a placeholders conhecidos.

## 3. Variáveis de produção do backend

Além dos secrets, confira no ambiente da API:

| Variável | Valor em produção |
|---|---|
| `DATABASE_URL` | URL do banco gerenciado, com TLS (`?ssl=require`) |
| `CORS_ORIGINS` | Domínio(s) reais do painel — o middleware CSRF valida `Origin` contra eles |
| `COOKIE_SECURE` | `true` (default) — cookie de sessão só por HTTPS |
| `COOKIE_SAMESITE` | `lax` (default). `none` exige `Secure` e a API recusa combinação incoerente |
| `COOKIE_DOMAIN` | Vazio (host-only), a menos que o cookie precise valer para subdomínios |
| `CADASTRO_PUBLICO_HABILITADO` | `false` (default) até existir onboarding/convite |
| `DEBUG` | `false` (default) — não logar SQL em produção |
| `JWT_EXPIRE_MINUTES` | 480 hoje; encurtar quando o S15 (refresh token) entrar. O `Max-Age` do cookie acompanha automaticamente |

> **Arquitetura da sessão (S6):** o painel web autentica por cookie `HttpOnly` emitido pelo
> backend e fala com a API pelo **proxy `/api/*` do Next** — o navegador nunca chama a API
> diretamente, o que torna o cookie first-party e permite `SameSite=Lax` independentemente de onde
> a API estiver hospedada. O mobile usa `Authorization: Bearer` (SecureStore).

## 4. Web (Next.js)

- `NEXT_PUBLIC_API_URL` com a **URL HTTPS real da API** — ela entra no `connect-src` da CSP;
  se ficar errada, todo `fetch` do painel vira violação.
- Build de produção: `npm run build` + `npm start` (🔜 S9: virar serviço no compose de produção).
- **CSP:** hoje sai em `Content-Security-Policy-Report-Only` (só registra violações no console).
  Promover a enforce após período de uso sem violações legítimas:
  1. Navegar pelo painel inteiro com o DevTools aberto e confirmar zero mensagens `[Report Only]`
     causadas pelo próprio app.
  2. Em `frontend/web/next.config.ts`, renomear o header para `Content-Security-Policy`.
  3. Evolução futura: substituir `'unsafe-inline'` de `script-src` por nonces (CSP por requisição).

## 5. Proxy TLS + HSTS

`Strict-Transport-Security` **não** é enviado pelo Next de propósito (em dev gravaria exigência de
HTTPS para `localhost`). Configure no proxy TLS (exemplo nginx, dentro do bloco TLS):

```nginx
# Começar SEM includeSubDomains/preload; adicionar depois que todos os subdomínios tiverem TLS
add_header Strict-Transport-Security "max-age=31536000" always;
```

## 6. Bootstrap do banco

```bash
docker compose exec backend python scripts/gerenciar_banco.py criar-empresa "<Empresa>" <CNPJ> "<Gestor>" <email> <senha-forte>
docker compose exec backend python scripts/gerenciar_banco.py aplicar-rls   # se o schema nasceu pelo create_all, o criar-empresa já garante as tabelas
```

**Não rode `semear` em produção** — cria usuários demo com senha padrão (bloqueio automático é o
item S10). O comando `reset` **destrói o banco** — jamais em produção.

## 7. Checklist final antes de liberar usuários

- [ ] 100% do tráfego por HTTPS; HSTS ativo no proxy (seção 5).
- [ ] `COOKIE_SECURE=true` e, no navegador, `document.cookie` **não** mostra o cookie `sessao`.
- [ ] `CORS_ORIGINS` apenas com os domínios reais (sem localhost).
- [ ] `JWT_SECRET` e senha do banco próprios do ambiente, cadastrados como secret (seção 2).
- [ ] Papel do banco sem superusuário e `verificar-rls` executado com sucesso contra o banco de produção vazio.
- [ ] CSP promovida a enforce após observação (seção 4).
- [ ] Nenhum dado demo no banco (`semear` nunca rodou).
- [ ] Swagger (`/docs`) inacessível publicamente (🔜 S8; até lá, bloquear no proxy).
- [ ] Logout entendido como client-side: token roubado vale até expirar (revogação real é 🔜 S14).

---

*Mantido por: Claude Code (agente de desenvolvimento). Este runbook fecha de vez junto com o item S9 do plano.*
