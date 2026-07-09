<!-- Arquivo de cabeçalho: documenta como o Codex deve diagnosticar bloqueios de sandbox e distinguir limite da sessão de erro de implementação. -->
---
name: diagnosticar-sandbox
description: Diagnostica limitações de sandbox, rede, escrita e integrações ausentes antes de culpar o código do projeto.
---

# Diagnosticar sandbox e integrações

## Checklist

1. Confirmar `cwd` e raiz gravável do workspace.
2. Verificar se a escrita necessária acontece dentro do workspace.
3. Verificar se o comando falhou por rede restrita.
4. Verificar se a ação depende de ferramenta externa não exposta nesta sessão.
5. Separar claramente:
   - erro do projeto
   - limitação do ambiente Codex
   - falta de autenticação/integração externa

## Achados já conhecidos neste repositório

- escrita fora de `D:\ProjetoDEV\FACILICHAT` exige permissão extra
- rede é restrita por padrão
- ClickUp pode não estar exposto como MCP ao Codex
- skills globais do Codex não devem ser assumidas como instaláveis sem acesso fora do workspace
