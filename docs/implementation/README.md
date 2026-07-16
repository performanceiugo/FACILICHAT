# FaciliChat - Especificações Detalhadas de Implementação

Este diretório contém apenas especificações executáveis que complementam itens do
`docs/plano-implementacao.md`. O plano principal e o ClickUp são as fontes de status e de
rastreabilidade por `CU:`; nenhum arquivo deste diretório mantém uma lista paralela de pendências.

## Como usar

1. Localize o item e seu `CU:` em `docs/plano-implementacao.md`.
2. Quando houver uma especificação detalhada abaixo, leia-a antes da implementação.
3. Para criar uma fase ou subfase detalhada, aplique `modelo-detalhamento-fase.md` e siga a trava
   de autorização definida no `AGENTS.md` e no `CLAUDE.md`.
4. Mantenha status somente no plano principal e no ClickUp.

## Especificações ativas

| Arquivo | Uso |
|---------|-----|
| `09-fase-08-consolidacao.md` | Especificação completa da Fase 0.8 |
| `10-fase-12-finalizacao-producao.md` | Especificação completa da preparação para produção |
| `11-fase-08-07-cancelamento-reabertura.md` | Contrato e subfases de cancelamento, reabertura, SLA, IA e comunicação |
| `12-fase-01-chat.md` | Chat seguro, presença, não lidas, confirmação configurável, SLA e integrações |
| `modelo-detalhamento-fase.md` | Padrão obrigatório para detalhar novas fases |

## Documentos relacionados

- Regras de produto consolidadas: `docs/instrucoes-branding.md`.
- Decisões aprovadas: `docs/decisoes/`.
- Arquitetura atual: `docs/arquitetura.md`.
- Histórico de alterações: `docs/changelog.md`.
