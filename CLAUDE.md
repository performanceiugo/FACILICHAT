# Instruções para o agente Claude Code — FaciliChat

## Atualização de documentação obrigatória

Após **qualquer alteração de código** neste projeto (nova funcionalidade, correção de bug, mudança de estrutura), você deve:

1. Atualizar `docs/changelog.md` — adicionar uma entrada com a data atual, o que foi alterado e por quê, em linguagem clara.
2. Atualizar o arquivo de documentação afetado:
   - Mudança no backend → `docs/tecnico-backend.md`
   - Mudança no frontend web → `docs/tecnico-frontend.md`
   - Mudança na arquitetura geral → `docs/arquitetura.md`
3. Se a mudança adicionar ou remover uma funcionalidade visível ao usuário, atualizar também `docs/visao-geral.md` na seção correspondente.

## Convenções do projeto

- Nomes de modelos, colunas e rotas em **português, PascalCase** (ex: `ChamadoStatus`, `ClienteID`)
- Código em **TypeScript** no frontend (web e mobile)
- Backend em **Python + FastAPI**, assíncrono
- Nunca commitar arquivos `.env` — usar sempre `.env.example`
- Manter tipos do frontend sincronizados com os modelos do backend

## Estrutura de pastas

```
backend/app/          → FastAPI (modelos, rotas, banco de dados)
frontend/web/         → Next.js 15 (web admin)
frontend/mobile/      → Expo React Native (app mobile)
docs/                 → documentação do projeto (sempre atualizar)
```
