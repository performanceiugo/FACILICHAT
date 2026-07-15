<!-- Arquivo de cabeçalho: descreve a camada local do Codex para este repositório e as regras obrigatórias antes de qualquer alteração. -->
# Codex no FaciliChat

Esta pasta guarda a camada local de compatibilidade do Codex para o FaciliChat.
Ela existe para reaproveitar as rotinas que antes ficavam só no Claude, sem
depender de instalação global fora do repositório.

## Regra de entrada

Antes de qualquer alteração de código, o agente deve:

1. Ler `CLAUDE.md`.
2. Ler `docs/plano-implementacao.md`.
3. Validar se o item existe no plano e se a mudança respeita `docs/FaciliChat-Regras/`.

Se o item não existir no plano, ele deve ser registrado primeiro. Se a mudança
quebrar um invariante de produto, ela para e pede confirmação explícita.

## O que existe aqui

- `skills/validar-regras/SKILL.md`: checklist de invariantes do produto.
- `skills/verificar-seguranca/SKILL.md`: rotina para checar segurança técnica com documentação atual.
- `skills/subir-projeto/SKILL.md`: runbook para levantar o projeto localmente.
- `skills/find-docs/SKILL.md`: regra de uso de documentação atualizada.
- `skills/commit-sync/SKILL.md`: fechamento de rodada com Git e ClickUp.
- `skills/diagnosticar-sandbox/SKILL.md`: diagnóstico dos limites do Codex nesta máquina.
- `scripts/diagnosticar-ambiente.ps1`: diagnóstico local de ambiente e permissões do workspace.
- `scripts/lembrete-clickup.ps1`: lembrete operacional para sincronização manual do board.

## Limites conhecidos desta sessão do Codex

- Escrita liberada apenas dentro do workspace `D:\ProjetoDEV\FACILICHAT`.
- Instalação global de skills/plugins fora do workspace depende de permissão extra.
- Rede restrita: consultas externas e instalações podem exigir liberação.
- O conector ClickUp está disponível pelo app desktop. Como há mais de um workspace autenticado,
  informar explicitamente `workspace_id: 9011725879` em todas as operações do FaciliChat.
- Board canônico: `Roadmap de Implementacao`, `list_id: 901114027434`, no Space
  `Operações Internas` (`space_id: 90114155244`). Sincronizar plano e board na mesma interação.

## Uso prático

Esses arquivos são referência operacional do projeto. Eles não garantem
carregamento automático pelo runtime do Codex; servem para padronizar o fluxo e
deixar o comportamento rastreável no repositório.
