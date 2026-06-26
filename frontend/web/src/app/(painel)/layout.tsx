'use client'

// Layout do painel administrativo — envolve todas as páginas dentro de /painel/
// Protege as rotas: redireciona para /login se o usuário não estiver autenticado
// Renderiza a sidebar de navegação com links e botão de logout

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { auth } from '@/lib/auth'
import styles from './painel.module.css'

export default function PainelLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  // Redireciona para login se não houver sessão ativa (token ausente no localStorage)
  useEffect(() => {
    if (!auth.autenticado()) router.push('/login')
  }, [router])

  function sair() {
    auth.sair()
    router.push('/login')
  }

  return (
    <div className={styles.wrapper}>
      {/* Sidebar de navegação lateral */}
      <aside className={styles.sidebar}>
        <div className={styles.logo}>FaciliChat</div>

        <nav className={styles.nav}>
          <Link href="/painel/chamados" className={styles.link}>Chamados</Link>
          {/* Link "Usuários" visível apenas para Supervisor e Gerente */}
          {auth.isSupervisor() && (
            <Link href="/painel/usuarios" className={styles.link}>Usuários</Link>
          )}
        </nav>

        {/* Rodapé da sidebar com nome do usuário e botão de logout */}
        <div className={styles.rodape}>
          <span className={styles.nomeUsuario}>{auth.nome()}</span>
          <button onClick={sair} className={styles.botaoSair}>Sair</button>
        </div>
      </aside>

      {/* Área de conteúdo principal — renderiza a página atual */}
      <main className={styles.conteudo}>{children}</main>
    </div>
  )
}
