# FaciliChat — Visão Geral do Sistema

> Documento para acompanhamento dos donos da empresa.
> Atualizado a cada alteração realizada no sistema.

---

## O que é o FaciliChat?

O **FaciliChat** é uma plataforma digital de atendimento criada para a gestão de condomínios. O objetivo é centralizar toda a comunicação entre moradores, funcionários, supervisores e gerentes em um único lugar — eliminando o uso de WhatsApp, e-mail e papéis avulsos para registrar chamados e solicitações.

---

## Para quem é o sistema?

| Perfil | Quem é | O que faz no sistema |
|---|---|---|
| **Cliente** | Morador do condomínio | Abre chamados, acompanha o andamento, conversa pelo chat |
| **Funcionário** | Equipe operacional, RH ou financeiro | Recebe e executa os chamados da sua fila |
| **Supervisor** | Coordenador de área | Acompanha todos os chamados, atribui prioridades |
| **Gerente** | Gestor geral | Visão completa de tudo, relatórios e controle |

---

## O que o sistema já faz hoje

### Autenticação e Segurança
- Login com email e senha para todos os perfis
- Cada usuário só vê o que tem permissão de ver
- Sessão protegida com token de segurança (expira em 8 horas)

### Cadastro de Usuários
- Criação de contas com nome, email, telefone, condomínio e função
- Proteção contra cadastros duplicados (mesmo email)

### Chamados (Solicitações)
- Moradores abrem chamados informando: departamento, categoria, descrição e prioridade
- Chamados são organizados em 3 filas: **Operacional**, **RH** e **Financeiro**
- Cada chamado tem um status acompanhável: Recebido → Em Andamento → Agendado → Concluído / Cancelado
- Prioridades: Baixa, Média, Alta e Crítica
- Supervisores e gerentes visualizam todos os chamados; moradores veem apenas os seus

### Painel Web (Administrativo)
- Área de login
- Painel com lista de chamados e filtro por perfil
- Sidebar de navegação com acesso às seções

### Aplicativo Mobile
- Login pelo celular (Android e iOS)
- Lista de chamados com atualização em tempo real (puxar para atualizar)
- Perfil do usuário com opção de sair

---

## O que está sendo desenvolvido (próximos passos)

- **Chat por chamado** — troca de mensagens dentro de cada solicitação, incluindo histórico completo
- **Inteligência Artificial** — triagem automática e sugestões de resposta usando IA
- **Configuração de migrações de banco** — controle de versão do banco de dados (Alembic)
- **Testes automatizados** — garantia de que nada quebra ao atualizar o sistema
- **Deploy em servidor** — publicação do sistema para uso em produção

---

## Estado atual do projeto

| Área | Status |
|---|---|
| Backend (servidor) | Em desenvolvimento |
| Web Admin (painel) | Estrutura inicial pronta |
| App Mobile | Estrutura inicial pronta |
| Chat / Mensagens | Banco de dados modelado, rotas pendentes |
| Inteligência Artificial | SDK instalado, integração pendente |
| Deploy / Publicação | Pendente |

---

*Última atualização: 25 de junho de 2025*
*Alterado por: Claude Code (agente de desenvolvimento)*
