// Chaves de armazenamento da sessao web.
// LocalStorage e cookies usam o mesmo mapa para manter middleware e cliente em sincronia.

export const TOKEN_KEY = 'token'
export const FUNCAO_KEY = 'funcao'
export const NOME_KEY = 'nome'
export const EMPRESA_ID_KEY = 'empresaId'
export const EMPRESA_NOME_KEY = 'empresaNome'

const COOKIE_MAX_AGE_SEGUNDOS = 60 * 60 * 24 * 7

export function serializarCookie(chave: string, valor: string): string {
  return `${chave}=${encodeURIComponent(valor)}; Path=/; Max-Age=${COOKIE_MAX_AGE_SEGUNDOS}; SameSite=Lax`
}

export function serializarRemocaoCookie(chave: string): string {
  return `${chave}=; Path=/; Max-Age=0; SameSite=Lax`
}
