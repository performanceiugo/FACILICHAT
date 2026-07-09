// Tipos TypeScript espelhando os modelos do backend (Python/FastAPI)
// Arquivo idêntico ao web/src/types/index.ts — manter os dois sincronizados com o backend

// Perfis de acesso do sistema — os 7 perfis definidos pelo branding (docs/FaciliChat-Regras/)
export type UsuarioFuncao = 'Cliente' | 'Supervisor' | 'Funcionario' | 'RH' | 'Financeiro' | 'Gestor' | 'Superadmin'

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
  EmpresaID: string
  ID: string
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
  EmpresaID: string
  ClienteID: string
  GrupoOrigemID: string | null
  Fila: ChamadoFila
  Categoria: string
  Status: ChamadoStatus
  Prioridade: ChamadoPrioridade
  Resumo: string | null
  Criacao: string  // ISO 8601 — converter com new Date() antes de exibir
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

// Resposta dos endpoints de login e de atualização de token (item S15) — contém o access token,
// o refresh token opaco (guardado no SecureStore, sem cookies no mobile) e dados do usuário.
export interface TokenResposta {
  token_acesso: string
  tipo_token: string
  refresh_token: string
  funcao: UsuarioFuncao
  nome: string
  empresa_id: string
  empresa_nome: string | null
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
