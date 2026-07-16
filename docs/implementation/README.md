# FaciliChat - Plano por Trilhas

Este diretorio reorganiza o roadmap do FaciliChat por frente de trabalho. O arquivo
historico `docs/plano-implementacao.md` continua preservado como mapa legado por fases e
como fonte de rastreabilidade dos `CU:` do ClickUp.

## Como usar

1. Ao criar uma fase, aplique `modelo-detalhamento-fase.md` e apresente a proposta ao usuario antes
   de alterar o plano ou o ClickUp.
2. Antes de implementar, confira a trilha correspondente e o `CU:` do item.
3. Ao iniciar uma entrega, marque o item como `[~]` no plano legado e sincronize o ClickUp.
4. Ao concluir, marque como `[x]`, registre em `docs/changelog.md` e atualize a trilha se o escopo mudou.
5. Para itens que cruzam web/mobile/backend, trate a trilha como dono tecnico e crie subtarefas por area quando necessario.

## Trilhas

| Arquivo | Trilha | Uso |
|--------|--------|-----|
| `00-visao-geral.md` | Visao geral | Ordem de execucao, regras de ClickUp e criterios globais |
| `01-seguranca.md` | Seguranca | Itens `S1`-`S17` e dependencias de hardening |
| `02-backend.md` | Backend | Modelos, rotas, IA, multi-tenant, chat, tickets e relatorios |
| `03-frontend-web.md` | Frontend Web | Painel, plataforma, gestor, catalogo, propostas e ajustes web |
| `04-frontend-mobile.md` | Frontend Mobile | Cliente, supervisor, funcionario, chat, visitas e notificacoes |
| `05-infra-integracoes.md` | Infra/Integracoes | Docker, board, automacoes locais, compatibilidade Claude -> Codex e limites de ambiente |
| `06-qa-validacao.md` | QA/Testes | Validacoes manuais/automatizadas, isolamento tenant, visual e aceite |
| `07-bugs-pendencias.md` | Bugs/Ajustes | Pendencias A/M/B/D e duplicidades conhecidas |
| `08-documentacao-deploy-operacao.md` | Docs/Deploy/Operacao | Documentacao tecnica, setup, changelog, deploy e operacao |
| `09-fase-08-consolidacao.md` | Fase 0.8 | RLS/papeis, sessao, regressao sob demanda e decisao Cancelado |
| `10-fase-12-finalizacao-producao.md` | Fase 12 | Migracoes, infraestrutura e gate de preparacao para producao |
| `11-fase-08-07-cancelamento-reabertura.md` | F08-07 | Contrato e subfases de cancelamento, reabertura, SLA, IA e comunicacao |
| `12-fase-01-chat.md` | Fase 1 | Chat seguro, presenca, nao lidas, confirmacao configuravel, SLA e integracoes |
| `modelo-detalhamento-fase.md` | Padrao de planejamento | Conteudo e fluxo obrigatorios para toda nova fase |
| `migration-map.md` | Mapa antigo -> novo | Rastreabilidade por fase antiga, `CU:` e nova trilha |

## Fonte da verdade

- O `CU:` e o status operacional ainda vivem no `docs/plano-implementacao.md`.
- Estes arquivos sao a visao de execucao por trilha, para facilitar planejamento e handoff.
- O `migration-map.md` preserva a correspondencia entre as fases antigas e as trilhas novas.
