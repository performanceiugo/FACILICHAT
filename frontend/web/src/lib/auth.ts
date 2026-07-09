// Gerenciamento de sessao no frontend web.
//
// Depois do item S6, o token NAO passa mais por aqui. Ele vive num cookie `HttpOnly` emitido pelo
// backend, invisivel para JavaScript — e portanto inalcancavel para um XSS. Este modulo cuida
// apenas do que a interface precisa exibir (nome, empresa) e de ler a funcao para rotear telas.
//
// Consequencia pratica: nao existe mais `auth.token()`. O navegador anexa o cookie sozinho nas
// chamadas para `/api/*` (mesma origem, via proxy do Next), entao o cliente HTTP nao precisa
// injetar `Authorization`.

import type { TokenResposta, UsuarioFuncao } from '@/types'
import {
  COOKIE_FUNCAO,
  EMPRESA_ID_KEY,
  EMPRESA_NOME_KEY,
  NOME_KEY,
  lerCookie,
} from '@/lib/auth-storage'

// Indica se o codigo esta rodando no navegador (cliente).
// No SSR do Next.js (servidor) o objeto `window` nao existe, e acessar localStorage lancaria erro.
const noNavegador = () => typeof window !== 'undefined'

export const auth = {
  // Guarda os dados de EXIBICAO do login. Os cookies (sessao, csrf, funcao) ja vieram no
  // `Set-Cookie` da resposta — o navegador os armazenou sozinho, sem passar por este codigo.
  salvar(dados: TokenResposta) {
    if (!noNavegador()) return
    localStorage.setItem(NOME_KEY, dados.nome)
    localStorage.setItem(EMPRESA_ID_KEY, dados.empresa_id)
    localStorage.setItem(EMPRESA_NOME_KEY, dados.empresa_nome ?? '')
  },

  // A funcao vem do cookie legivel emitido pelo backend (nao do localStorage), para que o
  // middleware do Next e o cliente enxerguem exatamente o mesmo valor.
  funcao(): UsuarioFuncao | null {
    return lerCookie(COOKIE_FUNCAO) as UsuarioFuncao | null
  },

  nome(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(NOME_KEY)
  },

  // ID da Empresa (tenant) do usuario logado — so existe para exibicao; nunca e enviado
  // de volta a API (o backend sempre resolve o tenant a partir do proprio token).
  empresaId(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(EMPRESA_ID_KEY)
  },

  empresaNome(): string | null {
    if (!noNavegador()) return null
    return localStorage.getItem(EMPRESA_NOME_KEY) || null
  },

  // Ha sessao ativa? O cookie de sessao e HttpOnly, entao o cliente NAO consegue ve-lo; usamos a
  // presenca do cookie `funcao`, que o backend emite junto e com a mesma validade. E so uma dica
  // de interface: quem de fato decide e o backend, que rejeita com 401 e dispara o redirecionamento.
  autenticado(): boolean {
    return this.funcao() !== null
  },

  // Limpa apenas os dados locais de exibicao. NAO apaga os cookies — so o backend consegue apagar
  // um cookie HttpOnly. Use `api.logout()` para encerrar a sessao de verdade.
  limparLocal() {
    if (!noNavegador()) return
    localStorage.removeItem(NOME_KEY)
    localStorage.removeItem(EMPRESA_ID_KEY)
    localStorage.removeItem(EMPRESA_NOME_KEY)
  },

  isGestor(): boolean {
    return this.funcao() === 'Gestor'
  },

  isSuperadmin(): boolean {
    return this.funcao() === 'Superadmin'
  },

  // Supervisores e gestores tem acesso as funcionalidades de supervisao
  isSupervisor(): boolean {
    const f = this.funcao()
    return f === 'Supervisor' || f === 'Gestor'
  },
}
