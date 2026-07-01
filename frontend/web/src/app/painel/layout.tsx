'use client'

// Layout do painel administrativo — envolve todas as páginas dentro de /painel/
// Protege as rotas: redireciona para /login se o usuário não estiver autenticado
// Renderiza a sidebar de navegação com links e botão de logout

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { auth } from '@/lib/auth'
import styles from './painel.module.css'

export default function PainelLayout({ children }: { children: React.ReactNode }) {
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
