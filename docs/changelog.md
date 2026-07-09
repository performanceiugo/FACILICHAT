# FaciliChat — Histórico de Alterações

> Registro de tudo que foi desenvolvido ou alterado no sistema, em ordem cronológica.
> Atualizado automaticamente a cada alteração pelo agente Claude Code.

---

## [não versionado] — 9 de julho de 2026

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

## [0.3.1] — 25 de junho de 2025

### Adicionado
- **`docs/setup.md`** — guia completo de configuração do ambiente para novos desenvolvedores (WSL 2, Docker, Python venv, Alembic, frontend web e mobile, tabela de solução de problemas)

---

## [0.3.0] — 25 de junho de 2025

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

## [0.2.0] — Junho de 2025

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

## [0.1.0] — Junho de 2025

### Adicionado
- Estrutura inicial do repositório
- Configuração de arquivos Git (`.gitignore`, `.gitattributes`)
- Arquivo `requirements.txt` com todas as dependências do backend

---

*Mantido por: Claude Code (agente de desenvolvimento)*
