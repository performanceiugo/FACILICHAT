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
│   └── auth.ts             ← dados de exibição da sessão (o token fica em cookie HttpOnly)
├── components/
│   └── painel/
│       ├── AdminShell.tsx        ← casca do painel (sidebar + nav + guarda de sessão)
│       └── AdminShell.module.css
└── app/                    ← Next.js App Router
    ├── layout.tsx           ← layout raiz (fonte Figtree via next/font, metadata)
    ├── globals.css          ← tokens do design system (:root) + reset
    ├── page.tsx             ← redireciona / → /login
    ├── (auth)/
    │   └── login/
    │       ├── page.tsx     ← tela de login
    │       └── login.module.css
    └── painel/              ← pasta real (não route group), URLs /painel/*
        ├── layout.tsx       ← delega para <AdminShell> (proteção de rota + sidebar)
        └── chamados/
            ├── page.tsx     ← listagem de chamados
            └── chamados.module.css
```

### Design system (tokens)

O `app/globals.css` contém o `:root` com o **design system do comercial** portado de
`docs/FaciliChat-Regras/FaciliChat-Design-System.html` (fonte da verdade): escalas de cor
(`--blue-*` com a primária **#148AF5**, `--ink-*`), feedback (`--success/warning/danger-*`),
semânticos (`--bg-*`, `--text-*`, `--border-*`), tipografia (`--fs-*`, `--fw-*`), espaçamento
(`--sp-*`, escala 4px), raio (`--r-*`), sombras (`--shadow-*`) e motion. **Use sempre esses
tokens** em novos CSS Modules — nunca cores/medidas hardcoded. Há aliases de compatibilidade
(`--primario`, `--fundo`, `--texto`…) apontando para os tokens novos, para código legado.
A fonte **Figtree** (pesos 300–800) é carregada via `next/font/google` em `layout.tsx` e exposta
como `--font-figtree`/`--font-sans`.

### Como adicionar uma nova tela no painel

1. Criar pasta em `src/app/painel/nome-da-tela/`
2. Criar `page.tsx` com `'use client'` se tiver interação
3. A proteção de rota já é feita automaticamente pelo `AdminShell` (via `painel/layout.tsx`)
4. Adicionar o link na sidebar dentro de `components/painel/AdminShell.tsx`

### Padrão do cliente HTTP (`lib/api.ts`)

Toda chamada ao backend passa pela função `req<T>()` que:
- Usa a base `/api` — o **proxy do Next** (`rewrites` no `next.config.ts`), nunca a API direto.
  Mesma origem ⇒ o cookie de sessão é first-party e a CSP fecha em `connect-src 'self'` (S6/M6).
- **Não** injeta credencial: o navegador envia sozinho o cookie `sessao` (`HttpOnly`).
- Anexa o header `X-CSRF-Token` (lido do cookie `csrf_token`) em `POST`/`PUT`/`PATCH`/`DELETE`.
- Lança erro com a mensagem do backend em caso de falha; em `401`, limpa o local e vai ao login.

> **Cuidado ao mexer no proxy:** as rotas do backend terminam em barra (`/chamados/`). O Next
> redirecionaria (308) e, depois, o FastAPI devolveria um 307 apontando para a **origem da API** —
> o `fetch` sairia do proxy. Por isso existem `skipTrailingSlashRedirect: true` e uma regra de
> rewrite que preserva a barra final. Não remova nenhum dos dois.

Para adicionar um novo endpoint:
```typescript
// Exemplo: buscar um chamado específico
chamados: {
  // ... existentes ...
  buscar: (id: string) => req<Chamado>(`/chamados/${id}`),
}
```

### Gerenciamento de sessão (`lib/auth.ts`)

Depois do item **S6**, o token **não passa mais pelo JavaScript**: ele vive no cookie `sessao`
(`HttpOnly`), emitido pelo backend no login. Um XSS no painel não consegue lê-lo. O `localStorage`
guarda apenas dados de **exibição** (nome, empresa). Não existe mais `auth.token()`.

| Função | O que faz |
|---|---|
| `auth.salvar(dados)` | Salva **só** nome/empresa no localStorage (os cookies vêm no `Set-Cookie`) |
| `auth.funcao()` | Lê o cookie legível `funcao` (usado para escolher a tela; forjável, não autoriza nada) |
| `auth.autenticado()` | `true` se o cookie `funcao` existe — dica de interface; quem decide é o backend (401) |
| `auth.limparLocal()` | Remove os dados locais de exibição. **Não** apaga cookies |
| `api.logout()` | Encerra a sessão de verdade: só o backend apaga um cookie `HttpOnly` |
| `auth.isSupervisor()` | Retorna `true` para Supervisor ou Gestor |
| `auth.isGestor()` | Retorna `true` apenas para Gestor |

### Headers de segurança (`next.config.ts`) — item S16

Todas as respostas do painel saem com headers de segurança definidos em `headers()` do
`next.config.ts`:

| Header | Valor / propósito |
|---|---|
| `Content-Security-Policy-Report-Only` | CSP em fase de observação: o navegador só registra violações no console, sem bloquear. Promover a `Content-Security-Policy` (enforce) após período sem violações — passos em `docs/deploy-producao.md` |
| `X-Content-Type-Options` | `nosniff` — impede sniffing de MIME type |
| `X-Frame-Options` | `DENY` — anti-clickjacking (redundância do `frame-ancestors 'none'` da CSP) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` — não vaza caminho/query para outras origens |
| `Permissions-Policy` | nega câmera, microfone e geolocalização |

Detalhes da CSP: `connect-src` inclui a origem da API (`NEXT_PUBLIC_API_URL`); em modo dev entram
`'unsafe-eval'` (HMR) e `ws:/wss:`, removidos automaticamente no build de produção. HSTS não é
enviado pelo Next — fica no proxy HTTPS de produção (ver `docs/deploy-producao.md`).

> **Atenção ao rodar `next build` localmente:** pare o `next dev` antes. Os dois compartilham a
> pasta `.next/` e um build feito com o dev server ativo sai contaminado com artefatos de dev
> (sintoma: `EvalError: Code generation from strings disallowed` no middleware ao usar `next start`).

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
| Armazenamento do token | Cookie `HttpOnly` (invisível ao JS) | `expo-secure-store` (criptografado) |
| Como autentica | Cookie + `X-CSRF-Token`, via proxy `/api/*` | `Authorization: Bearer`, direto na API |
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

## Multi-tenancy (SaaS) — impacto no frontend (Fase 0.7)

O FaciliChat será um **SaaS multi-tenant**: cada **Empresa** (empresa cliente) tem dados
isolados. O que muda nos frontends:

- **O tenant vem do token, não do frontend.** O backend já filtra tudo por `EmpresaID` (lido
  do JWT). Os frontends **não** enviam o tenant — apenas o `Authorization: Bearer <token>` de sempre.
- **Exibir a Empresa atual** no cabeçalho/perfil (nome da empresa do usuário logado), para o
  usuário saber em qual contexto está.
- **Papéis são por empresa:** `auth.isGerente()`/`isSupervisor()` continuam valendo, mas
  representam o papel **dentro** daquela Empresa. (O branding usa "Gestor" no lugar de "Gerente";
  a renomeação `isGerente→isGestor` e os perfis RH/Financeiro/Superadmin estão na Fase 0.6 do plano.)
- **Área de Superadmin (somente web):** um espaço separado do painel da empresa, para a Iugo
  Performance (dona da plataforma) cadastrar/suspender Empresas — provável route group
  `frontend/web/src/app/(plataforma)/...`.
- **Tipos:** adicionar `Empresa` e o campo `EmpresaID` em `frontend/web/src/types/index.ts`
  **e** `frontend/mobile/lib/types.ts`, mantendo a sincronia com o backend.

> Detalhes e checklist em `docs/plano-implementacao.md` (Fase 0.7); arquitetura em `docs/arquitetura.md`.

---

## Pendente de implementação

- [ ] **Suporte multi-tenant no front (Fase 0.7):** exibir Empresa atual + área de Superadmin + tipos
- [ ] Tela de chat/mensagens dentro de um chamado (web e mobile)
- [ ] Tela de criação de chamado (formulário) no mobile
- [ ] Tela de usuários no painel web (para Gerentes)
- [ ] Filtros e busca na listagem de chamados
- [ ] Notificações push no mobile
- [ ] Indicadores visuais de IA nas mensagens automáticas

---

*Última atualização: 2 de julho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
