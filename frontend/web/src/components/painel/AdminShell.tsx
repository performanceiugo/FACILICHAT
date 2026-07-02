'use client'

// AdminShell — casca do painel administrativo (sidebar + navegação + guarda de sessão).
// Extraído de painel/layout.tsx para virar componente reutilizável por todas as telas do
// painel do Gestor (Milestone 3). Comportamento idêntico ao layout anterior: protege as
// rotas (redireciona ao /login sem sessão), monta a sidebar e renderiza o conteúdo da página.

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { auth } from '@/lib/auth'
import styles from './AdminShell.module.css'

export function AdminShell({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  // Estado da sessão lido no cliente — NUNCA durante o render/SSR (onde localStorage não existe).
  // `carregado` evita o flash do painel e a divergência de hidratação (server x client).
  const [carregado, setCarregado] = useState(false)
  const [nome, setNome] = useState<string | null>(null)
  const [ehSupervisor, setEhSupervisor] = useState(false)

  useEffect(() => {
    // Sem sessão ativa → manda para o login e não revela o painel
    if (!auth.autenticado()) {
      router.push('/login')
      return
    }
    // Com sessão: carrega os dados do usuário para o estado
    setNome(auth.nome())
    setEhSupervisor(auth.isSupervisor())
    setCarregado(true)
  }, [router])

  // Encerra a sessão e volta ao login
  function sair() {
    auth.sair()
    router.push('/login')
  }

  // Enquanto a sessão não foi validada no cliente, não renderiza nada (sem flash de conteúdo protegido)
  if (!carregado) return null

  return (
    <div className={styles.wrapper}>
      {/* Sidebar de navegação lateral */}
      <aside className={styles.sidebar}>
        <div className={styles.logo}>FaciliChat</div>

        <nav className={styles.nav}>
          <Link href="/painel/chamados" className={styles.link}>Chamados</Link>
          {/* Link "Usuários" visível apenas para Supervisor e Gestor */}
          {ehSupervisor && (
            <Link href="/painel/usuarios" className={styles.link}>Usuários</Link>
          )}
        </nav>

        {/* Rodapé da sidebar com nome do usuário e botão de logout */}
        <div className={styles.rodape}>
          <span className={styles.nomeUsuario}>{nome}</span>
          <button onClick={sair} className={styles.botaoSair}>Sair</button>
        </div>
      </aside>

      {/* Área de conteúdo principal — renderiza a página atual */}
      <main className={styles.conteudo}>{children}</main>
    </div>
  )
}
