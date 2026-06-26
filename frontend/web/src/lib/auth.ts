// Gerenciamento de sessão no frontend web
// Armazena token, função e nome no localStorage do navegador

import type { TokenResposta, UsuarioFuncao } from '@/types'

// Chaves usadas no localStorage — centralizadas para evitar erros de digitação
const TOKEN_KEY = 'token'
const FUNCAO_KEY = 'funcao'
const NOME_KEY = 'nome'

export const auth = {
  // Salva os dados de sessão após login bem-sucedido
  salvar(dados: TokenResposta) {
    localStorage.setItem(TOKEN_KEY, dados.token_acesso)
    localStorage.setItem(FUNCAO_KEY, dados.funcao)
    localStorage.setItem(NOME_KEY, dados.nome)
  },

  token(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  funcao(): UsuarioFuncao | null {
    return localStorage.getItem(FUNCAO_KEY) as UsuarioFuncao | null
  },

  nome(): string | null {
    return localStorage.getItem(NOME_KEY)
  },

  // Verifica se há sessão ativa (token presente no localStorage)
  autenticado(): boolean {
    return !!localStorage.getItem(TOKEN_KEY)
  },

  // Remove todos os dados de sessão — chamado no logout
  sair() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(FUNCAO_KEY)
    localStorage.removeItem(NOME_KEY)
  },

  isGerente(): boolean {
    return this.funcao() === 'Gerente'
  },

  // Supervisores e gerentes têm acesso às funcionalidades de supervisão
  isSupervisor(): boolean {
    const f = this.funcao()
    return f === 'Supervisor' || f === 'Gerente'
  },
}
