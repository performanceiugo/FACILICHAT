# F08-07 - Cancelamento, reabertura e continuidade do responsavel

**Tarefa principal:** `CU: 868kd1jwx`  
**Status:** planejada  
**Decisao:** `docs/decisoes/ADR-001-cancelamento-reabertura-chamados.md`

## Objetivo

Implementar cancelamento rastreavel, reabertura pelo solicitante, continuidade do responsavel,
novos ciclos de SLA e comunicacao multicanal, sem confundir Cancelado com Concluido e sem perder
nenhum pedido do Cliente.

## Estado atual verificado

- `ChamadoStatus.Cancelado` ja existe.
- `PATCH /chamados/{id}/status` hoje permite Supervisor/Gestor e considera Concluido/Cancelado
  terminais; nao exige motivo e nao permite reabertura.
- `PATCH /chamados/{id}/supervisor` ja permite ao Gestor atribuir/trocar/remover (`CU: 868kcv8dp`).
- A interface web nao oferece a reatribuicao e o cliente web nao possui o metodo da API.
- Condominio nao possui Supervisor padrao e a criacao do chamado nao atribui responsavel.
- Fase 5 ja previa narracao de status (`868k60w3e`, `868k60w3h`), mas sem o contrato detalhado.
- Fase 1.5 possuia outbound generico, mas sem notificacao transacional de status.

## Invariantes aprovados

| Tema | Regra |
|------|-------|
| Gestor | Cancela qualquer chamado da propria Empresa |
| Supervisor | Cancela somente chamado atribuido a ele |
| RH | Cancela somente fila RH |
| Financeiro | Cancela somente fila Financeiro |
| Cliente | Nao cancela; reabre somente o proprio Cancelado |
| Estados cancelaveis | Recebido, Em andamento e Agendado |
| Concluido | Nao cancela/reabre; nova necessidade gera novo chamado |
| Motivo | Obrigatorio no cancelamento e na reabertura |
| Reabertura | Volta para Recebido, mesmo ticket, mesmo responsavel atual |
| SLA | Cancelamento encerra ciclo; reabertura cria novo ciclo e preserva anteriores |
| Comunicacao | Todas as transicoes geram mensagem interna e WhatsApp quando configurado |
| Testes | Preparados pelo agente; executados somente apos comando do usuario |

## Fluxo do cancelamento

1. Usuario interno autorizado abre a acao Cancelar.
2. Interface valida presenca do motivo e informa que o Cliente podera reabrir.
3. Backend revalida papel, fila, atribuicao, tenant e estado atual.
4. Na mesma transacao, grava Cancelado, encerra ciclo SLA e adiciona historico.
5. Depois do commit, publica evento idempotente.
6. Mensagem factual e criada no chat; IA pode narrar, com fallback obrigatorio.
7. WhatsApp tenta comunicar sem bloquear/desfazer o cancelamento.
8. Cliente visualiza motivo e opcao de reabrir.

## Fluxo da reabertura

1. Cliente solicitante abre o proprio chamado Cancelado.
2. Informa por que o atendimento precisa continuar.
3. Backend confirma posse, tenant e estado Cancelado.
4. Na mesma transacao, muda para Recebido, preserva o `SupervisorID` atual, cria novo ciclo SLA e
   registra historico.
5. Equipe recebe evento/mensagem; Cliente recebe confirmacao.
6. Repeticao da requisicao nao cria outro ciclo.

## Supervisor padrao e ausencia temporaria

O cadastro do Condominio tera `SupervisorPadraoID`. Novos chamados individuais e irmaos copiam o
valor vigente. Trocar o padrao vale apenas para futuros chamados. Para ferias, consulta medica ou
afastamento temporario, o Gestor seleciona substituto no Condominio e reatribui explicitamente os
abertos necessarios; nao desativa a conta apenas por indisponibilidade.

Se o responsavel atual for reatribuido antes da reabertura, a reabertura preserva o substituto. Se
estiver inativo, o sistema nao escolhe outro silenciosamente: sinaliza ao Gestor.

## Subfases e rastreabilidade

| ID | CU | Entrega | Dependencias | Criterio de aceite central |
|----|----|---------|--------------|----------------------------|
| F08-07A | `868kd2du1` | Regras, matriz e transicoes | Decisao do usuario | Contrato unico, sem regra implicita |
| F08-07B | `868kd2dua` | Historico e ciclos de SLA | F08-07A | Status/evento atomicos, append-only, tenant/RLS |
| F08-07C | `868kd2dug` | Backend de cancelamento | A/B | Motivo obrigatorio e matriz de autorizacao completa |
| F08-07D | `868kd2dum` | Backend de reabertura | A/B/C | Cliente correto, Recebido, responsavel preservado, novo ciclo |
| F08-07E | `868kd2dut` | Interfaces internas | C | Acao/modal so para papel/estado permitido |
| F08-07F | `868kd2dvc` | Interfaces do Cliente | D | Motivo visivel e reabertura do mesmo ticket |
| F08-07G | `868kd2dw0` | Evento, IA e chat | B/C/D + Fase 5 | Mensagem factual com fallback e sem duplicidade |
| F08-07H | `868kd2dw9` | SLA e relatorios | B/C/D | Cancelado nao e Concluido; ciclos auditaveis |
| F08-07I | `868kd2dwg` | Outbox/notificacoes | B/G | Falha externa recuperavel e nao bloqueante |
| F08-07J | `868kd2dwt` | Reatribuicao no painel | Backend `868kcv8dp` | Gestor troca responsavel pela UI e registra historico |
| F08-07K | `868kd2dx0` | Testes e documentacao | A-J + itens cruzados | Matriz requisito→teste; aguarda disparo do usuario |

## F08-07A - Regras e matriz

### Escopo

- manter este ADR e matriz ator × fila × atribuicao × transicao;
- definir mensagens e erros esperados;
- distinguir estado planejado, implementado e validado;
- documentar exemplos corretos: duplicidade/erro/desnecessario podem cancelar; servico realizado
  deve concluir.

### Fora do escopo

Escolher automaticamente motivos ou permitir cancelamento por IA.

## F08-07B - Historico e ciclos

### Dados

`EmpresaID`, `ChamadoID`, status anterior/novo, autor/papel, motivo, UTC, origem, ciclo e chave
idempotente. Reatribuicao guarda Supervisor anterior/novo. Tabela tem RLS e eventos sao append-only.

### Riscos e rollback

Concorrencia pode separar status/evento; por isso a mesma transacao e obrigatoria. Em dev, schema
pode ser recriado conforme F08-01; migracao sem perda fica para F12.

## F08-07C - Cancelamento

### API

`POST /chamados/{id}/cancelar`, payload com motivo de 10–1000 caracteres. O PATCH generico deve
recusar `Cancelado` para impedir bypass.

### Seguranca

Gestor/Empresa; Supervisor/atribuicao; RH/fila; Financeiro/fila. Revalidar tudo no backend mesmo se
a UI ocultar a acao. Transicao repetida/conflitante nao gera outro evento.

## F08-07D - Reabertura

### API

`POST /chamados/{id}/reabrir`, explicacao de 10–1000 caracteres. Somente `ClienteID`; Cancelado para
Recebido; mesmo `SupervisorID`; novo ciclo SLA.

### Casos de borda

Concluido, outro Cliente, outro tenant, chamada repetida, responsavel inativo e reatribuicao entre
cancelamento/reabertura.

## F08-07E/F - Interfaces

### Internas

Modal acessivel, justificativa, aviso de comunicacao/reabertura, bloqueio durante envio, erros
403/404/409/rede sem perder texto e nenhuma opcao para papel/estado proibido.

### Cliente

Mostrar status, motivo, data e papel sem nota interna. Reabrir exige explicacao. Concluido orienta
novo chamado. Web/mobile mantem estados de carregamento, offline, erro e conflito.

## F08-07G/I - Mensagens e entrega

Evento persistido alimenta chat, WhatsApp e notificacoes futuras. A IA recebe somente campos
permitidos; nunca decide, inventa ou fala pelo Supervisor. Fallback deterministico e obrigatorio.
Outbox registra pendente/enviado/entregue/lido/falhou e retry idempotente. Nada externo roda antes
do commit nem desfaz o status.

## F08-07H - SLA e relatorios

Cancelamento fecha o ciclo, reabertura cria outro e reativa o ticket. Cancelado nao conta como
Concluido/resolvido. Relatorios separam tickets e ciclos, volumes cancelados/reabertos e taxa de
reabertura com denominador documentado.

## F08-07J - Reatribuicao

Adicionar metodo no cliente web e controle no painel do Gestor, reutilizando `868kcv8dp`. Listar
somente Supervisores ativos do tenant; permitir atribuir/trocar/remover; registrar anterior/novo e
motivo opcional. Mudanca do padrao do Condominio nunca transfere abertos automaticamente.

## Itens cruzados

### Fase 1.5 - WhatsApp

`MO8`, `CU: 868kd2e33`: enviar todas as transicoes, respeitar janela/template/opt-in, usar outbox,
registrar status externo e oferecer reabertura por botao/comando/link quando aprovado.

### Fase 5 - IA

`868k60w3e` e `868k60w3h`: narracao factual de todas as transicoes, mensagem unica e fallback.

### Fase 7 - Condominio

- `F07-SP1`, `CU: 868kd2e3h`: modelo, validacao e atribuicao automatica/fallback.
- `F07-SP2`, `CU: 868kd2e3w`: configuracao pelo Gestor e explicacao do impacto.

## Ordem de implementacao

`A → B → F07-SP1/SP2 → C → D → J → E/F → G/I → MO8 → H → K`

O WhatsApp depende da Fase 1 e da Fase 5. O F08-07 nao pode ser marcado concluido enquanto seus
itens obrigatorios e dependencias aceitas para o MVP permanecerem pendentes.

## Protocolo de testes sob comando do usuario

1. Cada subfase implementa os testes previstos e documenta o comando.
2. O agente nao executa teste, suite, smoke ou validacao visual da fase por iniciativa propria.
3. Ao terminar o codigo, registra: **testes preparados - aguardando disparo do usuario**.
4. O usuario informa a fase/conjunto a executar.
5. Somente o resultado real pode mudar o estado para validado/concluido.

## Documentacao durante a implementacao

Atualizar conforme entrega real: ADR, plano, changelog, arquitetura, visao geral, tecnico backend,
tecnico frontend e documentacao multicanal. Nunca descrever como implementado antes do codigo e do
teste disparado pelo usuario.
