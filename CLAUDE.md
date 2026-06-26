# Instruções para o agente Claude Code — FaciliChat

---

## LEIA PRIMEIRO — Verificação obrigatória antes de qualquer implementação

**Antes de escrever qualquer código, leia `docs/plano-implementacao.md` na íntegra.**

1. Verifique se o item que será implementado está listado e com status `[ ]` (na fila).
2. Se estiver `[x]` (concluído), **não reimplemente** — leia o código existente antes de continuar.
3. Se estiver `[~]` (em andamento), continue de onde parou — não crie duplicatas.
4. Ao iniciar um item, mude seu status para `[~]`. Ao concluir, mude para `[x]`.

---

## Regra obrigatória de comentários

**Todo bloco de código criado ou alterado deve ter comentário. Sem exceção.**

O que comentar obrigatoriamente:
- **Cada arquivo**: comentário de cabeçalho descrevendo a responsabilidade do arquivo
- **Cada função/método/rota**: o que faz e por que existe
- **Cada bloco lógico relevante** (enum, classe ORM, hook, estado, constante de mapeamento): o que representa
- **Decisões não óbvias**: por que foi feito assim (ex: `expire_on_commit=False`, form-urlencoded no login)
- **Regras de negócio embutidas no código**: ex: "Gerente e Supervisor veem todos os chamados; Cliente vê apenas os seus"

O que **não** comentar:
- Importações óbvias
- Código autoexplicativo por nome (ex: `setCarregando(true)` não precisa de comentário)

---

## Atualização de documentação obrigatória

Após **qualquer alteração de código** neste projeto (nova funcionalidade, correção de bug, mudança de estrutura), você deve:

1. Atualizar `docs/changelog.md` — adicionar uma entrada com a data atual, o que foi alterado e por quê, em linguagem clara.
2. Atualizar `docs/plano-implementacao.md` — marcar o item como `[x]` e, se necessário, adicionar novos itens descobertos durante a implementação.
3. Atualizar o arquivo de documentação afetado:
   - Mudança no backend → `docs/tecnico-backend.md`
   - Mudança no frontend web → `docs/tecnico-frontend.md`
   - Mudança na arquitetura geral → `docs/arquitetura.md`
4. Se a mudança adicionar ou remover uma funcionalidade visível ao usuário, atualizar também `docs/visao-geral.md` na seção correspondente.

---

## Convenções do projeto

- Nomes de modelos, colunas e rotas em **português, PascalCase** (ex: `ChamadoStatus`, `ClienteID`)
- Código em **TypeScript** no frontend (web e mobile)
- Backend em **Python + FastAPI**, assíncrono
- Nunca commitar arquivos `.env` — usar sempre `.env.example`
- Manter tipos do frontend sincronizados com os modelos do backend após qualquer alteração de schema

---

## Design system (tokens obrigatórios para todo código de UI)

```
Azul primário:  #148AF5   (hover: #0E72D4,  fundo sutil: #EAF4FE)
Ink (texto):    #17171A / #34363D / #646874 / #868B97
Fundos:         #F7F9FA (página) / #F1F4F6 / #FFFFFF (card)
Bordas:         #E7ECEF (Ink 100) / #C1CCD3 (Ink 200)
Sucesso:        #1FAE68  bg: #E7F6EE
Atenção:        #F0961E  bg: #FEF4E6
Erro/Crítico:   #E5484D  bg: #FDECEC
Raios:          8px (card), 12px (modal), 999px (badge/pílula)
Espaçamento:    base 4px → use 4, 8, 12, 16, 24, 32, 48, 64
Fonte:          Figtree (sans-serif geométrica)
Ícones:         Line Awesome (18–24px, estilo linha)
```

---

## Estrutura de pastas

```
backend/app/          → FastAPI (modelos, rotas, banco de dados, serviços)
frontend/web/         → Next.js 15 (web admin — painel do gestor)
frontend/mobile/      → Expo React Native (app mobile — cliente e supervisor)
docs/                 → documentação do projeto (sempre atualizar)
docs/plano-implementacao.md  → backlog de desenvolvimento (consultar antes de qualquer sessão)
```
