# Trilha QA e Validacao

QA deve acompanhar cada entrega no planejamento e na preparacao da cobertura proporcional ao risco.
A execucao pertence ao usuario: suite seletiva/ampla, teste, build, smoke e validacao visual so
rodam quando ele disparar explicitamente a fase ou conjunto.

## Validacoes que devem ser preparadas por tipo de mudanca

> A cobertura e os comandos sao obrigatorios no planejamento/implementacao, mas a execucao e
> controlada pelo usuario. Nenhum agente roda testes, build, smoke ou validacao visual de uma fase
> sem comando explicito informando a fase/conjunto.

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
| `QA-F08-001` | `[ ]` | `F08-05` / `868kd1jvr` | Teste repetivel de refresh realmente concorrente |
| `QA-F08-002` | `[ ]` | `F08-06` / `868kd1jwg` | Suite seletiva por fase e execucao ampla sob solicitacao |
| `QA-F08-003` | `[ ]` | `F08-07K` / `868kd2dx0` | Matriz cancelamento/reabertura/SLA/IA/WhatsApp; aguarda disparo do usuario |
| `QA-F01-001` | `[ ]` | `F01-L` / `868kd35pv` | Matriz chat: papel/tenant, API/cursor/idempotencia, WS/recovery, leitura/presenca, confirmacao 24/48/72, SLA, web/mobile; aguarda disparo do usuario |
| `QA-PROD-001` | `[ ]` | `F12-06` / `868kd1k82` | Gate final com regressao solicitada, smoke e decisao go/no-go |

## Como solicitar a suite evolutiva

O pedido deve indicar fases ou dominios, por exemplo: “confira as Fases 1 e 1.5 rodando a suite”.
O relatorio registra o que foi executado, aprovado, reprovado ou nao executavel. Novos cenarios sao
acrescentados conforme o produto cresce. O comando e o mapa fase -> testes serao entregues no
`F08-06`. Mesmo quando os testes ja estiverem escritos, o estado permanece “testes preparados —
aguardando disparo do usuario” ate esse comando.

## Checklist de saida de uma entrega

- Item do plano legado atualizado.
- ClickUp sincronizado pelo `CU:`.
- Changelog com resumo de comportamento e validacao.
- Testes/build/smoke preparados e, quando disparados pelo usuario, resultado real registrado.
- Nenhuma tela nova sem estado de erro/vazio/carregamento.
- Nenhuma rota nova sem verificacao de tenant e permissao.
