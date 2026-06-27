---
name: validar-regras
description: Valida uma alteração de código contra os invariantes de produto do FaciliChat (branding, multi-tenant, 7 perfis, IA, visita técnica, design system) antes de implementar. Use SEMPRE antes de qualquer mudança de funcionalidade ou regra de negócio no código.
---

# Validar regras do FaciliChat — trava de segurança

Checklist obrigatório **antes** de implementar qualquer mudança de funcionamento ou regra de negócio.
Fonte da verdade: `docs/FaciliChat-Regras/` (material do comercial) + a seção "🔒 TRAVA DE SEGURANÇA"
do `CLAUDE.md`. Veja também o roteiro em `docs/plano-implementacao.md` e `docs/arquitetura.md`.

## Como usar
1. Descreva em uma frase o que a mudança altera (modelo, rota, fluxo, UI, regra).
2. Leia o item correspondente em `docs/plano-implementacao.md` e a regra em `docs/FaciliChat-Regras/`
   (ou o resumo de invariantes no `CLAUDE.md`).
3. Percorra o checklist abaixo. Para cada item: ✅ respeita / ⚠️ pode violar / ➖ não se aplica.

## Checklist de invariantes
- [ ] **Multi-tenant** — toda tabela nova tem `EmpresaID`? Toda query é escopada pela Empresa do usuário logado? Não há vazamento de dados entre tenants?
- [ ] **Perfis (7)** — usa Cliente, Funcionário, Supervisor, RH, Financeiro, **Gestor**, Superadmin? Não reintroduz "Gerente" como conceito novo nem cria subtipos de Funcionário? Papéis são por Empresa?
- [ ] **IA** — nenhuma geração de preço ou prazo pela IA? A IA só narra campos estruturados e nunca fala em nome de um supervisor?
- [ ] **Ticket / Chat** — estados continuam Recebido / Em andamento / Agendado / Concluído? O chat é o palco e o ticket o bastidor (status calmo, não alarmante)?
- [ ] **Visita técnica** — continua entidade irmã do ticket (não um tipo de ticket)? Duração derivada (não armazenada)? Cliente não aprova, só consulta?
- [ ] **Tickets irmãos** — fluxos que exigem 2 filas (ex.: atestado → RH + Supervisão) geram chamados irmãos sem o usuário precisar conhecer a estrutura interna?
- [ ] **Design system** — cores (#148AF5, Ink), fonte Figtree, ícones Line Awesome, raios e espaçamentos conforme os tokens? Interface discreta (hospeda a marca do cliente)?
- [ ] **Anti-amnésia** — nada que o cliente pede se perde; tudo fica registrado e rastreável?

## Resultado
- **Todos ✅** → prossiga com a implementação, seguindo as regras de comentário e de atualização de
  documentação do `CLAUDE.md` (changelog + plano + doc técnico afetado).
- **Algum ⚠️** → **PARE.** Explique ao usuário qual invariante a mudança quebra e **peça confirmação
  explícita** antes de alterar uma regra já definida. Não mude um invariante por conta própria.
