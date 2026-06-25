import type { TokenResposta, UsuarioFuncao } from '@/types'

const TOKEN_KEY = 'token'
const FUNCAO_KEY = 'funcao'
const NOME_KEY = 'nome'

export const auth = {
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

  autenticado(): boolean {
    return !!localStorage.getItem(TOKEN_KEY)
  },

  sair() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(FUNCAO_KEY)
    localStorage.removeItem(NOME_KEY)
  },

  isGerente(): boolean {
    return this.funcao() === 'Gerente'
  },

  isSupervisor(): boolean {
    const f = this.funcao()
    return f === 'Supervisor' || f === 'Gerente'
  },
}
