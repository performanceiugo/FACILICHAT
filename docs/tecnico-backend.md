# FaciliChat — Documentação Técnica: Backend

---

## Como rodar o backend

```bash
# 1. Subir o banco de dados
docker compose up -d

# 2. Instalar dependências Python
cd backend
pip install -r requirements.txt

# 3. Criar arquivo .env (copiar do exemplo)
cp .env.example .env
# (editar os valores no .env)

# 4. Rodar o servidor (a partir de backend/)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000/docs` — documentação automática da API (Swagger UI)

---

## Modelos de banco de dados

### `Usuarios` — Tabela de usuários

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador único |
| Nome | String(120) | Nome completo |
| Email | String(120) | Email único (login) |
| SenhaHash | String(255) | Senha em hash argon2 |
| Funcao | Enum | Cliente / Supervisor / Funcionario / Gerente |
| Telefone | String(20) | Opcional |
| Condominio | String(120) | Nome do condomínio, opcional |
| Criacao | DateTime | Data de cadastro |

### `Chamados` — Tabela de chamados/solicitações

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador único |
| EmpresaID | UUID → Empresas | Tenant do chamado |
| ClienteID | UUID → Usuarios | Quem abriu o chamado |
| GrupoOrigemID | UUID | Opcional; agrupa tickets irmãos nascidos do mesmo aviso/mensagem |
| SupervisorID | UUID → Usuarios | Supervisor atribuído (opcional) |
| Fila | Enum | Operacional / RH / Financeiro / Comercial |
| Categoria | String(80) | Ex: "Vazamento", "Folha de Pagamento" |
| Status | Enum | Recebido / EmAndamento / Agendado / Concluido / Cancelado |
| Prioridade | Enum | Baixa / Media / Alta / Critica |
| Resumo | Text | Descrição do problema (opcional) |
| PrazoSLA | DateTime | Prazo de atendimento (opcional) |
| Criacao | DateTime | Data de abertura |
| Atualizacao | DateTime | Última atualização |

### `Mensagens` — Tabela de mensagens do chat

| Coluna | Tipo | Descrição |
|---|---|---|
| ID | UUID | Identificador único |
| ChamadoID | UUID → Chamados | A qual chamado pertence |
| AutorID | UUID → Usuarios | Quem enviou (null se for IA/Sistema) |
| AutorTipo | Enum | Cliente / Supervisor / Funcionario / IA / Sistema |
| Conteudo | Text | Texto da mensagem |
| Anexo | String(500) | URL do arquivo anexado (opcional) |
| Criacao | DateTime | Data/hora do envio |

---

## Rotas da API

### Autenticação — `/autenticacao`

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| POST | `/autenticacao/login` | Login com email e senha, retorna JWT | Não |

**Resposta do login:**
```json
{
  "token_acesso": "eyJ...",
  "tipo_token": "bearer",
  "funcao": "Cliente",
  "nome": "João Silva"
}
```

### Usuários — `/usuarios`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/usuarios/` | Cadastro público — cria **sempre** um Cliente (campo `Funcao` não é aceito) | Não | Pública |
| POST | `/usuarios/equipe` | Criar usuário com função definida (Supervisor/Funcionario/Gerente) | Sim | Apenas Gerente (403 caso contrário) |
| GET | `/usuarios/eu` | Retorna dados do usuário logado | Sim | Qualquer perfil |

> **Primeiro Gerente:** como o cadastro público é Cliente-only e `/usuarios/equipe` exige um Gerente, o primeiro Gerente é criado pelo script `backend/scripts/criar_gerente.py` (ver `docs/setup.md`).

### Chamados — `/chamados`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/chamados/` | Abrir novo chamado | Sim | Qualquer perfil |
| POST | `/chamados/irmaos` | Abrir 2+ chamados simultâneos ligados pelo mesmo `GrupoOrigemID` | Sim | Qualquer perfil |
| GET | `/chamados/` | Listar chamados | Sim | Cliente vê só os seus; Supervisor/Gerente vê todos |
| PATCH | `/chamados/{id}/status` | Atualizar status | Sim | Apenas Supervisor/Gerente (403 caso contrário); chamado finalizado não reabre (409) |

> Banco de dev já existente: rode `python scripts/aplicar_fase_06_tickets_irmaos.py` a partir de
> `backend/` para adicionar `Chamados.GrupoOrigemID` sem recriar tabelas.

---

## Segurança

- Senhas armazenadas com hash **argon2** via `pwdlib` (nunca em texto puro)
- JWT assinado com `HS256` e chave secreta configurável
- Token válido por **8 horas** (configurável via `JWT_EXPIRE_MINUTES`)
- Dependência `obterUsuarioAtual` protege automaticamente qualquer rota que a use
- **CORS** restrito às origens em `CORS_ORIGINS` (config/.env) — sem `"*"` junto de credenciais
- **Cadastro público é Cliente-only**; perfis privilegiados só via `/usuarios/equipe` (Gerente)
- **Alteração de status de chamado** restrita a Supervisor/Gerente (evita IDOR)

---

## Multi-tenancy (SaaS) — a implementar (Fase 0.7, prioritária)

O FaciliChat será um **SaaS multi-tenant**: cada **Empresa** (a conservadora/facilities cliente) tem
seus dados isolados; os clientes de uma Empresa são os **Condomínios** que ela atende. Convenções que
valerão para **todo** o backend a partir desta fase:

- **Entidade `Empresa`** (o tenant), com `Nome`, `CNPJ`, `Status`.
- **Coluna `EmpresaID`** (FK, `NOT NULL`) em **todas** as tabelas: `Usuario`, `Condominio`,
  `Chamado`, `Mensagem` e qualquer modelo futuro.
- **Tenant no JWT:** o `criarToken` passa a incluir o `EmpresaID`; a dependência
  `obterTenantAtual` extrai esse valor do token e é injetada em todas as rotas.
- **Escopo obrigatório:** **toda** query (`select`, `update`, `delete`) filtra por
  `EmpresaID` do usuário logado. Nenhuma rota retorna dados de outro tenant.
- **Row-Level Security (RLS)** no PostgreSQL como segunda trava (defesa em profundidade).
- **Papéis por tenant:** `Gestor`/`Supervisor`/etc. valem dentro da sua Empresa.
- **Superadmin da plataforma (Iugo Performance):** nível acima dos tenants (rotas em `Plataforma.py`)
  para cadastrar/suspender Empresas e criar o 1º Gestor de cada uma. O bootstrap deixa de ser só
  `criar_gerente.py` e passa a `criar_empresa.py` (Empresa + 1º Gestor juntos).

> **Perfis (branding):** o produto define 7 perfis — Cliente, Funcionário, Supervisor, **RH**,
> **Financeiro**, **Gestor**, **Superadmin**. O código atual tem 4 (Cliente, Supervisor, Funcionario,
> **Gerente**); a renomeação `Gerente→Gestor` e a inclusão de RH/Financeiro/Superadmin estão na
> **Fase 0.6** do plano. As tabelas de rotas abaixo refletem o estado **atual** do código.

> Detalhamento e checklist completo em `docs/plano-implementacao.md` (Fase 0.7). Visão de
> arquitetura em `docs/arquitetura.md` (seção "Arquitetura Multi-Tenant (SaaS)").

---

## Pendente de implementação

- [ ] **Fundação Multi-Tenant (Fase 0.7) — prioritária** (ver seção acima)
- [ ] Rotas de Mensagens (`/mensagens/{chamadoID}`)
- [ ] Integração com Anthropic (triagem automática de chamados por IA)
- [ ] Configuração do Alembic para migrações versionadas
- [ ] Rota para listar/buscar usuários (para Gerentes)
- [ ] Atribuição de supervisor a um chamado
- [ ] Filtros na listagem de chamados (por status, fila, prioridade)

---

*Última atualização: 27 de junho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
