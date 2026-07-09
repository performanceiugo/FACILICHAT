// Cliente HTTP centralizado para o app mobile (Expo React Native)
// Idêntico ao web/src/lib/api.ts, mas usa SecureStore em vez de localStorage para o token
// SecureStore é armazenamento criptografado no dispositivo (iOS Keychain / Android Keystore)

import { router } from 'expo-router'
import type {
  Chamado,
  ChamadoCriar,
  ChamadosIrmaosCriar,
  ChamadoStatus,
  Mensagem,
  TokenResposta,
  Usuario,
} from './types'
import { auth } from './auth'

// URL base da API — 10.0.2.2 é o endereço do host no emulador Android
// Para dispositivo físico, substituir pelo IP da máquina na rede local via EXPO_PUBLIC_API_URL
const BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000'

async function redirecionarParaLoginPorSessaoExpirada() {
  await auth.sair()
  router.replace('/(auth)/login')
}

// Renovação de sessão (item S15): sem cookies no mobile, o refresh token guardado no SecureStore
// é reenviado no corpo de POST /autenticacao/atualizar quando o access token (15min) expira.
// Sucesso: os novos tokens substituem os antigos no SecureStore e a chamada original é repetida.
//
// Single-flight: várias telas podem tomar 401 ao mesmo tempo (ex.: fila + chamados carregando
// juntos); só a primeira aciona a renovação, as demais esperam a mesma promise — chamadas
// concorrentes ao `/atualizar` rotacionariam o MESMO refresh token duas vezes e disparariam a
// detecção de reuso do backend, derrubando a sessão à toa.
let renovacaoEmAndamento: Promise<boolean> | null = null

async function tentarRenovarSessao(): Promise<boolean> {
  if (!renovacaoEmAndamento) {
    renovacaoEmAndamento = (async () => {
      try {
        const refreshToken = await auth.refreshToken()
        if (!refreshToken) return false
        const res = await fetchOuErroDeConexao(`${BASE}/autenticacao/atualizar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
        if (!res.ok) return false
        await auth.salvar(await res.json() as TokenResposta)
        return true
      } catch {
        return false
      } finally {
        renovacaoEmAndamento = null
      }
    })()
  }
  return renovacaoEmAndamento
}

// Mensagem única para falha de rede (API fora do ar, sem conexão) — o fetch do React Native
// lança TypeError com texto em inglês ("Network request failed"), que não pode chegar ao usuário (M12).
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

// Função genérica de requisição HTTP com tipagem — injeta token e trata erros da API.
// `jaTentouRenovar` evita loop: só tenta renovar a sessão (item S15) UMA vez por chamada.
async function req<T>(path: string, options?: RequestInit, jaTentouRenovar = false): Promise<T> {
  const t = await auth.token()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  }
  if (t) headers['Authorization'] = `Bearer ${t}`

  const res = await fetchOuErroDeConexao(`${BASE}${path}`, { ...options, headers })
  if (res.status === 401) {
    if (!jaTentouRenovar && (await tentarRenovarSessao())) {
      return req<T>(path, options, true)
    }
    await redirecionarParaLoginPorSessaoExpirada()
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

export const api = {
  // Login usa form-urlencoded conforme exigido pelo OAuth2PasswordRequestForm do FastAPI
  async login(email: string, senha: string): Promise<TokenResposta> {
    const form = new URLSearchParams({ username: email, password: senha })
    const res = await fetchOuErroDeConexao(`${BASE}/autenticacao/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    if (!res.ok) {
      const erro = await res.json().catch(() => null)
      throw new Error(extrairDetail(erro) ?? 'Email ou senha incorretos')
    }
    return res.json() as Promise<TokenResposta>
  },

  // Retorna os dados do usuário autenticado
  eu: () => req<Usuario>('/usuarios/eu'),

  chamados: {
    listar: () => req<Chamado[]>('/chamados/'),
    criar: (payload: ChamadoCriar) =>
      req<Chamado>('/chamados/', { method: 'POST', body: JSON.stringify(payload) }),
    criarIrmaos: (payload: ChamadosIrmaosCriar) =>
      req<Chamado[]>('/chamados/irmaos', { method: 'POST', body: JSON.stringify(payload) }),
    atualizarStatus: (id: string, status: ChamadoStatus) =>
      req<Chamado>(`/chamados/${id}/status?status=${status}`, { method: 'PATCH' }),
  },

  mensagens: {
    listar: (_chamadoID: string) => Promise.reject(funcionalidadeFutura('Mensagens')),
    enviar: (_chamadoID: string, _conteudo: string) => Promise.reject(funcionalidadeFutura('Mensagens')),
  },
}
