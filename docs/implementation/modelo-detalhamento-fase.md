# Padrao obrigatorio para criar novas fases

Este modelo vale para Codex, Claude e qualquer outro agente que crie ou amplie uma fase do
FaciliChat. O objetivo e permitir que uma nova sessao entenda a decisao sem depender da memoria
da conversa que originou o planejamento.

## Fluxo antes de registrar a fase

1. Conferir o codigo, o plano vigente e as fontes de produto relacionadas.
2. Apresentar a proposta completa ao usuario na conversa, antes de criar ou alterar ClickUp/planos.
3. Explicar por que a fase existe, por que entra nessa posicao e por que itens foram incluidos,
   adiados ou direcionados a outra fase.
4. Obter autorizacao explicita quando houver mudanca de escopo, prioridade, ordem, aceite ou status.
5. Criar a tarefa-pai e as subtarefas no ClickUp com tags ja existentes.
6. Registrar os `CU:` no plano canonico e nas visoes auxiliares.

## Conteudo minimo de uma fase

Cada fase deve registrar, quando aplicavel:

- **Contexto e evidencia:** o que foi observado e em quais arquivos, fluxos ou testes.
- **Problema:** comportamento atual e impacto concreto, sem presumir solucao.
- **Motivo da decisao:** por que tratar agora, adiar ou mover para outra fase.
- **Objetivo e resultado esperado:** estado verificavel ao terminar.
- **Escopo:** alteracoes funcionais e tecnicas previstas.
- **Fora do escopo e destino:** tudo que nao sera feito e o `CU:`/fase onde nao pode ser esquecido.
- **Dependencias e ordem:** pre-condicoes, itens bloqueadores e consumidores posteriores.
- **Arquivos/componentes provaveis:** pontos de impacto conhecidos, sem transformar estimativa em
  obrigacao cega.
- **Dados e migracao:** efeito em schema, dados existentes, seed, ambientes e compatibilidade.
- **Seguranca e privacidade:** tenant, autorizacao, sessao, dados sensiveis e abuso, quando houver.
- **Riscos, casos de borda e rollback:** falhas previsiveis e como recuperar.
- **Validacao:** testes automatizados/manuais, ambiente, dados e evidencias esperadas.
- **Criterios de aceite:** frases objetivas que permitam aprovar ou reprovar a entrega.
- **Documentacao:** arquivos que precisarao refletir a implementacao.
- **Rastreabilidade:** tarefa-pai, subtarefas, tags e dependencias no ClickUp.
- **Decisoes abertas:** perguntas que exigem produto/equipe e nao podem ser inventadas pelo agente.

## Regra para itens descobertos

Uma descoberta nao deve ser automaticamente transformada em codigo. Primeiro classificar como:

- correcao necessaria agora;
- decisao de produto;
- preparacao para producao;
- evolucao pos-MVP;
- item que ja pertence a outra fase.

Se for movida, a origem deve apontar para o destino. Se uma decisao ainda estiver aberta, o item
deve descrever as perguntas e opcoes sem escolher silenciosamente pela equipe.

## Regra para testes

Cada fase deve detalhar quais testes, builds, smoke checks e validacoes visuais serao necessarios e
deixar os comandos preparados. A execucao, porem, e disparada exclusivamente pelo usuario:

1. o agente implementa/atualiza os testes da subfase;
2. documenta dados, ambiente, comando e resultado esperado;
3. nao executa teste, suite, build, smoke ou validacao visual da fase por iniciativa propria;
4. registra “testes preparados - aguardando disparo do usuario”;
5. somente executa quando o usuario nomear explicitamente a fase/conjunto;
6. somente o resultado real permite registrar “validado” ou concluir o aceite dependente de teste.

Isso vale tanto para teste seletivo quanto para a suite ampla evolutiva. Uma fase nao pode ocultar
essa pendencia nem tratar teste escrito como teste aprovado.
