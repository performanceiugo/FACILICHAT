import * as SecureStore from 'expo-secure-store'
import type { Chamado, ChamadoCriar, ChamadoStatus, Mensagem, TokenResposta, Usuario } from './types'

const BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000'

async function token(): Promise<string | null> {
  return SecureStore.getItemAsync('token')
}

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const t = await token()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  }
  if (t) headers['Authorization'] = `Bearer ${t}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const erro = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
    throw new Error(erro.detail ?? 'Erro na requisição')
  }
  return res.json() as Promise<T>
}

export const api = {
  async login(email: string, senha: string): Promise<TokenResposta> {
    const form = new URLSearchParams({ username: email, password: senha })
    const res = await fetch(`${BASE}/autenticacao/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    if (!res.ok) throw new Error('Email ou senha incorretos')
    return res.json() as Promise<TokenResposta>
  },

  eu: () => req<Usuario>('/usuarios/eu'),

  chamados: {
    listar: () => req<Chamado[]>('/chamados/'),
    criar: (payload: ChamadoCriar) =>
      req<Chamado>('/chamados/', { method: 'POST', body: JSON.stringify(payload) }),
    atualizarStatus: (id: string, status: ChamadoStatus) =>
      req<Chamado>(`/chamados/${id}/status?status=${status}`, { method: 'PATCH' }),
  },

  mensagens: {
    listar: (chamadoID: string) => req<Mensagem[]>(`/mensagens/${chamadoID}`),
    enviar: (chamadoID: string, conteudo: string) =>
      req<Mensagem>(`/mensagens/${chamadoID}`, {
        method: 'POST',
        body: JSON.stringify({ Conteudo: conteudo }),
      }),
  },
}
