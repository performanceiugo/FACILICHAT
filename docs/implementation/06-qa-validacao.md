# Trilha QA e Validacao

QA deve acompanhar cada entrega, com validacao especifica para multi-tenant, seguranca e layout.

## Validacoes obrigatorias por tipo de mudanca

| Tipo | Validar |
|------|---------|
| Backend multi-tenant | Usuario de Empresa A nao acessa dados da Empresa B; RLS e filtro de app batem |
| Auth/sessao | Login, logout, expiracao, 401, CSRF quando aplicavel, mobile separado do web |
| Web | `npm run build`, navegacao protegida, responsivo desktop/mobile e estados vazios/erro |
| Mobile | Expo/typecheck quando disponivel, login, refresh, tabs, estados offline/erro |
| IA | Resposta ancorada em dados cadastrados, sem preco/prazo inventado, auditoria registrada |
| Docs | Changelog e docs tecnicas atualizados no mesmo PR/entrega |

## Itens de QA mapeados

| Novo ID | Status | Origem/CU | Entrega |
|---------|--------|-----------|---------|
| `QA-TENANT-001` | `[x]` | `S2` / `868kaa359` | Verificador automatizado de isolamento tenant |
| `QA-WEB-001` | `[~]` | `B7` / `868k7vx0v` | Validar painel web em navegador mobile |
| `QA-LAYOUT-001` | `[~]` | Revisao layout 09/07 | Validar desktop/mobile/Expo apos ajustes visuais |
| `QA-DOC-001` | `[ ]` | `D8` / `868kaa3h4` | Checklist de aceite dos HTMLs de branding |
| `QA-SEC-001` | `[x]` | `S12` / `868kaa3dz` | Automatizar auditoria Python em CI/docs |
| `QA-MOB-001` | `[ ]` | `S11` / `868kaa3dh` | Audit mobile reproduzivel com lockfile |

## Checklist de saida de uma entrega

- Item do plano legado atualizado.
- ClickUp sincronizado pelo `CU:`.
- Changelog com resumo de comportamento e validacao.
- Teste/build/audit registrado quando aplicavel.
- Nenhuma tela nova sem estado de erro/vazio/carregamento.
- Nenhuma rota nova sem verificacao de tenant e permissao.

