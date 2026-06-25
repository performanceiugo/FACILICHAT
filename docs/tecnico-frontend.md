# FaciliChat — Documentação Técnica: Frontend

---

## Web Admin (Next.js)

### Como rodar

```bash
cd frontend/web
npm install
cp .env.example .env        # ajustar a URL da API se necessário
npm run dev
```

Acesse: `http://localhost:3000`

### Estrutura de pastas

```
frontend/web/src/
├── types/
│   └── index.ts            ← todos os tipos TypeScript do projeto
├── lib/
│   ├── api.ts              ← todas as chamadas para o backend
│   └── auth.ts             ← leitura e gravação do token JWT
└── app/                    ← Next.js App Router
    ├── layout.tsx           ← layout raiz (fonte, metadata)
    ├── globals.css          ← variáveis CSS globais
    ├── page.tsx             ← redireciona / → /login
    ├── (auth)/
    │   └── login/
    │       ├── page.tsx     ← tela de login
    │       └── login.module.css
    └── (painel)/
        ├── layout.tsx       ← sidebar + proteção de rota
        ├── painel.module.css
        └── chamados/
            ├── page.tsx     ← listagem de chamados
            └── chamados.module.css
```

### Como adicionar uma nova tela no painel

1. Criar pasta em `src/app/(painel)/nome-da-tela/`
2. Criar `page.tsx` com `'use client'` se tiver interação
3. A proteção de rota já é feita automaticamente pelo `layout.tsx` do painel
4. Adicionar o link na sidebar em `(painel)/layout.tsx`

### Padrão do cliente HTTP (`lib/api.ts`)

Toda chamada ao backend passa pela função `req<T>()` que:
- Lê o token do `localStorage` automaticamente
- Adiciona o header `Authorization: Bearer <token>`
- Lança erro com a mensagem do backend em caso de falha

Para adicionar um novo endpoint:
```typescript
// Exemplo: buscar um chamado específico
chamados: {
  // ... existentes ...
  buscar: (id: string) => req<Chamado>(`/chamados/${id}`),
}
```

### Gerenciamento de sessão (`lib/auth.ts`)

| Função | O que faz |
|---|---|
| `auth.salvar(dados)` | Salva token, funcao e nome no localStorage |
| `auth.token()` | Retorna o token atual |
| `auth.funcao()` | Retorna a função do usuário logado |
| `auth.autenticado()` | Retorna `true` se há token salvo |
| `auth.sair()` | Remove todos os dados de sessão |
| `auth.isSupervisor()` | Retorna `true` para Supervisor ou Gerente |
| `auth.isGerente()` | Retorna `true` apenas para Gerente |

---

## App Mobile (Expo)

### Como rodar

```bash
cd frontend/mobile
npm install
cp .env.example .env        # ajustar a URL da API
npx expo start
```

- Pressione `a` para Android (emulador ou dispositivo)
- Pressione `i` para iOS (apenas Mac)
- Escaneie o QR code com o app **Expo Go** no celular para testar diretamente

> **Nota:** No emulador Android, use `http://10.0.2.2:8000` como URL da API (aponta para o localhost do PC). No iOS Simulator e dispositivo físico na mesma rede, use o IP local do PC.

### Estrutura de pastas

```
frontend/mobile/
├── lib/
│   ├── types.ts            ← tipos TypeScript (espelha o backend)
│   ├── api.ts              ← chamadas ao backend (usa SecureStore para token)
│   └── auth.ts             ← armazenamento seguro de sessão
└── app/                    ← Expo Router (navegação por arquivos)
    ├── _layout.tsx          ← layout raiz da navegação
    ├── index.tsx            ← redireciona conforme autenticação
    ├── (auth)/
    │   └── login.tsx        ← tela de login nativa
    └── (tabs)/
        ├── _layout.tsx      ← configuração das abas
        ├── chamados.tsx     ← lista de chamados com pull-to-refresh
        └── perfil.tsx       ← perfil do usuário + botão sair
```

### Como adicionar uma nova tela nas abas

1. Criar o arquivo em `app/(tabs)/nome.tsx`
2. Adicionar a entrada em `app/(tabs)/_layout.tsx`:
```tsx
<Tabs.Screen
  name="nome"
  options={{ title: 'Nome da Tela', tabBarLabel: 'Nome' }}
/>
```

### Diferenças importantes entre Web e Mobile

| Aspecto | Web (Next.js) | Mobile (Expo) |
|---|---|---|
| Armazenamento do token | `localStorage` | `expo-secure-store` (criptografado) |
| URL da API | `NEXT_PUBLIC_API_URL` | `EXPO_PUBLIC_API_URL` |
| Navegação | `useRouter()` do Next.js | `useRouter()` do Expo Router |
| Proteção de rota | `useEffect` no layout | `app/index.tsx` redireciona |
| Funções de `auth` | Síncronas (`string \| null`) | Assíncronas (`Promise<string \| null>`) |

---

## Tipos compartilhados

Os tipos TypeScript são **idênticos** nos dois frontends e espelham os modelos do backend. Qualquer alteração de modelo no backend deve ser replicada em `frontend/web/src/types/index.ts` **e** `frontend/mobile/lib/types.ts`.

```typescript
// Enums
UsuarioFuncao: 'Cliente' | 'Supervisor' | 'Funcionario' | 'Gerente'
ChamadoFila:  'Operacional' | 'RH' | 'Financeiro'
ChamadoStatus: 'Recebido' | 'EmAndamento' | 'Agendado' | 'Concluido' | 'Cancelado'
ChamadoPrioridade: 'Baixa' | 'Media' | 'Alta' | 'Critica'
AutorTipo: 'Cliente' | 'Supervisor' | 'Funcionario' | 'IA' | 'Sistema'
```

> Sempre que um enum for adicionado ou alterado no backend Python, deve ser atualizado nos dois arquivos de tipos do frontend.

---

## Pendente de implementação

- [ ] Tela de chat/mensagens dentro de um chamado (web e mobile)
- [ ] Tela de criação de chamado (formulário) no mobile
- [ ] Tela de usuários no painel web (para Gerentes)
- [ ] Filtros e busca na listagem de chamados
- [ ] Notificações push no mobile
- [ ] Indicadores visuais de IA nas mensagens automáticas

---

*Última atualização: 25 de junho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
