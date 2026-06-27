// Gerenciamento de sessão no frontend web
// Armazena token, função e nome no localStorage do navegador

import type { TokenResposta, UsuarioFuncao } from '@/types'

// Chaves usadas no localStorage — centralizadas para evitar erros de digitação
const TOKEN_KEY = 'token'
const FUNCAO_KEY = 'funcao'
const NOME_KEY = 'nome'

// Indica se o código está rodando no navegador (cliente).
// No SSR do Next.js (servidor) o objeto `window` não existe, e acessar localStorage lançaria erro.
const noNavegador = () => typeof window !== 'undefined'

export const auth = {
  // Salva os dados de sessão após login bem-sucedido
  salvar(dados: TokenResposta) {
    if (!noNavegador()) return
    localStorage.setItem(TOKEN_KEY, dados.token_acesso)
    localStorage.setItem(FUNCAO_KEY, dados.funcao)
    localStorage.setItem(NOME_KEY, dados.nome)
  },

  token(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(TOKEN_KEY)
  },

  funcao(): UsuarioFuncao | null {
    if (!noNavegador()) return null
    return localStorage.getItem(FUNCAO_KEY) as UsuarioFuncao | null
  },

  nome(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(NOME_KEY)
  },

  // Verifica se há sessão ativa (token presente no localStorage)
  autenticado(): boolean {
    if (!noNavegador()) return false
    return !!localStorage.getItem(TOKEN_KEY)
  },

  // Remove todos os dados de sessão — chamado no logout
  sair() {
    if (!noNavegador()) return
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
