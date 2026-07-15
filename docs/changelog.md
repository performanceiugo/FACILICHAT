# FaciliChat — Histórico de Alterações

> Registro de tudo que foi desenvolvido ou alterado no sistema, em ordem cronológica.
> Atualizado automaticamente a cada alteração pelo agente Claude Code.

---

## [não versionado] — 15 de julho de 2026

### Fase 4 — atribuição de supervisor a chamados (`CU: 868kcv8dp`)
- **Motivação:** ao popular o banco de demonstração com mais de um supervisor, descobrimos que
  não existia nenhuma rota de API para atribuir um supervisor a um chamado — só acontecia por
  inserção direta via script de seed. Isso também era uma lacuna real do painel do Gestor.
- **Nova rota:** `PATCH /chamados/{id}/supervisor` — exclusiva do Gestor; recebe
  `{"SupervisorID": "<uuid>" | null}`; o supervisor precisa existir com esse perfil na mesma
  Empresa (404 caso contrário); `null` remove a atribuição atual ("sem supervisor").
- **Validado:** atribuição, remoção e reatribuição retornaram `200` com `SupervisorNome`
  correto; tentativa por um Supervisor (não Gestor) retornou `403`; UUID de supervisor
  inexistente e chamado inexistente retornaram `404`; import do backend confirmado no contêiner.
- Arquivo: `backend/app/rotas/Chamados.py`.

### Dev — banco de demonstração populado com mais supervisores e chamados variados
- **Motivação:** ampliar a massa de dados de teste para validar as telas do painel (Visão geral,
  Supervisores, Todos os tickets) com mais volume e variedade antes de uma rodada de validação
  visual da aplicação.
- **Novos supervisores demo:** Fernanda Ribeiro (`fernanda@demo.facilichat.dev`) e Bruno Andrade
  (`bruno@demo.facilichat.dev`), criados via `POST /usuarios/equipe` como Gestor, mesma senha
  padrão de demonstração.
- **13 novos chamados** criados via API (nunca SQL direto) pelos 4 clientes demo, cobrindo as 4
  filas (Operacional/RH/Financeiro/Comercial), as 4 prioridades e categorias inéditas
  (Ar-condicionado, Portão, Pintura, Atestado, Proposta, Segurança, Limpeza, Inadimplência,
  Elevador, Jardinagem, Escala, Renovação, Boleto); parte deles distribuída entre Roberto,
  Fernanda e Bruno com status variados (`EmAndamento`/`Agendado`/`Concluido`/`Cancelado`) via a
  nova rota de atribuição, para dar lastro real ao relatório de desempenho por supervisor.
- **Sem alteração de esquema:** só dado de demonstração; qualquer registro pode ser removido a
  qualquer momento sem risco (não é dado real de cliente).

### Fase 4 — página de tickets com filtros e busca por cliente (`CU: 868k60w2j`)
- **Tabela pesquisável:** `/painel/chamados` (agora "Todos os tickets") lista os chamados da
  Empresa em tabela com colunas Ticket/Cliente/Supervisor/Status/Abertura, em vez dos cards
  anteriores.
- **Filtros combináveis:** busca por nome de cliente (tolerante a acento/caixa), supervisor
  (incluindo "sem supervisor"), status, categoria e período (De/Até); todas as opções vêm dos
  dados reais da Empresa, sem lista fixa.
- **Backend:** `GET /chamados/` passa a fazer join com `Usuario` (cliente e supervisor, via
  `aliased`) e devolve `ClienteNome`/`SupervisorNome` junto de `ClienteID`/`SupervisorID`, sempre
  escopado pela Empresa autenticada — nenhum nome de usuário de outro tenant é exposto.
- **Compatibilidade:** filtragem por texto/data acontece no cliente sobre a lista já carregada,
  preservando o polling existente e a ordenação por criação mais recente.
- **Validado:** `tsc --noEmit` e `npm run lint` sem erros; import do backend (`app.main`)
  confirmado no contêiner.
- Arquivos: `backend/app/rotas/Chamados.py`, `frontend/web/src/app/painel/chamados/page.tsx`,
  `chamados.module.css`, `frontend/web/src/types/index.ts`.

### Login — primeira página pós-login passa a ser a Visão geral
- Após autenticar, usuários não-Superadmin agora são redirecionados para `/painel/visao-geral`
  em vez de `/painel/chamados`, para que a leitura executiva (KPIs, desempenho por supervisor)
  seja a primeira coisa vista ao entrar no painel.
- Mudança puramente de navegação, sem alteração de regra de negócio.
- Arquivo: `frontend/web/src/app/(auth)/login/page.tsx`.

### Correção — middleware ainda mandava para `/painel/chamados` após login
- **Bug:** a mudança acima só ajustou o `router.push` do formulário de login. O `middleware.ts`
  (que roda no servidor antes do React) ainda tinha `/painel/chamados` hardcoded nos redirects de
  `/login` (usuário já autenticado) e de `/plataforma` (não-Superadmin). Resultado: abrir
  `localhost:3000` com uma sessão já ativa (cookie presente) caía direto em `/painel/chamados` —
  não em `/painel/visao-geral` —, ignorando o comportamento client-side.
- **Correção:** os dois redirects do `middleware.ts` agora apontam para `/painel/visao-geral`,
  igual ao `login/page.tsx`. O mesmo ajuste foi replicado no guard client-side de
  `/plataforma/empresas` (que mandava um não-Superadmin para `/painel/chamados`).
- Arquivos: `frontend/web/src/middleware.ts`, `frontend/web/src/app/plataforma/empresas/page.tsx`.

### Fase 0.5 — ESLint com config explícita no web (`V2`, `CU: 868kb32cg`)
- **Motivação:** `npm run lint` caía no assistente interativo do `next lint` (nenhum
  `eslint.config.*` existia); esse comando some no Next.js 16.
- **Config explícita:** novo `frontend/web/eslint.config.mjs` (flat config) usa `FlatCompat` para
  reaproveitar os presets `next/core-web-vitals`/`next/typescript`; artefatos de build
  (`.next/`, `out/`, `build/`) ficam fora do lint.
- **Script:** `package.json` → `"lint": "eslint ."`; nova dependência de dev `@eslint/eslintrc`.
- **Validado:** `npm run lint` roda sem interação (exit 0; 4 warnings pré-existentes e não
  relacionados em `lib/api.ts`), `tsc --noEmit` e `npm run build` sem erro.
- Arquivos: `frontend/web/package.json`, `frontend/web/eslint.config.mjs` (novo).

### Fase 0.5 — Docker Desktop/Engine atualizado (`V1`, `CU: 868kb32ap`)
- **Motivação:** auditoria de versões de 10/07/2026 apontou o Docker Engine 29.5.3 desatualizado;
  a 29.6.1 traz correções de segurança do Engine.
- **Atualização:** Docker Desktop 4.79.0 → 4.82.0 via `winget upgrade`, trazendo Engine
  29.5.3 → 29.6.1 e Compose v5.1.4 → v5.3.0.
- **Impacto observado:** o reinício do daemon derrubou os containers do projeto
  (`facilichat_db`, `facilichat_backend`); religados com `docker compose up -d` e confirmados
  saudáveis (`docker ps`).
- Nenhum arquivo do repositório foi alterado — mudança na máquina local, conforme o item já
  previa.

### Painel — botão de saída visível no ambiente de desenvolvimento
- O rótulo do botão “Sair” foi centralizado para não ficar encoberto pelo indicador flutuante do
  Next.js durante a validação local; o comportamento de logout não foi alterado.
- Arquivo: `frontend/web/src/components/painel/AdminShell.module.css`.

### Fase 4 — seção Desempenho por supervisor (`CU: 868k60w1y`)
- **Leitura executiva:** a Visão geral combina carga, primeira resposta, resolvidos/recebidos e
  gargalos reais para apresentar o estado operacional de cada supervisor.
- **Integração:** os contratos de carga e desempenho são carregados junto aos demais dados do
  painel e cruzados pelo ID do supervisor, sem métricas inventadas no frontend.
- **Validado:** TypeScript sem erros, rota local com status `200` e aprovação visual do usuário;
  Roberto Supervisor exibiu 5 abertos, 2 de 7 resolvidos, primeira resposta de 34 min e estado
  "Precisa de atenção".
- Arquivos: `frontend/web/src/app/painel/visao-geral/page.tsx`, `visao-geral.module.css`,
  `frontend/web/src/lib/api.ts`, `frontend/web/src/types/index.ts`.

### Fase 4 — desempenho por supervisor com lastro (`CU: 868k7vrwh`)
- **Relatório objetivo:** `GET /relatorios/desempenho-supervisores` retorna recebidos (atribuições),
  resolvidos (`Concluido`), parados (`Atualizacao` além do limite configurável) e taxa de resolução.
- **Sem ranking inventado:** supervisores sem chamados permanecem na resposta com contagens zero e
  taxa `null`; não há nota subjetiva.
- **Validado:** Roberto Supervisor retornou 7 recebidos, 2 resolvidos e 28,57%; parados mudou de
  3 para 5 ao reduzir temporariamente o limite 72h→1h, depois restaurado para 72h.
- Arquivo: `backend/app/rotas/Relatorios.py`.

### Fase 4 — alerta de cobertura descoberta (`CU: 868k7vrw8`)
- **Fonte estruturada:** nova entidade `CoberturaTurno` registra Empresa, condomínio, posto, turno,
  início/fim, Funcionário responsável e momento da confirmação; nenhuma regra interpreta texto.
- **Operação:** Supervisor e Gestor podem registrar/listar coberturas e confirmar um Funcionário do
  mesmo tenant pelas rotas `/coberturas`.
- **Alerta:** `GET /relatorios/coberturas-descobertas`, exclusivo do Gestor, lista períodos atuais ou
  futuros sem responsável confirmado; turnos encerrados deixam de exigir ação.
- **Isolamento:** tabela com `EmpresaID`, filtros explícitos e RLS forçada.
- **Validado:** duas descobertas passaram a uma após confirmação; responsável/data foram
  persistidos e turno passado foi excluído. Banco dev resetado, recriado e deixado limpo ao final.
- Arquivos: `backend/app/modelos/CoberturaTurno.py`, `modelos/__init__.py`,
  `backend/app/rotas/Coberturas.py`, `Relatorios.py`, `backend/app/main.py`, `backend/app/rls.sql`.

### Fase 4 — alerta configurável de gargalo (`CU: 868k7vrvm`)
- **Configuração por Empresa:** nova tabela `EmpresaConfiguracoes` persiste
  `LimiteGargaloHoras`, com padrão efetivo de 72h e isolamento por `EmpresaID`/RLS.
- **Gestão:** Gestor consulta e altera o limite por `GET/PATCH /relatorios/configuracao-gargalo`;
  valores aceitos ficam entre 1 e 720 horas.
- **Relatório:** `GET /relatorios/gargalos` lista apenas chamados ativos parados além do limite e
  calcula `TempoParadoHoras` a partir de `Chamado.Atualizacao`, sem duração armazenada ou estimada.
- **Compatibilidade:** a nova tabela é criada idempotentemente por `create_all`, sem exigir reset ou
  `ALTER TABLE` nas instalações existentes enquanto Alembic permanece pendente.
- **Validado:** limite 72→24→72, gargalos 4→8, todas as durações respeitando o limite e payload
  zero rejeitado com `422`; políticas RLS reaplicadas com sucesso.
- Arquivos: `backend/app/modelos/Empresa.py`, `modelos/__init__.py`,
  `backend/app/rotas/Relatorios.py`, `backend/app/rls.sql`, `docs/tecnico-backend.md`.

### Fase 4 — painel “O que precisa da sua atenção” (`CU: 868k7vrx5`)
- **Três tipos reais:** chamados abertos são apresentados como Crítico, Atenção ou Oportunidade;
  oportunidade significa fila Comercial já persistida, sem alegar detecção de IA antes da Fase 5.
- **Rastreabilidade:** cada alerta abre diretamente o card correspondente em Todos os tickets e o
  destino recebe realce azul por `:target`.
- **Ordem operacional:** críticos aparecem primeiro, depois atenções e oportunidades; dentro do
  tipo, prioridade e antiguidade organizam a leitura.
- **Validado:** `tsc --noEmit`, 2 críticos e 5 atenções reais no banco local, destinos sem erro de
  runtime e aprovação visual do usuário. Não havia oportunidade aberta e nenhum dado foi inventado.
- Arquivos: `frontend/web/src/app/painel/visao-geral/page.tsx`, `visao-geral.module.css`,
  `frontend/web/src/app/painel/chamados/page.tsx`, `chamados.module.css`.

### Fase 4 — navegação completa do painel (`CU: 868k60w2w`)
- **Sidebar:** adicionados os atalhos Visão geral, Supervisores, Todos os tickets e Alertas, com
  ícones de linha, estado ativo e `aria-current` nas rotas principais.
- **Destino honesto:** Alertas aponta para `#atencao` na Visão geral; não foi criada uma rota vazia
  nem antecipada a página de oportunidades comerciais prevista para a Fase 6.
- **Validado:** `tsc --noEmit`, destinos com resposta `200` e aprovação visual do usuário.
- Arquivos: `frontend/web/src/components/painel/AdminShell.tsx`,
  `frontend/web/src/app/painel/visao-geral/page.tsx`, `visao-geral.module.css`.

### Fase 4 — página de Supervisores com dados reais (`CU: 868k60w2a`)
- **Métricas da equipe:** `/painel/supervisores` passou a consumir o relatório real de supervisores
  e derivar dele os totais de equipe, chamados abertos e SLA atrasado.
- **Fila sob demanda:** abrir um card consulta `GET /chamados/?supervisor_id={UUID}`; cada fila tem
  carregamento, erro com repetição e cache próprios, sem bloquear os demais cards.
- **Sem dados simulados:** estados vazio e sem amostra permanecem explícitos; nomes, contagens e
  chamados vêm sempre da Empresa autenticada.
- **Atualização:** métricas usam polling de ~20 segundos e mantêm a última leitura boa em falha de
  fundo; a fila expandida conserva o recorte carregado no clique.
- **Validado:** `tsc --noEmit`, resposta `200` sem erro de runtime e aprovação visual do usuário.
- Arquivos: `frontend/web/src/app/painel/supervisores/page.tsx`, `supervisores.module.css`,
  `frontend/web/src/lib/api.ts`, `frontend/web/src/types/index.ts`, `docs/tecnico-frontend.md`.

### Fase 4 — fila de chamados por supervisor (`CU: 868k60w1g`)
- **Filtro do Gestor:** `GET /chamados/?supervisor_id={UUID}` retorna somente os chamados
  atribuídos ao supervisor solicitado, preservando a ordenação decrescente por criação.
- **Isolamento e autorização:** o filtro é exclusivo do Gestor; o supervisor precisa existir com
  esse perfil na mesma Empresa. Outros perfis recebem `403` e UUID inexistente, de outro tenant ou
  de outro perfil recebe `404`, sem permitir enumeração entre Empresas.
- **Compatibilidade:** chamadas sem `supervisor_id` mantêm a visibilidade anterior — Gestor e
  Supervisor veem todos os chamados da Empresa; Cliente vê somente os próprios.
- **Validado na API real:** supervisor válido retornou 7 chamados (`200`) e todos tinham a
  atribuição solicitada; UUID inexistente retornou `404`; uso pelo Supervisor retornou `403`.
- Arquivos: `backend/app/rotas/Chamados.py`, `docs/tecnico-backend.md`.

### Fechada a seção 📄 Documentação do levantamento (`D1`, `D2`, `D4`, `D5`, `D7`, `D8`)
- **`D1`/`D7` — enums `AutorTipo` divergentes:** as duas ocorrências de `Humano/IA/Sistema` no
  `plano-implementacao.md` (item histórico da Fase 0 e notas rápidas de arquitetura) foram
  sincronizadas com o enum real do código (`Cliente/Supervisor/Funcionario/IA/Sistema`);
  o `tecnico-backend.md` já estava correto nesse ponto, mas ainda citava `Gerente` na tabela de
  `Funcao` (4 perfis) e nas permissões de chamados — atualizado para os 7 perfis com `Gestor`.
- **`D2` — datas 2025/2026 no changelog:** as versões antigas `0.1.0`, `0.2.0`, `0.3.0` e `0.3.1`
  diziam "2025" entre entradas do mesmo período de 2026 (typo de calendário) — padronizadas para
  junho de 2026. Mantido o "07/2025" da nota de WhatsApp (data externa real da política da Meta).
- **`D4` — comando de execução do backend:** o "Como rodar" do `tecnico-backend.md` foi reescrito:
  o caminho padrão é `docker compose up -d` (sobe Postgres **e** API juntos, como o
  `docker-compose.yml` faz hoje) e o `uvicorn` direto virou alternativa documentada com
  `docker compose up -d db` — o comando funciona desde o `C2` (`backend/app/__init__.py`).
- **`D5` — `visao-geral.md` desatualizado:** reescrito para o estado real — 7 perfis implementados
  (removida a nota "código ainda tem 4 perfis"), 4 filas com `Comercial`, multi-tenant/Superadmin
  como entregues, painel com KPIs reais e atualização automática, segurança atual (senha 15+,
  sessão revogável), tickets irmãos; "próximos passos" agora só lista o que de fato falta
  (chat, WhatsApp, IA, visitas, relatório por supervisor, deploy) e a tabela de estado separa
  feito de planejado.
- **`D8` — checklist de aceite do branding:** criada a seção "Checklist de aceite do branding"
  no `arquitetura.md` com critérios verificáveis por eixo — design system, anti-amnésia,
  multi-tenant, IA ancorada, visita técnica e jornadas — e nota de status por eixo; o aceite é
  reavaliado a cada entrega que toque o eixo.
- Arquivos: `docs/plano-implementacao.md`, `docs/tecnico-backend.md`, `docs/changelog.md`,
  `docs/visao-geral.md`, `docs/arquitetura.md`.

### Fase 4 — relatório de carga por supervisor (`CU: 868k60w1e`)
- **Endpoint:** criado `GET /relatorios/supervisores`, exclusivo do Gestor, com supervisores da
  Empresa autenticada, total de chamados abertos, atrasados e primeira resposta média em minutos.
- **Lastro da métrica:** a primeira resposta exige mensagem do supervisor atribuído ao chamado,
  posterior à abertura; mensagens de outro autor, sistema ou IA não contaminam a média.
- **Estado vazio honesto:** supervisores sem chamados continuam na lista com contagens zero e
  média `null`, permitindo que o Gestor veja toda a equipe.
- **Validado:** AST do módulo íntegra e consulta executada contra o PostgreSQL local, retornando
  `RELATORIO_OK` com os dados sem erro de SQL.
- Arquivos: `backend/app/rotas/Relatorios.py`, `docs/tecnico-backend.md`.

### Fase 4 — KPIs reais na visão geral do Gestor (`CU: 868k60w1r`)
- **Integração:** `/painel/visao-geral` passou a consumir `GET /relatorios/visao-geral` junto da
  lista de chamados, substituindo os indicadores aproximados por chamados abertos, SLA estourado,
  primeira resposta média e resolução média calculados no backend para a Empresa autenticada.
- **Sem dados inventados:** médias sem amostra aparecem como travessão; durações são apresentadas
  em minutos ou horas sem alterar a precisão retornada pela API.
- **Atualização automática:** o polling existente atualiza KPIs e distribuições em conjunto e
  preserva a última leitura boa quando uma atualização de fundo falha.
- **Validado:** `npm.cmd run build` concluído com compilação, lint, checagem de tipos e geração
  estática da rota `/painel/visao-geral`. A inspeção no navegador integrado não foi executada
  porque nenhum navegador estava disponível na sessão.
- Arquivos: `frontend/web/src/types/index.ts`, `frontend/web/src/lib/api.ts`,
  `frontend/web/src/app/painel/visao-geral/page.tsx`, `docs/tecnico-frontend.md`.

### Fechado `B5` — acessibilidade no web: foco de teclado, ARIA na navegação e estados anunciados
- **Problema:** nenhum anel de foco global para navegação por teclado (e `outline: none` em pontos
  do login/erro), `<nav>` da sidebar sem `aria-label`/`aria-current`, e estados de
  carregando/erro sem live region (leitores de tela não anunciavam falhas nem carregamento).
- **Correção:** regra global `:focus-visible` no `globals.css` (anel de 2px em `--border-focus`,
  vale para qualquer elemento focável; regras locais mais específicas continuam valendo);
  removido o `:focus-visible` local redundante do `erro.module.css`; sidebar com
  `aria-label="Navegação principal"`, `aria-current="page"` no link ativo e ícones/avatar com
  `aria-hidden`; estados de carga com `role="status"` e erros com `role="alert"` (aria-live
  implícito) em chamados, visão geral, login e empresas. Supervisores já estava conforme.
- **Validado:** `tsc --noEmit` limpo; Playwright no dev server real — Tab pelo teclado mostra
  outline computado `2px solid rgb(20,138,245)` no botão do login e nos links da sidebar,
  senha errada dispara o `p[role="alert"]`, e a navegação autenticada expõe `aria-label` +
  `aria-current="page"` no link da rota atual.
- Arquivos: `frontend/web/src/app/globals.css`, `erro.module.css`,
  `frontend/web/src/components/painel/AdminShell.tsx`, `app/painel/chamados/page.tsx`,
  `app/painel/visao-geral/page.tsx`, `app/(auth)/login/page.tsx`,
  `app/plataforma/empresas/page.tsx`.

### Fechado `B3` — páginas de erro globais do web (`error.tsx` e `not-found.tsx`)
- **Problema:** o painel web não tinha `error.tsx` nem `not-found.tsx` — erro de runtime mostrava a
  tela técnica padrão do Next (em inglês, com stack trace em dev) e rota inexistente caía no 404
  genérico do framework.
- **Correção:** criados `app/error.tsx` (boundary global client-side com botão "Tentar novamente"
  via `reset()`) e `app/not-found.tsx` (404 com link "Voltar ao início"), ambos em PT e no design
  system (tokens de `globals.css`, card no mesmo padrão visual do login). Estilos compartilhados no
  novo `app/erro.module.css`.
- **Validado:** `tsc --noEmit` limpo; Playwright no dev server real — rota inexistente renderiza o
  404 customizado (desktop 1440×900 e mobile 390×844) e uma rota temporária que lança exceção
  renderiza o boundary com título e botão corretos (rota de teste removida após a captura).
- Arquivos: `frontend/web/src/app/error.tsx` (novo), `frontend/web/src/app/not-found.tsx` (novo),
  `frontend/web/src/app/erro.module.css` (novo).

### Fechado `B2` — guarda de montagem nos `useEffect` de fetch (web e mobile)
- **Problema:** telas que buscam dados ao montar podiam chamar `setState` depois de o componente
  já ter sido desmontado (ex.: usuário navega para outra tela antes da API responder).
- **Correção:** `painel/chamados/page.tsx` e `painel/visao-geral/page.tsx` já tinham a guarda
  (`montadoRef`/`ativoRef`); adicionada a mesma guarda em `plataforma/empresas/page.tsx` (web) e em
  `(tabs)/chamados.tsx`/`(tabs)/perfil.tsx` (mobile). Convenção documentada no
  `tecnico-frontend.md` para telas novas.
- **Validado:** `tsc --noEmit` limpo nos dois fronts.
- Arquivos: `frontend/web/src/app/plataforma/empresas/page.tsx`,
  `frontend/mobile/app/(tabs)/chamados.tsx`, `frontend/mobile/app/(tabs)/perfil.tsx`,
  `docs/tecnico-frontend.md`.

### Fechado `M9` — comentários nos arquivos CSS do frontend web
- **Problema:** vários `*.module.css` do painel não tinham nenhum comentário, violando a regra
  obrigatória de comentários do `CLAUDE.md`.
- **Correção:** adicionado cabeçalho de arquivo + comentário por bloco lógico em
  `login.module.css`, `chamados.module.css`, `empresas.module.css` e `visao-geral.module.css`.
  `globals.css` e `supervisores.module.css` já estavam conformes (não precisaram de mudança).
  Mudança puramente de comentários — nenhuma classe ou valor de estilo foi alterado (conferido
  com `git diff` antes de fechar o item).
- Arquivos: `frontend/web/src/app/**/*.css`.

### Fechado `M8` (obsoleto) — `token()` duplicado entre `api.ts` e `auth.ts`
- **Contexto:** o problema descrito (duas fontes de verdade para o token de acesso) deixou de
  existir como efeito colateral do item `S6` — a sessão do painel web passou a viajar num cookie
  `HttpOnly`, e nenhum dos dois arquivos guarda ou injeta token em JavaScript hoje.
- **Ação:** fechado sem alteração de código, com a nota de que a correção original (`api.ts`
  importar `auth.token()`) não se aplica mais.
- Arquivos: nenhum alterado.

### Fechado `M7` — tipagem estrita na página de chamados do painel (web)
- **Contexto:** dos três pontos originais do item, `erro.detail` não tipado já havia sido resolvido
  pelo M12 (`extrairDetail` com `unknown` em `lib/api.ts`) e quase todos os `catch` já usavam
  `err instanceof Error` — restava a página de chamados.
- **Correção:** `STATUS_LABEL`/`STATUS_COR` tipados como `Record<ChamadoStatus, string>` e
  `PRIORIDADE_COR` como `Record<ChamadoPrioridade, string>` (um valor novo no enum passa a quebrar
  a compilação em vez de renderizar badge vazio); `catch` do fetch com `err: unknown` +
  `instanceof Error` e mensagem padrão em português. Regra registrada no `tecnico-frontend.md`
  (mapas de exibição sempre tipados pelo enum), aproveitando para corrigir a lista de enums
  defasada da seção "Tipos compartilhados" (ainda citava 4 perfis/"Gerente" e 3 filas).
- **Validado:** `tsc --noEmit` limpo; página de chamados servindo normalmente no dev server.
- Arquivos: `frontend/web/src/app/painel/chamados/page.tsx`, `docs/tecnico-frontend.md`.

### Fechado `M2` — `IntegrityError` do cadastro tratado (corrida TOCTOU no check de e-mail)
- **Problema:** o check de e-mail duplicado no cadastro não é atômico; duas requisições simultâneas
  passavam juntas por ele e a segunda estourava a `UNIQUE` do banco como **500** não tratado.
- **Correção:** `IntegrityError` capturado no commit de `_persistirUsuario` → rollback + **400 com a
  mesma resposta neutra do S7** ("Nao foi possivel concluir o cadastro com os dados informados") —
  resposta específica reabriria a enumeração de e-mail. Mesmo tratamento na rota da plataforma
  (`POST /plataforma/empresas`): CNPJ no `flush` e e-mail do gestor no `commit` (mensagens
  específicas lá, rota exclusiva do Superadmin; rollback nunca deixa Empresa órfã).
- **Validado:** 4 requisições paralelas reais via curl (um 200, três 400 neutros, nenhum 500) e
  teste determinístico dentro do container forçando a corrida exata (duas `_persistirUsuario`
  concorrentes com barreira após os pre-checks: A criou, B recebeu 400 neutro da constraint —
  antes vazaria `IntegrityError`). Usuários de teste removidos ao final.
- Arquivos: `backend/app/rotas/Usuarios.py`, `backend/app/rotas/Plataforma.py`,
  `docs/tecnico-backend.md`.

### Fechado `M13` — validação nativa do navegador traduzida para português (web)
- **Problema (relatado pelo usuário com screenshot):** os balões de validação nativa do HTML5
  (`required`, `type="email"`) aparecem no idioma do navegador — "Please include an '@' in the
  email address..." — no login do painel e no cadastro de Empresas. Complemento do M12, que só
  cobriu erros vindos da API.
- **Correção:** novo `frontend/web/src/lib/validacao.ts` com handlers reutilizáveis
  `aoInvalidarCampo` (`onInvalid` → `setCustomValidity` em PT por motivo: campo vazio, e-mail sem
  formato, genérico) e `limparValidacaoCustomizada` (`onInput` → limpa para o navegador revalidar);
  aplicados aos campos de `(auth)/login/page.tsx` e `plataforma/empresas/page.tsx`.
- **Validado:** `tsc --noEmit` limpo e Playwright lendo `validationMessage` na página real —
  e-mail sem `@` → "Informe um e-mail válido (ex.: nome@dominio.com).", campos vazios → "Preencha
  este campo.", e o campo destrava ao digitar valor válido.

### Fechado `M1` — validação Pydantic de tamanho/força de senha e limites de entrada
- **Consulta prévia (`verificar-seguranca`):** OWASP Authentication Cheat Sheet atual — mínimo de
  senha **15 caracteres para aplicação sem MFA** (8 com MFA), máximo ≥ 64 para passphrases, **sem**
  regras de composição, aceitar todos os caracteres, nunca truncar. **Decisão do usuário: adotar 15**
  (em vez dos 8 que o `SenhaAlterar` do S14 usava), com teto 128.
- **Backend:** `UsuarioCriar.Senha` e `SenhaAlterar.SenhaNova` com `min_length=15, max_length=128`
  (`SenhaAtual` só com teto — senhas legadas mais curtas ainda precisam ser conferidas);
  `PrimeiroGestorCriar.Senha` (rota da plataforma) na mesma política; `max_length` nos campos de
  texto livres (`Nome`/`Condominio` 120, `Telefone` 20, `Categoria` 80 com `min_length=1`, `Resumo`
  2000, `CNPJ` 20).
- **Coerência do ambiente demo:** senha padrão do seed rotacionada de `Senha123` (8) para
  `FaciliChat2026Demo` (18) em `gerenciar_banco.py`; Gestor Demo rotacionado **pela própria API**
  (`PATCH /usuarios/eu/senha`); usuários demo recriados com `limpar-demo` + `semear`; referências
  atualizadas em `docs/setup.md` e nas skills `chamados-teste`/`subir-projeto`.
- **Validado com curl na API real:** senha curta/longa no cadastro → 422 em PT ("O campo 'Senha' é
  muito curto/longo" — traduções do M12 já cobriam `string_too_short/long`); `SenhaNova` curta →
  422; troca real do Gestor → 200 e login com a nova senha ok; `Categoria` vazia → 422; `Resumo` de
  2500 chars → 422; login demo com a senha nova ok após o re-seed.
- Arquivos: `backend/app/rotas/Usuarios.py`, `Chamados.py`, `Plataforma.py`,
  `backend/scripts/gerenciar_banco.py`, `docs/setup.md`, `docs/tecnico-backend.md`,
  `.claude/skills/chamados-teste/SKILL.md`, `.claude/skills/subir-projeto/SKILL.md`.

### Fechado `S11` (auditoria reprodutível do mobile) — fecha a seção 🔐 Segurança da Fase 0.5
- **Problema original:** o app mobile não tinha lockfile versionado, então `npm audit` não rodava de
  forma reproduzível.
- **Achado ao investigar:** o lockfile (`frontend/mobile/package-lock.json`, `lockfileVersion: 3`) já
  existia e estava commitado desde o `A8` (gerado como efeito colateral do `npx expo install --fix`).
  Faltava automatizar a auditoria e decidir o que fazer com o resultado.
- **`npm audit` local:** 13 vulnerabilidades moderadas, todas transitivas do Expo SDK 53 (`postcss`,
  `uuid`/`xcode`), com correção disponível **só** via `expo@57.0.6` (bump major). Essa migração
  sequencial (53→54→55→56→57) já está registrada como item `V3` do plano — decisão: não duplicar essa
  migração dentro do `S11`, e sim fechar o `S11` com uma auditoria automatizada que falha para
  vulnerabilidade **alta/crítica** (limiar `--audit-level=high`), deixando as moderadas conhecidas
  explicitamente sob o `V3`.
- **Implementado:** workflow `.github/workflows/auditoria-mobile.yml` (`npm ci` + `npm audit
  --audit-level=high` em push/PR que altere `package.json`/lockfile do mobile, mais agendamento
  semanal e disparo manual — mesmo padrão do `auditoria-python.yml` do `S12`); seção "Auditoria de
  dependências do mobile" no `docs/setup.md` com a rotina local e o critério de quando tratar uma
  vulnerabilidade como correção avulsa vs. parte do `V3`.
- **Validado:** `npm audit --audit-level=high` local rodou com exit code `0` (moderadas não derrubam
  o job); relatório completo (`npm audit`) conferido item a item para confirmar que as 13
  vulnerabilidades são as mesmas do `V3` e não algo novo.
- Com o `S11` fechado, todos os itens `S1`–`S17` da seção 🔐 Segurança (levantamento de 08/07/2026)
  ficam concluídos.

---

## [não versionado] — 10 de julho de 2026

### Fase 1.5 criada — Fundação Multicanal (WhatsApp como porta de entrada) — só planejamento
- **Decisão do usuário (10/07/2026):** incluir o WhatsApp como porta de entrada do sistema de
  chamados, sem parar nem reestruturar o projeto — o material comercial já previa ("o WhatsApp vira
  um canal, nunca o dono dos seus dados"). **Nenhum código foi implementado**: esta entrada registra
  apenas análise arquitetural, roadmap e sincronização com o ClickUp.
- **Posicionamento:** nova Fase 1.5 entre a Fase 1 (base de mensagens) e a Fase 2; a IA (Fase 5)
  passa a depender dela. Dois blocos: **📥 Inbound MVP** (MC1–MC14: enum de canal, `ContatoCanal`,
  correlação externa idempotente por `wamid`, auditoria de payload, entrada normalizada com
  adaptador sem regra de negócio, webhook GET/POST com `X-Hub-Signature-256`, resolução de tenant,
  mídia dependente da Fase 9, status externos, testes de robustez, observabilidade, docs) e
  **📤 Outbound posterior** (MO1–MO7: janela de 24h, templates por Empresa, opt-in/opt-out,
  onboarding de números, custos/qualidade, campanhas) — outbound só depois da Fase 5/5.5.
- **Confirmado na documentação da Meta (10/07/2026):** entrega at-least-once (dedup por `wamid`
  obrigatório; retries até 7 dias), assinatura HMAC-SHA256 do corpo bruto, resposta 200 rápida com
  processamento assíncrono, URL de mídia efêmera, janela de 24h com templates fora dela, pricing
  por mensagem desde 07/2025 e cobrança de mensagens de serviço a partir de 01/10/2026.
- **Decisões pendentes de validação humana (bloqueiam o MC8 no ClickUp):** número por Empresa vs
  compartilhado; contato desconhecido (pré-cadastro/pendente/triagem); multi-condomínio; retenção
  LGPD do payload; Meta direta vs BSP; escopo do outbound no MVP.
- **ClickUp:** tarefa-pai `868kb75yf` + 2 grupos + 22 subtarefas criadas com tags do padrão do
  Space; dependências registradas (Fase 1.5 ← Fase 1; MC10 ← Fase 9; Fase 5 ← Fase 1.5;
  Outbound ← Inbound + Fase 5; MC8 ← decisões).

### Visão geral operacional do Gestor — endpoint de relatório
- Criado `GET /relatorios/visao-geral`, exclusivo do Gestor e escopado à Empresa autenticada por
  filtro explícito e RLS. A resposta consolida chamados abertos, SLA vencido, primeira resposta
  humana interna média e resolução média em minutos; médias sem amostra retornam `null`.
- O novo roteador foi registrado na aplicação e seu contrato foi validado no OpenAPI dentro do
  contêiner do backend.

### `S10` — Seed nunca roda em produção; limpeza de dados demo (fechado)
- **Problema:** `gerenciar_banco.py semear` cria usuários de demonstração com a mesma senha padrão
  (`Senha123`) em toda instalação — nada impedia rodar isso contra o banco de produção, e não
  havia jeito documentado de rotacionar/remover esses dados num ambiente compartilhado (staging).
- **Feito:** nova config `AMBIENTE` (`dev`/`staging`/`producao`, default `dev`, validada — falha
  cedo num typo). `_semear()` recusa rodar (sai com erro, sem tocar no banco) quando
  `AMBIENTE=producao`; `.env.prod.example` passa a declarar `AMBIENTE=producao` explicitamente.
  Novo subcomando `limpar-demo`: apaga os usuários demo (marcados pelo domínio `DOMINIO_DEMO`) e
  tudo que depende deles (chamados, mensagens, refresh tokens, sessões revogadas), respeitando a
  ordem das foreign keys; idempotente.
- **Validado de ponta a ponta:** rodei `semear` com `AMBIENTE=producao` de verdade — recusou (exit
  1) sem tocar no banco. Rodei `limpar-demo` de verdade (removeu 5 usuários e 14 chamados),
  confirmei via API que a lista ficou vazia, rodei de novo para confirmar a idempotência (nada a
  fazer), e por fim `semear` restaurou os 12 chamados originais do seed.

### Atualização automática (polling) da Visão geral e da lista de Chamados
- **Pedido do usuário:** ao criar um chamado direto no banco para testar, percebeu que o painel só
  refletia depois de um reload manual — pediu algo "estilo Power BI", atualizando sozinho.
- **Decisão técnica (confirmada com o usuário):** polling simples via `setInterval`, sem adotar
  SWR/React Query (nenhuma dependência nova) — as duas páginas já usavam `useEffect` +
  `fetch` direto, então o padrão mais simples de manter é reaproveitar isso com um hook.
- **Feito:** novo hook `frontend/web/src/lib/useAtualizacaoPeriodica.ts` — reexecuta uma função de
  busca a cada 20s enquanto a aba está visível (Page Visibility API pausa o polling em segundo
  plano e busca na hora ao voltar, em vez de esperar o próximo tick). `visao-geral` e `chamados`
  passaram a usá-lo; a tela só mostra "Carregando..."/erro na carga inicial — atualizações de
  fundo trocam os dados em silêncio e mantêm a última leitura boa se uma falhar.
- **Validado com Playwright** (instalado no S14/B7 anterior): abri o painel, criei um chamado via
  API sem tocar na página, e confirmei que os dados mudaram sozinhos — KPI "Chamados abertos" de
  10→11 na visão geral e total de 14→15 na lista de chamados, ambos sem reload.

### Script de consultas manuais ao banco (dev)
- Movido `backend/scripts/consultas/consultas-facilichat.sql` (antes um arquivo temporário de
  scratchpad) para dentro do repositório, versionado. Referência de conexão local (host/porta/
  banco/usuário) e SELECTs genéricos prontos para as 7 tabelas reais do projeto, para quem quiser
  consultar o Postgres de dev diretamente (DBeaver, TablePlus, psql etc.) sem depender da API. Não
  é executado por nenhum script/CI — é só material de consulta manual.

### `S14` — Revogação de sessão em troca de senha e mudança de função (fechado)
- **Problema:** o logout já revogava a sessão de verdade (denylist de `jti` + família de refresh),
  mas não havia onde acionar isso em troca de senha ou mudança de função — essas rotas não
  existiam no código.
- **Feito:** `PATCH /usuarios/eu/senha` (exige `SenhaAtual`, seguindo a OWASP Authentication Cheat
  Sheet) e `PATCH /usuarios/{usuarioID}/funcao` (só Gestor, mesma Empresa). Ao trocar a própria
  senha, denylista o `jti` da sessão atual e revoga **todas** as famílias de refresh do usuário —
  força novo login em todo dispositivo, incluindo o que fez a troca. Ao mudar a função de outro
  usuário, revoga todas as famílias de refresh dele; o access token que ele já tem em mãos continua
  válido até expirar (no máximo 15min, janela curta do `S15`), já que não há como localizar o `jti`
  de um dispositivo que não é o da requisição atual. Novo helper
  `revogarTodasFamiliasDoUsuario` em `app/servicos/refresh.py`.
- **Consultado `verificar-seguranca` antes de implementar:** OWASP Session Management Cheat Sheet
  recomenda regenerar/invalidar sessão em troca de senha e mudança de privilégio; Authentication
  Cheat Sheet recomenda exigir a senha atual — abordagem planejada já batia com a recomendação
  atual, sem necessidade de mudar a regra antes de codar.
- **Validado com curl:** senha errada → 400; senha certa → sessão atual revogada na hora (`401
  "Sessão encerrada"` reusando o token antigo); login com senha antiga falha, com a nova funciona;
  troca de função de outro usuário → `401` ao ele tentar `/autenticacao/atualizar`; 403 para
  quem não é Gestor; 404 para usuário inexistente ou de outra Empresa.
- **Bug de ambiente encontrado durante a validação:** o hot-reload do `uvicorn --reload` (bind
  mount do Docker Desktop no Windows) perdeu a mudança de um dos três arquivos editados
  (`Autenticacao.py`) — as rotas novas só apareceram no `/openapi.json` depois de um
  `docker compose restart backend`. Não é um problema do código; é uma limitação do watcher sobre
  bind mount nesse ambiente.

### Reorganização do board da Fase 0.5 (grupos por categoria no ClickUp)
- **Problema:** as ~50 subtarefas da Fase 0.5 pendente (`868k60v1m`) estavam todas soltas, direto
  sob a fase, misturando Altos/Segurança/Médios/Baixos/Documentação/Versões.
- **Limitação encontrada:** o MCP do ClickUp disponível não tem operação de reparentar uma tarefa
  existente (só define `parent` na criação; `move_task` só move entre listas) nem de criar tag nova
  no Space (`add_tag_to_task` exige tag já existente). Por isso não deu para mover os itens já
  existentes automaticamente.
- **Feito:** criados 6 grupos vazios como subtarefas de `868k60v1m` — 🟠 Altos (`868kb37kx`),
  🔐 Segurança (`868kb37me`), 🟡 Médios (`868kb37nf`), 🟢 Baixos (`868kb37nt`),
  📄 Documentação (`868kb37p9`), 🔄 Atualização de versões (`868kb37q9`). Os CUs foram anotados ao
  lado do cabeçalho de cada categoria em `docs/plano-implementacao.md`.
- **Pendente (ação manual do usuário):** arrastar as subtarefas existentes (A/S/M/B/D/V) para dentro
  do grupo correspondente na UI do ClickUp — a API não permite fazer isso de fora.

### `B7` — Validação visual de responsividade do painel web (mobile)
- **Problema:** o CSS responsivo do painel (`AdminShell`, lista de chamados) já tinha sido aplicado,
  mas nunca houve uma validação visual real em viewport mobile — só inspeção de código.
- **Feito:** instalado Playwright (Chromium) como devDependency em `frontend/web` (fica disponível
  para validações futuras); script temporário logou como Gestor Demo e tirou screenshots de
  `/painel/chamados`, `/painel/supervisores` e `/painel/visao-geral` em 390×844 (mobile) e
  1440×900 (desktop). Resultado: sem overflow horizontal em nenhuma página/viewport, sidebar
  colapsa para o topo em mobile, cards empilham em coluna única, sem erros de console. Screenshots
  eram temporários (scratchpad da sessão) e foram apagados após a checagem.
- **Pendência separada:** a mesma validação no app mobile (Expo) não foi feita agora — exige
  emulador/dispositivo, fora do escopo desta checagem de browser.

### `S9` — Compose de produção (backend + web containerizados + proxy TLS)
- **Problema:** não existia forma de rodar o FaciliChat em produção — o backend só tinha o compose
  de dev (`--reload`, bind mount do código) e o painel web só rodava com `npm run dev` fora do
  Docker, sem TLS/HSTS na frente.
- **Feito nesta sessão (o código já existia, sem commit; a entrega desta sessão foi validar e
  fechar):**
  - `backend/Dockerfile` endurecido: usuário não-root `appuser` (`useradd --system`), mesma imagem
    para dev e produção — só o `command`/volume do compose muda.
  - `frontend/web/Dockerfile` (novo): build em dois estágios usando `output: 'standalone'` do Next
    (`next.config.ts`), imagem final roda como usuário `node` sem código-fonte/toolchain.
  - `docker-compose.prod.yml` (novo): `db` sem `ports:` (só rede interna), `backend` sem
    `--reload`/bind mount e com `--proxy-headers` (IP real do cliente atrás do Caddy, necessário
    para o rate limit do `S7`), serviço `web` (Next standalone) e **Caddy** como único serviço com
    portas publicadas (80/443/443-udp) — TLS automático via Let's Encrypt (`deploy/Caddyfile`) com
    HSTS, para os domínios `DOMINIO_PAINEL`/`DOMINIO_API`.
  - `deploy/backup-banco.sh` (novo): dump diário comprimido do Postgres de produção + cópia externa
    opcional via `rclone`; retenção configurável.
  - `.env.prod.example` (novo): modelo do `.env` de produção (domínios, ACME, Postgres, JWT).
  - `docs/deploy-producao.md`: runbook atualizado de "em construção" para concluído — status de
    cada item, seção nova de backup/restauração e nota sobre nomes de projeto Docker (ver bug
    abaixo).
- **Bug encontrado e corrigido durante a validação:** nem `docker-compose.yml` nem
  `docker-compose.prod.yml` declaravam `name:` — o Compose usa o nome da pasta como projeto por
  padrão, então os dois arquivos competiam pelo **mesmo projeto Docker**. Ao validar o compose de
  produção localmente, o Compose **recriou (substituiu) os containers `facilichat_db`/
  `facilichat_backend` do dev** pelos containers `_prod`. Nenhum dado foi perdido — o volume do
  Postgres de dev (`facilichat_pgdata`) tem nome próprio, diferente do `pgdata_prod` — mas o
  incidente expôs um risco real para quem rodar os dois composes na mesma máquina. Corrigido com
  `name: facilichat` (dev, igual ao nome de projeto implícito anterior — preserva o volume
  existente) e `name: facilichat_prod` (produção) explícitos nos dois arquivos.
- **Validado (localmente, sem VPS/DNS real):**
  - `docker build` das duas imagens de produção limpo.
  - `docker compose -f docker-compose.prod.yml config` sem erros (todas as variáveis obrigatórias
    resolvidas via `.env` de teste).
  - Subida isolada (`docker compose -p facilichat_prod_validacao ...`) de `db`+`backend`+`web`:
    todos os healthchecks ficaram `healthy`; `whoami` dentro dos containers confirmou `appuser`
    (backend) e `node` (web); `GET /` da API respondeu `200`; `GET /docs` respondeu `404`
    (`API_DOCS_HABILITADO=false`); `GET /login` do web respondeu `200`.
  - `caddy validate` confirmou o `Caddyfile` sintaticamente válido (a emissão real de certificado
    Let's Encrypt exige DNS público, não reproduzível localmente).
  - Após o incidente do `name:`, o dev foi restaurado (`docker compose up -d`) e a contagem de
    linhas em `Usuarios` conferida (7, igual a antes) antes de devolver os containers ao estado
    parado original.
- **Pendente:** rodar de fato num VPS com DNS público para confirmar a emissão do certificado TLS
  (não é possível validar isso localmente); item `S10` (bloquear seed em produção) continua em
  aberto.

### Fase 4 — Recorte visual da visão geral do painel web
- **Implementado:** nova rota `/painel/visao-geral`, com cards de indicadores derivados dos chamados
  existentes, painel "O que precisa da sua atenção", gráfico de fluxo por status, volume por fila e
  volume por categoria vindo dos dados reais.
- **Navegação:** `/painel` agora redireciona para `/painel/visao-geral`, e a sidebar ganhou o link
  "Visao geral" mantendo "Chamados" para a fila detalhada.
- **Escopo deliberado:** a tela não inventa SLA, tempo de primeira resposta nem resolução média. Esses
  pontos continuam dependentes dos endpoints de relatório da Fase 4; por isso os itens relacionados
  ficaram parcialmente em andamento no plano.
- **Validado:** `tsc --noEmit` e `npm run build` do frontend web passaram limpos.

### Fase 4 — Página Supervisores (`868k60w2a`, frontend-first)
- **Implementado:** nova rota `/painel/supervisores`, com cabeçalho executivo, resumo da supervisão,
  contrato visual de cards expansíveis e estrutura da fila de cada supervisor.
- **Sem dados fictícios:** enquanto o endpoint `GET /relatorios/supervisores` (`868k60w1e`) não existe,
  a página mostra indicadores indisponíveis, skeletons neutros e uma mensagem explícita de integração.
  Nomes, carga, atrasos e tempo de primeira resposta não são simulados.
- **Responsividade e acessibilidade:** expansão preparada como botão navegável por teclado, com
  `aria-expanded`/`aria-controls`, foco visível e layouts próprios para desktop, tablet e mobile.
- **Validado:** `npm run build` passou e registrou a rota estática `/painel/supervisores`. A inspeção
  visual no navegador integrado ficou pendente porque nenhum navegador estava disponível na sessão.

### `S12` — Auditoria de dependências Python automatizada (primeiro CI do projeto)
- **Problema:** o baseline do `pip-audit` tinha sido rodado uma única vez, manualmente (encontrou e
  resolveu o `ecdsa`/`python-jose` → `PyJWT`), mas nada garantia que a auditoria voltasse a rodar —
  uma CVE publicada amanhã numa versão já fixada passaria despercebida.
- **Correção:** criado `.github/workflows/auditoria-python.yml`, o primeiro workflow de CI do
  repositório. Roda `pip-audit -r backend/requirements.txt` (Python 3.12, igual ao Dockerfile) em
  todo push/PR que altere o `requirements.txt` ou o próprio workflow, **toda segunda-feira às
  09:00 UTC** (agendamento pega CVE nova sem precisar de commit) e sob demanda
  (`workflow_dispatch`). Vulnerabilidade conhecida = job vermelho. Permissões do job restritas a
  `contents: read`.
- **Documentado:** nova seção "Auditoria de dependências Python (`pip-audit`)" no `docs/setup.md`
  (rotina local + passo a passo quando o CI acusar vulnerabilidade) e item na seção Segurança do
  `docs/tecnico-backend.md`.
- **Validado:** `python -m pip_audit -r backend/requirements.txt` local retornou
  `No known vulnerabilities found` (baseline segue limpo). O workflow em si roda no primeiro push
  para o GitHub (o gatilho inclui o próprio arquivo do workflow).

### Sincronização ClickUp — correção de 8 subtarefas desatualizadas
- **Problema:** validação cruzada entre `docs/plano-implementacao.md`, o código e o board do
  ClickUp (via MCP) encontrou subtarefas cujo status no board estava atrás do plano/código —
  nenhum caso inverso (ClickUp nunca estava mais avançado que o plano). A lista bateu com o
  checklist manual deixado em `.codex/clickup-sync-pendencias.md` por uma sessão do Codex sem
  MCP do ClickUp disponível (8 itens registrados ali; a primeira rodada desta sessão moveu 7 e
  deixou o `S9` passar — corrigido na sequência ao cruzar com esse arquivo).
- **Corrigido no ClickUp** (sem nenhuma mudança de conteúdo do plano, só sincronização de status):
  - Para `✅ concluída`: `868kaa3cg` (`S9`), `868kaa3dz` (`S12`), `868k60w1k` (redirect `/painel`),
    `868k60w26` (Volume por categoria), `868k7vrwr` (Hierarquia do painel).
  - Para `🚧 em andamento`: `868k60w1r` (KPIs da visão geral), `868k7vrx5` (painel "O que precisa
    da sua atenção"), `868k60w2w` (links do sidebar).
- **Confirmado no código antes de mover** o `S9`/`S12` (`docker-compose.prod.yml` e
  `.github/workflows/auditoria-python.yml` existem) e os itens de Fase 4
  (`frontend/web/src/app/painel/visao-geral/page.tsx` implementa KPIs, volume por categoria e
  hierarquia do painel).
- **Board confirmado no lugar certo:** `clickup_get_workspace_hierarchy` e `clickup_get_task`
  confirmaram a lista em `Operações Internas` → `FaciliChat - Desenvolvimento` →
  `Roadmap de Implementacao` (`list_id 901114027434`) — bate com o board documentado no plano e
  com o `.codex/clickup-sync-pendencias.md`. "Iugo Performance" que aparece junto é o nome do
  criador/workspace da tarefa, não um board diferente.

---

## [não versionado] — 9 de julho de 2026

### `S7` — Fechado após verificação (sem mudança de código nesta sessão)
- **Contexto:** o item estava `em andamento` no ClickUp e `[~]` no plano, mas ninguém estava
  trabalhando nele. Verificação de código confirmou que todo o escopo descrito no ClickUp já está
  implementado: rate limit em memória por IP/e-mail no login e no cadastro público
  (`app/servicos/seguranca.py` — 5 tentativas/5min, bloqueio de 15min), hash dummy no login
  uniformizando o timing (anti-enumeração) e respostas neutras ("Email ou senha incorretos";
  cadastro público não revela e-mail já cadastrado).
- **Ação:** plano marcado `[x]` e subtarefa `868kaa3ax` movida para ✅ concluída no ClickUp, com
  comentário registrando as evoluções futuras: rate limit compartilhado (Redis) para produção
  multi-réplica fica no endurecimento do `S9`; resposta neutra no fluxo de convite/onboarding
  quando ele existir (evolução do `S3`).

### `S8` — Docs da API (`/docs`, `/redoc`, `/openapi.json`) configuráveis por ambiente
- **Problema:** o FastAPI expõe Swagger, ReDoc e o schema OpenAPI por padrão, sem nenhuma opção de
  desligar por ambiente — em produção isso documenta publicamente todas as rotas, schemas de
  request/response e mensagens de erro, um mapa pronto para quem for atacar a API.
- **Correção:** nova config `API_DOCS_HABILITADO` (`configuracoes.py`, default `true` — dev
  depende disso). Em `main.py`, `docs_url`/`redoc_url`/`openapi_url` da instância `FastAPI(...)`
  viram `None` quando desligado — o FastAPI nem registra essas rotas nem gera o schema, não é só
  uma UI escondida atrás de uma URL. Vira um flag no `.env` de produção, sem tocar código.
- **Validado:** com o flag ligado (default), `/docs`, `/redoc` e `/openapi.json` respondem 200;
  com `API_DOCS_HABILITADO=false` (via `docker compose up -d --force-recreate` — `restart` sozinho
  não relê o `.env`), as três respondem 404 e o resto da API (`GET /`) continua 200 normalmente.
  Revertido para o default (dev) ao final. `verificar-rls` OK.

### Bug — Empresa da plataforma (Iugo) vazava na listagem de tenants do Superadmin
- **Reportado pelo usuário:** a tela do Superadmin deveria mostrar só as Empresas-cliente (para
  cadastrar Gestores), mas a própria Empresa que hospeda o Superadmin (`Iugo Performance`,
  criada pelo bootstrap `criar-superadmin`) aparecia misturada na lista — inclusive documentado
  como comportamento esperado em `docs/tecnico-backend.md`. Pior: a tela permite suspender
  qualquer item da lista, então um Superadmin podia suspender a própria Iugo por engano e ficar
  trancado para fora da plataforma.
- **Causa raiz:** `Usuario.EmpresaID` é `NOT NULL` (regra de ouro da Fase 0.7), então a Empresa da
  Iugo precisa existir como uma linha comum em `Empresas` — mas nada a distinguia de um tenant de
  verdade, e `GET /plataforma/empresas` listava todas sem filtro.
- **Correção:** nova coluna `Empresa.EhPlataforma` (bool, default `False`). O bootstrap
  `criar-superadmin` marca `True` na Empresa que cria (e corrige instalações antigas ao reutilizar
  a Empresa existente). `listarEmpresas` filtra `EhPlataforma=False`. `atualizarStatusEmpresa`
  recusa (400) alterar o status dessa Empresa mesmo via chamada direta à API — defesa em
  profundidade, não só esconder da lista.
- **Também corrigido nesta sessão:** `backend/scripts/gerenciar_banco.py` tinha um caractere `c`
  perdido na primeira linha (fora de qualquer comentário), quebrando `python scripts/
  gerenciar_banco.py` com `NameError` antes mesmo de chegar no parser de argumentos — corrigido.
- **Banco de dev resetado** a pedido do usuário: `reset` → `criar-empresa` (Cefram Demo) →
  `criar-superadmin` (Iugo) → `semear`. Validado via curl: `GET /plataforma/empresas` como
  Superadmin retorna só a `Cefram Demo`; `PATCH .../status` na Empresa da Iugo responde 400;
  `verificar-rls` OK.

### `S15` — Access token curto (15min) + refresh token rotativo com detecção de reuso
- **Problema:** o access token durava 8h inteiras sem refresh token — uma janela longa demais para
  um token roubado (XSS, infostealer) continuar valendo. Diminuir a duração sem um mecanismo de
  renovação faria o usuário digitar a senha de novo a cada 15min, o que não é aceitável.
- **Access token:** `JWT_EXPIRE_MINUTES` baixado de `480` para `15` (padrão atual OWASP/2026 para
  access token; confirmado via `verificar-seguranca` antes de implementar).
- **Refresh token opaco com rotação e família:** formato `"{ID}.{segredo}"` — o `ID` é a chave
  primária (lookup indexado) e só o **hash sha256** do segredo fica no banco (`RefreshTokens`,
  modelo `RefreshToken`, serviço `app/servicos/refresh.py`), no mesmo espírito de uma senha. Todo
  refresh nascido do mesmo login compartilha um `FamiliaID`. A cada uso (`POST
  /autenticacao/atualizar`) o token é consumido e um novo nasce na mesma família — **reuso de um
  token já consumido revoga a família inteira** (sinal de furto/replay), não só o token usado.
  `REFRESH_TOKEN_EXPIRE_DIAS=30` (sessão "deslizante": cada rotação renova a janela).
- **Logout revoga a família também:** além da denylist de `jti` do access token (S14),
  `POST /autenticacao/logout` agora também localiza e revoga toda a família do refresh token —
  um refresh ainda válido na mão do cliente no momento do logout não pode ser usado depois.
- **Web (`lib/api.ts`):** cookie `refresh` `HttpOnly` (emitido junto no login/refresh,
  `servicos/sessao.py`). Num `401`, `req()` chama `/autenticacao/atualizar` automaticamente e
  repete a requisição original uma única vez (evita loop). **Single-flight:** requisições
  paralelas que tomam 401 ao mesmo tempo compartilham a mesma promise de renovação — chamadas
  concorrentes ao `/atualizar` rotacionariam o mesmo refresh token duas vezes e disparariam a
  própria detecção de reuso do backend, derrubando a sessão à toa.
- **Mobile (`lib/api.ts`/`lib/auth.ts`):** sem cookies — `refresh_token` guardado no SecureStore e
  reenviado no corpo de `/autenticacao/atualizar`; mesmo retry único e single-flight do web.
- **Efeito colateral esperado:** sessões abertas antes desta mudança (sem refresh token salvo)
  caem para login normal assim que o access token de 8h antigo expirar ou for revogado — não há
  como "migrar" uma sessão já emitida para o novo esquema.
- **Validado:** curl direto na API — cadeia de rotações legítimas em sequência, reuso de um token
  já consumido derrubando a família inteira (inclusive o token novo e válido), logout revogando a
  família. Repetido através do **proxy real do Next** (`docker compose up -d --force-recreate
  backend` foi necessário para o container pegar o `JWT_EXPIRE_MINUTES` novo do `.env` — `restart`
  sozinho não relê o `env_file`) confirmando cookie `refresh` + CSRF + rotação funcionando de
  ponta a ponta. `tsc --noEmit` limpo nos dois frontends.

### Bootstrap do 1º Superadmin (Iugo Performance) — subcomando `criar-superadmin`
- **Problema (ovo e galinha):** o painel de plataforma (`/plataforma/empresas`) exige o perfil
  `Superadmin`, e `POST /plataforma/empresas` exige um Superadmin **já autenticado**. Mas nenhum
  usuário tinha esse perfil e **nada no backend o criava** — a varredura não encontrou nenhuma
  atribuição `Funcao = UsuarioFuncao.Superadmin`. `criar-empresa` grava `Gestor` fixo. Também não
  havia item de plano cobrindo isso (criado na Fase 0.7 antes da implementação).
- **Decisão de produto (com o usuário):** a documentação posiciona a Iugo *acima* dos tenants, mas o
  schema exige `Usuario.EmpresaID NOT NULL`. Em vez de mexer no schema (o que tocaria o invariante
  "toda tabela tem EmpresaID"), a Iugo passa a existir como uma **Empresa** que hospeda o Superadmin.
  Isso funciona porque a tabela `Empresas` está **fora da RLS** e `/plataforma/*` usa
  `obterBancoDados` puro — qualquer Superadmin enxerga todos os tenants.
- **Implementado** em `backend/scripts/gerenciar_banco.py` (CLI unificado, sem script novo):
  `criar-superadmin "<Nome>" <email> <senha> [--empresa-nome] [--cnpj]`. **Idempotente**: reutiliza a
  Empresa, reativa se estiver `Suspensa` (senão o próprio Superadmin tomaria 403 e ficaria trancado
  para fora) e sai em silêncio se o Superadmin já existir.
- **Recusa promover usuário existente.** Se o e-mail já pertence a outro perfil, aborta com exit 1.
  Um bootstrap que transforma qualquer conta em Superadmin seria escalonamento de privilégio
  disfarçado — quem tivesse shell promoveria o próprio Cliente.
- **Verificado de ponta a ponta:** criação; 2ª execução idempotente (exit 0, sem duplicar); tentativa
  de promover o Gestor → abortou com exit 1 e o Gestor continuou Gestor; login → `funcao: Superadmin`;
  `GET /plataforma/empresas` como Superadmin → 200 com as 2 Empresas, como Supervisor → **403**;
  `POST /plataforma/empresas` como Superadmin → 200 (tenant de teste criado e removido depois);
  pelo proxy do Next, o cookie `funcao=Superadmin` é emitido — é o que o `middleware.ts` usa para
  redirecionar `/painel` → `/plataforma/empresas`.
- **CNPJ:** `unique NOT NULL`, sem validação de dígito verificador no projeto. O padrão é um
  placeholder de dev (`00.000.000/0001-00`); `--cnpj` informa o real em produção.
- **Ressalva registrada:** a Empresa da Iugo **aparece** na lista do painel de plataforma, porque
  `listarEmpresas` (`Plataforma.py:64`) não filtra. Cosmético; filtrar exigiria decidir como marcar
  a Empresa-plataforma.
- **Docs:** `setup.md` (Passo 3), `deploy-producao.md` (bootstrap em 2 passos), `tecnico-backend.md`
  (tabela de subcomandos + nuance de modelo).

### `S14` (+ `B6`) — Logout revoga de verdade a sessão; claims `iat/iss/aud/jti` no JWT
- **Problema:** o JWT era stateless demais — o logout só apagava os cookies do navegador, mas o
  token em si continuava válido até expirar (até 8h). Quem já tivesse copiado o token (ex.: XSS,
  infostealer) continuava autenticado mesmo depois do usuário "sair". O token também não carregava
  `iat`/`iss`/`aud`/`jti`, e o hasher de senha (`PasswordHash.recommended()`) estava duplicado em
  4 arquivos (`Autenticacao.py`, `Usuarios.py`, `Plataforma.py` — este último não constava no
  levantamento original — e `gerenciar_banco.py`).
- **`B6` — claims e hasher centralizado:** `criarToken` passou a incluir `iat` (emissão), `iss`
  (`facilichat-api`) e `aud` (`facilichat-clientes`), configuráveis via `JWT_ISSUER`/`JWT_AUDIENCE`
  (`configuracoes.py`), além do `jti` (ID único do token, pré-requisito do `S14`). O decode
  (`_decodificarToken`) agora valida `iss`/`aud` antes de qualquer outra checagem. Hasher
  centralizado em `app/servicos/hasher.py`, reaproveitado pelos 4 pontos que o duplicavam.
  `@app.on_event("startup")` (deprecado no FastAPI) virou `lifespan` em `main.py`.
- **`S14` — denylist de sessão por `jti`:** nova tabela `SessoesRevogadas` (modelo
  `SessaoRevogada`, `app/servicos/revogacao.py`) guarda o `jti` de todo token revogado no logout.
  `POST /autenticacao/logout` agora decodifica o token recebido e registra sua revogação (além de
  apagar os cookies); `obterUsuarioAtual`/`obterTenantAtual` (`rotas/Autenticacao.py`) checam a
  denylist a cada requisição autenticada, em ambas as dependências (a de tenant sozinha também,
  não só a que carrega o `Usuario` inteiro). A limpeza de entradas vencidas é feita "na unha" (sem
  Redis no stack): cada novo registro apaga as entradas cujo `ExpiraEm` já passou.
  **Decisão deliberada:** `SessoesRevogadas` fica de fora da RLS — a checagem roda em
  `obterBancoDados` puro, antes de `app.empresa_id` ser setado; com `FORCE ROW LEVEL SECURITY` a
  query sempre veria zero linhas (fail-closed) e a revogação nunca funcionaria de verdade.
- **Pendente (registrado no plano, não bloqueia o fechamento do que foi feito):** a exigência de
  "revogar todas as sessões em troca/reset de senha e mudança de função" não tem endpoint para
  acionar — o código ainda não tem rota de troca de senha nem de edição de função de um usuário.
  Fica para quando essas rotas existirem.
- **Efeito colateral esperado:** como o decode agora exige `iss`/`aud`, qualquer token emitido
  antes desta mudança deixa de ser aceito — usuários com sessão aberta precisam logar de novo.
- **Validado:** `import app.main` dentro do container, reset+seed do banco de dev (schema novo
  aplicado), `verificar-rls` OK, e teste real via curl — login → `GET /usuarios/eu` com o token
  (200) → `POST /autenticacao/logout` → reuso do MESMO token no `GET /usuarios/eu` (401 "Sessão
  encerrada", não mais um 200 revogado só no cliente).

### Docs — implantação reorganizada em 3 documentos com papéis claros
- **Motivação (pedido do usuário):** o `setup.md` tinha ~510 linhas misturando três papéis —
  onboarding de dev via Docker, onboarding manual via WSL e notas de produção acumuladas pelos
  itens de segurança — o que passava a impressão de que subir/publicar o app exigia dezenas de
  passos.
- **`docs/setup.md` (reescrito):** só o caminho rápido de dev — 4 passos com Docker (~5 min),
  tabela de referência das variáveis do `backend/.env` (agora incluindo as `COOKIE_*` do S6),
  comandos do dia a dia e troubleshooting. Aponta para os outros dois documentos.
- **`docs/setup-manual.md` (novo):** os antigos Passos 1–11 do caminho WSL/venv, atualizados
  (bootstrap via `gerenciar_banco.py`, aviso sobre Alembic/reset) — apêndice para quem precisa
  rodar o Python fora do container.
- **`docs/deploy-producao.md` (novo):** runbook único de produção, consolidando as 4 seções
  "Produção — ..." que estavam no setup (JWT_SECRET/secrets, credenciais do banco/S4,
  sessão-cookies/S6, headers-CSP-HSTS/S16) + tabela "pronto vs pendente" e checklist final
  numerado. Marcado como em construção: fecha de vez com o **S9**.
- **`S9` ampliado no plano e no ClickUp** (`868kaa3cg`, segue `[ ]`): além do compose de produção
  endurecido, agora cobre o serviço do web (build standalone do Next + Dockerfile), proxy TLS com
  HSTS, `.env.prod.example` e a finalização do runbook — meta: deploy em ~4 comandos.
- **Referências atualizadas** para as seções movidas: `.env.example` (raiz), `backend/.env.example`,
  `frontend/web/next.config.ts`, `docs/arquitetura.md`, `docs/tecnico-frontend.md` e a trilha
  `docs/implementation/08-documentacao-deploy-operacao.md`.

### `S6` (+ `M6`) — Sessão do painel em cookie `HttpOnly`, com CSRF e proxy do Next
- **Problema:** o JWT ficava no `localStorage` **e** num cookie escrito por JavaScript, sem
  `HttpOnly`/`Secure` e com `Max-Age` de 7 dias para um token de 8h. Qualquer XSS no painel lia e
  exfiltrava o token. O `middleware.ts` roteava com base em cookies graváveis pelo cliente.
- **Decisões tomadas com o usuário** (registradas no plano):
  - **Proxy do Next** (`/api/*`) em vez de chamada direta com `credentials`. Motivo: se web e API
    ficassem em domínios registráveis diferentes, o cookie viraria de terceira parte
    (`SameSite=None`), **bloqueado por padrão no Safari**. Com o proxy o cookie é first-party e a
    hospedagem da API deixa de afetar a autenticação. Isso **inverteu** a cláusula final do S6
    (`allow_credentials` do CORS **permanece `False`**) e absorveu o `M6`.
  - **Middleware do Next só checa a presença** do cookie (evitar flash de conteúdo). Não valida
    assinatura, para não espalhar o `JWT_SECRET` a um segundo serviço. Autorização real é do backend.
- **Backend:** `login` emite `sessao` (`HttpOnly`), `csrf_token` e `funcao`, com `Max-Age` **igual à
  validade real do token**. `obterTokenDaRequisicao` aceita cookie (web) **ou** `Bearer` (mobile),
  com precedência do header. Novo `POST /autenticacao/logout`. Novo `app/servicos/csrf.py`
  (middleware): valida `Origin`/`Referer` em métodos que mudam estado — o que cobre também o
  **login CSRF** do form-urlencoded — e exige double-submit (`X-CSRF-Token` == cookie, comparado com
  `compare_digest`) quando a credencial é o cookie. Bearer pula o double-submit por não ser
  credencial ambiente. Logout é isento do double-submit (senão um cookie CSRF perdido prenderia o
  usuário numa sessão que ele não consegue encerrar); a validação de origem continua valendo.
- **Configuração por ambiente:** `COOKIE_SECURE`/`COOKIE_SAMESITE`/`COOKIE_DOMAIN`, com defaults de
  produção. `SameSite=none` sem `Secure` **falha na subida** (o navegador descartaria o cookie em
  silêncio). Em dev, `COOKIE_SECURE=false` porque o painel roda em `http://localhost`.
- **Web:** `api.ts` chama `/api/*` e anexa o `X-CSRF-Token`; `auth.ts` não guarda mais token nem
  escreve cookies (só nome/empresa, para exibição) e perdeu o `auth.token()`; `auth-storage.ts` não
  serializa mais cookies; `middleware.ts` lê o cookie `sessao`; CSP fechou em `connect-src 'self'`.
  Mobile **inalterado**.
- **Achado durante a verificação:** o Next redireciona (308) URLs terminadas em barra, e as rotas do
  backend usam barra final. Sem correção, o `fetch` seguiria um 307 do FastAPI **para a origem da
  API**, saindo do proxy e esbarrando na CSP. Resolvido com `skipTrailingSlashRedirect: true` mais
  uma regra de rewrite que preserva a barra — ambos comentados no `next.config.ts`.
- **Verificado por requisição real** (12 casos, backend direto e através do proxy): `Set-Cookie` com
  `HttpOnly` só no `sessao` e `Max-Age=28800` (8h); GET autenticado só com cookie; POST sem CSRF →
  403; com CSRF errado → 403; com CSRF correto → 200; `Bearer` puro sem cookie nem CSRF → 200
  (mobile preservado); `Origin` maliciosa → 403 mesmo com CSRF válido; login com `Origin` maliciosa
  → 403; sem credencial → 401; logout devolve os três cookies expirados.
- **Não verificado:** a interface clicada em navegador real — o Chrome disponível nesta sessão não
  alcançava o servidor de dev. A garantia do `HttpOnly` está no header `Set-Cookie` e no cookie jar.
- **Escopo:** logout apaga o cookie, mas **o JWT continua válido até expirar**. Revogação server-side
  é o `S14`; refresh token com janela curta é o `S15`.
- **Docs:** nova seção "Produção — sessão e cookies" no `setup.md` (com checklist de deploy);
  `tecnico-backend.md` e `tecnico-frontend.md` atualizados.

### `S17` — CORS sem wildcards e sem credentials
- **Problema:** o `CORSMiddleware` rodava com `allow_credentials=True` mesmo sem a API usar cookies,
  e com `allow_methods=["*"]` / `allow_headers=["*"]`.
- **Por que os wildcards importavam:** lendo o código do Starlette 1.3.1 instalado, `allow_headers=["*"]`
  faz o middleware **espelhar de volta qualquer header** que o cliente pedir no
  `Access-Control-Request-Headers` — uma permissão em branco, não apenas uma lista genérica. E
  `allow_methods=["*"]` expandia para os 7 verbos (incluindo `PUT`/`DELETE`/`HEAD`, que a API não tem).
- **O que mudou** (`backend/app/main.py`): `allow_credentials=False`; `allow_methods` e `allow_headers`
  viraram as constantes `CORS_METODOS_PERMITIDOS` (`GET, POST, PATCH, OPTIONS`) e
  `CORS_HEADERS_PERMITIDOS` (`Authorization, Content-Type`). `configuracoes.py` não precisou mudar —
  as origens já vinham explícitas do `.env`.
- **Escopo ajustado ao código real:** o plano previa liberar também `DELETE`, mas a auditoria das rotas
  mostrou que a API só expõe `GET` (3), `POST` (6) e `PATCH` (2) — nenhum `PUT`/`DELETE`. Verbo novo
  exige incluir em `CORS_METODOS_PERMITIDOS` (documentado no `tecnico-backend.md`).
- **Verificado com preflights reais** contra a API no ar: origem autorizada + `POST` + `Authorization`
  → 200 com `Access-Control-Allow-Methods: GET, POST, PATCH, OPTIONS` e **sem**
  `Access-Control-Allow-Credentials`; `DELETE` → 400 `Disallowed CORS method`; header arbitrário →
  400 `Disallowed CORS headers`; origem estranha → 400 `Disallowed CORS origin`; `PATCH` → 200.
  Fluxo real preservado: login (form-urlencoded) e `GET /chamados/` autenticado devolvendo 12 chamados.
- **`allow_credentials` volta a `True` apenas no `S6`**, junto do cookie `HttpOnly` e da proteção CSRF
  (token imprevisível + validação de `Origin`/`Referer`) — a spec proíbe `*` em requisição credenciada,
  e as listas explícitas já deixam a configuração pronta para essa virada.
- **Nota da checagem (`verificar-seguranca`):** as origens explícitas já estavam alinhadas ao OWASP; o
  `pg_hba.conf` do container usa `trust` no loopback interno (padrão do initdb), sem efeito para quem
  vem de fora do container.

### `S4` — Credenciais do Postgres saem do `docker-compose.yml`
- **Problema:** usuário, senha e nome do banco estavam escritos em texto puro no
  `docker-compose.yml` (inclusive a senha repetida dentro da `DATABASE_URL` do serviço backend), e o
  arquivo é versionado — ou seja, a credencial de desenvolvimento estava no Git e duplicada em dois
  lugares que podiam sair de sincronia.
- **O que mudou:**
  - Novo **`.env` na raiz** (ignorado pelo Git) com `POSTGRES_USER`, `POSTGRES_PASSWORD` e
    `POSTGRES_DB`, e o modelo correspondente em **`.env.example`**. É o arquivo que o Docker Compose
    lê automaticamente para interpolar `${...}`.
  - `docker-compose.yml` passou a usar `${VAR:?mensagem}`: sem o `.env`, a subida **falha com um
    aviso claro** em vez de usar um default fraco. O healthcheck usa `$$POSTGRES_USER` e a
    `DATABASE_URL` do backend é **montada a partir das mesmas variáveis** — a senha vive num lugar só.
  - **Senha local rotacionada** via `ALTER USER` no banco em execução, preservando os dados
    (a variável `POSTGRES_PASSWORD` só tem efeito na criação do volume).
- **Verificado:** `docker compose up -d` recria os serviços, o db fica `healthy`, o backend loga
  "Banco de dados conectado!", `GET /` responde e os 6 usuários seguem no banco. Testado de outro
  container pela rede: a senha antiga é **rejeitada** (`password authentication failed`) e a nova é
  aceita. Observação registrada: o `pg_hba.conf` da imagem usa `trust` para o loopback **dentro** do
  container (padrão do initdb); qualquer outra origem cai em `scram-sha-256`.
- **Docs:** `docs/setup.md` ganhou a seção "Produção — credenciais do banco por ambiente" (tabela
  dev/staging/produção, exigência de papel não-superusuário em produção para a RLS valer também para
  a aplicação, TLS, banco fora da internet) e o passo a passo de rotação da senha local; `docs/setup.md`
  e `docs/arquitetura.md` não exibem mais a senha real.

### Tooling — scripts do banco unificados num único CLI (`gerenciar_banco.py`)
- **Motivação (pedido do usuário):** havia 7 scripts espalhados em `backend/scripts/`, e a cada
  mudança de schema estava sendo criado um novo script de migração incremental — desnecessário em
  dev, onde o banco pode ser recriado. Consolidado tudo num ponto de entrada visível.
- **Removidos 7 scripts**, substituídos por **`backend/scripts/gerenciar_banco.py`** com subcomandos:
  `reset [--semear]` (dropa o schema, recria as tabelas e aplica RLS), `criar-empresa`, `semear`,
  `aplicar-rls` e `verificar-rls`. Absorve `criar_empresa.py`, `semear_chamados.py`, `aplicar_rls.py`
  e `verificar_isolamento_tenant.py`; **elimina** as três migrações incrementais
  (`aplicar_fase_06_tickets_irmaos.py`, `aplicar_fase_06_condominios.py`, `aplicar_m5_timestamptz.py`),
  já que `Base.metadata.create_all` reconstrói o schema completo a partir dos modelos.
- **`app/rls.sql` mantido** como fonte das políticas (lido pelo `aplicar-rls`/`reset`).
- **Verificado no container:** `reset` → `criar-empresa` → `semear` → `verificar-rls`, seed
  idempotente na 2ª execução, e login/listagem de chamados pela API funcionando após o reset.
  Documentada a pegadinha do `reset` com a API no ar (cache de prepared statements do asyncpg gera
  um 500 transitório auto-corrigido; recomendação: `docker compose restart backend`).
- **Docs atualizadas:** `docs/tecnico-backend.md` (nova seção "Scripts do banco"), `docs/setup.md`,
  as skills `subir-projeto` (`.claude` e `.codex`) e o cabeçalho do `app/rls.sql`. Referência de
  arquivo do item S10 no plano ajustada para o novo CLI.

### `M4` + `M5` — Modernização do backend: SQL echo configurável e datas UTC timezone-aware
- **Trabalho iniciado em sessão paralela e finalizado aqui.** O que já estava feito: modelos com
  `DateTime(timezone=True)` e default `agoraUtc()` (novo `app/tempo.py`), `configuracoes.py`
  migrado para `SettingsConfigDict` (Pydantic v2) e `M4` (`echo=configuracoes.DEBUG`, com `DEBUG`
  no `.env.example`).
- **Finalização nesta sessão:** os três `datetime.utcnow()` restantes trocados por `agoraUtc()`
  (`criarToken` em `Autenticacao.py`, `atualizarStatus` em `Chamados.py` e o seed
  `semear_chamados.py`) e criado **`scripts/aplicar_m5_timestamptz.py`** — converte as colunas do
  banco de dev existente de `TIMESTAMP` naive para `TIMESTAMPTZ` interpretando os valores antigos
  como UTC (sem isso, o asyncpg rejeita datetime com timezone em coluna naive).
- **Verificado no ambiente real:** migração executada no container; login (JWT com `exp` aware),
  criação de chamado (resposta com `Criacao` em `...Z`), atualização de status e listagem com as
  datas antigas preservadas. `DEBUG` documentado no `setup.md`; regra "sempre `agoraUtc()`"
  registrada no `tecnico-backend.md`.
- **Nota:** o `scripts/aplicar_m5_timestamptz.py` citado acima foi **removido no mesmo dia** pela
  unificação dos scripts de banco (ver a entrada "Scripts do banco unificados" no topo) — em dev,
  a conversão de schema passa a ser feita por `gerenciar_banco.py reset`.

### `M12` — Retornos de erro do projeto inteiro traduzidos para português
- **Origem:** o usuário viu um aviso em inglês na tela de login do web. Diagnóstico: as mensagens
  do nosso código já eram PT; o inglês vazava de (1) erros de validação automáticos do
  FastAPI/Pydantic (422 — "Field required", "value is not a valid email address", com `detail` em
  lista que o front exibiria como `[object Object]`) e (2) falhas de rede do `fetch`
  ("Failed to fetch" no navegador / "Network request failed" no React Native).
- **Backend:** handler global de `RequestValidationError` em `main.py` traduz os tipos comuns de
  erro Pydantic para PT com o nome do campo e devolve `detail` como string única — mesmo formato
  dos `HTTPException` das rotas (ex.: `"O campo 'Email' deve ser um e-mail válido"`).
- **Web e mobile:** `lib/api.ts` de ambos ganhou `extrairDetail` (aceita `detail` string ou lista,
  por defesa) e `fetchOuErroDeConexao` (falha de rede → "Não foi possível conectar ao servidor.
  Verifique sua conexão e tente novamente."), aplicados ao `req` genérico e ao `login`.
- **Verificado:** curls de 422 (campo faltando, UUID inválido, e-mail inválido) e 401 respondendo
  em português; `tsc --noEmit` limpo no web e no mobile. Regra registrada no `tecnico-backend.md`:
  rotas novas devem escrever `detail` em português.

### Segurança — `S7` parcial: rate limit e resposta menos enumerável em login/cadastro
- Criado `backend/app/servicos/seguranca.py` com rate limit em memória por IP e e-mail para fluxos
  públicos de autenticação (`login` e cadastro público), retornando `429` após excesso de tentativas.
- `POST /autenticacao/login` agora sempre executa uma verificação de hash: quando o e-mail não existe,
  usa um hash dummy para reduzir diferença de timing e mantém resposta uniforme.
- `POST /usuarios/` passou a aplicar rate limit e deixou de responder "Email ja cadastrado",
  reduzindo enumeração direta no cadastro público. Observação operacional: o rate limit atual é
  por processo; produção multi-réplica deve evoluir para Redis ou mecanismo compartilhado.

### Segurança — `S3` implementado: cadastro público sem escolha livre de Empresa
- **`POST /usuarios/` agora falha fechado por padrão**: o cadastro público só funciona quando
  `CADASTRO_PUBLICO_HABILITADO=true` e `CADASTRO_PUBLICO_EMPRESA_ID` aponta para uma Empresa ativa.
- Mesmo habilitado, o `EmpresaID` recebido no payload precisa bater exatamente com a Empresa liberada
  em configuração; isso remove a possibilidade de um cadastro público escolher qualquer tenant.
- **Documentação atualizada:** `backend/.env.example`, `docs/setup.md` e `docs/tecnico-backend.md`
  explicam o fluxo seguro e o bootstrap por `scripts/criar_empresa.py`.

### Infra/Integrações — camada local do Codex para o FaciliChat
- **Camada `.codex/` criada no repositório** com skills/checklists equivalentes às rotinas do Claude:
  `validar-regras`, `verificar-seguranca`, `subir-projeto`, `find-docs`, `commit-sync` e
  `diagnosticar-sandbox`. O objetivo é manter o fluxo operacional rastreável no próprio projeto,
  sem depender de instalação global fora do workspace.
- **Scripts locais de apoio adicionados**: `.codex/scripts/diagnosticar-ambiente.ps1` verifica se o
  problema é do projeto ou do ambiente da sessão; `.codex/scripts/lembrete-clickup.ps1` reforça a
  sincronização manual do board quando o Codex não tiver integração ativa.
- **Documentação de infra atualizada** em `docs/implementation/05-infra-integracoes.md` e
  `docs/implementation/README.md`, registrando os limites reais desta sessão do Codex:
  escrita restrita ao workspace, rede limitada e ausência atual de MCP de ClickUp.
- **Plano ajustado** para incluir a trilha de compatibilidade Claude -> Codex e deixar explícita a
  pendência externa: habilitar uma integração nativa de ClickUp no ambiente do Codex ainda depende
  de instalação/autenticação fora do repositório.

### Planejamento — reorganizacao por trilhas
- Criada a nova visao de execucao em `docs/implementation/`, separando o roadmap em trilhas de
  seguranca, backend, frontend web, frontend mobile, infra/integracoes, QA, bugs/pendencias e
  documentacao/deploy/operacao.
- Mantido `docs/plano-implementacao.md` como fonte canonica por fase, status e `CU:` do ClickUp,
  agora com ponteiro para a visao por trilhas e para o mapa de migracao.
- Adicionado `docs/implementation/migration-map.md` para preservar a rastreabilidade entre as fases
  antigas, os `CU:` existentes e a nova organizacao por trilhas.

### Revisão de layouts web/mobile
- **Web alinhado aos tokens do design system** — login e cards de chamados usam raio de 8px, botões
  ganharam altura mínima adequada e a sidebar do painel agora se adapta a telas estreitas.
- **Mobile sem valores visuais soltos nas telas existentes** — login, chamados, perfil, tabs e estado
  inicial passaram a consumir `theme.spacing`, `theme.fontSize`, `theme.control` e cores do tema.
- **Plano atualizado** — `B1` marcado como concluído, `B7` colocado em andamento e criada uma trilha
  ordenada para a revisão de layouts web/mobile de 09/07/2026.

### Segurança — `S16` concluído: CSP e headers de segurança no painel web
- **`frontend/web/next.config.ts`** ganhou `headers()` aplicado a todas as rotas: CSP em modo
  **Report-Only** (fase de observação — só registra violações no console, sem bloquear),
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy:
  strict-origin-when-cross-origin` e `Permissions-Policy` negando câmera/microfone/geolocalização.
- A CSP inclui a origem da API no `connect-src` (via `NEXT_PUBLIC_API_URL`) e afrouxa só em dev
  (`'unsafe-eval'` para HMR e `ws:`), removendo isso automaticamente em produção. HSTS ficou
  documentado para o proxy HTTPS de produção (não faz sentido em dev HTTP).
- **Documentação:** `docs/setup.md` ganhou a seção "Produção — headers de segurança, CSP e HSTS"
  com o passo a passo de promoção da CSP de Report-Only para enforce; `docs/tecnico-frontend.md`
  ganhou a tabela dos headers.
- **Verificado de ponta a ponta:** `next build` + `next start` com inspeção dos headers na resposta
  HTTP real (variante de produção sem `unsafe-eval`) e middleware de rotas protegidas funcionando
  (307 → `/login`). Aprendizado registrado no `tecnico-frontend.md`: rodar `next build` com o
  `next dev` ativo contamina a pasta `.next/` compartilhada e quebra o `next start` com
  `EvalError` no middleware — parar o dev antes de buildar.

### Segurança — auditoria de autenticação/sessão incorporada ao plano (sem código)
- **Auditoria completa de autenticação, sessão e cookies** feita sobre backend (FastAPI/JWT), web
  (Next.js) e mobile (Expo), usando como referência as cheat sheets da OWASP (Session Management,
  CSRF, XSS, Authentication) e o MDN (Set-Cookie). **Nenhum código foi alterado** — os achados
  viraram itens do plano, seguindo a Regra de Ouro.
- **Novos itens `S14`–`S17`** na tabela 🔐 Segurança do `plano-implementacao.md` (subtarefas criadas
  no ClickUp sob a Fase 0.5): `S14` revogação de sessão server-side (logout hoje só limpa o cliente;
  token roubado vale as 8h), `S15` access token curto + refresh com rotação, `S16` CSP e headers de
  segurança no web, `S17` endurecimento do CORS (`allow_credentials` sem uso + wildcards).
- **Escopo ampliado de itens existentes:** `S6` agora cobre também o cookie duplicado sem
  `HttpOnly`/`Secure` criado via `document.cookie` (`auth-storage.ts`), a estratégia CSRF completa
  (token + validação de Origin/Referer) e o middleware do Next que confia em cookies forjáveis;
  `S7` ganhou o hash dummy contra enumeração por timing no login e resposta neutra no cadastro;
  `B6` anotado como pré-requisito do `S14` (claim `jti`). Ordem recomendada registrada no plano:
  `S16` → `S17` → `S7` → `S6` → `S14`(+`B6`) → `S15`.
- **Higiene do board ClickUp (achado do usuário):** a Fase 0.6 estava ✅ concluída, mas 4 subtarefas
  seguiam em 📋 backlog sob ela — eram os itens realocados no plano para outras fases (1 de IA →
  Fase 5; 3 de Visita Técnica → Fase 8) sem a subtarefa acompanhar. Como a API do ClickUp não move
  subtarefa de pai, as 4 antigas (`868k60vf2/vf7/vfc/vfg`) foram **arquivadas** com ponteiro e
  **recriadas sob as fases corretas** (`868kahvau/vb2/vbe/vbk`); os `CU:` das Fases 5 e 8 no plano
  foram atualizados. A Fase 0.6 agora não tem pendência real.

### Segurança — `S3` iniciado (sem código ainda)
- Seguindo a ordem do plano ("corrigir um `S*` por vez, começando por `S1` e `S2`"), o próximo item
  da fila de segurança é o `S3`: o cadastro público (`POST /usuarios/`) aceita qualquer `EmpresaID`
  no payload, permitindo que um usuário se registre em uma Empresa que não é a dele.
- **Nada foi alterado em código nesta entrada** — apenas o status do item foi movido para
  "em andamento" para retomar na próxima sessão. Decisão pendente com o usuário: aplicar a correção
  interina (restringir/desabilitar o cadastro público em produção) ou já partir para o convite/
  onboarding por Empresa, que é a correção definitiva.

### Frontend web — polimento visual das telas existentes (continuação da A5)
- **Objetivo:** aproximar o visual das telas que já existem no código (login, sidebar do painel,
  lista de chamados) do protótipo comercial em `docs/FaciliChat-Regras/FaciliChat-Apresentacao.html`
  (seção `id="admin"`), sem adicionar telas/funcionalidades novas (essas ficam para os Milestones 3a-4
  já planejados — ver `plano-implementacao.md`).
- **`AdminShell` (sidebar do painel):** adicionada a marca oficial do FaciliChat (logo SVG inline,
  mesma arte do protótipo), ícone de linha no item "Chamados", estado ativo por rota
  (`usePathname`), e avatar circular com iniciais + nome + Empresa no rodapé, no lugar do texto
  solto. `frontend/web/src/components/painel/AdminShell.tsx`, `.module.css`.
- **Login:** adicionada a marca acima do título, fundo com gradiente radial sutil em azul-marca, e
  o CSS migrado dos valores antigos em `rem`/aliases para os tokens novos (`--sp-*`, `--r-*`,
  `--fs-*`, `--shadow-lg`), alinhando com o restante do painel. `frontend/web/src/app/(auth)/login/*`.
- **Lista de chamados:** cabeçalho passou a mostrar o nome da Empresa (tenant) abaixo do título;
  status ganhou pílula colorida por semântica (Recebido neutro, Em andamento âmbar, Agendado azul,
  Concluído verde, Cancelado apagado); prioridade passou a ter indicador de cor + label, separado
  visualmente do status; cards com sombra e hover. `frontend/web/src/app/painel/chamados/*`.
- Verificado com `next build` (typecheck + lint limpos).

### Infraestrutura de acompanhamento — Sincronização do board ClickUp com o plano
- **Board reconciliado com o `plano-implementacao.md`** — comparado o status de cada subtarefa do
  ClickUp (`list_id 901114027434`) com o status esperado (`[x]`/`[~]`/`[ ]`) do plano; corrigidas 3
  divergências onde o ClickUp estava atrás do código: `868k60v1q` (A1, já corrigido) e `868k60veu`
  (Cliente = Condomínio/contrato) movidos para "✅ concluída", e a tarefa-pai da Fase 0.6
  (`868k60vdy`) também movida para "✅ concluída" (todos os itens da fase já estavam feitos).
- **Subtarefas de segurança e documentação criadas** — os itens `S1`–`S12` (revisão de segurança de
  08/07/2026) e `D5`–`D8` (divergências de documentação) ainda não tinham subtarefa no ClickUp;
  criadas todas como filhas de `868k60v1m` (Fase 0.5 pendente), com `S5` já como "✅ concluída" e
  `S12` como "🚧 em andamento" (refletindo o estado real descrito no plano), as demais em
  "📋 backlog". Os novos `CU:` foram gravados no `plano-implementacao.md` no lugar de `a-criar`.
- **Anomalia encontrada (não corrigida)** — a tarefa `868k60w3y` ("Criar alerta comercial ao detectar
  oportunidade") existe no board com status "📦 arquivada" mas não corresponde a nenhum item do
  plano atual; mantida como está para o usuário decidir (arquivar de vez ou reaproveitar).
- Motivação: manter o board como espelho fiel do plano (regra de ouro do `CLAUDE.md`), sem alterar
  nenhum código de produto.

### Fase 0.6 — Tickets irmãos
- **Vínculo de origem em chamados** — `Chamado` agora tem `GrupoOrigemID` opcional para ligar tickets
  nascidos do mesmo aviso/mensagem.
- **Criação simultânea de tickets irmãos** — novo endpoint `POST /chamados/irmaos` cria 2+ chamados
  em uma única operação, todos escopados à `EmpresaID` do usuário e com o mesmo `GrupoOrigemID`.
- **Clientes web/mobile sincronizados** — tipos e APIs passam a expor `GrupoOrigemID` e
  `chamados.criarIrmaos(...)`.
- **Banco existente em dev** — adicionado script idempotente
  `backend/scripts/aplicar_fase_06_tickets_irmaos.py` para criar a coluna/índice sem recriar tabelas.
- **Plano atualizado** — itens `868k60vem` e `868k7vrt2` marcados como concluídos.

### Modernização SQLAlchemy 2.0 / Pydantic v2 (refatoração, sem mudança de regra de negócio)
- **Modelos ORM** (`Chamados.py`, `Empresa.py`, `Mensagens.py`, `Usuarios.py`) migrados do estilo
  legado `Column(...)` para `mapped_column()` + anotações `Mapped[...]`, o padrão atual do
  SQLAlchemy 2.0. Nulabilidade de cada coluna foi conferida e preservada exatamente como antes
  (validado por import real dos modelos e inspeção de `__table__.columns`).
- **Fábrica de sessões assíncronas** (`banco_dados.py`) trocada de
  `sessionmaker(engine, class_=AsyncSession, ...)` para `async_sessionmaker(engine, ...)`, a fábrica
  dedicada recomendada pela doc atual do SQLAlchemy para asyncio.
- **Schemas de saída Pydantic** (`Chamados.py`, `Usuarios.py`, `Plataforma.py`) trocaram o
  `class Config: from_attributes = True` (estilo Pydantic v1, oficialmente deprecated) por
  `model_config = ConfigDict(from_attributes = True)`.
- Motivação: verificação feita via Context7 (doc oficial atualizada) a pedido do usuário, comparando
  o código com os padrões atuais de FastAPI/SQLAlchemy/Pydantic.

### Fase 0.7 — Fundação SaaS Multi-Tenant concluída
- **Superadmin da plataforma implementado** — novas rotas `/plataforma/empresas` para listar Empresas,
  criar tenant com primeiro Gestor e alternar status `Ativa`/`Suspensa`, restritas a `Funcao=Superadmin`.
- **Suspensão com efeito real** — Empresa `Suspensa` passa a bloquear login e uso de tokens já emitidos.
- **Área web de plataforma** — nova tela `/plataforma/empresas` para onboarding e suspensão/reativação
  de Empresas, com redirecionamento automático do login quando o usuário é Superadmin.
- **Plano atualizado** — itens `868k60vkz` e `868k60vnh` marcados como concluídos; fase `868k60vfm`
  passa para `✅ Concluída`.

### Segurança — auditoria Python e JWT
- **Backend auditado com `pip-audit`** — o baseline local encontrou `ecdsa==0.19.2`
  (`PYSEC-2026-1325` / `CVE-2024-23342`), trazido pelo ecossistema do `python-jose`.
- **JWT migrado de `python-jose` para `PyJWT`** — como o backend usa JWT simétrico `HS256`,
  removemos `python-jose`, `ecdsa`, `rsa` e `pyasn1` de `backend/requirements.txt` e passamos a usar
  `PyJWT==2.13.0`.
- **Auditoria final limpa** — após a troca, `python -m pip_audit -r backend/requirements.txt`
  retornou `No known vulnerabilities found`.
- **A1 corrigido** — `obterUsuarioAtual` agora converte o `sub` do token dentro do `try` e captura
  `PyJWTError`/`ValueError`, retornando 401 para token malformado em vez de 500.
- **`JWT_SECRET` endurecido** — a configuração agora recusa segredo curto ou placeholder na
  inicialização; `.env.example` e `docs/setup.md` documentam a geração com `secrets.token_urlsafe(32)`.
- **`.env` tolerante a BOM no Windows** — `backend/app/configuracoes.py` lê o arquivo como
  `utf-8-sig`, evitando falha de inicialização quando editores/PowerShell salvam o `.env` com BOM.
- **S5 corrigido: Postgres preso ao localhost** - `docker-compose.yml` agora publica o banco em
  `127.0.0.1:5432:5432`, mantendo acesso local de desenvolvimento sem abrir o Postgres na rede.
- **S13: guia de produção para o `JWT_SECRET`** — nova seção "Produção — `JWT_SECRET` e secrets por
  ambiente" no `docs/setup.md`: como gerar a chave (PowerShell/Python/openssl, uma por ambiente) e
  como cadastrá-la como secret no destino (VPS com Docker Compose, Render/Railway/Fly.io, GitHub
  Actions), com aviso de que Docker Desktop/Docker Hub não guardam secrets e de que rotacionar a
  chave derruba todos os logins. Item espelhado no ClickUp (`868ka61e5`).
- **Chave removida do código-fonte** — uma chave gerada havia sido colada por engano na lista de
  placeholders de `backend/app/configuracoes.py` (lista de valores *proibidos*, não de chaves
  válidas). O texto de exemplo foi restaurado antes de qualquer commit; a chave real do
  `backend/.env` é outra e permanece secreta, sem necessidade de rotação.

### Planejamento — revisão de segurança e validação contra branding
- **Só documentação/planejamento** — nenhuma linha de código de produto alterada.
- **`docs/plano-implementacao.md`:** os achados da revisão de segurança foram convertidos em itens
  rastreáveis `S1`–`S12`, para execução por partes. Inclui atualização segura do Next/PostCSS, RLS
  realmente tenant-aware nas rotas, fechamento do cadastro público por `EmpresaID`, hardening do
  Docker/dev mode, rate limit, docs Swagger por ambiente, lockfile/audit do mobile e auditoria Python.
- **Validação dos HTMLs de branding:** os documentos em `docs/FaciliChat-Regras/` reforçam seis
  invariantes: design discreto com azul `#148AF5`/Figtree, chat como palco e ticket como bastidor,
  anti-amnésia, SaaS multi-tenant Empresa→Condomínios com Iugo como Superadmin, IA ancorada em fatos
  configurados por Empresa e visita técnica como entidade irmã do ticket.
- **Divergências documentais registradas:** adicionados `D5`–`D8` para corrigir `visao-geral.md`,
  `arquitetura.md` e notas rápidas do plano, que ainda têm trechos defasados em relação ao código
  atual ou ao branding.

## [não versionado] — 2 de julho de 2026

### Painel do gestor — Milestone 2: fundação visual (design system no web)
- **Escopo:** portar o design system do comercial para o `frontend/web`, base para as 8 telas do painel
  do Gestor (Milestone 3). Mudança cosmética/refatoração — não toca regra de negócio.
- **Tokens (`frontend/web/src/app/globals.css`):** o `:root` (que tinha só 9 cores, com a primária
  **errada** `#1a56db`) foi substituído pelo conjunto completo de `docs/FaciliChat-Regras/FaciliChat-Design-System.html`:
  escalas azul (`--blue-*`, primária correta **#148AF5**) e ink, feedback, semânticos de
  superfície/texto/borda, tipografia, espaçamento (`--sp-*`), raio (`--r-*`), sombras e motion. Os 9
  nomes antigos viraram **aliases** para os novos tokens, mantendo as telas atuais funcionando.
- **Fonte (`layout.tsx`):** **Geist → Figtree** via `next/font/google` (pesos 300–800), a fonte oficial
  do design system, exposta como `--font-figtree`/`--font-sans`.
- **Cores hardcoded corrigidas (teste de fumaça):** o mapa `PRIORIDADE_COR` em `chamados/page.tsx`
  passou a usar tokens (Crítica usa `--danger-700`, já que o DS não tem roxo); `#fff` do botão de login
  virou `--text-onbrand`.
- **`AdminShell` (`frontend/web/src/components/painel/AdminShell.tsx` + `.module.css`, novos):** a
  sidebar/navegação/guarda de sessão saiu de `painel/layout.tsx` para um componente reutilizável
  (primeira peça de `src/components/`, que não existia); `painel.module.css` (órfão) foi removido.
- **Verificação:** `next build` compila, tipos válidos, Figtree carrega e as 6 rotas geram; nenhuma
  referência a `Geist` ou à cor antiga restante.
- **Plano/ClickUp:** item **A5** → `[~]` (metade web feita; tokens/Figtree do **mobile** seguem
  pendentes); subtarefa `868k60v2e` movida para `🚧 em andamento`.

### Integração do plano com o ClickUp (board como espelho vivo do roadmap)
- **Só planejamento/infra de acompanhamento** — nenhuma linha de código de produto alterada.
- **Board ClickUp "Roadmap de Implementação"** (`list_id 901114027434`, space "Operações Internas" ›
  folder "FaciliChat - Desenvolvimento") passou a refletir a realidade e ficou completo:
  - **Progresso sincronizado:** as subtarefas já concluídas em código das Fases **0.6** (7 perfis, fila
    Comercial) e **0.7** (fundação multi-tenant) e o item **M3** foram movidos para `✅ concluída`; as
    tarefas-pai 0.6/0.7 ficaram `🚧 em andamento` (ainda têm itens `[ ]` de escopo futuro).
  - **Fases de discovery criadas no board:** **4.5** (Catálogo), **5.5** (Governança de IA), **11**
    (Experiência do Funcionário) e a seção **Adiados**, além de 14 itens extras de discovery espalhados
    nas Fases 0.6/1/3/4/5 e do item **B7** (responsivo do painel web) que faltava.
- **Fonte única do plano:** os `CU:` (IDs de subtarefa) foram embutidos em cada item do
  `docs/plano-implementacao.md` (nova coluna **CU** nas tabelas e o `CU:` da pai em cada título de fase),
  e o arquivo-espelho `docs/plano-implementacao_1_clickup.md` foi **removido** — agora há uma única
  fonte da verdade dos IDs.
- **Hook ativado:** `.claude/hooks/plano-clickup-reminder.js` simplificado (sem depender do
  `clickup-sync-map.json` inexistente, que foi descartado) e **registrado** em `.claude/settings.json`
  como `PostToolUse` (matcher `Edit|Write`) — a cada edição do plano, lembra de sincronizar o ClickUp.
- **Por quê:** dar ao acompanhamento uma barra de progresso automática e confiável, sem duplicidade de
  arquivos, para que fechar um item no código e no board seja um passo só.

### Planejamento — incorporado o material de discovery (jornadas + How Might We + Governança de IA)
- **Origem:** 7 documentos novos em `docs/FaciliChat-Regras/Novos arquivos/` (4 jornadas — Cliente,
  Funcionário, Supervisor, Dono; 2 "How Might We"; 1 Governança de IA), material do Duplo Diamante
  (fase Definir). Nenhum contraria os invariantes do `CLAUDE.md` — todos **reforçam** e **adicionam
  escopo** antes ausente do plano.
- **Só documentação/planejamento** — nenhuma linha de código alterada nesta entrega.
- **`docs/plano-implementacao.md`:** adicionadas 3 fases novas e refinadas 5 existentes:
  - **Fase 4.5 — Catálogo de Serviços e Parceiros** (novo): `CatalogoServico`/`Parceiro` por Empresa,
    **sem campo de preço**; é o portão que a IA consulta antes de sinalizar oportunidade.
  - **Fase 5.5 — Governança e guardrails da IA** (novo): matriz de 7 perfis (pode/não-pode) como camada
    verificável, validação pós-geração, log de auditoria (`IaAuditoria`) e base de regras RH/Financeiro
    (`BaseRegra`) para resposta automática de dúvidas recorrentes.
  - **Fase 11 — Experiência do Funcionário** (novo): canal único com voz/foto, sensor de campo,
    reposição de insumo e dúvida pessoal — perfil que quase não existia no plano.
  - Refinos: Fase 0.6 (vínculo dos tickets irmãos), Fase 1 (confirmação "Recebido" + voz/foto como
    primeira classe), Fase 3 (aprovação do cliente encerra o ticket, agenda com prioridade visual),
    Fase 4 (alertas de gargalo/cobertura, desempenho por supervisor, hierarquia do painel), Fase 5
    (portão do catálogo + entidade `Oportunidade`), Fase 6 (proposta ligada à `Oportunidade`).
  - **Seção "Adiados (pós-MVP)"**: privacidade por tópico e integração ERP — registrados, fora do MVP.
- **Convenção reforçada no plano:** personas e exemplos dos documentos (nomes de pessoas, serviços,
  parceiros, valores) são **ilustrativos** — viram **dados configuráveis por Empresa no banco**, nunca
  nome fixo/enum/constante no código. Só os enums já definidos nos invariantes são "fixos".
- **Housekeeping:** removido `FaciliChat-Jornada-Dono_1.html` (duplicata idêntica, mesmo hash, de
  `FaciliChat-Jornada-Dono.html`).
- **Por quê:** deixar o backlog pronto e coerente com o material comercial **antes** de retomar código —
  garante que cada nova tabela/rota já nasça com o escopo e o isolamento por tenant corretos.

---

## [0.6.5] — 1 de julho de 2026

### Domínio — Fase 0.7 aplicada (fundação SaaS multi-tenant)
- **Modelo `Empresa`** (`backend/app/modelos/Empresa.py`, novo) — o tenant do SaaS (`Nome`, `CNPJ`,
  `Status` Ativa/Suspensa).
- **`EmpresaID` (FK NOT NULL)** adicionado a `Usuario`, `Chamado` e `Mensagem`. Toda rota que cria ou
  lista esses registros agora escopa pelo `EmpresaID` do usuário autenticado — regra de ouro do
  multi-tenant aplicada em `GET/POST/PATCH /chamados/*` e `POST /usuarios/*`.
- **JWT carrega `empresa_id`** (`backend/app/rotas/Autenticacao.py`) — o frontend nunca escolhe nem
  envia o tenant, só lê do token/login. Duas dependências novas: `obterTenantAtual` (extrai só o
  tenant, sem carregar o `Usuario`) e `obterBancoDadosComTenant` (define `app.empresa_id` na sessão
  do Postgres antes da rota rodar, para a RLS).
- **Row-Level Security (RLS)** — `backend/app/rls.sql` (políticas `FORCE ROW LEVEL SECURITY` em
  `Usuarios`/`Chamados`/`Mensagens`, usando `current_setting('app.empresa_id')`) e
  `backend/scripts/aplicar_rls.py` para aplicar. Trava secundária — o filtro por aplicação continua
  sendo a primeira linha de defesa.
- **Bootstrap multi-tenant**: `backend/scripts/criar_empresa.py` (novo) substitui
  `backend/scripts/criar_gerente.py` (removido) — cria a Empresa e o 1º Gestor numa transação só.
  `backend/scripts/semear_chamados.py` atualizado para semear dados dentro da primeira Empresa
  existente em vez de usuários "soltos".
- **Frontend web**: `TokenResposta`/`Usuario`/`Chamado` ganham `EmpresaID`; `auth.ts` guarda
  `empresaId`/`empresaNome` (exibição no cabeçalho do painel fica para a Milestone do `AdminShell`).
- **Cadastro público (`POST /usuarios/`) precisa de `EmpresaID` explícito no payload** — paliativo
  documentado no código: sem tenant no token (rota não autenticada), não há como resolver a Empresa
  sozinho ainda; um fluxo real de convite/onboarding por Empresa é trabalho da Fase 7.
- **Por quê:** fundação obrigatória (Fase 0.7, `PRIORITÁRIO`) antes de construir qualquer tela nova do
  painel do gestor — evita criar tabelas (`Proposta`, `Condominio`) sem isolamento por tenant.
- **Decisão operacional:** como o ambiente ainda não tem dado de produção, o banco de dev é
  **resetado** (em vez de introduzir Alembic) para recriar o schema já com `EmpresaID NOT NULL` —
  decisão confirmada com o usuário antes da implementação.

---

## [0.6.5] — 8 de julho de 2026

### Domínio — fechamento do fluxo de Condomínio na Fase 0.6
- **`Cliente = Condomínio/contrato` passou a ser regra efetiva de cadastro**: `POST /usuarios/` e
  `POST /usuarios/equipe` agora exigem `Condominio` quando a função criada é `Cliente`, impedindo
  o estado inconsistente de um síndico/responsável sem contrato vinculado. Implementado em
  `backend/app/rotas/Usuarios.py`.
- **Resolução de condomínio normalizada e case-insensitive**: o backend reaproveita a mesma entidade
  `Condominio` do tenant mesmo quando o nome chega com variação de caixa (`"Cond. X"` vs
  `"cond. x"`), evitando duplicatas acidentais e mantendo estável o `CondominioID`.
- **Hardening do backfill da Fase 0.6**: `backend/scripts/aplicar_fase_06_condominios.py` agora cria
  também um índice único por `EmpresaID + lower(Nome)`, reforçando no banco a unicidade lógica do
  condomínio dentro do tenant.
- **Seed alinhado ao modelo estruturado**: `backend/scripts/semear_chamados.py` deixou de criar
  clientes demo apenas com o campo textual legado e passou a criar/reaproveitar a entidade
  `Condominio`, preenchendo `CondominioID` já na origem. O campo textual `Condominio` permanece por
  compatibilidade de contrato com os frontends atuais.
- **Validação manual do fluxo**: confirmado em ambiente local que cadastro de `Cliente` sem
  condomínio retorna `400`, e que um cadastro interno com `Condominio` em caixa diferente reaproveita
  o mesmo `CondominioID` existente.
- **Reclassificação das pendências remanescentes da 0.6 no plano**: o item de IA
  `868k60vf2` foi movido para a **Fase 5 — IA**, e os refinamentos de Visita Técnica
  `868k60vf7`, `868k60vfc` e `868k60vfg` foram movidos para a **Fase 8 — MVP 02: Visitas Técnicas**,
  onde essas capacidades serão implementadas de fato. A Fase 0.6 deixa de carregar pendências que
  dependem de fases posteriores para existir.

---

## [0.5.11] — 8 de julho de 2026

### Frontend — tratamento de sessão expirada (A3)
- **Web e mobile passaram a tratar `401/token expirado` no cliente HTTP centralizado**: ao receber
  `401` em rotas autenticadas, ambos agora limpam a sessão local via `auth.sair()` e redirecionam o
  usuário para a tela de login, evitando ficar preso em estado inválido com token vencido.
- **Web:** `frontend/web/src/lib/api.ts` passou a reutilizar `auth.token()` e, em `401`, limpar a
  sessão e redirecionar para `/login`.
- **Mobile:** `frontend/mobile/lib/api.ts` passou a reutilizar `auth.token()` e, em `401`, limpar o
  `SecureStore` e redirecionar para `/(auth)/login` via `expo-router`.

---

## [0.5.12] — 8 de julho de 2026

### Frontend web — proteção de rota no servidor (A4)
- **Rotas protegidas do web deixaram de depender só de guarda client-side**: foi adicionado
  `frontend/web/src/middleware.ts` para interceptar `/painel/*`, `/plataforma/*` e `/login` antes do
  render, evitando o flash de conteúdo protegido durante a hidratação.
- **Sessão web passou a espelhar `token` e `funcao` em cookies legíveis pelo middleware**:
  `frontend/web/src/lib/auth.ts` continua salvando no `localStorage`, mas agora também sincroniza esses
  dois campos em cookie no login e os remove no logout.
- **Regras aplicadas no middleware**:
  `/painel/*` exige sessão e bloqueia `Superadmin` fora da área de plataforma;
  `/plataforma/*` exige sessão de `Superadmin`;
  `/login` redireciona usuários já autenticados para a área correta.

---

## [0.5.13] — 8 de julho de 2026

### Frontend — fechamento do bloco restante de Altos da Fase 0.5
- **A5 concluído no mobile**: o app ganhou tokens compartilhados em
  `frontend/mobile/lib/theme.ts`, carregamento da fonte **Figtree** via `expo-font` no
  `frontend/mobile/app/_layout.tsx`, e atualização visual das telas de login, chamados, perfil e
  tabs para a paleta oficial do design system (`#148AF5`, inks, bordas e superfícies corretas).
- **A6 tratado como código futuro seguro**: `api.mensagens.*` no web e no mobile deixou de chamar
  uma rota inexistente do backend e agora falha explicitamente com a mensagem de que Mensagens será
  entregue na **Fase 1 do chat**, evitando erro silencioso/enganoso de integração.
- **A7 corrigido**: o link `/usuarios` foi removido da sidebar do painel enquanto a página ainda não
  existe, eliminando o 404 navegável.
- **A8 corrigido**: o mobile foi alinhado ao baseline oficial do **Expo SDK 53**, com atualização
  para `react 19`, `expo-router 5`, ajuste das dependências de navegação/fontes e geração do
  `package-lock.json` local.
- **Ganhos colaterais já fechados no mesmo bloco**:
  `M10` (erros engolidos em `chamados.tsx`/`perfil.tsx`) passou a exibir estado de erro com botão
    "Tentar novamente";
    `M11` (paleta/tipografia mobile) foi resolvido junto do A5;
    `B4` (ícones nas tabs) foi entregue no layout das abas do mobile.

  ---

## [0.5.14] — 8 de julho de 2026

### Segurança — fechamento de `S1` e `S2` da Fase 0.5
- **`S1` corrigido no frontend web**: `next` e `eslint-config-next` foram atualizados para
  **`15.5.20`**, e o `postcss` transitivo vulnerável foi fixado em **`8.5.10`** com `overrides` no
  `frontend/web/package.json`. A árvore instalada ficou limpa em `npm audit --json` e o
  `npm run build` do painel passou com sucesso na mesma revisão.
- **`S2` corrigido no backend**: as rotas multi-tenant de `Chamados` e os endpoints autenticados de
  `Usuarios` deixaram de usar sessão pura e passaram a depender de `obterBancoDadosComTenant`.
  A própria dependência foi endurecida para usar `set_config('app.empresa_id', ..., false)` e
  `RESET app.empresa_id`, preservando o tenant durante toda a request mesmo após `commit()`.
- **RLS ampliada para `Condominios`**: `backend/app/rls.sql` agora aplica a política também à tabela
  `Condominios`, cobrindo a nova entidade introduzida na Fase 0.6 e alinhando a defesa em
  profundidade com o fluxo real de cadastro de clientes.
- **Verificação automatizada de isolamento adicionada**:
  `backend/scripts/verificar_isolamento_tenant.py` cria dois tenants temporários, grava
  `Condominios`/`Usuarios`/`Chamados`, valida o filtro por `EmpresaID` e tenta validar a RLS do
  banco. No ambiente local atual, o script detectou que o papel `facilichat` está com
  `rolsuper=true` e `rolbypassrls=true`, então a checagem de RLS foi conscientemente pulada e ficou
  registrada no output; a camada da aplicação continuou validada.
- **Documentação sincronizada (`D6`)**: `docs/arquitetura.md` deixou de afirmar que toda rota usa
  `obterTenantAtual` diretamente e passou a descrever a dependência tenant-aware real do projeto.

  ---

## [0.6.4] — 1 de julho de 2026

### Domínio — Fase 0.6 aplicada em código (alinhamento com o branding)
- **`UsuarioFuncao` migrado para os 7 perfis do branding**: `Gerente` renomeado para **`Gestor`**;
  adicionados **`RH`**, **`Financeiro`** e **`Superadmin`**. Atualizado em
  `backend/app/modelos/Usuarios.py`, nas checagens de autorização de `backend/app/rotas/Usuarios.py`
  e `backend/app/rotas/Chamados.py`, nos tipos e no `auth.ts`/`isGestor()` do frontend web
  (`frontend/web/src/types/index.ts`, `frontend/web/src/lib/auth.ts`) e do mobile
  (`frontend/mobile/lib/types.ts`, `frontend/mobile/lib/auth.ts`) — contrato de JWT/tipos mantido
  sincronizado nas duas pontas.
- **Fila `Comercial` adicionada a `ChamadoFila`** (`backend/app/modelos/Chamados.py`) — chamados
  roteados a essa fila alimentam a futura tela de Alertas comerciais/Propostas (Fase 6).
- **Correção de segurança residual (item M3 da Fase 0.5)**: `GET /chamados/` comparava o papel do
  usuário com string literal `"Gerente"` em vez do enum `UsuarioFuncao` — trocado para comparação
  tipada `UsuarioFuncao.Gestor`/`.Supervisor`, eliminando o risco de digitação silenciosa.
- **Por quê:** pré-requisito da Fase 0.7 (fundação multi-tenant) e das telas do "painel do dono", que
  dependem dos perfis e da fila corretos existirem antes de construir a UI sobre eles — evita
  retrabalho, conforme a ordem de prioridade definida em `docs/plano-implementacao.md`.
- **Nota:** `backend/scripts/criar_gerente.py` ainda referencia `UsuarioFuncao.Gerente` e ficará
  quebrado até ser substituído por `criar_empresa.py` na Fase 0.7 (próxima entrega desta mesma sessão).

---

## [0.6.3] — 1 de julho de 2026

### Processo / DevX
- **Nova skill `/subir-projeto`** (`.claude/skills/subir-projeto/SKILL.md`) — runbook que sobe o FaciliChat de ponta a ponta para análise em funcionamento: pré-voo do Docker Desktop, criação do `frontend/web/.env.local`, `docker compose up -d --build` (Postgres + API FastAPI com healthcheck e criação automática das tabelas), seed idempotente do primeiro Gestor via `scripts/criar_gerente.py` dentro do container, `npm run dev` do web e abertura no navegador (Swagger `/docs` + login do painel) para validação visual. Objetivo: o usuário só pede "suba o projeto" e o agente coloca tudo no ar. O mobile (Expo) fica fora do fluxo por exigir emulador/dispositivo.
- **Novo script de seed de análise `backend/scripts/semear_chamados.py`** — popula o banco com dados realistas para inspeção do produto em funcionamento: 4 clientes de demonstração (cada um em um condomínio), 1 supervisor e 12 chamados cobrindo as 3 filas (Operacional/RH/Financeiro), todos os status (Recebido/EmAndamento/Agendado/Concluído/Cancelado) e as 4 prioridades, cada chamado com o histórico de chat (Mensagens) preenchido — Cliente, Supervisor e mensagens do Sistema narrando as mudanças de status. É idempotente (não duplica em reexecuções). Não altera nenhuma regra de negócio; apenas insere dados usando os modelos/enums existentes. Login dos clientes demo: `<nome>@demo.facilichat.dev` / `Senha123`.

---

## [0.6.2] — 27 de junho de 2026

### Processo / governança
- **Trava de segurança de produto** — adicionada a seção "🔒 TRAVA DE SEGURANÇA — invariantes do produto" no topo do `CLAUDE.md` (lida por qualquer sessão do Claude Code no repositório). Ela define a fonte da verdade (`docs/FaciliChat-Regras/`) e os invariantes que **não podem ser alterados sem confirmação explícita do usuário**: SaaS multi-tenant (Empresa/Condomínios/Superadmin), os 7 perfis, a regra da IA (nunca inventa preço/prazo), estados do ticket, visita técnica como entidade irmã, tickets irmãos, design system fixo e o princípio anti-amnésia. Antes de qualquer mudança de funcionamento/regra, é obrigatório validar contra esses invariantes.
- **Nova skill `/validar-regras`** (`.claude/skills/validar-regras/SKILL.md`) — checklist invocável que percorre os invariantes acima e instrui a **parar e pedir confirmação** caso a mudança quebre alguma regra definida.

---

## [0.6.1] — 27 de junho de 2026

### Revisão e alinhamento com o branding
- **Revisão dos documentos comerciais** (`docs/FaciliChat-Regras/`: apresentação, personas, design system, MVP02) revelou divergências entre o código/docs e o produto definido pelo comercial. Correções de documentação:
  - **Tenant renomeado de "Administradora" para "Empresa"** em todos os docs e na memória. O termo do branding para quem compra o sistema é a **conservadora/empresa de facilities** (ex.: "Cefram"); os clientes dela são os **Condomínios**. "Administradora" no branding é um papel de cliente, então o termo anterior conflitava.
  - **Enquadramento do produto corrigido** em `visao-geral.md`: o FaciliChat é para **empresas de facilities atenderem seus clientes (condomínios)**, não para "gestão de condomínios".
  - **Perfis alinhados ao branding (7):** Cliente, Funcionário, Supervisor, **RH**, **Financeiro**, **Gestor** (não "Gerente"), **Superadmin** (Iugo Performance). Tabela de perfis da `visao-geral.md` atualizada.
- **`docs/plano-implementacao.md` — nova Fase 0.6 (Alinhamento de domínio com o branding)** com itens de migração de código: renomear `Gerente→Gestor`, adicionar `RH`/`Financeiro`/`Superadmin`, adicionar fila `Comercial`, "tickets irmãos" (uma mensagem → 2 chamados), Cliente = Condomínio/contrato, e refinos da Visita Técnica (duração derivada, `ticket_id` opcional, cliente não aprova).
- **`docs/plano-implementacao.md` reorganizado** para melhor visão: adicionado um **🗺️ Mapa das fases** (status de cada fase de relance) e o conteúdo dividido em **Parte 1 — ✅ Concluído** (Fase 0 + correções já aplicadas) e **Parte 2 — 🚧 Em desenvolvimento** (na ordem recomendada). Apenas reorganização — itens e status preservados.
- **Nota:** o código ainda usa "Gerente" e 4 perfis; as mudanças de código estão registradas como itens `[ ]` na Fase 0.6, não foram aplicadas nesta entrega (apenas documentação).

---

## [0.6.0] — 27 de junho de 2026

### Decisão de arquitetura
- **FaciliChat definido como SaaS multi-tenant** — o produto será vendido para várias **Empresas** (empresas que gerem condomínios), cada uma com dados totalmente isolados. Hierarquia: **Empresa (tenant) → Condomínios → Usuários/Chamados**. Estratégia escolhida: **banco compartilhado + coluna `EmpresaID` em todas as tabelas + Row-Level Security (RLS) no PostgreSQL + tenant no JWT**. Nenhuma mudança de código nesta entrega — apenas documentação do plano a partir de agora.

### Documentação
- **`docs/plano-implementacao.md`** — criada a **Fase 0.7 — Fundação SaaS Multi-Tenant** (prioritária, antes das features), com checklist de backend e frontend; a antiga "Fase 7 — Condomínios e multi-tenant" foi reescrita como "Gestão de Empresas e Condomínios (telas/CRUD)", dependente da 0.7; notas de arquitetura do rodapé atualizadas com o conceito de tenant/Superadmin.
- **`docs/arquitetura.md`** — nova seção "Arquitetura Multi-Tenant (SaaS)" (hierarquia, estratégia de isolamento, RLS, regra de ouro); fluxo de autenticação atualizado para incluir o `EmpresaID` no JWT.
- **`docs/tecnico-backend.md`** — nova seção "Multi-tenancy (SaaS)" com as convenções de `EmpresaID`, escopo por dependência, RLS, Superadmin e bootstrap; item adicionado em "Pendente".
- **`docs/tecnico-frontend.md`** — nova seção sobre o impacto do multi-tenant no front (tenant vem do token, exibir Empresa atual, área de Superadmin, tipos a adicionar).
- **`docs/setup.md`** — aviso de que o onboarding passará a criar Empresa + 1º Gerente juntos.
- **`docs/visao-geral.md`** — adicionado o item "Plataforma multi-empresa (SaaS)" nos próximos passos. **D3 corrigido**: removido o texto espúrio "oi", data 2025→2026 e troca de "atualização em tempo real" por "pull-to-refresh".

---

## [0.5.4] — 27 de junho de 2026

### Segurança
- **A9 — Next.js atualizado para corrigir a CVE-2025-66478** — o `npm install` da web acusou que `next@15.3.4` está afetado por uma vulnerabilidade crítica (RCE no protocolo RSC do App Router, CVSS 10.0). Atualizados `next` e `eslint-config-next` de `15.3.4` para `15.3.6` (patch da própria linha 15.3.x, mantém React 19). Dev server reiniciado e validado (`/login` e `/painel/chamados` → 200). A app nunca esteve online, então não foi necessário rotacionar segredos. Arquivo: `frontend/web/package.json`.

### Corrigido
- **C5 — Assets faltantes do mobile** — criados os arquivos `icon.png`, `splash.png` e `adaptive-icon.png` em `frontend/mobile/assets/` (1024×1024, "F" branco sobre a cor primária `#148AF5`), que o `app.json` referenciava mas não existiam — o build do Expo quebrava. As `backgroundColor` do splash e do adaptiveIcon também foram corrigidas de `#1a56db` para `#148AF5` (design system). Os placeholders podem ser substituídos pela arte final depois. Arquivos: `frontend/mobile/assets/*.png` (novos), `frontend/mobile/app.json`.

---

## [0.5.3] — 27 de junho de 2026

### Corrigido
- **C3 — Rotas `/painel/*` davam 404** — o route group `(painel)` (parênteses são omitidos da URL pelo Next.js) foi renomeado para a pasta real `painel/`. Agora as URLs `/painel/chamados` etc., que o código de navegação já usava, existem de fato. Login → painel funciona. Arquivos: `frontend/web/src/app/painel/**`.
- **C4 — `auth.ts` quebrava no SSR** — adicionada guarda `typeof window !== 'undefined'` em todos os métodos que acessam `localStorage`. O `painel/layout.tsx` passou a ler a sessão via estado (`useEffect`) e só renderiza o painel após validar a autenticação, eliminando o "flash" de conteúdo protegido (melhora parcial do A4). Arquivos: `frontend/web/src/lib/auth.ts`, `frontend/web/src/app/painel/layout.tsx`.

### Adicionado (infraestrutura)
- **Backend conteinerizado** — novos `backend/Dockerfile` (Python 3.12-slim) e `backend/.dockerignore`; o `docker-compose.yml` ganhou o serviço `backend` (com `depends_on` + healthcheck do Postgres, volume do código para hot-reload e `DATABASE_URL` apontando para o serviço `db`). Agora `docker compose up --build` sobe API + banco juntos, sem instalar Python localmente. Validado de ponta a ponta: criação do 1º Gerente, cadastro público (vira Cliente), bloqueios 403 de C6/C7 e fluxo de chamado.
- **`backend/scripts/criar_gerente.py`** — ajustado para inserir a raiz do backend no `sys.path`, permitindo rodar `python scripts/criar_gerente.py` direto (inclusive via `docker compose exec`).

---

## [0.5.2] — 27 de junho de 2026

### Segurança
- **C6 — Escalonamento de privilégio no cadastro corrigido** — `POST /usuarios/` (cadastro público) agora **sempre** cria usuário com função `Cliente`; o campo `Funcao` foi removido do schema público. A criação de perfis privilegiados passou para a nova rota protegida **`POST /usuarios/equipe`**, que exige um usuário autenticado com função `Gerente` (retorna 403 caso contrário). Arquivo: `backend/app/rotas/Usuarios.py`.
- **C7 — Autorização no `PATCH /chamados/{id}/status` (IDOR) corrigida** — alterar status agora é permitido apenas a `Supervisor` e `Gerente` (403 para os demais), impedindo que um Cliente altere chamados de qualquer um. Adicionada também regra de negócio: chamado em estado terminal (`Concluido`/`Cancelado`) não pode ser reaberto (409). Arquivo: `backend/app/rotas/Chamados.py`.

### Adicionado
- **CORS (A2)** — registrado `CORSMiddleware` em `main.py` com origens explícitas (sem `"*"` junto de credenciais), configuráveis pela nova variável `CORS_ORIGINS` (padrão: `http://localhost:3000,http://127.0.0.1:3000`). Sem isso, os frontends no navegador não conseguiam chamar a API. Arquivos: `backend/app/main.py`, `backend/app/configuracoes.py`, `backend/.env.example`.
- **`backend/scripts/criar_gerente.py` (novo)** — script de bootstrap para criar o primeiro usuário `Gerente`, necessário porque o cadastro público virou Cliente-only (C6). Uso: `python scripts/criar_gerente.py "Nome" email senha`.

### Documentação
- **`docs/setup.md` atualizado** — detalhada cada variável do `.env` (incluindo `CORS_ORIGINS` e como gerar `JWT_SECRET`); **corrigido** o passo de banco de dados, que mandava rodar `alembic upgrade head` (Alembic não está configurado) — as tabelas são criadas automaticamente no startup via `create_all`; adicionado passo para criar o primeiro Gerente.

---

## [0.5.1] — 27 de junho de 2026

### Corrigido
- **Imports do backend (C1 + C2)** — todos os imports dos 9 arquivos Python passaram a ser qualificados pelo pacote `app` (ex: `from app.banco_dados import Base`, `from app.modelos.Usuarios import Usuario`, `from app.rotas.Autenticacao import obterUsuarioAtual`). Antes usavam nomes que não correspondiam aos arquivos reais (`from BancoDados`, `from Modelos`, `from Rotas`, `from Configuracoes`), causando `ModuleNotFoundError` e impedindo a API de iniciar. Arquivos: `main.py`, `banco_dados.py`, `modelos/__init__.py`, `modelos/Usuarios.py`, `modelos/Chamados.py`, `modelos/Mensagens.py`, `rotas/Autenticacao.py`, `rotas/Usuarios.py`, `rotas/Chamados.py`.
- **`backend/app/__init__.py` (novo)** — criado o marcador de pacote Python que faltava, permitindo executar a aplicação com `uvicorn app.main:app` a partir de `backend/` (conforme já documentado em `tecnico-backend.md`).

---

## [0.5.0] — 27 de junho de 2026

### Adicionado
- **`docs/plano-implementacao.md` — Fase 0.5 (Correções prioritárias)** — incorporado ao backlog o levantamento técnico completo realizado em 27/06/2026 (análise de backend, frontend web, mobile e documentação). A nova seção lista os problemas encontrados como itens rastreáveis e numerados por ID (C1–C7 críticos, A1–A8 altos, M1–M11 médios, B1–B6 baixos, D1–D4 de documentação), ordenados por severidade. Os críticos vêm primeiro porque, no estado atual, o app não sobe (imports do backend quebrados) nem navega (rotas `/painel/*` em 404). A correção será conduzida um item por vez.

### Configuração
- **`.claude/settings.json` (novo)** — definido o modelo padrão do projeto como Sonnet 4.6 (`"model": "sonnet"`), adequado a tarefas de rotina; a troca para Opus passa a ser feita manualmente por sessão quando necessário.

---

## [0.4.0] — 26 de junho de 2026

### Adicionado
- **`docs/plano-implementacao.md`** — backlog completo de desenvolvimento organizado em 10 fases (Fase 0 a Fase 10), com status rastreável por item (`[ ]` na fila, `[~]` em andamento, `[x]` concluído). Inclui os tokens de design system, regras de negócio e notas de arquitetura para consulta rápida durante o desenvolvimento.
- **`CLAUDE.md` atualizado** — adicionadas regras obrigatórias: (1) verificar `plano-implementacao.md` antes de qualquer implementação para evitar duplicações; (2) todo bloco de código deve ter comentário sem exceção; (3) atualizar o plano e o changelog ao concluir cada item. Adicionados também os tokens de design visual como referência permanente.

---

## [0.3.3] — 26 de junho de 2026

### Melhorado
- **Comentários em todo o código-fonte** — adicionados comentários explicativos em todos os 27 arquivos do projeto (10 Python no backend, 8 TypeScript/TSX no frontend web, 9 TypeScript/TSX no frontend mobile). Cada arquivo recebeu:
  - Comentário de cabeçalho descrevendo a responsabilidade do arquivo
  - Comentários inline em cada bloco lógico (enums, classes, funções, rotas, hooks, estados)
  - Explicações de decisões não óbvias (ex: por que `expire_on_commit=False`, por que form-urlencoded no login, diferença SecureStore vs localStorage)
  - Indicação de cores em constantes de estilo e valores de configuração

---

## [0.3.2] — 25 de junho de 2026

### Corrigido
- **`backend/.env` movido** — arquivo de configuração estava em `backend/app/.env` (local errado); movido para `backend/.env`, onde o `configuracoes.py` realmente o procura ao iniciar com `uvicorn` a partir de `backend/`
- **`frontend/mobile/lib/types.ts`** — adicionada interface `ChamadoCriar` que existia no web mas estava ausente no mobile
- **`frontend/mobile/lib/api.ts`** — tipo corrigido em `chamados.criar()` de `object` para `ChamadoCriar`; adicionado método `chamados.atualizarStatus()` em paridade com o web
- **`frontend/mobile/lib/auth.ts`** — adicionados métodos `isGerente()` e `isSupervisor()` (assíncronos, via `expo-secure-store`), em paridade com o web
- **`.gitignore`** — adicionadas entradas `node_modules/`, `.next/` e `.expo/` que estavam ausentes

---

## [0.3.1] — 25 de junho de 2026

### Adicionado
- **`docs/setup.md`** — guia completo de configuração do ambiente para novos desenvolvedores (WSL 2, Docker, Python venv, Alembic, frontend web e mobile, tabela de solução de problemas)

---

## [0.3.0] — 25 de junho de 2026

### Adicionado
- **Frontend Web (Next.js 15)** — estrutura inicial completa:
  - Tela de login com validação e tratamento de erro
  - Painel administrativo com sidebar de navegação
  - Listagem de chamados com cores por prioridade e status
  - Cliente HTTP com autenticação JWT automática
  - Gerenciamento de sessão via localStorage
  - Proteção de rotas (redireciona para login se não autenticado)
  - Variáveis CSS globais para identidade visual

- **Frontend Mobile (Expo + React Native)** — estrutura inicial completa:
  - Tela de login nativa (iOS e Android)
  - Redirecionamento automático baseado em autenticação
  - Lista de chamados com pull-to-refresh
  - Tela de perfil com botão de logout
  - Armazenamento seguro do token JWT via `expo-secure-store`
  - Navegação por abas com Expo Router

- **Documentação** (`docs/`):
  - `visao-geral.md` — documento para donos da empresa
  - `arquitetura.md` — estrutura técnica e tecnologias
  - `tecnico-backend.md` — backend, modelos, rotas e como rodar
  - `tecnico-frontend.md` — web e mobile, padrões e como expandir
  - `changelog.md` — este arquivo

- **`CLAUDE.md`** — instruções para o agente de IA manter a documentação atualizada a cada alteração

---

## [0.2.0] — Junho de 2026

### Adicionado
- **Backend FastAPI** — estrutura inicial completa:
  - Modelo `Usuario` com funcoes: Cliente, Supervisor, Funcionario, Gerente
  - Modelo `Chamado` com fila (Operacional/RH/Financeiro), status, prioridade e SLA
  - Modelo `Mensagem` com suporte a AutorTipo IA e Sistema (preparado para IA)
  - Rota `POST /autenticacao/login` — login com JWT
  - Rota `POST /usuarios/` — criação de usuário
  - Rota `GET /usuarios/eu` — perfil do usuário logado
  - Rota `POST /chamados/` — abertura de chamado
  - Rota `GET /chamados/` — listagem (filtro por perfil automático)
  - Rota `PATCH /chamados/{id}/status` — atualização de status
  - Configuração via variáveis de ambiente (pydantic-settings)
  - Conexão assíncrona com PostgreSQL (SQLAlchemy + asyncpg)

- **Docker Compose** — banco PostgreSQL 16 em container

---

## [0.1.0] — Junho de 2026

### Adicionado
- Estrutura inicial do repositório
- Configuração de arquivos Git (`.gitignore`, `.gitattributes`)
- Arquivo `requirements.txt` com todas as dependências do backend

---

*Mantido por: Claude Code (agente de desenvolvimento)*
