// Cliente HTTP centralizado para comunicação com o backend FastAPI
// Todas as chamadas de API passam por aqui — adiciona token de autenticação automaticamente

import type {
  Chamado,
  ChamadoCriar,
  ChamadosIrmaosCriar,
  ChamadoStatus,
  Empresa,
  EmpresaCriadaResposta,
  EmpresaCriar,
  EmpresaStatus,
  DesempenhoSupervisorRelatorio,
  Mensagem,
  SupervisorRelatorio,
  TokenResposta,
  Usuario,
  VisaoGeralRelatorio,
} from '@/types'
import { auth } from '@/lib/auth'
import { COOKIE_CSRF, HEADER_CSRF, lerCookie } from '@/lib/auth-storage'

// URL base da API — o painel chama o PROXY do Next (`/api/*` → backend, rewrite em next.config.ts),
// nunca a API direto. Isso mantém tudo na mesma origem, o que (a) torna o cookie de sessão
// first-party, (b) dispensa CORS com credenciais no backend e (c) permite CSP `connect-src 'self'`.
// Itens S6 e M6 do plano.
const BASE = '/api'

// Métodos que mudam estado precisam do token CSRF (o backend exige — ver servicos/csrf.py).
const METODOS_QUE_MUDAM_ESTADO = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

// Monta o header CSRF lendo o cookie `csrf_token` que o backend emitiu no login. O cookie é
// legível por JavaScript de propósito: um site atacante consegue fazer o navegador ENVIAR o
// cookie, mas a same-origin policy o impede de LÊ-LO, então não sabe qual header repetir.
function headerCsrf(metodo: string): Record<string, string> {
  if (!METODOS_QUE_MUDAM_ESTADO.has(metodo.toUpperCase())) return {}
  const token = lerCookie(COOKIE_CSRF)
  return token ? { [HEADER_CSRF]: token } : {}
}

function redirecionarParaLoginPorSessaoExpirada() {
  // Só limpa os dados locais: o cookie HttpOnly já está inválido (foi ele que gerou o 401),
  // e apagá-lo exigiria uma chamada ao backend que não tem serventia aqui.
  auth.limparLocal()
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.assign('/login')
  }
}

// Renovação de sessão (item S15): quando o access token (15min) expira, o cookie `refresh`
// (bem mais longo) permite trocar por um access token novo sem pedir senha de novo. `req()`
// dispara isso automaticamente num 401 e repete a chamada original uma única vez.
//
// Single-flight: se várias chamadas tomam 401 ao mesmo tempo (ex.: a página dispara 3 fetches em
// paralelo com o access token já vencido), só a PRIMEIRA aciona /autenticacao/atualizar; as
// demais esperam a mesma promise em vez de cada uma tentar rotacionar o refresh token — rotações
// concorrentes disparariam a própria detecção de reuso do backend e derrubariam a sessão à toa.
let renovacaoEmAndamento: Promise<boolean> | null = null

async function tentarRenovarSessao(): Promise<boolean> {
  if (!renovacaoEmAndamento) {
    renovacaoEmAndamento = (async () => {
      try {
        const res = await fetchOuErroDeConexao(`${BASE}/autenticacao/atualizar`, {
          method: 'POST',
          headers: headerCsrf('POST'),
          credentials: 'same-origin',
        })
        return res.ok
      } catch {
        return false
      } finally {
        renovacaoEmAndamento = null
      }
    })()
  }
  return renovacaoEmAndamento
}

// Mensagem única para falha de rede (API fora do ar, sem conexão, bloqueio de CORS) — o fetch
// lança TypeError com texto em inglês ("Failed to fetch"), que não pode chegar ao usuário (M12).
const ERRO_CONEXAO = 'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.'

// Extrai uma mensagem legível do corpo de erro da API. O `detail` normalmente é string (os
// HTTPException e o handler de validação do backend já mandam português), mas mantemos o
// tratamento de lista por defesa (formato 422 cru do FastAPI, caso o handler mude).
function extrairDetail(corpo: unknown): string | null {
  const d = (corpo as { detail?: unknown } | null)?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    const msgs = d.map(e => (typeof e === 'string' ? e : (e as { msg?: string })?.msg)).filter(Boolean)
    return msgs.length ? msgs.join('; ') : null
  }
  return null
}

// Executa o fetch convertendo falha de rede em erro com mensagem em português
async function fetchOuErroDeConexao(url: string, options?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, options)
  } catch {
    throw new Error(ERRO_CONEXAO)
  }
}

// Função genérica de requisição HTTP com tipagem — anexa o CSRF e trata erros da API.
// A credencial de sessão NÃO é injetada aqui: o navegador manda o cookie `HttpOnly` sozinho,
// por ser mesma origem. `credentials: 'same-origin'` é o padrão do fetch, mas fica explícito
// para deixar claro que a chamada é autenticada por cookie.
//
// `jaTentouRenovar` evita loop: só tenta renovar a sessão UMA vez por chamada. Se o access token
// renovado ainda assim tomar 401 (ex.: usuário foi removido, Empresa suspensa), vai direto pro
// login em vez de tentar renovar de novo.
async function req<T>(path: string, options?: RequestInit, jaTentouRenovar = false): Promise<T> {
  const metodo = options?.method ?? 'GET'
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headerCsrf(metodo),
    ...(options?.headers as Record<string, string>),
  }

  const res = await fetchOuErroDeConexao(`${BASE}${path}`, {
    ...options,
    headers,
    credentials: 'same-origin',
  })
  if (res.status === 401) {
    if (!jaTentouRenovar && (await tentarRenovarSessao())) {
      return req<T>(path, options, true)
    }
    redirecionarParaLoginPorSessaoExpirada()
    throw new Error('Sessao expirada. Faca login novamente.')
  }
  if (!res.ok) {
    const erro = await res.json().catch(() => null)
    throw new Error(extrairDetail(erro) ?? 'Erro na requisição')
  }
  return res.json() as Promise<T>
}

function funcionalidadeFutura(nome: string): never {
  throw new Error(`${nome} sera entregue na Fase 1 do chat`)
}

// Métodos disponíveis para o frontend consumir a API
export const api = {
  // Login usa form-urlencoded conforme exigido pelo OAuth2PasswordRequestForm do FastAPI.
  // A resposta traz os cookies de sessão no `Set-Cookie`; o navegador os guarda sozinho.
  // O `token_acesso` do corpo é ignorado pelo painel (existe para o app mobile).
  async login(email: string, senha: string): Promise<TokenResposta> {
    const form = new URLSearchParams({ username: email, password: senha })
    const res = await fetchOuErroDeConexao(`${BASE}/autenticacao/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
      credentials: 'same-origin',
    })
    if (!res.ok) {
      const erro = await res.json().catch(() => null)
      throw new Error(extrairDetail(erro) ?? 'Email ou senha incorretos')
    }
    return res.json() as Promise<TokenResposta>
  },

  // Encerra a sessão: só o backend consegue apagar o cookie `HttpOnly`, então o logout é uma
  // chamada de rede — não um `localStorage.clear()`. Se a rede falhar, ainda assim limpamos os
  // dados locais e devolvemos o controle ao chamador, que redireciona para o login.
  async logout(): Promise<void> {
    try {
      await fetchOuErroDeConexao(`${BASE}/autenticacao/logout`, {
        method: 'POST',
        credentials: 'same-origin',
      })
    } finally {
      auth.limparLocal()
    }
  },

  // Retorna os dados do usuário autenticado (baseado no token da requisição)
  eu: () => req<Usuario>('/usuarios/eu'),

  chamados: {
    listar: () => req<Chamado[]>('/chamados/'),
    // Carrega sob demanda somente a fila do supervisor aberto pelo Gestor.
    listarPorSupervisor: (supervisorID: string) =>
      req<Chamado[]>(`/chamados/?supervisor_id=${encodeURIComponent(supervisorID)}`),
    criar: (payload: ChamadoCriar) =>
      req<Chamado>('/chamados/', { method: 'POST', body: JSON.stringify(payload) }),
    criarIrmaos: (payload: ChamadosIrmaosCriar) =>
      req<Chamado[]>('/chamados/irmaos', { method: 'POST', body: JSON.stringify(payload) }),
    atualizarStatus: (id: string, status: ChamadoStatus) =>
      req<Chamado>(`/chamados/${id}/status?status=${status}`, { method: 'PATCH' }),
  },

  // Relatorios executivos sao agregados no backend para preservar permissoes e tenant.
  relatorios: {
    visaoGeral: () => req<VisaoGeralRelatorio>('/relatorios/visao-geral'),
    supervisores: () => req<SupervisorRelatorio[]>('/relatorios/supervisores'),
    desempenhoSupervisores: () =>
      req<DesempenhoSupervisorRelatorio[]>('/relatorios/desempenho-supervisores'),
  },

  mensagens: {
    listar: (_chamadoID: string) => Promise.reject(funcionalidadeFutura('Mensagens')),
    enviar: (_chamadoID: string, _conteudo: string) => Promise.reject(funcionalidadeFutura('Mensagens')),
  },

  plataforma: {
    listarEmpresas: () => req<Empresa[]>('/plataforma/empresas'),
    criarEmpresa: (payload: EmpresaCriar) =>
      req<EmpresaCriadaResposta>('/plataforma/empresas', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    atualizarStatusEmpresa: (id: string, status: EmpresaStatus) =>
      req<Empresa>(`/plataforma/empresas/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ Status: status }),
      }),
  },
}
