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
