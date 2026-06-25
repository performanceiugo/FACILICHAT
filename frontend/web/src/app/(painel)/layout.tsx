'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { auth } from '@/lib/auth'
import styles from './painel.module.css'

export default function PainelLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    if (!auth.autenticado()) router.push('/login')
  }, [router])

  function sair() {
    auth.sair()
    router.push('/login')
  }

  return (
    <div className={styles.wrapper}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>FaciliChat</div>
        <nav className={styles.nav}>
          <Link href="/painel/chamados" className={styles.link}>Chamados</Link>
          {auth.isSupervisor() && (
            <Link href="/painel/usuarios" className={styles.link}>Usuários</Link>
          )}
        </nav>
        <div className={styles.rodape}>
          <span className={styles.nomeUsuario}>{auth.nome()}</span>
          <button onClick={sair} className={styles.botaoSair}>Sair</button>
        </div>
      </aside>
      <main className={styles.conteudo}>{children}</main>
    </div>
  )
}
