'use client'

// Tela de login do painel web
// Após autenticação bem-sucedida, redireciona para /painel/chamados

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import styles from './login.module.css'

export default function LoginPage() {
  const router = useRouter()

  // Estado dos campos do formulário e controle de carregamento/erro
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErro('')
    setCarregando(true)
    try {
      // Autentica com o backend e salva token + dados no localStorage
      const dados = await api.login(email, senha)
      auth.salvar(dados)
      router.push(dados.funcao === 'Superadmin' ? '/plataforma/empresas' : '/painel/chamados')
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Erro ao fazer login')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <main className={styles.container}>
      <div className={styles.card}>
        {/* Marca oficial do FaciliChat — mesma arte usada no painel (AdminShell) e no protótipo comercial */}
        <svg className={styles.logo} viewBox="0 0 1200 1200" aria-hidden="true">
          <path fill="#148AF5" d="M780.23,311.51h-360.45c-67.19,0-121.65,54.47-121.65,121.65v267.89c0,.93.05,1.84.07,2.77h-.07v156.2c0,15.71,12.74,28.45,28.45,28.45,6.4,0,12.61-2.16,17.63-6.12l75.57-59.65h360.45c67.19,0,121.65-54.47,121.65-121.65v-267.89c0-67.19-54.47-121.65-121.65-121.65Z" />
          <path fill="#fff" d="M566.14,687.93c-9.96,0-19.51-3.96-26.54-11.01l-78.59-78.76c-14.63-14.66-14.6-38.4.06-53.03,14.66-14.63,38.4-14.6,53.03.06l51.74,51.85,119.76-122.78c14.46-14.82,38.2-15.12,53.02-.66,14.82,14.46,15.12,38.2.66,53.02l-146.3,149.98c-7.01,7.18-16.6,11.26-26.63,11.31h-.21Z" />
        </svg>
        <h1 className={styles.titulo}>FaciliChat</h1>
        <p className={styles.subtitulo}>Acesse sua conta</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Campo de email */}
          <div className={styles.campo}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="seu@email.com"
              required
              autoComplete="email"
            />
          </div>

          {/* Campo de senha */}
          <div className={styles.campo}>
            <label htmlFor="senha">Senha</label>
            <input
              id="senha"
              type="password"
              value={senha}
              onChange={e => setSenha(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          {/* Mensagem de erro exibida quando login falha */}
          {erro && <p className={styles.erro}>{erro}</p>}

          <button type="submit" disabled={carregando} className={styles.botao}>
            {carregando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </main>
  )
}
