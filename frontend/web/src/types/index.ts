// Tipos TypeScript espelhando os modelos do backend (Python/FastAPI)
// Manter sincronizados com os enums e schemas definidos em backend/app/modelos/

// Perfis de acesso do sistema — os 7 perfis definidos pelo branding (docs/FaciliChat-Regras/)
export type UsuarioFuncao = 'Cliente' | 'Supervisor' | 'Funcionario' | 'RH' | 'Financeiro' | 'Gestor' | 'Superadmin'

export type EmpresaStatus = 'Ativa' | 'Suspensa'

// Filas de atendimento dos chamados
export type ChamadoFila = 'Operacional' | 'RH' | 'Financeiro' | 'Comercial'

// Ciclo de vida de um chamado
export type ChamadoStatus = 'Recebido' | 'EmAndamento' | 'Agendado' | 'Concluido' | 'Cancelado'

// Nível de urgência do chamado
export type ChamadoPrioridade = 'Baixa' | 'Media' | 'Alta' | 'Critica'

// Tipo de autor de uma mensagem no chat do chamado
export type AutorTipo = 'Cliente' | 'Supervisor' | 'Funcionario' | 'IA' | 'Sistema'

// Dados públicos de um usuário retornados pela API
export interface Usuario {
  ID: string
  EmpresaID: string  // Tenant ao qual o usuário pertence (Fase 0.7)
  Nome: string
  Email: string
  Funcao: UsuarioFuncao
  Telefone: string | null
  CondominioID: string | null
  Condominio: string | null
}

// Dados de um chamado retornados pela API
export interface Chamado {
  ID: string
  EmpresaID: string  // Tenant do chamado (Fase 0.7)
  ClienteID: string
  ClienteNome: string | null
  GrupoOrigemID: string | null
  SupervisorID: string | null
  SupervisorNome: string | null
  Fila: ChamadoFila
  Categoria: string
  Status: ChamadoStatus
  Prioridade: ChamadoPrioridade
  Resumo: string | null
  Criacao: string  // ISO 8601 — converter com new Date() antes de exibir
}

// Resumo executivo calculado pelo backend para o painel do Gestor.
// Medias permanecem nulas quando a Empresa ainda nao possui amostra suficiente.
export interface VisaoGeralRelatorio {
  TotalAbertos: number
  SlaEstourado: number
  PrimeiraRespostaMediaMinutos: number | null
  ResolucaoMediaMinutos: number | null
  AtualizadoEm: string
}

// Carga operacional de um supervisor calculada pelo backend para o painel do Gestor.
export interface SupervisorRelatorio {
  ID: string
  Nome: string
  Abertos: number
  Atrasados: number
  PrimeiraRespostaMediaMinutos: number | null
}

// Lastro de fechamento e gargalo do supervisor, sem nota subjetiva.
export interface DesempenhoSupervisorRelatorio {
  ID: string
  Nome: string
  Recebidos: number
  Resolvidos: number
  Parados: number
  TaxaResolucaoPercentual: number | null
}

// Mensagem do chat interno de um chamado
export interface Mensagem {
  ID: string
  ChamadoID: string
  AutorID: string | null  // Nulo quando AutorTipo é IA ou Sistema
  AutorTipo: AutorTipo
  Conteudo: string
  Anexo: string | null    // URL do arquivo anexado
  Criacao: string
}

// Resposta dos endpoints de login e de atualização de token (item S15) — contém o access token e
// dados básicos do usuário. O tenant (empresa_id) vem sempre do token/login — o frontend nunca
// escolhe ou envia a Empresa.
export interface TokenResposta {
  token_acesso: string
  tipo_token: string
  // Refresh token opaco (item S15). O painel web ignora este campo — ele usa o cookie HttpOnly
  // `refresh` que o backend já emite junto na mesma resposta. Só o app mobile (sem cookies) lê
  // este valor para guardar no SecureStore.
  refresh_token: string
  funcao: UsuarioFuncao
  nome: string
  empresa_id: string
  empresa_nome: string | null
}

export interface Empresa {
  ID: string
  Nome: string
  CNPJ: string
  Status: EmpresaStatus
  Criacao: string
}

export interface EmpresaCriar {
  Nome: string
  CNPJ: string
  Gestor: {
    Nome: string
    Email: string
    Senha: string
    Telefone?: string
  }
}

export interface EmpresaCriadaResposta {
  Empresa: Empresa
  GestorID: string
}

// Payload enviado ao criar um novo chamado
export interface ChamadoCriar {
  Fila: ChamadoFila
  Categoria: string
  Resumo?: string
  Prioridade?: ChamadoPrioridade
}

export interface ChamadosIrmaosCriar {
  Chamados: ChamadoCriar[]
}
