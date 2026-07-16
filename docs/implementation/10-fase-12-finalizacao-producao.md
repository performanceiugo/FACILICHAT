# Fase 12 - Finalizacao do desenvolvimento e preparacao para producao

**Tarefa-pai:** `CU: 868kd1jc8`  
**Status:** planejada  
**Posicao:** depois das fases funcionais, usando os resultados de escala, seguranca e regressao.

## Por que esta fase foi criada

Alguns controles sao indispensaveis para publicar, mas geram retrabalho quando mantidos durante o
primeiro desenvolvimento: migracoes incrementais de um banco descartavel, infraestrutura
compartilhada antes de existir mais de uma replica e configuracao de borda antes dos dominios finais.
A Fase 12 e o gate de transformacao do ambiente de desenvolvimento em um produto publicavel. Ela
nao recebe novas funcionalidades de negocio.

## Dependencias

- fases funcionais concluidas ou explicitamente adiadas;
- Fase 4.1 fornecendo evidencias de desempenho/escala, sem duplicar seus testes;
- Fase 0.8 concluida e suite F08-06 executada para o conjunto solicitado;
- decisao F08-07 incorporada ou formalmente adiada.
- Fase 1 concluida e topologia de WebSocket/presenca conhecida para decidir se havera mais de uma
  replica do backend.

## Itens

| ID | CU | Entrega | Motivo e aceite resumido |
|----|----|---------|--------------------------|
| F12-01 | `868kd1k6v` | Implantar Alembic e migracoes versionadas | Baseline do schema final; banco vazio e existente chegam ao `head`; SQL de RLS/grants faz parte das revisoes; fluxo deixa de depender de reset em producao. |
| F12-02 | `868kd1k7a` | Validar upgrade sem perda e papeis/RLS produtivos | Ensaio em copia representativa, credencial da API sem privilegios de bypass, backup e rollback/roll-forward provados. |
| F12-03 | `868kd1k7e` | Estado efemero compartilhado | Redis ou equivalente para rate limit e, se houver multiplas replicas, pubsub/salas/presenca WebSocket; TTL/atomicidade e politica de indisponibilidade documentadas. |
| F12-04 | `868kd1k7p` | Endurecimento de borda/configuracao | TLS/DNS, cookies/origens, CSP aplicada, segredos, exposicao de endpoints e logs validados no dominio real. |
| F12-05 | `868kd1k7w` | Backup, restauracao e recuperacao | RPO/RTO definidos; restauracao real ensaiada; integridade, versao e RLS verificadas. |
| F12-06 | `868kd1k82` | Gate final e decisao go/no-go | Regressao solicitada, smoke, observabilidade, riscos, implantacao e rollback possuem evidencias e responsaveis. |

## F12-01 - Alembic e migracoes versionadas

Configurar Alembic para a conexao do projeto, criar uma baseline coerente e estabelecer convencoes
para schema, dados, downgrade e SQL que o autogenerate nao representa. A baseline deve reconhecer
um banco existente sem recriar objetos indevidamente. Um banco vazio deve chegar ao mesmo schema
por `alembic upgrade head`.

## F12-02 - Preservacao de dados e RLS de producao

Ensaiar o upgrade sobre copia sanitizada/representativa, comparar contagens e integridade, validar
grants depois de cada revisao e executar os testes de isolamento com a credencial real da API. Os
scripts de reset/seed devem recusar producao. Definir criterios objetivos para abortar e restaurar.

## F12-03 - Estado efemero compartilhado

Substituir o contador em memoria por mecanismo atomico compartilhado antes de multiplas replicas.
Definir chaves/TTL por ambiente, protecao de identificadores, metricas e comportamento quando o
armazenamento estiver indisponivel. Trocar de replica nao pode contornar o bloqueio. Se a topologia
usar mais de uma replica do backend, o mesmo item entrega pubsub/roteamento de salas e presenca
compartilhada da Fase 1: uma mensagem e um estado online precisam chegar a conexoes em instancias
diferentes sem duplicidade. Com uma replica, documentar explicitamente que o broker de chat nao e
necessario; nao implantar complexidade sem consumidor.

## F12-04 - Borda e configuracao

Fechar apenas com os dominios reais: TLS e redirect, cookies e origens, CSP em enforcement apos
observacao, segredos rotacionaveis, CORS/hosts, endpoints administrativos/documentacao, logs e modo
nao-debug. A aprovacao exige evidencia do ambiente candidato, nao apenas valores de exemplo.

## F12-05 - Recuperacao

Definir retencao, criptografia, acesso, RPO/RTO e alertas. Restaurar de verdade em ambiente isolado,
medir o tempo e validar integridade e isolamento. Um backup nunca restaurado nao atende este item.

## F12-06 - Gate final

Consolidar, sem refazer a Fase 4.1, as evidencias de funcionalidade, seguranca, escala,
observabilidade e recuperacao. Registrar bloqueadores, riscos aceitos, responsaveis, plano de
implantacao, comunicacao e rollback. A decisao final deve ser `go` ou `no-go` explicita.

## Fora do escopo

- novas funcionalidades de Empresa/Condominio (Fase 7);
- privacidade sensivel/RH por topico (Adiados, salvo nova decisao de prioridade);
- otimizacoes ja pertencentes a Fase 4.1;
- qualquer mudanca de produto sem item e aprovacao especificos.
