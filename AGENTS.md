# Instrucoes para agentes - FaciliChat

Este arquivo vale para agentes que leem instrucoes de repositorio, incluindo Codex. As regras de
produto completas continuam em `CLAUDE.md`.

## Trava do plano de implementacao

Arquivos protegidos:

- `docs/plano-implementacao.md`
- `docs/implementation/**`

Regra obrigatoria:

- Nao altere arquivos de plano sem antes avisar o usuario em mensagem visivel.
- Se a mudanca alterar escopo, prioridade, ordem, criterio de aceite, status ou criar/remover item,
  peca confirmacao explicita antes de editar.
- Se a mudanca for apenas marcar status durante uma implementacao solicitada pelo usuario, avise
  antes da edicao e explique qual `CU:`/item sera alterado.
- Nunca reorganize, "limpe", renomeie ou compacte o plano por iniciativa propria.
- O `CU:` do ClickUp e a chave de rastreabilidade; nao remova nem substitua sem confirmacao.

Frase minima antes de editar:

```text
Vou alterar o plano agora: <arquivo>, item <ID/CU>, motivo <motivo>. Posso seguir?
```

Excecao:

- Se o usuario pedir explicitamente nesta conversa para alterar/reorganizar o plano, essa solicitacao
  ja conta como autorizacao para o escopo pedido. Ainda assim, informe o que sera alterado antes de
  aplicar o patch.

Observacao para Claude Code:

- O hook `.claude/hooks/plano-guard.js` bloqueia edicoes diretas no plano.
- Depois de confirmacao explicita do usuario, crie a flag local `.claude/plan-edit-approved.flag`.
- A flag e ignorada pelo Git e vale por 30 minutos; remova ou deixe expirar depois da edicao.

## Padrao obrigatorio para novas fases

Antes de criar uma fase no ClickUp ou nos arquivos de planejamento:

1. Confira codigo, plano e fontes de produto relacionadas.
2. Apresente a fase completa ao usuario na conversa e explique por que ela existe, por que entra
   nessa ordem e por que cada item foi incluido, adiado ou movido.
3. Aguarde autorizacao quando a proposta mudar escopo, prioridade, ordem ou aceite.
4. Aplique integralmente `docs/implementation/modelo-detalhamento-fase.md`.
5. Crie tarefa-pai/subtarefas no ClickUp com tags existentes e registre todos os `CU:` no plano.

O detalhamento minimo inclui contexto/evidencia, problema, motivo da decisao, objetivo, escopo, fora
do escopo com destino, dependencias, componentes provaveis, dados/migracao, seguranca, riscos/casos
de borda/rollback, validacao, criterios de aceite, documentacao, rastreabilidade e decisoes abertas.
Uma descoberta nao autoriza automaticamente implementacao: primeiro classifique se e correcao
imediata, decisao de produto, preparacao para producao, pos-MVP ou item de outra fase.

## Testes disparados pelo usuario

- Toda fase/subfase deve detalhar e preparar seus testes, dados, ambiente e comandos.
- Nao execute testes, suites, builds, smoke tests ou validacoes visuais de fase por iniciativa
  propria, mesmo depois de implementar o codigo.
- Ao terminar a implementacao, registre: `testes preparados - aguardando disparo do usuario`.
- Execute somente quando o usuario indicar explicitamente a fase ou conjunto a validar.
- Nunca marque como validado/concluido um aceite dependente de teste antes do resultado real.
