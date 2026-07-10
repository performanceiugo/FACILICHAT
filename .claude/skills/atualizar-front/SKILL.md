---
name: atualizar-front
description: Reinicia o frontend web (Next.js) limpando o cache de build depois de uma alteração de código, quando o dev server já estava no ar e passou a dar erro (ex.: "Cannot find module './NNN.js'", tela em branco, runtime error). Use quando o usuário disser algo como "atualizei o front", "recarrega o front", "limpa o cache e sobe de novo" ou relatar que o painel quebrou depois de uma mudança de código com o projeto já rodando.
---

# Atualizar o front (Next.js) após alteração de código

O dev server do Next.js (`npm run dev`) às vezes não recompila corretamente depois de mudanças de
código enquanto está rodando — o sintoma típico é `Runtime Error: Cannot find module './NNN.js'`
(cache de build em `.next` corrompido/desatualizado). A correção é sempre a mesma: matar o processo
antigo, apagar o cache e subir de novo. Este runbook automatiza isso.

**Escopo:** só mexe no `frontend/web` (Next.js). Não reinicia banco/backend (`docker compose`) — se o
problema for na API, isso é outro fluxo.

## Passo 1 — Descobrir e encerrar o processo que está na porta 3000 (e 3001, se houver vazamento)

Processos do `next dev` às vezes deixam um filho órfão que não morre com um simples Ctrl+C/TaskStop,
e aí o próximo `npm run dev` sobe em outra porta (3001, 3002...). Verifique as duas antes de seguir:

```powershell
Get-NetTCPConnection -LocalPort 3000,3001 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort,OwningProcess
```

Para cada `OwningProcess` retornado, encerre:

```powershell
Stop-Process -Id <PID> -Force -ErrorAction SilentlyContinue
```

Se havia uma task em background desta mesma sessão rodando `npm run dev`, pare-a também com
`TaskStop` — mas **não confie só nisso**: sempre confirme via `Get-NetTCPConnection` que a porta
ficou livre, porque o `TaskStop` nem sempre mata o processo filho do Next.

## Passo 2 — Apagar o cache de build

Da raiz do repositório:

```bash
rm -rf frontend/web/.next
```

## Passo 3 — Subir o dev server de novo

Rode **em background** (não bloqueie a sessão), a partir de `frontend/web`:

```bash
npm run dev
```

## Passo 4 — Validar que subiu limpo, na porta certa e sem erro de runtime

1. Faça polling em `http://localhost:3000` até responder (HTTP 200/307/302).
2. Leia a saída do processo em background e confirme a linha `- Local: http://localhost:3000`
   (se aparecer outra porta, é sinal de que o Passo 1 não liberou a 3000 — volte lá).
3. Baixe a página (`curl -s -L http://localhost:3000/`) e confira que o HTML normal veio (título,
   CSS do Next), sem `Runtime Error` / `Cannot find module` no corpo.

## Passo 5 — Relatório final

Confirme ao usuário: porta em que subiu, que o cache foi limpo e que a página carregou sem erro.
Se o erro persistir mesmo depois de limpar o cache, **não repita o ciclo às cegas** — isso indica
algo real no código novo (erro de sintaxe, import quebrado, etc.); leia a saída do dev server e
investigue o erro em vez de só reiniciar de novo.
