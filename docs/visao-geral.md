# FaciliChat — Visão Geral do Sistema

> Documento para acompanhamento dos donos da empresa.
> Atualizado a cada alteração realizada no sistema.

O painel do Gestor já dispõe de um resumo operacional por Empresa com chamados abertos, SLA vencido,
tempo médio até a primeira resposta humana interna e tempo médio de resolução. Quando ainda não há
dados suficientes para uma média, o sistema informa ausência de amostra em vez de estimar um valor.

---

## O que é o FaciliChat?

O **FaciliChat** é uma plataforma digital de atendimento para **empresas de facilities (conservadoras)** — as que prestam limpeza, portaria, zeladoria e serviços para condomínios. O objetivo é centralizar a comunicação entre a empresa e os seus clientes (os condomínios, representados pelos síndicos), além da própria equipe (supervisores, funcionários, RH, financeiro e o gestor) — eliminando o WhatsApp solto, o e-mail e os papéis avulsos para registrar chamados e solicitações.

> É vendido como **SaaS multi-tenant**: cada empresa cliente (a conservadora) tem seus dados totalmente isolados das demais. A própria Iugo Performance opera a plataforma como Superadmin.

---

## Para quem é o sistema?

O branding define **7 perfis**:

| Perfil | Quem é | O que faz no sistema |
|---|---|---|
| **Cliente** | Síndico / representante do condomínio atendido | Abre chamados, acompanha o andamento, conversa pelo chat |
| **Funcionário** | Equipe de campo (limpeza, portaria, zeladoria) — perfil único | Avisa faltas, envia atestado, pede materiais |
| **Supervisor** | Coordenador de campo, na rua | Resolve e agenda as demandas pelo celular |
| **RH** | Analista de RH | Trata atestados, documentos e pedidos de pessoal |
| **Financeiro** | Analista financeiro / DP | Trata holerites, vales e pagamentos |
| **Gestor** | Dono / diretor da empresa | Visão total, cobra a equipe com histórico, monta propostas |
| **Superadmin** | Iugo Performance (plataforma) | Opera o sistema e cadastra as empresas clientes |

> Nota: o código atual ainda implementa só 4 perfis (Cliente, Supervisor, Funcionário e "Gerente"); a migração para os 7 perfis acima está planejada (Fase 0.6).

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
- Lista de chamados com atualização ao puxar para baixo (pull-to-refresh)
- Perfil do usuário com opção de sair

---

## O que está sendo desenvolvido (próximos passos)

- **Plataforma multi-empresa (SaaS)** — o FaciliChat será oferecido para várias empresas de facilities (conservadoras), cada uma com seus dados totalmente separados e protegidos das demais. É a base para vender o sistema para vários clientes. *(prioridade técnica antes das demais funcionalidades)*
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

*Última atualização: 27 de junho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
