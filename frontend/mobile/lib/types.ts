export type UsuarioFuncao = 'Cliente' | 'Supervisor' | 'Funcionario' | 'Gerente'
export type ChamadoFila = 'Operacional' | 'RH' | 'Financeiro'
export type ChamadoStatus = 'Recebido' | 'EmAndamento' | 'Agendado' | 'Concluido' | 'Cancelado'
export type ChamadoPrioridade = 'Baixa' | 'Media' | 'Alta' | 'Critica'
export type AutorTipo = 'Cliente' | 'Supervisor' | 'Funcionario' | 'IA' | 'Sistema'

export interface Usuario {
  ID: string
  Nome: string
  Email: string
  Funcao: UsuarioFuncao
  Telefone: string | null
  Condominio: string | null
}

export interface Chamado {
  ID: string
  ClienteID: string
  Fila: ChamadoFila
  Categoria: string
  Status: ChamadoStatus
  Prioridade: ChamadoPrioridade
  Resumo: string | null
  Criacao: string
}

export interface Mensagem {
  ID: string
  ChamadoID: string
  AutorID: string | null
  AutorTipo: AutorTipo
  Conteudo: string
  Anexo: string | null
  Criacao: string
}

export interface TokenResposta {
  token_acesso: string
  tipo_token: string
  funcao: UsuarioFuncao
  nome: string
}
