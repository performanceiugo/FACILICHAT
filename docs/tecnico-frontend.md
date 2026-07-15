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
    ├── error.tsx            ← boundary global de erro de runtime (B3, client component)
    ├── not-found.tsx        ← página 404 global (B3)
    ├── erro.module.css      ← estilos compartilhados de error.tsx e not-found.tsx
    ├── page.tsx             ← redireciona / → /login
    ├── (auth)/
    │   └── login/
    │       ├── page.tsx     ← tela de login
    │       └── login.module.css
    └── painel/              ← pasta real (não route group), URLs /painel/*
        ├── layout.tsx       ← delega para <AdminShell> (proteção de rota + sidebar)
        ├── page.tsx         ← redireciona /painel → /painel/visao-geral
        ├── visao-geral/
        │   ├── page.tsx     ← visão executiva com KPIs e agregações dos chamados existentes
        │   └── visao-geral.module.css
        ├── chamados/
            ├── page.tsx     ← listagem de chamados
            └── chamados.module.css
        └── supervisores/
            ├── page.tsx     ← cards expansíveis da equipe (frontend-first)
            └── supervisores.module.css
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

### Páginas de erro globais (`app/error.tsx` e `app/not-found.tsx`) — item B3

O App Router usa esses dois arquivos na raiz do `app/` como fallback de **toda** a aplicação:
`error.tsx` é o boundary de erro de runtime (client component obrigatório — recebe `reset()` para
re-renderizar o segmento que falhou, exposto como botão "Tentar novamente") e `not-found.tsx` é o
404 (rota inexistente ou `notFound()` chamado em página). Ambos em PT, com estilos compartilhados
em `app/erro.module.css` no mesmo padrão visual do card de login (tokens do design system, sem
valores hardcoded). O `error.tsx` loga o erro só no `console.error` — o usuário nunca vê stack
trace. Se alguma seção futura precisar de tratamento próprio, basta criar um `error.tsx` local no
segmento, que o Next usa o mais próximo da falha.

### Acessibilidade (a11y) — item B5

Convenções aplicadas em todo o web e obrigatórias em telas novas:
- **Foco de teclado:** regra global `:focus-visible` no `globals.css` (anel de 2px em
  `--border-focus`) cobre qualquer elemento focável. Não escrever `outline: none` sem entregar
  indicação visual equivalente na mesma regra (como fazem os inputs do login com borda+sombra).
- **Navegação:** `<nav>` com `aria-label`, link da rota atual com `aria-current="page"`,
  ícones decorativos (SVGs, avatar de iniciais) com `aria-hidden="true"`.
- **Estados assíncronos:** mensagem de carregamento com `role="status"` e mensagem de erro com
  `role="alert"` — ambos têm `aria-live` implícito (polite/assertive), então o leitor de tela
  anuncia a mudança sem foco no elemento. Padrão já usado em chamados, visão geral, login e
  empresas; cards expansíveis usam `aria-expanded`/`aria-controls` (ver supervisores).

### Visão geral do painel (`/painel/visao-geral`)

A visão geral combina duas fontes reais do mesmo tenant. `api.relatorios.visaoGeral()` consome
`GET /relatorios/visao-geral` para os quatro KPIs executivos — chamados abertos, SLA estourado,
primeira resposta média e resolução média — enquanto `api.chamados.listar()` alimenta distribuição
por status, volume por fila, categorias e a lista de atenção. O contrato
`VisaoGeralRelatorio` fica em `types/index.ts`; médias sem amostra permanecem `null` e são exibidas
como travessão, nunca substituídas por números fictícios.

**Atualização automática (`useAtualizacaoPeriodica`):** esta página e a de Chamados (abaixo)
reexecutam o fetch a cada ~20s, estilo painel de BI, em vez de exigir reload manual — hook em
`frontend/web/src/lib/useAtualizacaoPeriodica.ts`, sem dependência nova (SWR/React Query ficaram de
fora por decisão de escopo). O hook pausa o polling quando a aba fica em segundo plano (Page
Visibility API) e busca na hora ao voltar. Nas duas páginas, `carregando`/`erro` só aparecem na
carga inicial — atualizações de fundo trocam os dados em silêncio e mantêm a última leitura boa se
uma falhar. Na visão geral, o mesmo ciclo busca relatório e chamados com `Promise.all`, evitando
mostrar KPIs de uma leitura e distribuições de outra.

### Guarda de montagem em `useEffect` com fetch — item B2

Toda tela (web ou mobile) que busca dados assíncronos ao montar guarda um `useRef(true)`
(`montadoRef`/`ativoRef`) setado para `false` no cleanup do `useEffect`, e só chama `setState` no
`then`/`catch`/`finally` da chamada se a ref ainda estiver `true`. Evita o warning/estado
inconsistente de atualizar um componente já desmontado (ex.: usuário navega para outra tela antes
da API responder). Preferido a `AbortController` aqui porque o cliente HTTP (`lib/api.ts` web e
mobile) não expõe `signal` nas suas funções — a ref é a forma mais simples de obter o mesmo efeito
sem mexer no cliente. Exemplos: `painel/chamados/page.tsx`, `painel/visao-geral/page.tsx`,
`plataforma/empresas/page.tsx` (web) e `(tabs)/chamados.tsx`, `(tabs)/perfil.tsx` (mobile).
**Toda tela nova com fetch em `useEffect` deve seguir o mesmo padrão.**

### Supervisores (`/painel/supervisores`)

A página de supervisores conclui o item `868k60w2a` com dados reais dos endpoints
`GET /relatorios/supervisores` e `GET /chamados/?supervisor_id={UUID}`. Os indicadores de topo são
derivados das métricas da equipe; cada card apresenta abertos, atrasados e primeira resposta média.
Ao expandir, a fila daquele supervisor é buscada sob demanda e mantida em cache para reaberturas.
Carregamento e erro da fila são isolados por card, sem bloquear os demais supervisores, e ausência
de dados continua explícita — nunca são usados nomes ou números fictícios.

A lista de métricas usa a atualização automática existente a cada ~20 segundos, preservando a
última leitura boa se uma atualização de fundo falhar. A fila aberta não é substituída durante esse
polling; ela representa o recorte carregado quando o Gestor abriu o card.

O link na sidebar permanece separado porque pertence ao item `868k60w2w`; a rota também pode ser
acessada diretamente em `/painel/supervisores`.

### Navegação do painel

A sidebar concluída no item `868k60w2w` oferece quatro destinos: Visão geral
(`/painel/visao-geral`), Supervisores (`/painel/supervisores`), Todos os tickets
(`/painel/chamados`) e Alertas (`/painel/visao-geral#atencao`). O último é uma âncora para o painel
operacional já existente; a página de oportunidades comerciais continua reservada para a Fase 6.
As rotas principais expõem `aria-current="page"` e conservam o destaque visual azul.

### Painel de atenção

O item `868k7vrx5` classifica chamados abertos em três tipos: **Crítico** (prioridade crítica),
**Oportunidade** (fila Comercial já roteada) e **Atenção** (alta prioridade ou ainda recebido).
Essa classificação não antecipa a IA: somente a fila persistida permite usar “Oportunidade”. Cada
linha aponta para `/painel/chamados#chamado-{UUID}`; o card de destino usa `:target` para receber
foco visual azul e preservar a rastreabilidade do alerta até o ticket.

### Padrão do cliente HTTP (`lib/api.ts`)

Toda chamada ao backend passa pela função `req<T>()` que:
- Usa a base `/api` — o **proxy do Next** (`rewrites` no `next.config.ts`), nunca a API direto.
  Mesma origem ⇒ o cookie de sessão é first-party e a CSP fecha em `connect-src 'self'` (S6/M6).
- **Não** injeta credencial: o navegador envia sozinho o cookie `sessao` (`HttpOnly`).
- Anexa o header `X-CSRF-Token` (lido do cookie `csrf_token`) em `POST`/`PUT`/`PATCH`/`DELETE`.
- Em `401` (access token de 15min expirado — item S15), chama `/autenticacao/atualizar`
  automaticamente (o cookie `refresh` vai sozinho, sendo mesma origem) e repete a chamada
  original **uma única vez**. Só se essa renovação falhar é que limpa o local e vai ao login.
  **Single-flight:** chamadas paralelas que tomam 401 ao mesmo tempo compartilham a mesma
  renovação em vez de cada uma tentar rotacionar o refresh token — rotações concorrentes
  disparariam a própria detecção de reuso do backend (S15) e derrubariam a sessão à toa.

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

### Validação nativa em português (`lib/validacao.ts`) — item M13

Os balões de validação do HTML5 (`required`, `type="email"`) aparecem no idioma do **navegador**,
não do app — um Chrome em inglês mostraria "Please include an '@' in the email address..." mesmo com
a página em português. O módulo `lib/validacao.ts` exporta dois handlers que traduzem essas
mensagens via `setCustomValidity`, mantendo a validação nativa (o formulário continua bloqueando o
submit sozinho):

- `aoInvalidarCampo` (em `onInvalid`) — traduz o motivo (`valueMissing` → "Preencha este campo.",
  `typeMismatch` de e-mail → "Informe um e-mail válido...", genérico → "Valor inválido.").
- `limparValidacaoCustomizada` (em `onInput`) — **obrigatório junto**: enquanto houver
  `customValidity` setada o campo fica inválido para sempre; limpar ao digitar devolve a validação
  ao navegador.

Aplicado no login (`(auth)/login/page.tsx`) e no cadastro de Empresas (`plataforma/empresas/page.tsx`).
**Todo formulário novo com `required`/`type="email"` deve usar os dois handlers** — complemento do
M12, que cobre os erros vindos da API.

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
> (sintoma: `EvalError: Code generation from strings disallowed` no proxy ao usar `next start`).

### Imagem de produção (item S9)

`output: 'standalone'` no `next.config.ts` faz o `next build` gerar um servidor Node autocontido em
`.next/standalone` (só o `server.js` + os `node_modules` realmente usados). `frontend/web/Dockerfile`
(novo) usa isso num build de dois estágios: o primeiro compila com `npm ci` + `next build`, o
segundo copia só o resultado standalone e roda como usuário não-root `node`. `NEXT_PUBLIC_API_URL`
entra como build-arg (resolvida em tempo de build, não de runtime) apontando para o serviço
`backend` na rede interna do `docker-compose.prod.yml`. Dev continua usando `npm run dev` fora do
Docker — esta imagem só existe para produção. Passo a passo completo: `docs/deploy-producao.md`.

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
// Enums (estado atual — 7 perfis e fila Comercial das Fases 0.6/0.7)
UsuarioFuncao: 'Cliente' | 'Supervisor' | 'Funcionario' | 'RH' | 'Financeiro' | 'Gestor' | 'Superadmin'
ChamadoFila:  'Operacional' | 'RH' | 'Financeiro' | 'Comercial'
ChamadoStatus: 'Recebido' | 'EmAndamento' | 'Agendado' | 'Concluido' | 'Cancelado'
ChamadoPrioridade: 'Baixa' | 'Media' | 'Alta' | 'Critica'
AutorTipo: 'Cliente' | 'Supervisor' | 'Funcionario' | 'IA' | 'Sistema'
```

> Sempre que um enum for adicionado ou alterado no backend Python, deve ser atualizado nos dois arquivos de tipos do frontend.

**Mapas de exibição tipados pelos enums (item M7):** tabelas de label/cor derivadas de um enum
(ex.: `STATUS_LABEL`, `STATUS_COR`, `PRIORIDADE_COR` em `painel/chamados/page.tsx`) devem ser
`Record<ChamadoStatus, string>`/`Record<ChamadoPrioridade, string>` — nunca `Record<string, string>`.
Assim, quando um valor novo entrar no enum, o compilador aponta a tabela incompleta em vez de a
tela exibir badge vazio em runtime. Nos `catch`, tipar `err: unknown` e estreitar com
`err instanceof Error` antes de usar `.message`.

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
- [ ] Completar a visão geral com endpoints reais de relatório (SLA, primeira resposta e resolução média)
- [ ] Filtros e busca na listagem de chamados
- [ ] Notificações push no mobile
- [ ] Indicadores visuais de IA nas mensagens automáticas

---

*Última atualização: 15 de julho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
