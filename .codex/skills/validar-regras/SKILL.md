<!-- Arquivo de cabeçalho: checklist de invariantes do produto para uso manual do Codex antes de mexer em regra de negócio. -->
---
name: validar-regras
description: Valida uma alteração contra os invariantes de produto do FaciliChat antes de qualquer mudança de funcionalidade ou regra de negócio.
---

# Validar regras do FaciliChat

## Quando usar

Use antes de alterar fluxo, modelo, rota, UI com regra de negócio ou comportamento
visível ao usuário.

## Passos

1. Resuma em uma frase o que a mudança altera.
2. Leia o item correspondente em `docs/plano-implementacao.md`.
3. Leia a regra de negócio em `docs/FaciliChat-Regras/` ou o resumo em `CLAUDE.md`.
4. Passe pelo checklist abaixo.

## Checklist

- [ ] Multi-tenant: tabela nova com `EmpresaID`, query escopada e sem vazamento entre tenants.
- [ ] Perfis: manter Cliente, Funcionário, Supervisor, RH, Financeiro, Gestor e Superadmin.
- [ ] IA: não inventa preço/prazo e não fala em nome de humano.
- [ ] Chat e ticket: estados continuam simples e rastreáveis.
- [ ] Visita técnica: continua entidade irmã do ticket.
- [ ] Tickets irmãos: fluxo pode abrir filas paralelas quando necessário.
- [ ] Design system: respeita tokens oficiais do branding.
- [ ] Anti-amnésia: nada pedido pelo cliente se perde.

## Decisão

- Todos ok: implementar e atualizar documentação.
- Algum risco: parar e pedir confirmação explícita ao usuário.
