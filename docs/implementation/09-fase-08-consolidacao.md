# Fase 0.8 - Consolidacao pos-auditoria

**Tarefa-pai:** `CU: 868kd1jc1`  
**Status:** planejada  
**Posicao:** depois da Fundacao SaaS Multi-Tenant (0.7) e antes das novas features da Fase 1.

## Por que esta fase foi criada

A verificacao das entregas concluidas mostrou que a arquitetura principal existe, mas alguns
limites entre banco, sessao e clientes ainda permitem uma falsa sensacao de fechamento. A fase
agrupa somente o que precisa ser consolidado agora para o desenvolvimento continuar sobre uma base
confiavel. Atividades que so protegem um banco produtivo ou uma infraestrutura multi-replica foram
direcionadas a Fase 12 para evitar custo repetido durante o primeiro desenvolvimento.

## Ordem obrigatoria

`F08-01 RLS/papeis -> F08-02 destinacao -> F08-03 logout mobile -> F08-04 usuario inativo -> F08-05 concorrencia do refresh -> F08-06 suite sob demanda -> F08-07 cancelamento/reabertura`

## F08-01 - Tornar o RLS efetivo com papeis corretos de banco

**CU:** `868kd1jtu`  
**Tags:** `seguranca`, `backend`

### Evidencia e problema

`backend/app/rls.sql` ativa e forca RLS, enquanto o backend usa a credencial definida pelo mesmo
bootstrap do banco. O ambiente precisa separar quem administra/cria objetos de quem executa a API.
Sem essa separacao, uma verificacao pode passar com privilegios que a aplicacao de producao nao deve
possuir.

### Decisao e motivo

Como o aplicativo esta no primeiro desenvolvimento e os dados locais sao descartaveis, esta entrega
nao precisa atualizar bancos existentes sem reset. O caminho aprovado e ajustar `rls.sql`, os papeis
e `backend/scripts/gerenciar_banco.py`, apagar/recriar o banco local e repopula-lo para os testes.
Preservacao de dados existentes vira obrigacao somente na preparacao para producao (`F12-01/02`).

### Escopo

- separar papel administrativo/migracao do papel restrito usado pela API;
- impedir `SUPERUSER`, `BYPASSRLS` e propriedade indevida no papel da aplicacao;
- conceder apenas os privilegios necessarios em schema, tabelas e sequencias;
- adaptar reset, aplicacao de RLS, seed e verificacao em `gerenciar_banco.py`;
- validar duas Empresas usando a credencial real da aplicacao;
- manter o filtro explicito por `EmpresaID` como primeira trava e RLS como defesa em profundidade.

### Validacao e aceite

- `reset --semear` constroi um ambiente funcional do zero;
- a API opera com o papel restrito;
- sem `app.empresa_id`, tabelas tenant nao retornam linhas;
- Empresa A nao le, altera ou remove dados da Empresa B;
- o verificador reprova papel com privilegio capaz de ignorar RLS.

### Fora do escopo

Upgrade incremental, Alembic, preservacao de banco existente e rollback produtivo. Destino:
`F12-01` e `F12-02`.

## F08-02 - Registrar a destinacao de migracoes e escopos complementares

**CU:** `868kd1juf`  
**Tags:** `docs-operacao`, `qa-validacao`

### Por que este item existe

Os topicos retirados da implementacao imediata precisam continuar rastreaveis. Este item e um
registro de decisao e referencias cruzadas, nao uma etapa de codigo.

| Topico | Decisao | Destino |
|--------|---------|---------|
| Alembic e migracoes versionadas | Manter no projeto, implantar perto do go-live | `F12-01` (`868kd1k6v`) |
| Atualizar banco existente sem reset/perda | Obrigacao de producao, nao de dev local atual | `F12-01/02` (`868kd1k6v`, `868kd1k7a`) |
| Rate limit compartilhado/Redis | Necessario antes de multiplas replicas | `F12-03` (`868kd1k7e`) |
| Privacidade por assunto sensivel e isolamento de mensagens de RH por topico | Evolucao futura; as personas nao definem regra atual | Adiados, `CU: 868k7vrgk` |
| Novas funcionalidades de Empresa/Condominio | Nao antecipar na consolidacao | Fase 7, `CU: 868k60wgx` |

### Aceite

Cada assunto possui destino no plano e no ClickUp; nenhum e tratado como esquecido nem executado em
duplicidade dentro da Fase 0.8.

## F08-03 - Fazer o logout mobile revogar a sessao no backend

**CU:** `868kd1juu`  
**Tags:** `frontend-mobile`, `seguranca`

### Evidencia e problema

A tela `frontend/mobile/app/(tabs)/perfil.tsx` chama apenas `auth.sair()`. Isso apaga o SecureStore,
mas nao usa `POST /autenticacao/logout`, que ja revoga o `jti` e a familia do refresh no servidor.

### Escopo e casos de borda

- adicionar contrato `api.logout()` mobile enviando access e refresh;
- tentar revogacao antes de limpar tokens locais;
- sempre permitir saida local se a rede falhar;
- evitar refresh automatico durante o proprio logout;
- proteger contra toques repetidos e navegacao duplicada.

### Aceite

Online, access e refresh reutilizados falham depois do logout. Offline, o aparelho termina a sessao
local e volta ao login sem travar. Tokens nunca permanecem no SecureStore depois da acao.

## F08-04 - Impedir acesso de usuario inativo em toda a sessao

**CU:** `868kd1jvc`  
**Tags:** `seguranca`, `backend`

### Evidencia e problema

O login rejeita `Usuario.Ativo=False` e a desativacao revoga refresh tokens, mas
`obterUsuarioAtual` nao verifica `Ativo`. Um access token emitido pode continuar valido ate expirar;
dependencias que usam apenas o tenant tambem precisam de uma regra que nao contorne a desativacao.

### Escopo

- negar access token de usuario inativo em todas as rotas protegidas;
- negar refresh para usuario inativo;
- revisar dependencias tenant-only;
- preservar historico e relacionamentos: desativacao nunca exclui o usuario;
- reativacao permite um novo login, sem ressuscitar sessoes antigas.

### Aceite

Depois da desativacao, login, refresh e access token previamente emitido falham. O usuario continua
no historico e fora de novas atribuicoes. Ao reativar, somente credenciais obtidas em novo login
voltam a funcionar.

## F08-05 - Tornar a rotacao de refresh segura sob concorrencia real

**CU:** `868kd1jvr`  
**Tags:** `seguranca`, `backend`, `qa-validacao`

### Evidencia e problema

Web e mobile ja implementam single-flight dentro de uma instancia JavaScript. Isso nao cobre abas,
reinicio do app, retry de rede ou outras instancias. No backend, `servicos/refresh.py` faz leitura e
alteracao sem bloqueio explicito; chamadas simultaneas podem consumir o mesmo elo e interpretar uma
corrida legitima como roubo, revogando a familia correta.

### Decisao tecnica que deve anteceder o codigo

Comparar e documentar uma destas abordagens: falha segura da segunda chamada, pequena resposta
idempotente/janela de tolerancia ou outra operacao atomica. A escolha deve impedir dois sucessores
validos sem enfraquecer a deteccao de replay posterior.

### Escopo e aceite

- consumo atomico/transacional do refresh no banco;
- single-flight mantido nos clientes como primeira defesa;
- teste simultaneo em mais de um contexto;
- duas chamadas nao geram dois sucessores nem derrubam silenciosamente a sessao legitima;
- replay posterior segue sendo detectado conforme a regra aprovada;
- testes repetidos nao apresentam intermitencia.

## F08-06 - Criar suite automatizada executavel sob solicitacao

**CU:** `868kd1jwg`  
**Tags:** `qa-validacao`, `backend`

### Modelo de uso aprovado

A suite e um instrumento evolutivo de auditoria. O usuario pode pedir, por exemplo, a conferencia
das Fases 1 e 1.5; o executor seleciona esses cenarios e as invariantes compartilhadas. A regressao
completa nao se torna regra automatica depois de cada manutencao.

### Escopo inicial

- estrutura backend e comandos por dominio/fase;
- mapa fase -> testes e dados controlados;
- cobertura inicial de RLS/papeis, logout, usuario inativo e refresh concorrente;
- execucao local completa ou seletiva;
- CI manual (`workflow_dispatch`) ou equivalente, sem obrigatoriedade em todo commit;
- relatorio com aprovado, falhou, nao executado e evidencias.

### Regra e aceite

Cada implementacao prepara cobertura proporcional ao risco, dados e comandos. Nada e executado ate
o usuario disparar a fase/conjunto. Um comando documentado executa tudo ou fases selecionadas, falha
com codigo diferente de zero e permite crescer sem reestruturar o conjunto inteiro.

## F08-07 - Implementar cancelamento, reabertura e continuidade do responsavel

**CU:** `868kd1jwx`  
**Tags:** `docs-operacao`, `qa-validacao`

### Descoberta original e decisao

> O produto definiu claramente a jornada de conclusao do chamado, mas ainda nao definiu o que deve
> acontecer quando uma solicitacao deixa de ser necessaria. Os materiais comerciais usam Recebido,
> Em andamento, Agendado e Concluido. O codigo antecipou Cancelado sem regra completa.

Em 16/07/2026, a equipe aprovou cancelamento com motivo obrigatorio, reabertura pelo Cliente,
responsavel preservado, novo ciclo de SLA e comunicacao de todas as transicoes. A decisao formal
esta em `docs/decisoes/ADR-001-cancelamento-reabertura-chamados.md`.

### Evidencias consultadas

- `FaciliChat-Apresentacao.html`, jornadas e materiais de branding: quatro estados da jornada;
- `FaciliChat-Design-System.html`: “Cancelar” aparece como acao de formulario, nao estado do chamado;
- `FaciliChat-Personas.md.docx`: nenhuma regra de cancelamento; privacidade sensivel aparece como
  evolucao futura;
- modelos, documentos tecnicos, changelog e seed: ja usam/antecipam `Cancelado`.

### Regras aprovadas

- Gestor cancela qualquer chamado do tenant; Supervisor somente o atribuido; RH/Financeiro somente
  suas filas.
- Recebido/Em andamento/Agendado podem ser cancelados com motivo; Concluido nao cancela/reabre.
- Cliente solicitante reabre Cancelado para Recebido com explicacao, mesmo responsavel atual e novo
  ciclo SLA, preservando anteriores.
- IA apenas narra fatos; falha usa fallback; WhatsApp nao bloqueia/desfaz status.
- Supervisor padrao por Condominio pertence a Fase 7; reatribuicao pela UI do Gestor integra F08-07.

### Especificacao executavel

As onze subfases, APIs, dados, permissoes, UI, casos de borda, riscos, dependencias e criterios de
aceite estao em `docs/implementation/11-fase-08-07-cancelamento-reabertura.md`.

### Regra de testes

Testes sao preparados em cada subfase, mas executados somente quando o usuario disparar
explicitamente a fase/conjunto. Antes disso, nenhum item pode ser descrito como validado.

## Riscos gerais e rollback

- Mudancas de sessao podem deslogar ambientes de desenvolvimento; reset/novo login e esperado.
- Mudancas de papel podem quebrar grants; manter comando de reconstrucao local e diagnostico claro.
- Cancelamento/reabertura alteram varios consumidores; seguir a ordem e o contrato detalhado para
  nao criar status sem historico, SLA ou comunicacao coerente.
- Se uma estrategia de refresh falhar na validacao concorrente, nao publicar a mudanca parcial:
  retornar ao comportamento anterior e manter o item em revisao.

## Documentacao esperada durante a implementacao

Atualizar, conforme o item: `docs/tecnico-backend.md`, `docs/tecnico-frontend.md`, `docs/setup.md`,
`docs/deploy-producao.md`, `docs/arquitetura.md`, `docs/visao-geral.md` e `docs/changelog.md`.
