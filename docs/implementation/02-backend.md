# Trilha Backend

Esta trilha agrupa modelos, rotas, servicos, IA, tenant e regras de negocio. O plano antigo
continua sendo a fonte dos detalhes por fase e dos `CU:`.

## Fundacao ja entregue

| Grupo | Status | CUs |
|-------|--------|-----|
| Auth, usuarios, chamados, mensagens, banco async e Docker base | `[x]` | `868k60uxr`, `868k60uxu`, `868k60uy1`, `868k60uy4`, `868k60uya`, `868k60uyf`, `868k60uym`, `868k60uyp` |
| Correcoes backend iniciais | `[x]` | `868k60v03`, `868k60v05`, `868k60v0h`, `868k60v0m`, `868k60v1q`, `868k60v33` |
| Branding de dominio e multi-tenant | `[x]` | `868k60ve3`, `868k60ve6`, `868k60ve8`, `868k60vee`, `868k60vem`, `868k7vrt2`, `868k60veu`, `868k60vft`, `868k60vg4`, `868k60vgm`, `868k60vhk`, `868k60vjt`, `868k60vjw`, `868k60vk6`, `868k60vkz`, `868k60vn1` |

## Pendencias tecnicas de base

| Novo ID | Status | CU | Origem | Entrega |
|---------|--------|----|--------|---------|
| `BE-FIX-001` | `[ ]` | `868k60v2w` | `M1` | Validacoes Pydantic de tamanho/forca |
| `BE-FIX-002` | `[ ]` | `868k60v30` | `M2` | Tratar `IntegrityError` no cadastro |
| `BE-FIX-003` | `[ ]` | `868k60v3c` | `M4` | Tornar `echo` SQL configuravel |
| `BE-FIX-004` | `[ ]` | `868k60vam` | `M5` | Pydantic v2/datetime timezone-aware |
| `BE-FIX-005` | `[ ]` | `868k60vd4` | `B6` | Claims JWT, hasher centralizado e `lifespan` |

## Chat e mensagens

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `BE-CHAT-001` | `[ ]` | `868k60vpu`, `868k60vq1`, `868k60vrq` | Rotas e schemas de mensagens |
| `BE-CHAT-002` | `[ ]` | `868k60vrt` | WebSocket por chamado |
| `BE-CHAT-003` | `[ ]` | `868k7vrte` | Confirmacao automatica "Recebido" |
| `BE-CHAT-004` | `[ ]` | `868k7vrtu` | Mensagens de texto/audio/imagem como primeira classe |

## Multicanal — WhatsApp como porta de entrada (Fase 1.5, nova em 10/07/2026)

> WhatsApp e adaptador de entrada; o nucleo permanece independente do canal. Detalhe completo,
> criterios de aceite e decisoes pendentes na Fase 1.5 do `docs/plano-implementacao.md`
> (CU pai `868kb75yf`). Inbound roda apos `BE-CHAT-001`; outbound so depois da IA (Fase 5).

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `BE-CANAL-001` | `[ ]` | `868kb77b5`, `868kb77jm`, `868kb77m6`, `868kb77pw` | Modelos: CanalOrigem, ContatoCanal, correlacao externa idempotente (wamid) e auditoria de eventos |
| `BE-CANAL-002` | `[ ]` | `868kb77rb`, `868kb77u1`, `868kb77vb` | Entrada normalizada (adaptador → DTO neutro) + webhook GET/POST com assinatura X-Hub-Signature-256 |
| `BE-CANAL-003` | `[ ]` | `868kb77zj`, `868kb781w`, `868kb783m`, `868kb7855` | Resolucao de tenant/contato, criacao de chamado, midia (depende Fase 9) e status externos |
| `BE-CANAL-004` | `[ ]` | `868kb786k`, `868kb788v`, `868kb78ar` | Testes de robustez (duplicado/ordem/assinatura/tenant), observabilidade/reprocessamento e docs |
| `BE-CANAL-005` | `[ ]` | `868kb78gx`–`868kb78y9` | Outbound (janela 24h, templates, opt-in, numeros, custos) — posterior a Fase 5 |

## Chamados, fila e operacao

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `BE-TICKET-001` | `[ ]` | `868k60vvx` | `POST /chamados/` retorna ID para redirecionamento |
| `BE-TICKET-002` | `[ ]` | `868k60vxf`, `868k60vxk`, `868k60vya`, `868k60vym` | Fila do supervisor, agendamento, nota interna e conclusao |
| `BE-TICKET-003` | `[ ]` | `868k7vruk` | Aprovacao do cliente encerra ticket |

## Relatorios e gestor

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `BE-REL-001` | `[ ]` | `868k60w1b`, `868k60w1e`, `868k60w1g` | Endpoints de visao geral e supervisores |
| `BE-REL-002` | `[ ]` | `868k7vrvm`, `868k7vrw8`, `868k7vrwh` | Alertas operacionais e metricas derivadas |

## Catalogo, IA e governanca

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `BE-CAT-001` | `[ ]` | `868k7vr66`, `868k7vr6h`, `868k7vr6z` | Parceiros, catalogo de servicos e CRUD escopado por Empresa |
| `BE-IA-001` | `[ ]` | `868k60w36`, `868k60w38`, `868k60w3e`, `868k60w3h` | Classificacao, roteamento e narracao de status |
| `BE-IA-002` | `[ ]` | `868k7vrxw`, `868k60w3m`, `868kahvau`, `868k7vryf`, `868k7vryy` | Oportunidades ancoradas em catalogo e sem preco inventado |
| `BE-IA-003` | `[ ]` | `868k7vraj`, `868k7vray`, `868k7vrbc`, `868k7vrbh` | Guardrails, validacao pos-geracao e auditoria |
| `BE-IA-004` | `[ ]` | `868k7vrc1`, `868k7vrcg`, `868k7vrcn` | Base de regras RH/Financeiro por Empresa |

## Propostas, cadastros, visitas, upload e push

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `BE-PROP-001` | `[ ]` | `868k60w47`, `868k60w4a`, `868k60w4e`, `868k60w4g` | Propostas e alertas comerciais |
| `BE-CAD-001` | `[ ]` | `868k60wh3`, `868k60wh7`, `868k60whc` | CRUD de condominios e empresas |
| `BE-VIS-001` | `[ ]` | `868k60wj5`, `868kahvb2`, `868kahvbe`, `868k60wjj`, `868k60wjq`, `868k60wjv`, `868k60wk2`, `868k60wk9`, `868k60wkf`, `868k60wkn`, `868kahvbk`, `868k60wkq` | Visitas tecnicas |
| `BE-UP-001` | `[ ]` | `868k60wnd`, `868k60wng`, `868k60wnh` | Storage, upload e imagem no chat |
| `BE-PUSH-001` | `[ ]` | `868k60wpx`, `868k60wq2` | Envio push e token de dispositivo |
| `BE-FUNC-001` | `[ ]` | `868k7vrew`, `868k7vrfc`, `868k7vrfv`, `868k7vrg7` | Fluxos IA/backend do funcionario |

