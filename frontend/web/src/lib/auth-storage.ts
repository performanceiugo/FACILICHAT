// Chaves de armazenamento da sessao web.
//
// Depois do item S6, o cliente NAO escreve mais nenhum cookie: quem os emite e o backend.
// Restam aqui (a) os nomes dos cookies que o backend define, para middleware e cliente lerem,
// e (b) as chaves de localStorage usadas apenas para dados de EXIBICAO.

// --- Cookies emitidos pelo backend -----------------------------------------------------------
// `sessao` guarda o JWT e e HttpOnly: nem este arquivo nem qualquer outro JavaScript o enxerga.
// Ele so aparece aqui como nome, para o middleware do Next (que roda no servidor) checar presenca.
export const COOKIE_SESSAO = 'sessao'

// Token CSRF: legivel de proposito. O cliente le e repete no header X-CSRF-Token.
export const COOKIE_CSRF = 'csrf_token'
export const HEADER_CSRF = 'X-CSRF-Token'

// Funcao do usuario: legivel, usada so para decidir QUAL TELA abrir (roteamento).
// Forjavel — e tudo bem: a autorizacao real acontece no backend, a partir do JWT assinado.
export const COOKIE_FUNCAO = 'funcao'

// --- localStorage: apenas dados de exibicao, nunca credenciais --------------------------------
export const NOME_KEY = 'nome'
export const EMPRESA_ID_KEY = 'empresaId'
export const EMPRESA_NOME_KEY = 'empresaNome'

// Le um cookie nao-HttpOnly do documento. Retorna null no SSR (onde `document` nao existe) e
// quando o cookie nao esta presente.
export function lerCookie(nome: string): string | null {
  if (typeof document === 'undefined') return null
  const encontrado = document.cookie
    .split('; ')
    .find(parte => parte.startsWith(`${nome}=`))
  if (!encontrado) return null
  return decodeURIComponent(encontrado.slice(nome.length + 1))
}
