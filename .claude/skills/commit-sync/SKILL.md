---
name: commit-sync
description: Commita as alterações pendentes para o GitHub e sincroniza os status correspondentes no ClickUp. Use quando o usuário pedir para "commitar", "subir para o GitHub", "atualizar o commit" ou "/commit-sync".
---

# Commit + sincronização ClickUp

Fluxo padrão do FaciliChat para fechar uma rodada de trabalho: commit no GitHub e board do
ClickUp em dia, num passo só.

## Passos

1. **Levantar o que mudou:**
   - `git status --short` e `git log --oneline -3` para ver o pendente e o contexto.
   - `git diff docs/changelog.md` — a entrada nova do changelog descreve o trabalho (é a base da
     mensagem de commit).
   - `git diff docs/plano-implementacao.md` filtrando linhas de tabela (`^[+-]\|`) — os status
     alterados (`[ ]`→`[~]`/`[x]`) indicam o que sincronizar no ClickUp, com o `CU:` de cada item.

2. **Conferir segurança antes de commitar:**
   - Nenhum `.env` ou segredo pode estar staged (`git status` não pode listar `backend/.env`).
   - Se aparecer algo suspeito (chave, senha, token em arquivo versionado), PARE e avise o usuário.

3. **Sincronizar o ClickUp** (lista "Roadmap de Implementacao", `list_id 901114027434`):
   - Para cada item do plano cujo status mudou, mover a subtarefa (ID do `CU:`) para o status
     equivalente: `[~]` → `🚧 em andamento`, `[x]` → `✅ concluída`.
   - Se o item tem `CU: a-criar`, criar a subtarefa primeiro (pai indicado na seção do plano),
     já no status certo, e gravar o ID real no lugar do `a-criar` no plano.
   - Se **todos** os itens de uma fase ficaram `[x]` e o Mapa das fases diz "Concluída", mover
     também a tarefa-pai da fase.

4. **Commit e push:**
   - `git add -A`.
   - Mensagem em português, no estilo do repositório (assunto curto e imperativo + corpo com
     bullets resumindo os blocos do changelog). Se houver aspas ou acentos problemáticos, gravar
     a mensagem em arquivo no scratchpad e usar `git commit -F <arquivo>`.
   - Terminar a mensagem com a linha `Co-Authored-By` padrão do agente.
   - `git push origin main` e confirmar com `git status --short --branch` que ficou em dia.

5. **Relatar ao usuário:** hash e título do commit, arquivos/linhas, e quais tarefas do ClickUp
   foram movidas (com IDs).

## Regras

- O changelog e o plano devem estar atualizados ANTES do commit (regra do `CLAUDE.md`). Se o
  trabalho pendente não tem entrada no changelog, escreva-a primeiro.
- Nunca commitar `.env` ou qualquer valor de segredo — só nomes de campos e placeholders.
- Um commit por rodada é suficiente; não fatiar hunks de um mesmo arquivo.
