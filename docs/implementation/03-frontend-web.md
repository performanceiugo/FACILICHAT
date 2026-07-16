# Trilha Frontend Web

Esta trilha cobre o painel web, area de plataforma, gestor, cadastros e interfaces administrativas.

## Base entregue

| Grupo | Status | CUs |
|-------|--------|-----|
| Login, painel e protecao inicial | `[x]` | `868k60uyx`, `868k60uz4`, `868k60v07`, `868k60v0a`, `868k60v1x`, `868k60v29` |
| Design system e polimento | `[x]` | `868k60v2e`, `868k60vc3` |
| Area Superadmin inicial | `[x]` | `868k60vnh` |
| Tipos tenant/web | `[x]` | `868k60vn7`, `868k60vnp` |

## Pendencias de qualidade web

| Novo ID | Status | CU | Origem | Entrega |
|---------|--------|----|--------|---------|
| `WEB-FIX-001` | `[ ]` | `868k60vay` | `M6` | Escolher estrategia de base URL/rewrite |
| `WEB-FIX-002` | `[ ]` | `868k60vb1` | `M7` | Tipar enums, erros e `detail` |
| `WEB-FIX-003` | `[ ]` | `868k60vb3` | `M8` | Remover duplicidade de `token()` |
| `WEB-FIX-004` | `[ ]` | `868k60vbb` | `M9` | Comentar CSS conforme regra do projeto |
| `WEB-FIX-005` | `[ ]` | `868k60vca` | `B2` | AbortController/cleanup em fetch |
| `WEB-FIX-006` | `[ ]` | `868k60vck` | `B3` | Criar `error.tsx` e `not-found.tsx` |
| `WEB-FIX-007` | `[ ]` | `868k60vcx` | `B5` | Foco visivel, ARIA e `aria-live` |
| `WEB-FIX-008` | `[~]` | `868k7vx0v` | `B7` | Validacao mobile do painel web |

## Chat e chamados

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `WEB-CHAT-001` | `[ ]` | `868k60vt2`, `868k60vt8`, `868k60vtc`, `868k60vun`, `868kd35n1` | Central lista+thread, API/cursor, bolhas acessiveis, retry, nao lidas, WS/recovery, presenca/digitacao |
| `WEB-CHAT-002` | `[ ]` | `868kd35m7` | Solicitar/retirar/confirmar/recusar conclusao e tela Gestor para configurar 24/48/72 |
| `WEB-CHAM-001` | `[ ]` | `868k60vvz` | Modal "Novo chamado" |
| `WEB-CHAM-002` | `[ ]` | `868kd2dut`, `868kd2dvc` | Cancelamento interno e motivo/reabertura do Cliente conforme papel |

Seguir `docs/implementation/12-fase-01-chat.md`: Supervisor participa de todos no tenant, mas a UI
nao amplia cancelamento/reatribuicao; Concluido/Cancelado somente leitura; midia nao aparece antes
da Fase 9. Testes/visual/build aguardam comando do usuario.

## Gestor e operacao

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `WEB-GEST-001` | `[ ]` | `868k60w1k`, `868k60w1r`, `868k60w1y`, `868k60w26` | Visao geral e KPIs |
| `WEB-GEST-002` | `[ ]` | `868k7vrwr`, `868k7vrx5` | Painel orientado a urgencia/alertas |
| `WEB-GEST-003` | `[ ]` | `868k60w2a`, `868k60w2j`, `868k60w2w` | Supervisores, tickets e sidebar |
| `WEB-GEST-004` | `[ ]` | `868kd2dwt` | Reatribuicao de Supervisor no ticket usando backend `868kcv8dp` |

## Catalogo, regras, propostas e cadastros

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `WEB-CAT-001` | `[ ]` | `868k7vr7n`, `868k7vr7y`, `868k7vr8d` | Catalogo de servicos, parceiros e tipos |
| `WEB-IA-001` | `[ ]` | `868k7vrd0` | Tela de base de regras |
| `WEB-PROP-001` | `[ ]` | `868k60w4n`, `868k60w4u` | Alertas e formulario de proposta |
| `WEB-CAD-001` | `[ ]` | `868k60whj`, `868k60whn`, `868kd2e3w` | Cadastros, area de plataforma e Supervisor padrao por Condominio |
| `WEB-VIS-001` | `[ ]` | `868k60wmu`, `868k60wn0` | Pagina de visitas e link no sidebar |
