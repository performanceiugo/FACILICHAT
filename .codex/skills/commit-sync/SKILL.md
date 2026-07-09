<!-- Arquivo de cabeçalho: define o fechamento de uma rodada de trabalho com Git e sincronização do plano, incluindo fallback quando o ClickUp não estiver exposto ao Codex. -->
---
name: commit-sync
description: Fecha uma rodada de trabalho com conferência de changelog, plano, Git e sincronização do ClickUp quando a ferramenta estiver disponível.
---

# Commit e sincronização

## Passos

1. Revisar `git status --short` e `git log --oneline -3`.
2. Confirmar que `docs/changelog.md` e `docs/plano-implementacao.md` refletem o trabalho.
3. Conferir se não há `.env` ou segredos versionados.
4. Se houver integração de ClickUp disponível no Codex, sincronizar cada `CU:` alterado.
5. Se não houver integração de ClickUp, registrar explicitamente essa limitação ao usuário.
6. Fazer commit e push apenas quando solicitado.

## Regra

Sem changelog e plano atualizados, a rodada não está pronta para commit.
