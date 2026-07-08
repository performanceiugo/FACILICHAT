// Gerenciamento de sessão no frontend web
// Armazena token, função, nome e o tenant (EmpresaID) no localStorage do navegador

import type { TokenResposta, UsuarioFuncao } from '@/types'
import { serializarCookie, serializarRemocaoCookie } from '@/lib/auth-storage'

// Chaves usadas no localStorage — centralizadas para evitar erros de digitação
const TOKEN_KEY = 'token'
const FUNCAO_KEY = 'funcao'
const NOME_KEY = 'nome'
const EMPRESA_ID_KEY = 'empresaId'  // Tenant do usuário logado — sempre lido do token de login (Fase 0.7)
const EMPRESA_NOME_KEY = 'empresaNome'  // Nome da Empresa, só para exibição (ex.: "Admin · Cefram")

// Indica se o código está rodando no navegador (cliente).
// No SSR do Next.js (servidor) o objeto `window` não existe, e acessar localStorage lançaria erro.
const noNavegador = () => typeof window !== 'undefined'

function salvarCookie(chave: string, valor: string) {
  if (!noNavegador()) return
  document.cookie = serializarCookie(chave, valor)
}

function removerCookie(chave: string) {
  if (!noNavegador()) return
  document.cookie = serializarRemocaoCookie(chave)
}

export const auth = {
  // Salva os dados de sessão após login bem-sucedido
  salvar(dados: TokenResposta) {
    if (!noNavegador()) return
    localStorage.setItem(TOKEN_KEY, dados.token_acesso)
    localStorage.setItem(FUNCAO_KEY, dados.funcao)
    localStorage.setItem(NOME_KEY, dados.nome)
    localStorage.setItem(EMPRESA_ID_KEY, dados.empresa_id)
    localStorage.setItem(EMPRESA_NOME_KEY, dados.empresa_nome ?? '')
    salvarCookie(TOKEN_KEY, dados.token_acesso)
    salvarCookie(FUNCAO_KEY, dados.funcao)
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

  // ID da Empresa (tenant) do usuário logado — só existe para exibição; nunca é enviado
  // de volta à API (o backend sempre resolve o tenant a partir do próprio token).
  empresaId(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(EMPRESA_ID_KEY)
  },

  empresaNome(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(EMPRESA_NOME_KEY) || null
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
    localStorage.removeItem(EMPRESA_ID_KEY)
    localStorage.removeItem(EMPRESA_NOME_KEY)
    removerCookie(TOKEN_KEY)
    removerCookie(FUNCAO_KEY)
  },

  isGestor(): boolean {
    return this.funcao() === 'Gestor'
  },

  isSuperadmin(): boolean {
    return this.funcao() === 'Superadmin'
  },

  // Supervisores e gestores têm acesso às funcionalidades de supervisão
  isSupervisor(): boolean {
    const f = this.funcao()
    return f === 'Supervisor' || f === 'Gestor'
  },
}
