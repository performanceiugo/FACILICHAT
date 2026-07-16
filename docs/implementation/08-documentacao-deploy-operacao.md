# Trilha Documentacao, Deploy e Operacao

Esta trilha garante que cada entrega seja operavel, verificavel e compreensivel depois.

## Documentos principais

| Documento | Papel |
|-----------|-------|
| `docs/plano-implementacao.md` | Fonte legada por fase, status e `CU:` |
| `docs/changelog.md` | Historico de alteracoes e validacoes |
| `docs/arquitetura.md` | Decisoes arquiteturais atuais |
| `docs/tecnico-backend.md` | Rotas, modelos e execucao backend |
| `docs/tecnico-frontend.md` | Web/mobile, design system e build |
| `docs/setup.md` | Setup de dev rápido (Docker, ~5 min) |
| `docs/setup-manual.md` | Setup de dev alternativo sem Docker (WSL/venv) |
| `docs/deploy-producao.md` | Runbook de produção: secrets, banco, cookies/CSRF, CSP/HSTS, checklist final (fecha com o S9) |
| `docs/visao-geral.md` | Visao de produto e estado atual |
| `docs/implementation/modelo-detalhamento-fase.md` | Padrao obrigatorio para novas fases no ClickUp e no plano |
| `docs/implementation/09-fase-08-consolidacao.md` | Especificacao completa da Fase 0.8 |
| `docs/implementation/10-fase-12-finalizacao-producao.md` | Especificacao completa da preparacao para producao |
| `docs/implementation/11-fase-08-07-cancelamento-reabertura.md` | Especificacao executavel das onze subfases do F08-07 |
| `docs/implementation/12-fase-01-chat.md` | Especificacao executavel do chat, presenca, confirmacao configuravel, SLA e interfaces |
| `docs/decisoes/ADR-001-cancelamento-reabertura-chamados.md` | Decisao aprovada de produto; nao significa codigo ja implementado |
| `docs/decisoes/ADR-002-chat-presenca-confirmacao.md` | Decisoes aprovadas da Fase 1; nao significa codigo ja implementado |

## Itens documentais

| Novo ID | Status | CU | Origem | Entrega |
|---------|--------|----|--------|---------|
| `DOC-001` | `[x]` | `868k60uzn` | Fase 0 | Docs iniciais do projeto |
| `DOC-002` | `[ ]` | `868k60vrz` | Fase 1 | Rotas de mensagens no backend |
| `DOC-003` | `[ ]` | `868k60vv2` | Fase 1 | Frontend/chat/WebSocket |
| `DOC-004` | `[ ]` | `868k60vdg` | `D1` | Enums de mensagem sincronizados |
| `DOC-005` | `[ ]` | `868k60vdm` | `D2` | Datas do changelog padronizadas |
| `DOC-006` | `[ ]` | `868k60vdp` | `D4` | Comando backend correto |
| `DOC-007` | `[ ]` | `868kaa3f2` | `D5` | `visao-geral.md` atualizado |
| `DOC-008` | `[x]` | `868kaa3fz` | `D6` | `arquitetura.md` atualizada com RLS real |
| `DOC-009` | `[ ]` | `868kaa3ga` | `D7` | Notas de arquitetura sincronizadas |
| `DOC-010` | `[ ]` | `868kaa3h4` | `D8` | Checklist de aceite do branding |
| `DOC-011` | `[ ]` | `868kd2du1` | `F08-07A` | Consolidar a decisao aprovada com a matriz final durante a implementacao; ADR/especificacao inicial ja registrados |
| `DOC-012` | `[ ]` | `868kd35pv` | `F01-L` | Manter matriz, contratos, operacao e evidencias da Fase 1 sincronizados com a implementacao/testes disparados |

## Deploy e operacao

| Novo ID | Status | Origem | Entrega |
|---------|--------|--------|---------|
| `OPS-SEC-001` | `[x]` | `S13` | Guia de `JWT_SECRET` e secrets por ambiente |
| `OPS-SEC-002` | `[x]` | `S16` | Headers, CSP e HSTS documentados |
| `OPS-SEC-003` | `[x]` | `S4`/`S9` | Compose e credenciais separados por ambiente (S4 fechado antes; S9 fechado 10/07: compose prod + Caddy + backup, runbook completo) |
| `OPS-SEC-004` | `[ ]` | `S10` | Seeds demo bloqueados em producao |
| `OPS-QA-001` | `[x]` | `S12` | Auditoria Python automatizada |

## Regra de manutencao

Toda entrega relevante deve deixar tres rastros: status no plano, entrada no changelog e criterio de
validacao executado. Se um item so mudou documentacao, nao precisa build de produto, mas precisa
validacao de links/estrutura.
