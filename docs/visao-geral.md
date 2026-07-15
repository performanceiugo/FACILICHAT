# FaciliChat — Visão Geral do Sistema

> Documento para acompanhamento dos donos da empresa.
> Atualizado a cada alteração realizada no sistema.

O painel do Gestor já dispõe de um resumo operacional por Empresa com chamados abertos, SLA vencido,
tempo médio até a primeira resposta humana interna e tempo médio de resolução. Quando ainda não há
dados suficientes para uma média, o sistema informa ausência de amostra em vez de estimar um valor.

---

## O que é o FaciliChat?

O **FaciliChat** é uma plataforma digital de atendimento para **empresas de facilities (conservadoras)** — as que prestam limpeza, portaria, zeladoria e serviços para condomínios. O objetivo é centralizar a comunicação entre a empresa e os seus clientes (os condomínios, representados pelos síndicos), além da própria equipe (supervisores, funcionários, RH, financeiro e o gestor) — eliminando o WhatsApp solto, o e-mail e os papéis avulsos para registrar chamados e solicitações.

> É vendido como **SaaS multi-tenant**: cada empresa cliente (a conservadora) tem seus dados totalmente isolados das demais. A própria Iugo Performance opera a plataforma como Superadmin. **Essa fundação já está implementada e aplicada ao banco de dados** (isolamento por Empresa em todas as tabelas, reforçado por Row-Level Security no PostgreSQL).

---

## Para quem é o sistema?

O branding define **7 perfis** — **todos já implementados no sistema**:

| Perfil | Quem é | O que faz no sistema |
|---|---|---|
| **Cliente** | Síndico / representante do condomínio atendido | Abre chamados, acompanha o andamento, conversa pelo chat |
| **Funcionário** | Equipe de campo (limpeza, portaria, zeladoria) — perfil único | Avisa faltas, envia atestado, pede materiais |
| **Supervisor** | Coordenador de campo, na rua | Resolve e agenda as demandas pelo celular |
| **RH** | Analista de RH | Trata atestados, documentos e pedidos de pessoal |
| **Financeiro** | Analista financeiro / DP | Trata holerites, vales e pagamentos |
| **Gestor** | Dono / diretor da empresa | Visão total, cobra a equipe com histórico, monta propostas |
| **Superadmin** | Iugo Performance (plataforma) | Opera o sistema e cadastra as empresas clientes |

---

## O que o sistema já faz hoje

### Plataforma multi-empresa (SaaS)
- Cada Empresa (conservadora) tem seus dados totalmente isolados das demais
- O Superadmin (Iugo) tem uma área própria para cadastrar novas Empresas com o primeiro Gestor, e para suspender/reativar uma Empresa

### Autenticação e Segurança
- Login com email e senha para todos os perfis
- Cada usuário só vê o que tem permissão de ver; papéis valem por Empresa
- Sessão protegida que pode ser renovada sem novo login e revogada de verdade no logout ou na troca de senha
- Senhas fortes obrigatórias (mínimo de 15 caracteres, guardadas com criptografia moderna)
- Mensagens de erro sempre em português, sem vazar detalhes técnicos

### Cadastro de Usuários
- O Gestor cria a própria equipe (Supervisor, Funcionário, RH, Financeiro) logado no painel
- Proteção contra cadastros duplicados (mesmo email) e contra cadastro público indevido (fechado por padrão)

### Chamados (Solicitações)
- Clientes abrem chamados informando: departamento, categoria, descrição e prioridade
- Chamados organizados em **4 filas**: **Operacional**, **RH**, **Financeiro** e **Comercial** (contratos/propostas, roteada ao Gestor)
- Um mesmo aviso pode gerar mais de um chamado ao mesmo tempo (**tickets irmãos** — ex.: atestado → RH valida + Supervisão cobre o posto), sem que nada se perca
- Cada chamado tem um status acompanhável: Recebido → Em Andamento → Agendado → Concluído / Cancelado
- Prioridades: Baixa, Média, Alta e Crítica
- Supervisores e gestores visualizam todos os chamados; clientes veem apenas os seus

### Painel Web do Gestor
- Área de login com a identidade visual da marca
- **Visão geral executiva** com indicadores reais: chamados abertos, SLA vencido, tempo médio de primeira resposta e de resolução, distribuição por status, volume por fila e por categoria, e lista do que precisa de atenção
- Lista de chamados com atualização automática (estilo painel de BI, sem precisar recarregar a página)
- Tela de supervisores (estrutura pronta, aguardando os dados por supervisor)
- Navegação acessível por teclado e leitores de tela; páginas de erro amigáveis em português

### Aplicativo Mobile
- Login pelo celular (Android e iOS)
- Lista de chamados com atualização ao puxar para baixo (pull-to-refresh)
- Perfil do usuário com opção de sair
- Visual alinhado ao design system da marca (cores, fonte e ícones oficiais)

---

## O que está sendo desenvolvido (próximos passos)

- **Chat por chamado** — troca de mensagens dentro de cada solicitação, incluindo histórico completo *(é a base do produto: "o chat é o palco, o ticket é o bastidor")*
- **WhatsApp como porta de entrada** — o cliente conversa pelo WhatsApp que já usa, e o FaciliChat registra tudo como chamado
- **Criação de chamado e tela de detalhe** no aplicativo do cliente
- **Inteligência Artificial** — triagem automática e respostas ancoradas: a IA nunca inventa preço nem prazo, só narra o que está registrado
- **Visitas técnicas** — registro cronometrado de visitas proativas do supervisor, com prova para o cliente
- **Relatório por supervisor** — dados reais de carga e desempenho na tela de supervisores
- **Deploy em servidor** — publicação do sistema para uso em produção

---

## Estado atual do projeto

| Área | Status |
|---|---|
| Fundação multi-empresa (SaaS) | ✅ Pronta e aplicada ao banco |
| Backend (servidor) | Núcleo pronto (login, equipe, chamados, relatórios); chat e IA pendentes |
| Web Admin (painel do Gestor) | Visão geral com dados reais, chamados e supervisores no ar |
| Área da plataforma (Superadmin) | Cadastro e suspensão de Empresas no ar |
| App Mobile | Estrutura inicial pronta (login, lista de chamados, perfil) |
| Chat / Mensagens | Banco de dados modelado, rotas pendentes |
| Inteligência Artificial | SDK instalado, integração pendente |
| Deploy / Publicação | Ambiente de produção preparado (Docker); publicação pendente |

---

*Última atualização: 15 de julho de 2026*
*Alterado por: Claude Code (agente de desenvolvimento)*
