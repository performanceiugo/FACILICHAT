# FaciliChat — Documentação Técnica: Backend

---

## Como rodar o backend

```bash
# 1. Subir o banco de dados
docker-compose up -d

# 2. Instalar dependências Python
cd backend
pip install -r requirements.txt

# 3. Criar arquivo .env (copiar do exemplo)
cp app/.env.example app/.env
# (editar os valores no .env)

# 4. Rodar o servidor
cd app
uvicorn main:app --reload
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
| ClienteID | UUID → Usuarios | Quem abriu o chamado |
| SupervisorID | UUID → Usuarios | Supervisor atribuído (opcional) |
| Fila | Enum | Operacional / RH / Financeiro |
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

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| POST | `/usuarios/` | Criar novo usuário | Não |
| GET | `/usuarios/eu` | Retorna dados do usuário logado | Sim |

### Chamados — `/chamados`

| Método | Rota | Descrição | Autenticação | Permissão |
|---|---|---|---|---|
| POST | `/chamados/` | Abrir novo chamado | Sim | Qualquer perfil |
| GET | `/chamados/` | Listar chamados | Sim | Cliente vê só os seus; Supervisor/Gerente vê todos |
| PATCH | `/chamados/{id}/status` | Atualizar status | Sim | Qualquer perfil autenticado |

---

## Segurança

- Senhas armazenadas com hash **argon2** via `pwdlib` (nunca em texto puro)
- JWT assinado com `HS256` e chave secreta configurável
- Token válido por **8 horas** (configurável via `JWT_EXPIRE_MINUTES`)
- Dependência `obterUsuarioAtual` protege automaticamente qualquer rota que a use

---

## Pendente de implementação

- [ ] Rotas de Mensagens (`/mensagens/{chamadoID}`)
- [ ] Integração com Anthropic (triagem automática de chamados por IA)
- [ ] Configuração do Alembic para migrações versionadas
- [ ] Rota para listar/buscar usuários (para Gerentes)
- [ ] Atribuição de supervisor a um chamado
- [ ] Filtros na listagem de chamados (por status, fila, prioridade)

---

*Última atualização: 25 de junho de 2025*
*Alterado por: Claude Code (agente de desenvolvimento)*
