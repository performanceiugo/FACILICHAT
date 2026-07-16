# Fase 1 - Chat, presenca e confirmacao do atendimento

**Tarefa-pai:** `868k60vny`
**Posicao:** depois da consolidacao F08 e antes da Fundacao Multicanal 1.5
**Decisao:** `docs/decisoes/ADR-002-chat-presenca-confirmacao.md`
**Status:** planejada; nenhum item deste documento equivale a implementado ou validado

## Por que a fase existe

O FaciliChat depende de uma conversa confiavel para transformar solicitacoes em registros que nao
somem. A implementacao antiga da fase descrevia arquivos, bolhas e um WebSocket, mas nao dizia como
impedir acesso entre tenants, duplicidade, perda na reconexao, autoria falsa, presenca fantasma,
mensagens infinitas, conclusao sem o Cliente ou divergencia entre web/mobile/WhatsApp.

Esta especificacao torna a fase executavel por outra sessao sem depender da conversa que a criou.

## Evidencia conferida

- `backend/app/modelos/Mensagens.py`: tabela/RLS existem, mas AutorTipo nao inclui Gestor, RH ou
  Financeiro; Anexo e generico; nao ha idempotencia, leitura ou origem.
- `backend/app/main.py`: nao registra router de mensagens/WebSocket.
- `frontend/web/src/lib/api.ts` e `frontend/mobile/lib/api.ts`: mensagens sao placeholders.
- `frontend/mobile/lib/types.ts`: Chamado diverge do backend atual.
- Design System: bolhas, sistema/IA identificaveis, digitacao, lista+thread e contador de nao lidas.
- Jornadas: confirmacao imediata, Supervisor como ponte e Cliente aprovando o fechamento.
- Apresentacao: texto, foto, video, PDF e audio precisam ter destino rastreavel.

## Resultado esperado

Ao final, um usuario autorizado abre uma conversa, recebe historico paginado, envia texto uma unica
vez mesmo com retry, acompanha mensagens em tempo real, recupera lacunas apos reconectar, ve nao
lidas/digitacao/presenca verdadeiras e conclui pelo fluxo `AguardandoConfirmacao`. Tenant, autoria,
status e SLA permanecem auditaveis. Midia possui contrato, mas so e habilitada quando a Fase 9
entregar storage seguro.

## Decisoes funcionais fechadas

### Matriz de participacao

| Perfil | Le/participa | Nao recebe por esta permissao |
|--------|---------------|--------------------------------|
| Gestor | Qualquer chamado da propria Empresa | Acesso a outro tenant ou plataforma como conteudo operacional |
| Supervisor | Todos os chamados da propria Empresa, em todas as filas | Cancelar chamados nao atribuidos, reatribuir ou administrar configuracoes de Gestor |
| RH | Chamados da fila RH | Filas Financeiro/Comercial por ser RH |
| Financeiro | Chamados da fila Financeiro | Filas RH/Comercial por ser Financeiro |
| Cliente | Chamados que originou | Chamados de outro solicitante/Condominio |
| Funcionario | Chamados que originou | Chamados de colegas |
| Superadmin | Nenhum conteudo operacional automatico | Conversas de Empresas por ser operador da plataforma |

Visualizar/participar, cancelar, reatribuir, solicitar conclusao e configurar prazos sao permissoes
separadas. O frontend nunca e a autoridade.

### Estados e composicao do chat

| Estado | Texto humano | Acao estruturada |
|--------|--------------|------------------|
| Recebido | Permitido conforme matriz | Equipe inicia atendimento |
| EmAndamento | Permitido | Supervisor/Gestor pode solicitar conclusao |
| Agendado | Permitido | Supervisor/Gestor pode solicitar conclusao |
| AguardandoConfirmacao | Permitido; texto nao decide status sozinho | Cliente confirma/recusa; responsavel pode retirar solicitacao |
| Concluido | Somente leitura | Orientar novo chamado |
| Cancelado | Somente leitura | Cliente solicitante pode reabrir pelo F08-07 |

A IA futura pode interpretar uma fala, mas mudanca de estado continua em endpoint/acao estruturada,
com confirmacao e autorizacao deterministicas.

### Janela e SLA

- Configuracao por Empresa: 1440/2880/4320 minutos por padrao.
- Validar `0 < L1 < L2 < escalonamento`; horas corridas.
- Snapshot no chamado ao entrar; alteracao vale para novas janelas.
- Sem conclusao automatica.
- SLA operacional pausa; espera do Cliente e total sao registrados.
- Recusa justificada volta a EmAndamento, mesmo responsavel e mesmo ciclo SLA.

## Contratos HTTP previstos

### Historico

```http
GET /chamados/{chamadoID}/mensagens?limite=50&antes_de=<cursor>
```

Cursor e opaco, mas deriva de `Criacao+ID`. Resposta informa `Itens` e `ProximoCursor`; o limite tem
default/maximo documentados. Nao usar offset para historico mutavel.

### Envio

```http
POST /chamados/{chamadoID}/mensagens
Content-Type: application/json
```

```json
{
  "Tipo": "Texto",
  "Conteudo": "O prestador confirmou a visita para amanha.",
  "ChaveIdempotencia": "uuid"
}
```

Servidor ignora/rejeita tentativa de escolher EmpresaID, AutorID ou AutorTipo. Nova mensagem retorna
201; repeticao idempotente retorna o mesmo recurso sem novo evento.

### Leitura/lista

```http
GET /conversas?limite=30&antes_de=<cursor>&busca=<texto>
POST /chamados/{chamadoID}/leitura
```

```json
{ "UltimaMensagemID": "uuid" }
```

Marcacao e monotonicamente crescente; nao retrocede por chamada atrasada.

### Conclusao

```http
POST /chamados/{chamadoID}/solicitar-conclusao
POST /chamados/{chamadoID}/confirmar-conclusao
POST /chamados/{chamadoID}/recusar-conclusao
POST /chamados/{chamadoID}/retirar-conclusao
```

Solicitar exige resumo; recusar exige explicacao. Confirmar/recusar aceita somente Cliente
solicitante e versao/estado atual para impedir corrida.

### Configuracao

```http
GET /configuracoes/confirmacao-chamado
PATCH /configuracoes/confirmacao-chamado
```

```json
{
  "PrimeiroLembreteMinutos": 1440,
  "SegundoLembreteMinutos": 2880,
  "EscalonamentoMinutos": 4320
}
```

Somente Gestor altera; historico registra antes/depois, autor e UTC.

## WebSocket e eventos

```http
WS /ws/chamados/{chamadoID}
```

- Web: cookie HttpOnly first-party pelo dominio do painel.
- Mobile: credencial segura suportada pelo cliente nativo; nunca query string.
- O socket distribui; mensagens persistentes entram pelo POST.

Eventos iniciais versionados:

```json
{ "Versao": 1, "Evento": "conexao.pronta", "ChamadoID": "uuid" }
```

```json
{ "Versao": 1, "Evento": "mensagem.criada", "Mensagem": {} }
```

```json
{ "Versao": 1, "Evento": "digitacao.iniciada", "UsuarioID": "uuid", "Nome": "Bruno" }
```

```json
{ "Versao": 1, "Evento": "presenca.alterada", "UsuarioID": "uuid", "Estado": "Online" }
```

Heartbeat mantem presenca; 60s sem sinal vira offline. Reconexao busca HTTP pelo cursor e deduplica
por ID. Logout/revogacao/inatividade/suspensao fecham a conexao.

## Dados previstos

Detalhes finais devem respeitar convencoes do repositorio, mas a fase precisa representar:

- `Mensagem.Tipo`: Texto/Audio/Imagem/Video/Documento.
- `Mensagem.OrigemCanal`: AppWeb/AppMobile/WhatsApp/IA/Sistema ou contrato equivalente.
- `Mensagem.ChaveIdempotencia` e indice/constraint com escopo documentado.
- autoria historica completa, inclusive Gestor/RH/Financeiro.
- cursor de leitura por Empresa+Usuario+Chamado.
- `ChamadoStatus.AguardandoConfirmacao`.
- resumo/autor/UTC da solicitacao e snapshot dos tres prazos.
- pausa/acumulado do SLA sem apagar ciclos.
- configuracao por Empresa e historico de alteracao.
- eventos/lembretes com chave idempotente e proximo disparo consultavel.

Durante o primeiro desenvolvimento, ajustar ORM/RLS/seed e recriar banco local com
`gerenciar_banco.py` quando o usuario disparar. Upgrade sem perda/Alembic pertence a Fase 12.

## Ordem e subfases

| Ordem | Subfase | CU principal | Resultado/gate |
|------:|---------|--------------|----------------|
| 1 | F01-A - Contrato/permissoes | `868kd35hy` | Matriz unica aprovada antes de rotas |
| 2 | F01-B - Persistencia/autoria | `868kd35kj` | Modelo, constraints, indices e seed coerentes |
| 3 | F01-C - API | `868k60vpu`, `868k60vq1`, `868k60vrq` | GET/POST seguros, paginados e idempotentes |
| 4 | F01-D - Recebido | `868k7vrte` | Chamado+mensagem atomicos |
| 5 | F01-E - Confirmacao/SLA | `868kd35m7` | Estado, configuracao, scheduler e SLA |
| 6 | F01-F - Tempo real | `868k60vrt` | WS autenticado, proxy, evento e reconexao |
| 7 | F01-G - Leitura/presenca | `868kd35n1` | Nao lidas, dispositivos, heartbeat e recovery |
| 8 | F01-H - Web | `868k60vtc` + CUs web | Central lista+thread acessivel |
| 9 | F01-I - Mobile | `868k60vvh` + CUs mobile | Chat resiliente em celular/rede fraca |
| 10 | F01-J - Midia | `868k7vrtu` | Contrato completo; upload segue Fase 9 |
| 11 | F01-K - Integracoes | `868kd35p0` | Contrato de produtores/consumidores |
| 12 | F01-L - QA/docs | `868kd35pv`, `868k60vrz`, `868k60vv2` | Matriz, seed, comandos e documentacao |

## F01-A - Contrato e permissoes

### Por que agora

Toda camada depende deste contrato. Sem ele, web/mobile podem esconder botoes enquanto API/WS
continuam expondo dados.

### Implementar

- helper/servico unico para obter chamado acessivel e capacidade solicitada;
- separar leitura, envio, status, cancelamento, reatribuicao e configuracao;
- aplicar EmpresaID na query e RLS;
- mensagens de erro PT e sem enumeracao entre tenants;
- casos de usuario inativo/Empresa suspensa apos F08.

### Aceite

Matriz possui cenarios positivos/negativos para sete perfis; HTTP/WS usam o mesmo helper; nenhum
payload decide papel/tenant.

## F01-B - Persistencia e autoria

### Implementar

- enum de autores completo;
- UTC obrigatorio e autoria historica preservada;
- idempotencia/indices/cursor;
- constraint humano×AutorID e tipo×conteudo;
- relacoes/cascade/restricoes revisadas sem excluir historico por engano;
- seed com cada papel e estado.

### Casos de borda

Dois envios simultaneos, mesmo timestamp, mudanca posterior de papel, retry apos timeout, mensagem
de Sistema sem usuario, IA identificada e origem externa futura.

## F01-C - API

### Implementar

- schemas e respostas acima;
- normalizacao/limites de texto;
- commit antes de broadcast;
- paginacao anterior e proximo cursor;
- chave idempotente;
- status HTTP documentado;
- cliente API web/mobile tipado nas respectivas subfases.

### Casos de borda

Cursor invalido, chamado terminal, chamado removido durante envio, usuario perde acesso entre lista e
POST, timeout depois do commit e repeticao com mesma chave/payload diferente.

## F01-D - Confirmacao Recebido

Mensagem deterministica de Sistema nao depende da IA. Criar junto do chamado na mesma transacao e
publicar depois. Texto nao promete prazo nem responsavel inexistente. Tickets irmaos preservam
GrupoOrigemID e confirmacoes rastreaveis.

## F01-E - Aguardando confirmacao

### Backend

- novo estado e transicoes exclusivas;
- resumo/explicacao com limites;
- optimistic locking/versao ou condicao atomica contra duas decisoes;
- snapshot 24/48/72 configuravel;
- scheduler consulta itens vencidos com lock/idempotencia;
- mensagens internas e eventos pos-commit;
- pausa/retomada do mesmo ciclo SLA;
- configuracao/historico somente Gestor.

### Interfaces

- Supervisor/Gestor: solicitar e retirar conclusao;
- Cliente: confirmar ou recusar com explicacao;
- Gestor: tela de configuracao que explica efeito somente futuro e ausencia de auto-conclusao;
- alerta escalado permanece ate decisao.

### Casos de borda

Cliente e Supervisor agem simultaneamente, configuracao muda durante janela, worker reinicia,
relogio UTC, dois workers pegam mesmo lembrete, Cliente responde depois do escalonamento e chamado e
reatribuido enquanto aguarda.

## F01-F - Tempo real

### Implementar

- handshake autenticado e sala Empresa+Chamado;
- protocolo versionado;
- manager de conexoes por usuario/dispositivo;
- heartbeat, backoff, cleanup e expiracao;
- proxy `/ws/*` no painel e endpoint wss da API mobile;
- fetch de recovery apos reconectar;
- nao gravar mensagem pelo socket.

### Limite assumido

Manager em memoria atende uma instancia. Antes de multiplas replicas, Fase 12 exige broker/pubsub
compartilhado e teste de desconexao/rebalanceamento.

## F01-G - Leitura, presenca e sincronizacao

- leitura monotonicamente crescente por usuario/chamado;
- contador/ultima mensagem na lista;
- mensagem propria nao lida para os demais, nunca para o remetente;
- multiplos dispositivos sincronizam;
- online enquanto ao menos uma conexao valida existir;
- 60s sem heartbeat vira offline;
- digitacao expira automaticamente e nao persiste;
- online nao significa disponibilidade; sem visto por ultimo.

## F01-H - Web

Central conforme Design System: lista+busca+badges e thread. Em tela menor, separar navegacao.
Bolhas distinguem humano/IA/Sistema, sem HTML inseguro. Estados enviando/falhou/retry usam a mesma
chave. Implementar foco, ARIA live, teclado, contraste, rolagem/paginacao e estados de rede.

## F01-I - Mobile

Atualizar tipos divergentes antes da tela. FlatList preserva posicao; toque repetido nao duplica;
background/foreground reconecta e recupera; cleanup evita setState desmontado. Interface deve ser
leve para celular simples e dados limitados. Testar depois em Android/iOS quando o usuario disparar.

## F01-J - Midia

Modelar Texto/Audio/Imagem/Video/Documento e metadados sem habilitar controles vazios. Fase 9 deve
auditar MIME/tamanho/seguranca/compressao/retencao/URLs/WhatsApp e implementar fluxo real. Fase 11
usa voz/foto simples depois desse gate.

## F01-K - Consumidores

Servico de mensagem/evento e unico. WhatsApp, IA, status, visitas e push nao gravam diretamente nem
inventam autoria. Eventos externos usam outbox/idempotencia e falha nunca desfaz o fato interno.

## F01-L - Testes e documentacao

### Dados

Seed precisa conter dois tenants, sete perfis, filas, autores, estados, timestamps coincidentes,
nao lidas, multiplos dispositivos e configuracoes default/customizada.

### Comandos a preparar

Os nomes finais devem seguir a suite F08-06; referencia esperada:

```powershell
cd backend
python -m pytest tests/fases/test_fase_01_chat.py -q
```

```powershell
cd frontend/web
npm run lint
npx tsc --noEmit
npx playwright test tests/fase-01-chat.spec.ts
```

```powershell
cd frontend/mobile
npx tsc --noEmit
npx expo export --platform android
```

Reset/seed local, quando explicitamente disparado:

```powershell
cd backend
python scripts/gerenciar_banco.py reset
python scripts/gerenciar_banco.py semear
python scripts/gerenciar_banco.py verificar-rls
```

### Regra

Preparar scripts/testes/roteiros, mas nao executar teste, suite, build, smoke, export, reset de banco
ou validacao visual por iniciativa do agente. Registrar:

`testes preparados - aguardando disparo do usuario`.

## Matriz minima de aceite

1. Tenant B nunca le evento/mensagem/presenca do A.
2. Sete perfis seguem a matriz; Supervisor amplo nao ganha cancelamento/reatribuicao indevidos.
3. Retry/concorrencia nao duplicam mensagem/lembrete.
4. Historico pagina sem salto/duplicidade.
5. Reconexao recupera lacunas; HTTP+WS aparece uma vez.
6. Presenca multi-dispositivo/timeout/logout funciona.
7. Nao lidas sincronizam entre dispositivos.
8. Recebido e atomico e nao depende da IA.
9. Cliente correto aprova/recusa; silencio nunca conclui.
10. Configuracao respeita ordem e snapshot.
11. SLA pausa/retoma mesmo ciclo e relatorio separa tempos.
12. Web/mobile possuem loading, vazio, erro, offline, retry e acessibilidade.
13. Midia nao aparece como disponivel antes da Fase 9.
14. WhatsApp/push falham sem alterar chamado.
15. Documentacao e CUs permanecem rastreaveis.

## Fora do escopo com destino

| Item | Motivo | Destino |
|------|--------|---------|
| Upload/download/scan de midia | exige storage e politicas proprias | Fase 9 `868k60wn5` |
| Triagem/narracao inteligente | IA ancorada depende de catalogos/guardrails | Fase 5/5.5 |
| WhatsApp | adaptador multicanal | Fase 1.5/MO8 `868kd2e33` |
| Push | token/permissao do dispositivo | Fase 10 `868k60wpb` |
| Privacidade por assunto sensivel | decisao futura; MVP aprovou Supervisor amplo | backlog de evolucao existente |
| Presenca multi-replica | broker so e necessario ao escalar horizontalmente | Fase 12 |
| Dias uteis/feriados | calendario empresarial nao definido | decisao futura |
| Alembic/upgrade sem perda | ambiente ainda e primeiro desenvolvimento | Fase 12 |

## Rollback e recuperacao

- Mensagem persistida e fonte da verdade; falha no broadcast e recuperada por GET.
- Evento/lembrete externo reprocessa por chave idempotente.
- Falha de scheduler nao muda estado; item devido continua consultavel.
- Falha de UI nao reverte mensagem confirmada pelo servidor.
- Mudanca de configuracao nao reescreve snapshots existentes.
- Se presenca compartilhada nao estiver pronta para replica, manter uma instancia e documentar; nao
  mostrar estado possivelmente falso em topologia nao suportada.

