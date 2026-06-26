// Cliente HTTP centralizado para comunicação com o backend FastAPI
// Todas as chamadas de API passam por aqui — adiciona token de autenticação automaticamente

import type { Chamado, ChamadoCriar, ChamadoStatus, Mensagem, TokenResposta, Usuario } from '@/types'

// URL base da API — configurada via variável de ambiente, com fallback para desenvolvimento local
const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

// Lê o token JWT salvo no localStorage (retorna null no servidor — Next.js SSR não tem window)
function token(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

// Função genérica de requisição HTTP com tipagem — injeta token e trata erros da API
async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const t = token()
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

// Métodos disponíveis para o frontend consumir a API
export const api = {
  // Login usa form-urlencoded conforme exigido pelo OAuth2PasswordRequestForm do FastAPI
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

  // Retorna os dados do usuário autenticado (baseado no token da requisição)
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
