---
name: chamados-teste
description: Cria ou atualiza chamados de teste/demonstração no banco de dados local via API (nunca SQL bruto), para validar telas do painel (visão geral, lista de chamados, polling automático) sem precisar descrever o pedido em detalhe toda vez. Use quando o usuário pedir para "criar um chamado", "gerar um chamado crítico/de teste", "atualizar o status de um chamado" ou algo equivalente, para fins de teste/demonstração no ambiente de dev.
---

# Chamados de teste — criar/atualizar via API (nunca SQL direto)

Sempre pela **API real** (`POST /chamados/`, `PATCH /chamados/{id}/status`), nunca `INSERT`/`UPDATE`
direto no Postgres — assim o dado nasce escopado ao tenant certo (RLS/`EmpresaID`) exatamente como
nasceria de um uso real, e não corre risco de ficar em estado inconsistente.

**Escopo:** só ambiente de dev local (`docker compose`, API em `localhost:8000`). Nunca rodar isso
contra staging/produção.

## Pré-requisito
Confirmar que a API está no ar: `curl -s http://localhost:8000/` deve responder
`{"mensagem":"FaciliChat online!"}`. Se não responder, subir o projeto primeiro (skill
`subir-projeto`) antes de continuar.

## Credenciais de demonstração (seed — `backend/scripts/gerenciar_banco.py`)
Todas as senhas de demo: **`FaciliChat2026Demo`** (domínio `@demo.facilichat.dev`) — atualizada no
item M1 para cumprir a política de senha (mínimo 15 caracteres).

| Papel | Email |
|---|---|
| Cliente — Maria Silva (Cond. Jardim das Flores) | `maria@demo.facilichat.dev` |
| Cliente — João Souza (Ed. Solar das Acácias) | `joao@demo.facilichat.dev` |
| Cliente — Ana Costa (Res. Bosque Verde) | `ana@demo.facilichat.dev` |
| Cliente — Carlos Lima (Cond. Vista Alegre) | `carlos@demo.facilichat.dev` |
| Supervisor — Roberto Supervisor | `supervisor@demo.facilichat.dev` |

Gestor Demo (não é seed do `semear`, é o bootstrap da Empresa): `admin@facilichat.dev` / `FaciliChat2026Demo`
(ver `docs/setup.md`/skill `subir-projeto`). Use-o para ações que exigem Supervisor/Gestor (troca de
status).

## Enums reais (`backend/app/modelos/Chamados.py`)
- `Fila`: `Operacional` | `RH` | `Financeiro` | `Comercial`
- `Status`: `Recebido` | `EmAndamento` | `Agendado` | `Concluido` | `Cancelado` (novo chamado sempre
  nasce `Recebido` — não é campo de entrada em `POST /chamados/`)
- `Prioridade`: `Baixa` | `Media` | `Alta` | `Critica`

## Categoria (Fase 4: virou catálogo, não é mais texto livre)
`POST /chamados/` exige `CategoriaID` (UUID) de uma categoria **ativa** da mesma Empresa — não
aceita mais o nome em texto. Descubra o catálogo antes de montar o payload:
```bash
curl -s http://localhost:8000/categorias/ -H "Authorization: Bearer $TOKEN_GESTOR"
```
Se a categoria que o cenário pede ainda não existir no catálogo, crie com `POST /categorias/`
(exclusivo do Gestor) antes de abrir o chamado.

## Criar um chamado novo
1. Login como um Cliente demo (qualquer um da tabela acima, ou o que o usuário indicar):
   ```bash
   TOKEN=$(curl -s -X POST http://localhost:8000/autenticacao/login \
     -d "username=maria@demo.facilichat.dev&password=FaciliChat2026Demo" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     | grep -o '"token_acesso":"[^"]*"' | cut -d'"' -f4)
   ```
2. Criar o chamado — **se `Resumo` tiver acento (ã, ç, é...), não use `-d '{...}'`
   direto**: o Bash deste ambiente corrompe a codificação e a API responde
   `"There was an error parsing the body"`. Escreva o JSON num arquivo (Write, UTF-8) e envie com
   `--data-binary @arquivo`:
   ```bash
   curl -s -X POST http://localhost:8000/chamados/ \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     --data-binary "@/caminho/scratchpad/chamado.json"
   ```
   Sem acento nenhum no payload, `-d '{...}'` inline funciona normalmente.
3. Se o usuário não especificar algum campo, preencha com bom senso (não pergunte de volta por
   detalhe menor — é o motivo desta skill existir): `Fila: Operacional` e `Prioridade: Media` como
   padrão neutro; só suba para `Alta`/`Critica` se o pedido sugerir urgência ("crítico", "urgente",
   "parado"); resolva `CategoriaID` no catálogo (`GET /categorias/`) escolhendo o nome mais coerente
   com o cenário de condomínio (ex.: "Elevador", "Hidráulica", "Portaria", "Jardinagem" — já existem
   no seed); `Resumo` livre. Só pare para perguntar se o pedido for genuinamente ambíguo (ex.: qual
   cliente/condomínio usar, ou categoria nova que exigiria criar no catálogo primeiro).

## Atualizar o status de um chamado
A única mutação disponível hoje via API é `PATCH /chamados/{id}/status` (mudar `Prioridade` ou
`Categoria` depois de criado **não existe como rota** — se o usuário pedir isso, avise que exigiria
uma rota nova e siga a Regra de Ouro do `CLAUDE.md`: proponha o item, peça confirmação, só então
implemente).

1. Login como Gestor ou Supervisor (não Cliente — dá 403): use o Gestor Demo acima.
2. Descubra o `ID` do chamado (liste e filtre por categoria/resumo se o usuário não tiver o UUID):
   ```bash
   curl -s http://localhost:8000/chamados/ -H "Authorization: Bearer $TOKEN_GESTOR" \
     | grep -o '"ID":"[^"]*"[^}]*"Categoria":"[^"]*"'
   ```
3. Atualize — **`status` é query param, não corpo** (a rota recebe `status: ChamadoStatus` como
   parâmetro simples da função, sem `Body(...)`; FastAPI trata isso como query string):
   ```bash
   curl -s -X PATCH "http://localhost:8000/chamados/<ID>/status?status=EmAndamento" \
     -H "Authorization: Bearer $TOKEN_GESTOR"
   ```
   Chamado em estado terminal (`Concluido`/`Cancelado`) não reabre — a API responde `409`, isso é
   esperado (item C7/S2), não um bug.

## Depois de criar/atualizar
Diga ao usuário, em 1-2 linhas, o que foi criado/alterado (categoria, prioridade, status, ID) —
não é necessário relatório extenso. Se o dado for só para checar uma tela pontualmente (não para
ficar como demonstração permanente), pergunte se quer que você já limpe depois, ou deixe registrado
que aquele registro pode ser removido a qualquer momento sem risco (nunca é dado real de cliente).
