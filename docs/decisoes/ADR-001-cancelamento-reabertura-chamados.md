# ADR-001 - Cancelamento e reabertura de chamados

**Status:** aprovado para implementacao  
**Data:** 16/07/2026  
**Origem:** discussao da Fase 0.8, item F08-07 (`CU: 868kd1jwx`)

## Contexto

Os materiais comerciais definiam Recebido, Em andamento, Agendado e Concluido, sem regra para uma
solicitacao que deixa de prosseguir. O codigo antecipou `Cancelado`, mas sem motivo, reabertura,
historico de transicoes, comunicacao ou efeitos completos em SLA/relatorios.

## Decisao

O FaciliChat permitira cancelamento com justificativa obrigatoria e historico permanente.

### Autorizacao para cancelar

- Gestor: qualquer chamado da propria Empresa.
- Supervisor: somente chamado cujo `SupervisorID` seja o seu.
- RH: somente chamado da fila RH.
- Financeiro: somente chamado da fila Financeiro.
- Cliente, Funcionario e Superadmin: nao cancelam.

### Transicoes

- Recebido, Em andamento ou Agendado podem mudar para Cancelado.
- Concluido nao pode ser cancelado nem reaberto; nova necessidade gera novo chamado.
- Somente o Cliente solicitante pode reabrir o proprio Cancelado.
- Reabertura exige explicacao e retorna para Recebido.
- O chamado mantem o mesmo ID, todo o historico e o Supervisor atualmente atribuido.
- Reabertura inicia novo ciclo de SLA e preserva os ciclos anteriores.

### Significado dos estados

- Concluido: o servico/solicitacao foi atendido.
- Cancelado: o atendimento foi interrompido e nao prosseguira naquele ciclo.

Um servico realizado por completo nunca deve ser narrado como Cancelado.

### Supervisor por Condominio

Cada Condominio tera um Supervisor padrao ativo da mesma Empresa. Novos chamados do Cliente ligado
ao Condominio recebem esse Supervisor. Trocar o padrao afeta somente novos chamados; abertos mudam
apenas por reatribuicao explicita do Gestor. Se nao houver padrao valido, o chamado ainda e criado,
fica sem Supervisor e gera alerta, preservando a anti-amnesia.

### Comunicacao

Todas as transicoes (Recebido, Em andamento, Agendado, Concluido, Cancelado e Reaberto) geram
mensagem interna e, quando o canal estiver configurado, comunicacao transacional por WhatsApp.
Cancelamento informa o motivo e o direito de reabrir. A IA apenas narra dados estruturados e possui
fallback deterministico. Falha externa nao desfaz a transicao.

### Testes

Agentes devem preparar os testes e comandos de cada fase, mas a execucao ocorre somente quando o
usuario disparar explicitamente a fase ou o conjunto. Ate la, o estado correto e
`testes preparados - aguardando disparo do usuario`.

## Consequencias

- Sera necessario historico append-only de status, reatribuicao e ciclos de SLA.
- Cancelar/reabrir exigira endpoints proprios; o PATCH generico nao aceitara Cancelado.
- Relatorios separarao Cancelado, Concluido e Reaberto.
- Fases 1.5, 5 e 7 recebem itens vinculados ao F08-07.
- A documentacao tecnica atual so sera alterada para “implementado” quando o codigo correspondente
  existir; este ADR registra a regra aprovada, nao conclusao tecnica.
