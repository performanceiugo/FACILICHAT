# Visao Geral da Implementacao por Trilhas

## Objetivo

O plano antigo nasceu por fases. Essa organizacao por trilhas facilita a execucao diaria:
seguranca, backend, web, mobile, infra, QA, bugs e documentacao podem andar com donos claros,
sem perder o vinculo com ClickUp nem com as fases originais.

## Ordem recomendada

1. Seguranca critica e sessao: concluir `S3`, `S4`, `S6`, `S7`, `S8`, `S9`, `S10`, `S11`, `S12`, `S14`, `S15`, `S17`.
2. Backend base do produto: chat, mensagens, tickets, detalhes, fila e relatorios.
3. Frontend Web e Mobile em paralelo, sempre apos contrato de API minimamente estavel.
4. Catalogo, IA e guardrails, porque dependem de dados por Empresa e regras cadastradas.
5. Propostas, visitas, upload, push e experiencia do funcionario.
6. QA, docs e deploy em cada entrega, nao apenas no final.

## Estrutura sugerida no ClickUp

| Nivel | Sugestao |
|-------|----------|
| Lista | Uma lista por trilha ou uma lista unica com campo `Trilha` |
| Tarefa-pai | Epic funcional ou grupo tecnico |
| Subtarefa | Item implementavel com `CU:` |
| Campos | `Trilha`, `Fase antiga`, `Area`, `Risco`, `Dependencias`, `Ambiente validado` |

## Regras de aceite globais

- Todo item deve manter isolamento por `EmpresaID` quando envolver dados de negocio.
- Todo schema backend alterado deve ter tipos TypeScript sincronizados quando atingir web/mobile.
- Toda tela nova deve usar tokens do design system e validar desktop/mobile quando aplicavel.
- Toda alteracao relevante deve atualizar `docs/changelog.md`.
- Todo item com `CU:` deve ser sincronizado com o status correspondente no ClickUp.

## Duplicidades e pontos de atencao

| Tema | Itens envolvidos | Decisao recomendada |
|------|------------------|---------------------|
| Condominio | `868k60veu` e `868k60wh3` | Tratar `868k60veu` como fundacao/modelagem ja feita; `868k60wh3` como CRUD/telas da Fase 7 |
| Superadmin | `868k60vkz`, `868k60vnh`, `868k60whc`, `868k60whn` | Manter fundacao em 0.7; Fase 7 fica para expandir CRUD e UX |
| Mensagens | `868k60v2g` e Fase 1 | `868k60v2g` foi saneamento; Fase 1 entrega chat completo |
| Upload/foto | Fases 1, 8 e 9 | Fase 9 entrega storage comum; Fases 1/8 consomem o storage |
| JWT `jti` | `B6` e `S14` | Implementar juntos para evitar retrabalho |

