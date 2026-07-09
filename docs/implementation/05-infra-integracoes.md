<!-- Arquivo de cabeçalho: consolida a trilha de infraestrutura e integrações, incluindo o fluxo operacional Claude -> Codex. -->
# Trilha de Infra e Integracoes

Esta trilha cobre operacao local, Docker, board, automacoes de apoio e limites do
ambiente de desenvolvimento.

## Objetivo atual

Padronizar o uso do Codex no FaciliChat sem perder as regras ja formalizadas no
`CLAUDE.md`, no `docs/plano-implementacao.md` e no material comercial em
`docs/FaciliChat-Regras/`.

## Entregas feitas nesta rodada

| ID | Status | Origem | Resumo |
|----|--------|--------|--------|
| `INF-001` | `[x]` | Claude -> Codex | Criada a pasta `.codex/` com skills/checklists equivalentes para uso por referencia |
| `INF-002` | `[x]` | Operacao Codex | Documentados limites de sandbox, rede e escrita fora do workspace |
| `INF-003` | `[x]` | ClickUp | Registrada a ausencia atual de MCP de ClickUp nesta sessao e criado lembrete manual |

## Limites reais do Codex neste ambiente

- O workspace gravavel desta sessao e `D:\ProjetoDEV\FACILICHAT`.
- Escrita fora do workspace, como instalacao global de skill/plugin, depende de permissao adicional.
- A rede e restrita; installs e consultas externas podem falhar por politica do ambiente.
- O board do ClickUp depende de uma integracao exposta ao runtime. Nesta sessao, ela nao apareceu.

## Fluxo recomendado

1. Ler `CLAUDE.md`.
2. Ler `docs/plano-implementacao.md`.
3. Usar `.codex/skills/validar-regras/SKILL.md` antes de alterar regra de negocio.
4. Usar `.codex/skills/verificar-seguranca/SKILL.md` quando a mudanca tocar auth, sessao ou RLS.
5. Rodar `.codex/scripts/diagnosticar-ambiente.ps1` quando houver duvida entre bug do projeto e limite da sessao.
6. Usar `.codex/scripts/lembrete-clickup.ps1` quando o plano for alterado e nao houver automacao do board.

## Pendencia externa

- A equivalencia completa com a rotina do Claude para ClickUp continua pendente de instalacao/autenticacao fora do repositório, porque depende de ferramenta ausente na sessao do Codex.
