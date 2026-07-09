# Instruções para o agente Claude Code — FaciliChat

---

## 🔒 TRAVA DE SEGURANÇA — invariantes do produto (LER ANTES DE TUDO)

> Esta seção protege as decisões de produto **já fechadas com o comercial e o cliente**. Qualquer
> pessoa que use o Claude Code neste repositório está sujeita a ela. O objetivo é impedir que uma
> sessão futura altere — sem querer ou sem autorização — o que já foi definido.

**Fonte da verdade do produto:** `docs/FaciliChat-Regras/` (apresentação, personas, design system,
MVP02). É o material do comercial. **Nada implementado pode contrariá-lo.**

### Antes de QUALQUER alteração de funcionamento ou de regra de negócio no código, você DEVE:
1. **Ler** o item em `docs/plano-implementacao.md` e a regra correspondente em `docs/FaciliChat-Regras/`
   (ou o resumo em `docs/arquitetura.md`).
2. **Validar** que a mudança é coerente com os invariantes abaixo (pode rodar a skill `/validar-regras`).
3. Se a mudança **contrariar ou alterar** um invariante, **PARE e peça confirmação explícita ao
   usuário** antes de prosseguir. **Nunca** mude uma regra definida silenciosamente.

> Mudanças puramente cosméticas / de refatoração que **não** tocam regra de negócio estão liberadas
> (mas seguem as demais regras deste arquivo). Na dúvida, trate como alteração de regra e valide.

### Invariantes que NÃO podem ser quebrados sem autorização explícita do usuário
- **SaaS multi-tenant:** o tenant é a **Empresa** (conservadora/facilities); seus clientes são
  **Condomínios**; a Iugo Performance é o **Superadmin**. Toda tabela tem `EmpresaID`, toda query é
  escopada por ele, há **RLS** no Postgres e o tenant viaja no **JWT**. (Fundação: Fase 0.7.)
- **7 perfis:** Cliente, Funcionário, Supervisor, RH, Financeiro, **Gestor** (não "Gerente"),
  Superadmin. **Funcionário é perfil único** (sem subtipos). Papéis são por Empresa, não globais.
- **IA (inegociável):** detecta intenção de compra mas **nunca inventa preço nem prazo**; só narra
  campos estruturados (status, datas, responsável); **nunca** responde em nome de um supervisor.
- **Chat é o palco, ticket é o bastidor.** Estados do ticket (MVP): Recebido, Em andamento,
  Agendado, Concluído. Linguagem simples, sem jargão.
- **Visita técnica** é entidade **irmã do ticket** (não um tipo de ticket): proativa
  (supervisor→cliente), com tempo cronometrado; duração **derivada** (não armazenada); o cliente
  **não aprova**, só recebe/consulta a prova.
- **Tickets irmãos:** uma mensagem pode gerar mais de um chamado (ex.: atestado → RH + Supervisão).
- **Design system fixo:** azul #148AF5, Ink, Figtree, Line Awesome, raios e espaçamentos definidos.
  Interface discreta — ela hospeda a marca do cliente e nunca compete com ela.
- **Anti-amnésia (tese central):** nada que o cliente pede pode se perder; tudo fica registrado e
  rastreável.

> Onde estamos no roadmap: ver o **Mapa das fases** em `docs/plano-implementacao.md`. A migração do
> código para "Gestor"/7 perfis e a fundação multi-tenant são as Fases 0.6 e 0.7 (prioritárias).

---

## 🔐 Segurança técnica — avisar antes de consultar documentação atualizada

Práticas de segurança web (cookies `HttpOnly`/`SameSite`/`Secure`, CORS, JWT, headers HTTP,
isolamento multi-tenant/RLS) mudam com o tempo. Antes de alterar código que toca esses temas,
**avise o usuário que vai consultar a skill `verificar-seguranca`** e rode-a — ela compara a prática
atual do projeto com a recomendação mais recente (OWASP, docs oficiais do FastAPI/Next.js, MDN) e
classifica cada item como OK/ATENÇÃO/CRÍTICO.

- Dispare isso **só** quando a mudança realmente tocar segurança técnica (autenticação, cookies,
  CORS, JWT, isolamento multi-tenant/RLS, headers HTTP) — **não** para mudanças não relacionadas,
  para não gastar tokens à toa.
- É uma checagem informativa, não substitui a Trava de Segurança acima: se a skill encontrar algo
  desatualizado, trate como mudança de regra — adicione ao `docs/plano-implementacao.md` e peça
  confirmação explícita antes de alterar o código.

---

## LEIA PRIMEIRO — Verificação obrigatória antes de qualquer implementação

**Antes de escrever qualquer código, leia `docs/plano-implementacao.md` na íntegra.**

> ### 🚦 REGRA DE OURO DO FLUXO — nada é alterado sem estar no plano
> **Nenhuma alteração de código pode ser feita se o item correspondente não estiver no
> `docs/plano-implementacao.md`.** Esta verificação é **obrigatória e rotineira, a cada mudança** —
> não é opcional nem "só na primeira vez".
>
> **Rotina obrigatória, toda vez que for mexer em algo:**
> 1. **Abra `docs/plano-implementacao.md` e localize o item.** Se ele **não existe no plano, PARE.**
>    Não implemente nada ainda.
> 2. Se algo novo/necessário surgir (bug, refino, item descoberto), **primeiro adicione-o ao plano**
>    (na fase certa, status `[ ]`) e **peça confirmação ao usuário** — só depois implemente.
> 3. Só então siga o ciclo de status: `[ ]` → `[~]` ao iniciar → `[x]` ao concluir.
>
> O plano é a fonte da verdade da execução: **se não está no plano, não se faz.** A única exceção são
> as mudanças puramente cosméticas/refatoração já previstas na Trava de Segurança acima (e mesmo essas
> não podem contrariar um invariante).

1. Verifique se o item que será implementado está listado e com status `[ ]` (na fila).
2. Se estiver `[x]` (concluído), **não reimplemente** — leia o código existente antes de continuar.
3. Se estiver `[~]` (em andamento), continue de onde parou — não crie duplicatas.
4. Ao iniciar um item, mude seu status para `[~]`. Ao concluir, mude para `[x]`.
5. Se o item **não estiver no plano**, adicione-o primeiro (com confirmação) — ver Regra de Ouro acima.

---

## Regra obrigatória de comentários

**Todo bloco de código criado ou alterado deve ter comentário. Sem exceção.**

O que comentar obrigatoriamente:
- **Cada arquivo**: comentário de cabeçalho descrevendo a responsabilidade do arquivo
- **Cada função/método/rota**: o que faz e por que existe
- **Cada bloco lógico relevante** (enum, classe ORM, hook, estado, constante de mapeamento): o que representa
- **Decisões não óbvias**: por que foi feito assim (ex: `expire_on_commit=False`, form-urlencoded no login)
- **Regras de negócio embutidas no código**: ex: "Gerente e Supervisor veem todos os chamados; Cliente vê apenas os seus"

O que **não** comentar:
- Importações óbvias
- Código autoexplicativo por nome (ex: `setCarregando(true)` não precisa de comentário)

---

## Atualização de documentação obrigatória

Após **qualquer alteração de código** neste projeto (nova funcionalidade, correção de bug, mudança de estrutura), você deve:

1. Atualizar `docs/changelog.md` — adicionar uma entrada com a data atual, o que foi alterado e por quê, em linguagem clara.
2. Atualizar `docs/plano-implementacao.md` — marcar o item como `[x]` e, se necessário, adicionar novos itens descobertos durante a implementação.
3. Atualizar o arquivo de documentação afetado:
   - Mudança no backend → `docs/tecnico-backend.md`
   - Mudança no frontend web → `docs/tecnico-frontend.md`
   - Mudança na arquitetura geral → `docs/arquitetura.md`
4. Se a mudança adicionar ou remover uma funcionalidade visível ao usuário, atualizar também `docs/visao-geral.md` na seção correspondente.

---

## Convenções do projeto

- Nomes de modelos, colunas e rotas em **português, PascalCase** (ex: `ChamadoStatus`, `ClienteID`)
- Código em **TypeScript** no frontend (web e mobile)
- Backend em **Python + FastAPI**, assíncrono
- Nunca commitar arquivos `.env` — usar sempre `.env.example`
- Manter tipos do frontend sincronizados com os modelos do backend após qualquer alteração de schema

---

## Design system (tokens obrigatórios para todo código de UI)

```
Azul primário:  #148AF5   (hover: #0E72D4,  fundo sutil: #EAF4FE)
Ink (texto):    #17171A / #34363D / #646874 / #868B97
Fundos:         #F7F9FA (página) / #F1F4F6 / #FFFFFF (card)
Bordas:         #E7ECEF (Ink 100) / #C1CCD3 (Ink 200)
Sucesso:        #1FAE68  bg: #E7F6EE
Atenção:        #F0961E  bg: #FEF4E6
Erro/Crítico:   #E5484D  bg: #FDECEC
Raios:          8px (card), 12px (modal), 999px (badge/pílula)
Espaçamento:    base 4px → use 4, 8, 12, 16, 24, 32, 48, 64
Fonte:          Figtree (sans-serif geométrica)
Ícones:         Line Awesome (18–24px, estilo linha)
```

---

## Estrutura de pastas

```
backend/app/          → FastAPI (modelos, rotas, banco de dados, serviços)
frontend/web/         → Next.js 15 (web admin — painel do gestor)
frontend/mobile/      → Expo React Native (app mobile — cliente e supervisor)
docs/                 → documentação do projeto (sempre atualizar)
docs/plano-implementacao.md  → backlog de desenvolvimento (consultar antes de qualquer sessão)
```
