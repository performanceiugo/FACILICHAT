# Trilha Frontend Mobile

Esta trilha cobre cliente, supervisor, funcionario, chat, visitas, upload e push no app Expo.

## Base entregue

| Grupo | Status | CUs |
|-------|--------|-----|
| Login, lista, perfil e logout | `[x]` | `868k60uz9`, `868k60uzb`, `868k60uzj` |
| Compatibilidade Expo/design system | `[x]` | `868k60v0f`, `868k60v1x`, `868k60v2e`, `868k60v2r`, `868k60vbj`, `868k60vbz`, `868k60vc3`, `868k60vct` |

## Pendencias de qualidade mobile

| Novo ID | Status | CU | Origem | Entrega |
|---------|--------|----|--------|---------|
| `MOB-FIX-001` | `[ ]` | `868k60vca` | `B2` | Cleanup/AbortController nas telas com fetch |
| `MOB-FIX-002` | `[ ]` | `868kaa3dh` | `S11` | Lockfile e audit reproduzivel |
| `MOB-FIX-003` | `[~]` | sem CU | Layout review | Validar visualmente em Expo apos build/typecheck |

## Cliente

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `MOB-CHAT-001` | `[ ]` | `868k60vv3`, `868k60vv8`, `868k60vvh`, `868k60vvm`, `868k60vvp` | API, tipo, tela de chat, WebSocket e navegacao |
| `MOB-CHAM-001` | `[ ]` | `868k60vwa`, `868k60vwk`, `868k60vx1` | Novo chamado, aba Nova e detalhe/timeline |
| `MOB-PROP-001` | `[ ]` | `868k60w4x` | Card de proposta no chat |
| `MOB-VIS-CLI-001` | `[ ]` | `868k60wmm` | Aba de visitas do cliente |

## Supervisor

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `MOB-SUP-001` | `[ ]` | `868k7vru6`, `868k7vrv2` | Fechamento rapido e agenda do dia prioritaria |
| `MOB-SUP-002` | `[ ]` | `868k60vzj`, `868k60vzp`, `868k60vzr`, `868k60w0b`, `868k60w0v`, `868k60w13` | Fila, Hoje, ticket completo, tabs e roteamento por funcao |
| `MOB-SUP-003` | `[ ]` | `868k60wkv`, `868k60wm6`, `868k60wmf` | Visita em andamento, agendamento e Hoje com visitas |

## Funcionario

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `MOB-FUNC-001` | `[ ]` | `868k7vre5`, `868k7vreg`, `868k7vren` | Canal unico texto/voz/foto, confirmacao e tabs |

## Upload e push

| Novo ID | Status | CUs | Entrega |
|---------|--------|-----|---------|
| `MOB-UP-001` | `[ ]` | `868k60wnx` | Upload de imagem no chat com `expo-image-picker` |
| `MOB-PUSH-001` | `[ ]` | `868k60wpt` | Expo Push Notifications |

