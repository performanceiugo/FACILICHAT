# ADR-002 - Chat, presenca e confirmacao da conclusao

**Status:** aprovado para implementacao
**Data:** 16/07/2026
**Origem:** auditoria da Fase 1 (`CU: 868k60vny`)

## Contexto

A Fase 1 previa rotas, WebSocket e telas, mas nao definia autorizacao, sincronizacao, presenca,
leitura, idempotencia nem o fechamento aprovado pelo Cliente. As fontes de produto exigem que o
chat seja o palco, que o Cliente receba confirmacao imediata, que o Gestor tenha visao total e que
o Supervisor seja a ponte entre o solicitante e as areas internas.

## Decisoes

### Visibilidade

- Gestor le e participa de qualquer conversa da propria Empresa.
- Supervisor le e participa de todos os chamados da propria Empresa, inclusive filas RH e
  Financeiro, porque faz a ponte humana e mantem controle sobre o que entra do Cliente para a
  empresa gestora.
- RH participa da fila RH; Financeiro participa da fila Financeiro.
- Cliente e Funcionario acessam somente os chamados que originaram.
- Superadmin nao recebe acesso automatico ao conteudo operacional dos tenants.
- Ver uma conversa nao amplia permissao de cancelar, reatribuir ou concluir. As regras especificas
  de cada acao continuam valendo.
- A visibilidade sensivel pelo Supervisor e consciente no MVP. Isolamento por assunto permanece
  evolucao futura e nao pode ser ativado silenciosamente.

### Presenca

- Presenca online real faz parte da Fase 1.
- Online significa ao menos uma conexao WebSocket autenticada ativa.
- Multiplos dispositivos mantem o usuario online ate a ultima conexao encerrar.
- Heartbeat e timeout de 60 segundos removem conexao fantasma.
- Logout, token revogado, usuario inativo e Empresa suspensa encerram a presenca.
- Presenca so e exposta a quem pode acessar a conversa.
- Nao implementar "visto por ultimo" nem tratar online como promessa de disponibilidade.

### Conclusao

- Supervisor ou Gestor solicita conclusao com resumo obrigatorio.
- O chamado vai para `AguardandoConfirmacao`; nao vai direto para `Concluido`.
- Somente o Cliente solicitante confirma ou informa que o atendimento nao foi resolvido.
- Aprovacao leva a `Concluido`; recusa justificada volta a `EmAndamento`.
- O responsavel e o mesmo. A recusa retoma o mesmo ciclo SLA, sem criar reabertura.
- Nao se cancela diretamente em `AguardandoConfirmacao`; a solicitacao pode ser retirada para
  `EmAndamento`.
- O sistema nunca conclui automaticamente por silencio.

### Janela configuravel

- Cada Empresa configura, pelo Gestor, primeiro lembrete, segundo lembrete e escalonamento.
- Defaults: 1440, 2880 e 4320 minutos (24h, 48h e 72h).
- Validacao: `0 < primeiro < segundo < escalonamento`.
- Horas corridas no MVP; dias uteis/feriados exigem decisao futura.
- Ao entrar no estado, o chamado recebe um snapshot dos prazos. Alterar a configuracao afeta apenas
  novas janelas, sem mudar silenciosamente compromissos em andamento.
- Cada disparo e unico/idempotente. O alerta de escalonamento permanece visivel, sem spam infinito.

### SLA

- O SLA operacional pausa em `AguardandoConfirmacao`.
- Tempo de espera do Cliente e tempo total continuam registrados separadamente.
- Na recusa, o prazo e deslocado pela duracao da pausa e o mesmo ciclo retoma com o tempo restante.
- Na aprovacao, o ciclo fecha como concluido.

### Canais

- Chat e alerta interno pertencem a Fase 1.
- WhatsApp pertence a Fase 1.5/MO8.
- Push pertence a Fase 10.
- Falha externa nunca altera status nem desfaz SLA; outbox/idempotencia tratam retry.

## Consequencias

- `ChamadoStatus` ganha `AguardandoConfirmacao` e todas as tabelas/mapas/telas precisam reconhece-lo.
- Relatorios deixam de tratar toda espera como tempo operacional.
- Fase 1 precisa de scheduler/outbox para prazos, e de estado de leitura/presenca.
- Fases 1.5, 5, 8, 9, 10, 11 e F08-07 consomem o mesmo contrato de mensagem/evento.
- A primeira presenca pode operar em uma instancia; Fase 12 revisa broker antes de escala horizontal.

## Testes

Todos os testes serao preparados durante a implementacao e permanecerao com o registro:

`testes preparados - aguardando disparo do usuario`.

