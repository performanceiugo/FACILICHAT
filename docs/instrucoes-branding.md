# FaciliChat — Instruções do Branding (documento consolidado)

> **O que é este arquivo:** a consolidação, em um só lugar, de tudo que foi **definido no material de
> branding/produto** (`docs/FaciliChat-Regras/`) — tese, perfis, personas, fluxos, telas, estilos,
> regras da IA e jornadas — escrito como **instrução normativa** para quem for implementar.
>
> **Precedência:** este documento é DERIVADO. A fonte da verdade continua sendo
> `docs/FaciliChat-Regras/` (apresentação, design system, personas, MVP02, governança de IA,
> jornadas, HMW) e as decisões formais em `docs/decisoes/` (ADRs). Em caso de conflito, a fonte
> original + ADR mais recente prevalecem. Divergências conhecidas estão marcadas ao longo do texto
> e consolidadas na seção final.
>
> **Fontes lidas na íntegra (16/07/2026):** `FaciliChat-Apresentacao.html`,
> `FaciliChat-Design-System.html` (v1.0), `FaciliChat-Personas.md.docx`,
> `FaciliChat-MVP02-Visitas-Tecnicas.html`, `Novos arquivos/FaciliChat-Governanca-IA.html`,
> `Novos arquivos/FaciliChat-Jornada-{Cliente,Dono,Funcionario_1,Supervisor}.html`,
> `Novos arquivos/FaciliChat-How-Might-We{,-Supervisor-Gestor}.html`.

---

## 1. Tese central do produto

**Headline comercial:** "Transforme o atendimento da sua conservadora no maior diferencial que ela
tem diante do cliente." — "Simples como uma conversa de WhatsApp para o cliente. Completo como um
sistema de verdade para a sua operação. E, de quebra, uma máquina de identificar vendas."

**O problema:** "A maior reclamação que você recebe hoje é falta de retorno do supervisor. É também
o item nº 1 que faz um cliente escolher (e renovar) um contrato." O caso de referência que atravessa
todo o material: **o jardineiro que ficou três semanas sem resolução** — "Nenhum sistema falhou.
A demanda evaporou no espaço entre o pedido e a execução." Essa é a **falha silenciosa**, "o coração
do projeto".

**A trinca de sensações que o produto precisa entregar:**
- **Ouvido** — "Cada mensagem recebe resposta na hora, nunca cai no vazio."
- **Respondido** — "Toda demanda vira ticket com prazo, acompanhado até o fim."
- **Cuidado** — "A mesma atenção para todo cliente, não importa quem atende."

**Anti-amnésia (tese que sustenta tudo):** "Tudo registrado, nada se perde." O histórico "é da
empresa, para sempre" — não da Meta, não do celular do supervisor. "O relacionamento com o cliente
deixa de ser refém de quem opera e vira patrimônio da empresa."

**Chat é o palco, ticket é o bastidor:** "O cliente nunca vê essa engrenagem. Para ele, é só uma
conversa que sempre responde. A organização toda acontece invisível." O ticket é "infraestrutura
invisível"; a bolha de mensagem é o "componente-herói".

**Dois eixos do produto:**
- **MVP 01 (reativo):** "garante que nada que o cliente pede se perde".
- **MVP 02 (proativo):** "prova que a operação cuida mesmo quando ninguém pede" — a visita técnica
  é a primeira ferramenta desse eixo.

---

## 2. Modelo de negócio e atores

| Ator | Papel |
|---|---|
| **Iugo Performance** | Criadora/operadora da plataforma. É o **Superadmin** ("infraestrutura interna, não um usuário a ser pesquisado"). |
| **Empresa** (conservadora/facilities) | O **tenant** — compradora do produto. Dona do dado, do histórico e do canal oficial. |
| **Condomínios** | Os clientes da Empresa. Quem fala pelo condomínio é um responsável cadastrado (síndico, zelador ou administradora). |

Multi-tenant é regra de arquitetura: "cada conservadora tem seu próprio espaço isolado, com seus
clientes, sua equipe e suas regras. A IA de cada uma enxerga apenas o catálogo da sua empresa, e
nunca cruza fronteiras."

**Cadastro do cliente (Condomínio) guarda:** razão social, CNPJ, contrato (ex.: "Limpeza +
portaria"), responsável ("quem fala com a gente": nome, cargo, WhatsApp, e-mail) e **Supervisor
responsável**. Nota literal: "O WhatsApp e o e-mail ficam guardados para, no futuro, a gente poder
disparar mensagens e avisos para o cliente."

---

## 3. Os 7 perfis

Frase normativa das personas: "O FaciliChat tem sete perfis técnicos no sistema: **Cliente,
Funcionário, Supervisor, RH, Financeiro, Gestor e Superadmin**."

- **Cliente** — vê a conversa, "Minhas solicitações" (lista com status), o detalhe do pedido (linha
  do tempo, executor, data/hora, responsável) e propostas no chat com botões **Aprovar/Recusar**.
  Nunca vê a engrenagem interna nem a nota interna ("Nota interna · o cliente nunca vê").
- **Funcionário** — **perfil único, decisão de produto literal:** "Não existem subtipos de
  funcionário no FaciliChat. Auxiliar de limpeza, porteiro, zelador e qualquer outro colaborador de
  campo compartilham o mesmo perfil e a mesma experiência: uma conversa única na qual a IA roteia
  cada demanda para a fila correta." Usa voz e foto como entrada de primeira classe.
- **Supervisor** — "o eixo do produto: é nele que a demanda do cliente e a do funcionário se
  encontram e viram ação." App mobile: fila por prazo, agenda "Hoje", ticket completo, conversa.
  "Notificações apenas para demandas que ele próprio precisa resolver." "Cada ação cabe em menos de
  30 segundos."
- **RH** — fila própria de pessoal (atestados, férias, documentos, admissões, desligamentos);
  "fila própria e rastro"; fecha pendência "com motivo registrado"; mantém as respostas automáticas
  das dúvidas recorrentes de RH.
- **Financeiro / DP** — fila própria (folha, holerites, vales, adiantamentos, contas); pensa "por
  competência e verba"; exige "referências claras (competência, tipo de verba)". Pendência aberta:
  RH e Financeiro podem ser a mesma pessoa — "atribuir as duas filas ao mesmo login é decisão de
  cadastro, não de arquitetura."
- **Gestor** (o "dono" no material comercial) — painel desktop: **Visão geral, Supervisores, Todos
  os tickets, Alertas comerciais, Cadastros**. Poderes: "Ler a conversa inteira / Mandar mensagem
  direto ao cliente / Reatribuir a outro responsável / Cobrar o supervisor com histórico."
- **Superadmin** — a Iugo operando a plataforma, entre tenants.

> ⚠️ **Visibilidade entre áreas (regra vigente vs. futura):** o material declara explicitamente que
> "hoje o FaciliChat não aplica restrição de visibilidade entre áreas" — supervisor e gestor
> enxergam as conversas, inclusive folha/atestado. "Criar fronteiras de privacidade para conteúdo
> sensível é evolução de produto, não regra vigente." (Registrado como adiado no plano —
> `CU: 868k7vrgk`.)

---

## 4. Personas (proto-personas, fase Definir do Duplo Diamante)

Seis personas; "hipóteses sólidas o suficiente para guiar decisões, mas devem ser testadas".
O norte comum: "fazer uma comunicação que hoje falha em silêncio passar a ser **ouvida, respondida
e cuidada**".

| Persona | Perfil | Objetivo central (literal) | Citação-síntese |
|---|---|---|---|
| **Regina Mattos**, 52 | Cliente · Síndica (3 condomínios) | "Sentir-se ouvida, respondida e cuidada em cada pedido, sem nunca ter que perseguir uma resposta." | "Eu não quero administrar o problema. Quero saber que alguém competente já está com ele." |
| **Cleusa Andrade**, 56 | Funcionário · Limpeza (celular simples, voz e foto) | "Ser ouvida e atendida pela empresa de um jeito simples, com a tranquilidade de saber que o recado chegou a quem precisava." | "Eu só quero avisar a empresa e ter certeza de que alguém recebeu, sem ter que correr atrás do número de ninguém." |
| **Bruno Almeida**, 41 | Supervisor de campo (~45 postos, ~22 clientes) | "Dar conta de muitos postos sem deixar nenhuma demanda perdida ou esquecida, gastando menos tempo do que gasta hoje." | "Se o sistema me obriga a parar e preencher formulário pra cada uma, eu volto pro WhatsApp e ele vira enfeite." |
| **Júlia Reis**, 34 | Analista de RH | "Tratar cada demanda de pessoal com organização, registro e prazo, sem nada se perder no meio do caminho." | "Cada atestado é um documento, um prazo e a vida de uma pessoa. Não pode ficar solto num grupo." |
| **Marcos Campos**, 45 | Analista Financeiro / DP | "Tratar cada demanda financeira com rastro completo e organização, sem que nada se misture com outras áreas." | "Dinheiro e holerite exigem rastro. Se não dá pra provar o que foi pedido e quando, vira problema." |
| **Henrique Vargas**, 49 | Gestor / Dono | "Nunca mais perder um cliente por uma falha que aconteceu escondida dele, e poder confiar que a operação está sendo entregue." | "Eu não quero descobrir um problema por uma ligação irritada. Quero ver o problema antes do cliente ver." |

**Testes contra o caso de referência (usar como critério de design):**
- Regina: "Se uma decisão de design não muda o desfecho dessa história para Regina, ela não está
  fazendo seu trabalho."
- Cleusa: "Se a interface a obriga a entender a estrutura interna da empresa para ser atendida, ela
  falhou justamente com quem mais precisa de simplicidade."
- Bruno: "o sistema só funciona se for mais leve que o WhatsApp: cada toque a mais é uma chance de
  Bruno desistir e voltar ao canal informal."
- Henrique: "Toda decisão de produto deve permitir que o gargalo apareça no painel dele antes de
  virar a ligação irritada do cliente."

---

## 5. O chamado (ticket): estados, fluxo e regras

### 5.1 Estados canônicos do branding

O design system nomeia: **"Estados de ticket — 4 universais (MVP)"** — "Linguagem simples e direta,
iguais para todos os perfis. Refinamento por área fica para depois do piloto."

`Recebido → Em andamento → Agendado → Concluído`

> ⚠️ **Estado Cancelado e reabertura:** NÃO existem no material de branding — foram definidos
> depois, em decisão formal (`docs/decisoes/ADR-001-cancelamento-reabertura-chamados.md`, F08-07):
> cancelamento com motivo obrigatório; Gestor cancela no tenant, Supervisor só o atribuído,
> RH/Financeiro só suas filas; somente o Cliente solicitante reabre Cancelado→Recebido; Concluído
> não cancela/reabre. **O design system v1.0 não define cor para a pílula "Cancelado"** — precisa
> ser definida quando a UI for implementada (seguindo a família de feedback existente).

### 5.2 A jornada completa (nomes literais da apresentação)

1. **O cliente — Manda a mensagem:** "Escreve, manda foto, vídeo, PDF ou grava um áudio, como no
   WhatsApp."
2. **A IA — Responde na hora e organiza:** "Confirma o recebimento ('já encaminhei ao Bruno'),
   entende o pedido e abre um ticket pro responsável certo. O cliente nunca fica no vazio."
3. **A equipe — Resolve e agenda:** "O supervisor recebe no celular, na fila por urgência, e agenda
   em segundos. A IA avisa o cliente do agendamento automaticamente."
4. **O cliente — Acompanha sem precisar cobrar:** "Vê o status 'Agendado, quinta às 10h' e a
   conversa com o supervisor. Tudo no mesmo lugar."
5. **A equipe — Conclui, e o dono vê tudo:** "O ticket só fecha quando o serviço é entregue."

### 5.3 Regras de fluxo obrigatórias

- **Ticket nasce no instante da mensagem**, com confirmação automática ao cliente ("Recebido").
  "A demanda nasce com rastro, não na memória de alguém."
- **Roteamento por intenção:** a IA entende e envia à fila certa sem o usuário conhecer o
  organograma. (Apresentação cita "supervisor, financeiro ou contratos"; a modelagem vigente das
  personas usa as filas dos 7 perfis, incluindo RH.)
- **Tickets irmãos:** "um único aviso (ex.: doença) chega ao RH e à supervisão ao mesmo tempo" —
  um para o RH validar o atestado, outro para a supervisão cobrir o posto, "sem que Cleusa precise
  saber que existem duas filas". Princípio: "um único aviso humano pode gerar várias frentes de
  trabalho, cada uma na fila certa."
- **Cada área recebe só a sua fatia:** o supervisor recebe o ticket "já recortado para o que é
  dele"; "se o app o notifica de coisas que são do RH ou do financeiro, vira ruído e ele desliga o
  sino."
- **Agendamento alimenta a comunicação:** executor, data e hora; "Editar a data dispara uma nova
  mensagem ao cliente." A observação do supervisor "vai junto na mensagem" da IA.
- **Conclusão consciente:** modal literal — "O serviço já foi executado? Só conclua quando o
  serviço estiver entregue. O cliente recebe a mensagem de encerramento e o ticket é arquivado no
  histórico." (botões "Ainda não / Sim, concluir").
- **Fechamento com motivo registrado** — vira dado de desempenho "sem esforço extra" e protege em
  questionamento (RH/Financeiro).
- **Confirmação pelo cliente:** o material diz "o supervisor conclui e o cliente aprova no chat".
  Isso foi formalizado na `ADR-002` (estado `AguardandoConfirmacao`: Supervisor/Gestor envia resumo
  e o Cliente confirma ou recusa; sem conclusão automática) — implementar conforme a ADR-002 e a
  especificação da Fase 1.
- **Escalonamento:** sem resposta do responsável, o caso sobe — "Sem resposta do Rogério há 2 dias ·
  escalado ao dono"; o Gestor pode entrar na conversa (identificado) e reatribuir.
- **Tempo parado é sinal:** item "aberto tempo demais sobe no painel como gargalo, puxando atenção
  antes da reclamação". [Limiar numérico NÃO definido no branding — os valores "+48h" e "3 dias"
  dos mockups são ilustrativos. SLA concreto é decisão de implementação.]
- **Nota interna** existe no ticket e **o cliente nunca vê**.

### 5.4 Fluxo comercial (o "bônus")

"Quando o pedido é um serviço novo (pintura, reforma, câmeras): A IA percebe que é uma oportunidade
de venda e avisa o dono. O dono monta a proposta (escopo, prazo, preço) e envia no chat. O cliente
aprova ali mesmo." Funil literal: **Nova oportunidade → Proposta enviada → Aprovada no chat**.
Tela "Montar proposta": o que o cliente pediu, título, escopo, prazo médio, início previsto, valor,
"Enviar proposta no chat do cliente / Salvar rascunho", com preview de como o cliente verá.

---

## 6. Visita técnica (MVP 02)

**Decisão de arquitetura que define o MVP 02:** "A visita técnica é uma entidade nova, **irmã do
ticket, e não um tipo de ticket**. Tratá-la como ticket quebraria o modelo."

| Aspecto | Ticket | Visita técnica |
|---|---|---|
| Quem dispara | O cliente, de fora para dentro | O supervisor, de dentro para fora |
| Natureza | Reativa: responde a uma demanda | Proativa: prova um cuidado |
| Marca de tempo | Não tem cronômetro | Início e fim reais, **duração derivada** |
| Aprovação do cliente | Sim (confirmação de conclusão) | **Não — o cliente recebe e consulta a prova** |

**Estados:** `Agendada → Em andamento → Finalizada → Relatório enviado`. Cada transição é ação
concreta do supervisor; só o envio do relatório é automático ("Automático na finalização").

**Duas origens, mesmo objeto:**
- **A — Agendamento explícito:** supervisor escolhe cliente, data e hora; a IA avisa no chat.
- **B — Acordo no chat:** "vou aí amanhã às 10h" + confirmação do cliente → "a IA detecta o acordo
  e cria a visita agendada sozinha". Regra: "a IA só a cria porque **dois humanos confirmaram o
  compromisso por escrito**." Variante: cliente pede visita sem data → a visita nasce "Agendada sem
  data" e a IA grava dia/hora quando os dois combinarem no chat.

**Regras de dados (literais):** tabela `visita_tecnica` irmã de `ticket` — campos `cliente`,
`supervisor`, `status`, `agendada_para`, `iniciada_em`, `finalizada_em`, `relatorio_texto`,
`ticket_id` opcional. "**A duração não é coluna: deriva de `finalizada_em` menos `iniciada_em`.**"
Texto e fotos com **salvamento incremental** ("Se o app fechar, nada se perde"). Após finalizar,
"a visita vira **registro fechado e imutável**".

**Telas definidas:**
- **Visita em andamento (app do supervisor):** cronômetro visível no topo ("o cronômetro é
  proposital — é exatamente a prova que o gestor quer ter contra a reclamação de ausência"), campo
  único de texto corrido ("sem checklist, sem divisão por setor — a simplicidade é deliberada"),
  fotos empilhadas na ordem, botão "Finalizar visita".
- **Cliente:** narração no chat na finalização ("Foi realizada a vistoria hoje, das 10:00 às 10:42,
  pelo supervisor Bruno...") + **painel de visitas técnicas** (aba separada do chat) com data,
  início/fim, duração, supervisor, relatório e fotos — "a arma anti-amnésia".
- **Gestor:** KPIs Agendadas (semana) · Em andamento (agora no local) · Concluídas no mês ("todas
  com relatório") · **Agendadas e não feitas ("cobrar supervisor")**; tabela Cliente | Supervisor |
  Data | Duração | Status.

**Fora do MVP 02 (explícito):** registro estruturado por área/setor; checklist; relatórios
analíticos por período; visita conduzida pelo funcionário.

---

## 7. Governança da IA

**Princípio-mestre — geração ancorada:** "Toda mensagem da IA nasce de um fato registrado: um campo
do ticket, uma regra na base, um serviço no catálogo. **Se a fonte não existe, a mensagem não
existe.** A alucinação é eliminada por arquitetura, não por instrução."

**Catálogo por tenant:** cada Empresa configura os serviços que oferece (próprio ou parceria).
"Esse catálogo é a única fonte do que a IA pode reconhecer como oportunidade." **"O preço nunca
entra aqui: o catálogo diz o que pode ser oferecido, não por quanto."**

### As 6 regras que a IA nunca quebra ("nenhuma instrução de tenant pode sobrepô-las")

1. **Nunca inventa preço** — "Nenhuma proposta de preço sai da IA, em nenhum perfil."
2. **Nunca oferece o que não está no catálogo** — "Um serviço fora do catálogo daquela empresa não
   existe para a IA."
3. **Nunca fala por um humano** — "A IA se identifica sempre como assistente, nunca se passa por
   uma pessoa e nunca promete em nome do supervisor ou da empresa."
4. **Nunca promete prazo de execução** — "Prazos são decisão humana. A IA só narra uma data depois
   que ela está registrada no ticket por quem é responsável."
5. **Nunca responde regra não cadastrada** — "Para RH e financeiro, a IA só responde o que está na
   base de regras da empresa. Diante de regra ausente, ela encaminha, não inventa."
6. **Nunca cruza fronteiras entre empresas** — "O isolamento é por arquitetura."

### Matriz pode/não pode por perfil (resumo — íntegra na fonte)

| Perfil | PODE (essência) | NÃO PODE (essência) |
|---|---|---|
| Cliente | Confirmar recebimento; narrar status; avisar visita; oferecer serviço do catálogo quando há intenção | Preço/venda; serviço fora do catálogo; prometer prazo; falar em nome do supervisor |
| Funcionário | Rotear por intenção; confirmar atestado/falta/pedido; registrar reposição de insumos; captar relato como oportunidade | Tratá-lo como vendedor; exigir que entenda a estrutura interna; responder regra de RH não cadastrada |
| Supervisor | Entregar só a fatia operacional; registrar visita/relatório ancorado; criar visita de acordo confirmado; alertar tickets parados | Inventar compromisso; concluir ticket no lugar dele; notificar assuntos de RH/financeiro |
| RH | Só a fila de RH; atestado como ticket datado; responder regra cadastrada | Regra não cadastrada; validar atestado/aprovar afastamento sozinha; decidir prazo legal |
| Financeiro | Só a fila financeira; pedido como ticket datado; responder regra cadastrada | Valores/saldos não registrados; autorizar pagamento; regra não cadastrada |
| Gestor | Narrar indicadores de todas as filas; sinalizar gargalos; alertas de oportunidade (sem preço); desempenho por supervisor/fila | Construir/sugerir preço; decidir gestão no lugar dele; inventar número sem fato |
| Superadmin | Operar entre tenants; apoiar configuração; métricas de uso | Misturar/expor dados entre tenants; alterar conteúdo operacional sem solicitação |

### Sensor de campo (fluxo com portão obrigatório)

1. Funcionário relata (ex.: foco de baratas na garagem) — "só está relatando, não vendendo".
2. IA detecta a intenção (possível dedetização) — "detecta, mas ainda não fala nada ao cliente".
3. **O portão: consulta o catálogo** daquele cliente/empresa.
4. **Está no catálogo** → vira **alerta de oportunidade no painel do Gestor** (ele decide e monta a
   proposta com preço). **Não está** → **silêncio comercial**: "no máximo, registra a observação
   para a supervisão, como informação operacional." — "Pior que não detectar é oferecer o que não
   se pode entregar."

**Quem configura o quê:** Gestor → catálogo e regras comerciais; RH e Financeiro → bases de regras
das áreas; Superadmin → estrutura da plataforma e apoio ao onboarding.

**Fallback:** fonte ausente = mensagem não existe; regra ausente = encaminha. [O branding não define
comportamento em falha técnica do modelo — isso é decisão de implementação; o código usa fallback
determinístico.]

---

## 8. Design system (v1.0 — tokens obrigatórios)

Lead literal: "A interface é deliberadamente clean — branco, cinza e um único azul de destaque —
porque ela hospeda a marca de cada cliente e nunca deve competir com ela."

### 8.1 Os 4 princípios visuais

1. **"Discrição que dá palco ao cliente"** — "a marca do cliente seja sempre o elemento colorido
   mais forte da tela."
2. **"O chat é o palco, o ticket é o bastidor"** — bolha = componente-herói; status = "informação
   calma, nunca alarmante".
3. **"Clareza acima de ornamento"** — "estados em português direto e zero jargão técnico."
4. **"Consistência que se aprende uma vez"** — "Sete perfis usam o mesmo vocabulário visual. Um
   botão azul significa a mesma coisa para o cliente e para o gestor."

### 8.2 Cores

**Núcleo da marca (FIXAS, "não alterar"):** `#148AF5` (Azul) · `#17171A` (Ink) · `#C1CCD3` (Cinza)
· `#FFFFFF` (Branco).

**Escala azul:** 50 `#EAF4FE` · 100 `#D2E8FD` · 200 `#A6D0FB` · 300 `#6DB3F8` · 400 `#3D9BF6` ·
500 `#148AF5` (núcleo) · **600 `#0E72D4` (hover do primário; links)** · 700 `#0B5BAB` ·
800 `#0C4D8F` · 900 `#0E416F`.

**Escala Ink (neutros):** 900 `#17171A` · 800 `#25262B` · 700 `#34363D` (texto padrão) ·
600 `#4A4D57` · 500 `#646874` · 400 `#868B97` · 300 `#A7AEB8` · 200 `#C1CCD3` · 150 `#D8DFE5` ·
100 `#E7ECEF` · 75 `#F1F4F6` · 50 `#F7F9FA` · 25 `#FBFCFD`.

**Feedback ("intensidade mínima; o azul NUNCA é usado para erro ou alerta"):**
- Sucesso/Concluído: `#1FAE68` · bg `#E7F6EE` · texto `#157A49`
- Atenção/Agendado: `#F0961E` · bg `#FEF4E6` · texto `#B96E0F`
- Erro/Crítico: `#E5484D` · bg `#FDECEC` · texto `#B4282D`
- Info: alias do azul (50/500)

**Semânticos:** fundo da aplicação `--bg-app: #F4F6F8`; card `#FFFFFF`; bordas: sutil `#E7ECEF` /
padrão `#D8DFE5` / forte `#C1CCD3`; foco `#148AF5`. [Nota: o CSS fonte usa `#F4F6F8` como fundo de
página; o resumo do CLAUDE.md usa `#F7F9FA` (Ink 50). Na dúvida, seguir o token da fonte.]

### 8.3 Tipografia — Figtree (única)

Pesos: 400 corpo · 500 rótulos · 600 ênfase · 700 títulos · 800 display. Escala (usar `rem`):
Display 56/1.04 EB · H1 40/1.1 EB · H2 32/1.15 B · H3 24/1.25 B · H4 20/1.3 SB · Body LG 18/1.5 ·
**Body 16/1.55 (leitura padrão)** · Small 14/1.5 · Caption 12/1.45 SB caixa alta. Body padrão:
Figtree 400 16px, cor `#34363D`.

### 8.4 Espaçamento, raios, sombras, motion

- **Espaçamento base 4px** — degraus: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80. "Nunca valores
  soltos."
- **Raios:** 6 (xs) · **8 (botão)** · **12 (tabela/alerta/modal)** · **16 (card, bolha de chat)** ·
  20 · 28 · **999 (badge/pílula/switch/avatar)**.
- **Sombras** (base azul-acinzentada): cards usam SM; menus e modais usam LG.
  sm `0 1px 3px rgba(23,23,26,.06), 0 1px 2px rgba(23,23,26,.04)` ·
  lg `0 12px 32px rgba(23,23,26,.08), 0 4px 8px rgba(23,23,26,.04)`.
- **Motion:** `cubic-bezier(.4,0,.2,1)`; 120/200/320ms; respeitar `prefers-reduced-motion`.

### 8.5 Ícones

**Line Awesome** ("estilo linha, traço uniforme, cantos levemente arredondados"). **18–24px,
espessura ~1.6px, na cor do texto adjacente.** "No build use os SVGs oficiais da biblioteca."

### 8.6 Componentes essenciais (medidas na fonte; regras normativas aqui)

- **Botões:** "A ação primária é sempre azul e **única por tela**." Variantes: primária
  (azul→hover 600), secundária (contorno azul), fantasma, neutra, destrutiva (`#E5484D`).
  "O rótulo diz exatamente o que acontece ('Enviar', 'Concluir ticket'), **nunca 'Submeter'**."
- **Formulários:** "Rótulos sempre visíveis"; foco = borda azul + anel 3px `#D2E8FD`-claro
  (blue-100); "mensagens de erro que dizem **o que corrigir** — nunca um 'campo inválido'
  genérico" (ex.: "Digite um e-mail completo, como contato@empresa.com.br").
- **Badges/pílulas:** raio 999, 12px SemiBold, com ponto de cor. "Cores de feedback aparecem só
  quando carregam significado."
- **Alertas:** raio 12; exemplos de copy: "SLA próximo do limite — Este chamado está há 2 dias sem
  resposta da equipe. Recomendado priorizar." / "SLA estourado — O prazo combinado foi
  ultrapassado. Acione o supervisor responsável imediatamente."
- **Chat:** bolha recebida branca à esquerda; enviada azul à direita; **mensagem de
  sistema/ticket = pílula central neutra** ("infra invisível, narração neutra") — ex.: "Chamado
  #1042 aberto · roteado para Supervisor" · "Status atualizado para Agendado · 14/06". A IA assina
  como **"FaciliChat"**. Indicador de digitação com 3 pontos animados.
- **Tabela:** cabeçalho 12px caixa alta; hover de linha sutil; nº de ticket em SemiBold (`#1042`);
  campo vazio = "—".

### 8.7 Pílulas de status do chamado (cores exatas)

| Status | Fundo | Texto | Ponto |
|---|---|---|---|
| **Recebido** | `#F1F4F6` | `#4A4D57` | `#868B97` |
| **Em andamento** | `#EAF4FE` | `#0B5BAB` | `#148AF5` |
| **Agendado** | `#FEF4E6` | `#B96E0F` | `#F0961E` |
| **Concluído** | `#E7F6EE` | `#157A49` | `#1FAE68` |
| Cancelado | — | — | — ⚠️ não definido na fonte (pós-ADR-001; definir na implementação) |

### 8.8 Marca e logo ("Ativo travado — não modificar")

"A logo é fixa. Não pode ser redesenhada, recolorida fora das versões aprovadas, distorcida ou
reconstruída." Logo horizontal = assinatura principal (respiro mínimo = altura do símbolo; mínimo
**110px** de largura). Símbolo isolado (balão com check) = ícone de app/favicon/avatar (mínimo
**20px**). **NÃO PODE:** recolorir, distorcer, sombra/contorno/gradiente, girar, trocar o símbolo,
"colocar sobre fundo de baixo contraste ou **sobre a logo de um cliente**".

### 8.9 Padrões de tela

- **Central de conversas:** lista à esquerda (300px) + thread à direita; item ativo com fundo
  azul-claro e borda esquerda azul; rodapé "Escreva uma mensagem…" + botão enviar primário.
- **Painel do gestor:** fundo cinza-gelo; KPIs em grid de 4 cards (rótulo caixa alta, número
  grande, badge); "o azul aparece só nos pontos de ação".
- **Navegação:** sidebar branca; item ativo fundo blue-50 texto blue-700; vira drawer < 1024px;
  grids colapsam < 768px.
- **Acessibilidade:** foco visível (anel 3px), `rem` na tipografia, `prefers-reduced-motion`,
  `aria-label` em botões-ícone.

---

## 9. Jornadas (Duplo Diamante) — o que cada papel exige do produto

Síntese literal: **Regina** "faz o pedido e precisa de certeza de que foi ouvida" (inicia a demanda
externa) · **Cleusa** "precisa que o recado chegue certo, sem fricção" (inicia a interna) ·
**Bruno** "recebe os dois lados e transforma conversa em ação" (o eixo que executa) · **Henrique**
"não opera nada, vê a operação inteira e age antes da crise" (a camada de consciência). Júlia (RH) e
Marcos (Financeiro) "compartilham a mecânica de fila e registro" (sem jornada própria ainda).

**24 pontos de ruptura → 24 perguntas How-Might-We**, agrupadas em temas de design (usar como
critério de avaliação de qualquer tela nova — "cada tela nova nasce respondendo a uma delas"):

- **Certeza de ter sido ouvido** — confirmação imediata "que pareça resposta de gente e não recibo
  automático frio".
- **Roteamento sem carga sobre o usuário** — ticket invisível, ramificação, voz/foto valem como
  texto, "nada de campo obrigatório".
- **Memória e tempo que não somem** — fila que "não se apaga no fim do dia"; histórico datado como
  prova; "a idade da demanda como sinal".
- **Leveza para quem carrega volume** — "fechar um ticket em menos toques do que mandar um zap" (a
  régua de fricção do produto inteiro); só o que é dele no sino.
- **Prova de presença sem virar tarefa** — visita com cronômetro que "caiba entre dois postos".
- **Enxergar a tempo, antes da crise** — gargalo sobe sozinho no painel; do alerta direto para a
  conversa; "o urgente em primeiro plano, a tendência num segundo nível, o detalhe sob demanda"
  ("Excesso de dado é a nova cegueira").
- **Decidir com fato, não com impressão** — desempenho por supervisor com lastro; oportunidade sem
  preço, só do catálogo.

---

## 10. Linguagem e tom (para toda comunicação com o usuário)

- **Simplicidade WhatsApp-like:** "Simples como o WhatsApp que ele já usa." Cliente "não é técnica
  e não quer ser."
- **Confirmação imediata, concreta e humana**, nomeando o responsável: "Recebi seu áudio, João!
  Você pediu um jardineiro para o jardim da frente. Já encaminhei ao Bruno e em breve ele retorna
  por aqui. 🌿" (tom caloroso, primeira pessoa, frases curtas, emojis moderados).
- **Status em linguagem de gente:** "Agendado, quinta às 10h" · "Respondido há 2h" ·
  "Atrasados, resolva primeiro".
- **Português direto, zero jargão técnico**; status como informação calma, nunca alarme.
- **Rótulos dizem o que acontece** ("Enviar", "Concluir ticket") — nunca "Submeter".
- **Erros dizem o que corrigir** — nunca "campo inválido".
- **A IA se identifica como assistente** (assina "FaciliChat"), nunca como pessoa.
- **Cobrança com fato, não achismo** (linguagem do painel do gestor).
- **Interfaces leves:** "Cada ação cabe em menos de 30 segundos"; "nada pode ser pesado ou cheio de
  botões".

---

## 11. Divergências e lacunas conhecidas (consolidado)

Itens em que o material de branding diverge internamente, ficou desatualizado por decisão posterior,
ou não define algo necessário. **Não resolver por conta própria — consultar o usuário/ADR:**

1. **Cancelado/reabertura:** ausentes de todo o branding; regra vigente é a `ADR-001` (F08-07).
   Cor da pílula "Cancelado" não existe no design system — definir na implementação da UI.
2. **Aprovação de conclusão pelo cliente:** o branding afirma que "o cliente aprova a conclusão no
   chat"; formalizada como `AguardandoConfirmacao` na `ADR-002` (Fase 1). A visita técnica,
   ao contrário, **não tem aprovação** — só recebimento da prova.
3. **Privacidade entre áreas:** hoje NÃO há fronteira (supervisor/gestor veem tudo, inclusive
   folha/atestado) — "decisão consciente do estágio atual"; isolamento é evolução futura
   registrada (adiados, `CU: 868k7vrgk`).
4. **SLA:** nenhuma meta numérica definida no branding ("+48h", "3 dias", "38min" são números
   ilustrativos de mockup). Limiar de gargalo é configurável na implementação
   (`LimiteGargaloHoras`).
5. **Destinos de roteamento:** a apresentação simplifica em 3 ("supervisor, financeiro ou
   contratos"); o modelo vigente são as filas dos 7 perfis (com RH separado). O select demo do
   design system ("Administrativo", "Comercial") não é normativo.
6. **RH × Financeiro:** podem ser a mesma pessoa — decisão de cadastro, não de arquitetura
   (pendência aberta com o gestor da conservadora).
7. **Fundo de página:** fonte usa `#F4F6F8` (`--bg-app`); CLAUDE.md resume `#F7F9FA` (Ink 50).
8. **Rótulos extras de protótipo** ("Respondido", "Em proposta", "Estourado", "Vencendo") são UI
   ilustrativa, não máquina de estados formal.
9. **Futuro registrado (não implementar sem fase própria):** WhatsApp como porta de entrada
   (Fase 1.5); integração ERP/estoque/financeiro; privacidade por assunto sensível; status de
   visita "Não realizada" (aparece num mockup do gestor sem regra de transição definida).
10. **Módulo Funcionário:** na apresentação é futuro ("quando o módulo de funcionário entrar");
    nas personas/jornadas, Cleusa tem fluxos completos especificados. Implementação segue o
    roadmap do plano.
