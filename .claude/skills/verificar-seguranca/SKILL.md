---
name: verificar-seguranca
description: Consulta documentação de referência atualizada (OWASP, docs oficiais do FastAPI/Next.js, MDN) sobre cookies (HttpOnly/SameSite/Secure), CORS, JWT e isolamento multi-tenant (RLS), e compara com a implementação atual do FaciliChat — para saber se a política de segurança do projeto ficou desatualizada. Use quando uma alteração for tocar código de segurança (autenticação, cookies, CORS, JWT, multi-tenant/RLS), ou quando o usuário pedir explicitamente para checar/atualizar as práticas de segurança.
---

# Verificar segurança — comparação com documentação de referência atualizada

Skill de auditoria pontual: compara a prática de segurança **atual** do FaciliChat com a
recomendação **mais recente** encontrada em fontes de referência. Ela só compara e relata — não
aplica nenhuma mudança sozinha. Mudanças de regra de segurança seguem a Trava de Segurança do
`CLAUDE.md` (precisam estar no `docs/plano-implementacao.md` e ter confirmação explícita do usuário).

## Quando usar
- Antes de alterar código que toca: autenticação (JWT), cookies de sessão (HttpOnly/SameSite/Secure),
  CORS (`CORSMiddleware` no backend), isolamento multi-tenant (RLS/EmpresaID), ou headers de
  segurança HTTP.
- Quando o usuário pedir explicitamente para checar se a política de segurança está atualizada.

Não use para alterações que não tocam nesses temas — isso evita gastar tokens à toa (ver regra em
`CLAUDE.md`).

## Como usar
1. Identifique o(s) tema(s) específico(s) da mudança (ex.: só CORS, ou JWT + cookies) — não faça uma
   varredura geral se a mudança só toca um tema.
2. Leia o código atual relevante para descrever o estado atual (ex.: `backend/app/main.py` para
   CORS, o módulo de segurança do backend para JWT, o `proxy.ts`/cookies do `frontend/web`).
3. Busque a recomendação atual só para o(s) tema(s) identificado(s):
   - Biblioteca específica (FastAPI, Next.js) → use a skill `find-docs` (Context7).
   - Prática geral de segurança web (ex.: "recomendação atual de SameSite", "OWASP CORS") →
     `WebSearch`/`WebFetch` em fontes como OWASP Cheat Sheet Series, MDN, docs oficiais do framework.
4. Compare estado atual vs. recomendação encontrada e classifique cada item:
   - **OK** — alinhado com a recomendação atual.
   - **ATENÇÃO** — diverge, risco baixo/moderado.
   - **CRÍTICO** — diverge, risco real de segurança.
5. Se tudo **OK**, prossiga normalmente com a implementação planejada.
6. Se houver **ATENÇÃO** ou **CRÍTICO**, PARE: isso é uma mudança de regra de segurança, não um
   detalhe de implementação. Siga a Trava de Segurança do `CLAUDE.md` — adicione o item ao
   `docs/plano-implementacao.md` e peça confirmação explícita ao usuário antes de alterar o código.

## Saída
Resuma por tema, em poucas linhas: `Tema | Estado atual (arquivo:linha) | Recomendação (fonte) |
Classificação`. Não é necessário relatório extenso — só o suficiente para decidir se prossegue ou
pausa para confirmação.
