# Trilha de Seguranca

Esta trilha consolida os itens `S1`-`S17` do levantamento de seguranca. A prioridade pratica e
reduzir risco de tenant/session leakage antes de acelerar features novas.

## Sequencia recomendada

1. Fechar os itens independentes baratos: `S17`, `S8`, `S10`, `S12`.
2. Resolver onboarding/cadastro: `S3` e `S7`.
3. Corrigir sessao web: `S6`, `B6`, `S14`, `S15`.
4. Endurecer infraestrutura: `S4`, `S9`, `S11`.

## Itens

| Novo ID | Status | CU | Origem | Resumo | Dependencias |
|---------|--------|----|--------|--------|--------------|
| `SEC-001` | `[x]` | `868kaa34a` | `S1` | Corrigir vulnerabilidades `next`/`postcss` reportadas por audit | Nenhuma |
| `SEC-002` | `[x]` | `868kaa359` | `S2` | Aplicar tenant/RLS nas rotas normais | Nenhuma |
| `SEC-003` | `[x]` | `868kaa363` | `S3` | Impedir cadastro publico escolhendo qualquer `EmpresaID` | Correcao interina aplicada; convite/onboarding definitivo segue como evolucao futura |
| `SEC-004` | `[ ]` | `868kaa36v` | `S4` | Remover credenciais fixas do Postgres do compose | Politica de `.env`/secrets |
| `SEC-005` | `[x]` | `868kaa37j` | `S5` | Prender Postgres em `127.0.0.1` no dev | Nenhuma |
| `SEC-006` | `[ ]` | `868kaa382` | `S6` | Migrar web para cookie backend `HttpOnly; Secure; SameSite=Lax` com CSRF | `S17`; prepara `S15` |
| `SEC-007` | `[~]` | `868kaa3ax` | `S7` | Rate limit, respostas uniformes e hash dummy em login/signup | Parcial: rate limit em memoria, hash dummy e resposta neutra feitos; falta producao multi-replica/convite |
| `SEC-008` | `[ ]` | `868kaa3c6` | `S8` | Proteger/desabilitar `/docs`, `/redoc`, `/openapi.json` em prod | Config por ambiente |
| `SEC-009` | `[ ]` | `868kaa3cg` | `S9` | Separar compose dev/prod sem reload/bind mount em producao | `S4` recomendado |
| `SEC-010` | `[ ]` | `868kaa3ct` | `S10` | Impedir seed demo com senha padrao em producao | Config/flag dev |
| `SEC-011` | `[ ]` | `868kaa3dh` | `S11` | Versionar lockfile mobile e auditar dependencias | Escolha de package manager |
| `SEC-012` | `[~]` | `868kaa3dz` | `S12` | Automatizar auditoria Python (`pip-audit`) | CI/docs |
| `SEC-013` | `[x]` | `868ka61e5` | `S13` | Documentar `JWT_SECRET` por ambiente | Nenhuma |
| `SEC-014` | `[ ]` | `868kahv64` | `S14` | Revogacao server-side de sessao/logout com `jti` ou token version | `B6` |
| `SEC-015` | `[ ]` | `868kahv6r` | `S15` | Access token curto + refresh token rotativo | `S6`, `S14` |
| `SEC-016` | `[x]` | `868kahv8b` | `S16` | CSP e headers de seguranca no web | Nenhuma |
| `SEC-017` | `[ ]` | `868kahvad` | `S17` | Endurecer CORS e religar credentials apenas com CSRF | `S6` para credentials |

## Criterios de aceite da trilha

- Risco e comportamento documentados no `changelog.md`.
- Build/test/audit executado quando aplicavel.
- Rotas multi-tenant validadas com usuario de outra Empresa quando o item tocar dados.
- Configuracoes de producao documentadas sem gravar segredo no repositorio.
