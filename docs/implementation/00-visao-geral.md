# Visao Geral da Implementacao por Trilhas

## Objetivo

O plano antigo nasceu por fases. Essa organizacao por trilhas facilita a execucao diaria:
seguranca, backend, web, mobile, infra, QA, bugs e documentacao podem andar com donos claros,
sem perder o vinculo com ClickUp nem com as fases originais.

## Ordem recomendada

1. Concluir a Fase 0.8 na ordem registrada em `09-fase-08-consolidacao.md`.
2. Executar a Fase 1 na ordem de `12-fase-01-chat.md`: contrato/permissoes, dados, API,
   confirmacao, tempo real, leitura/presenca, interfaces, integracoes e QA.
3. Frontend Web e Mobile em paralelo, sempre apos contrato de API minimamente estavel.
4. Catalogo, IA e guardrails, porque dependem de dados por Empresa e regras cadastradas.
5. Propostas, visitas, upload, push e experiencia do funcionario.
6. QA e documentacao acompanham as entregas; testes/suites/builds/smoke da fase so rodam quando o
   usuario disparar explicitamente a fase/conjunto.
7. Executar a Fase 12 como preparacao final para producao, depois das fases funcionais.

## Padrao para novas fases

Toda nova fase deve seguir `modelo-detalhamento-fase.md`: contexto, evidencia, motivo da decisao,
escopo, fora de escopo com destino, dependencias, riscos, dados/migracao, validacao, aceite,
documentacao, ClickUp e decisoes abertas. A proposta deve ser apresentada na conversa antes de ser
registrada nos arquivos de planejamento ou no ClickUp.

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
| Mensagens | `868k60v2g` e Fase 1 | `868k60v2g` foi saneamento; Fase 1 entrega chat completo conforme `12-fase-01-chat.md` |
| Presenca/nao lidas | Fase 1 e Fase 12 | Fase 1 entrega uma instancia; Fase 12 revisa broker antes de multiplas replicas |
| Conclusao pelo Cliente | Fase 1/F01-E e fases de canal | `AguardandoConfirmacao`, 24/48/72 configuravel, SLA pausado e sem auto-conclusao; WhatsApp/push apenas entregam eventos |
| Upload/midia | Fases 1, 8, 9 e 11 | F01-J define Texto/Audio/Imagem/Video/Documento; Fase 9 reaudita e entrega storage/fluxos reais |
| JWT `jti` | `B6` e `S14` | Implementar juntos para evitar retrabalho |
| Banco descartavel x banco produtivo | `F08-01`, `F12-01`, `F12-02` | Reset/seed e papel restrito agora; migracao sem perda e ensaio produtivo somente na Fase 12 |
| Rate limit | `S7` e `F12-03` | Memoria atende dev/instancia unica; Redis ou equivalente antes de multi-replica |
| Cancelamento/reabertura | `F08-07A`–`K`, Fases 1.5/5/7 | Decisao aprovada; implementar na ordem, preservar historico/responsavel e aguardar disparo dos testes |
