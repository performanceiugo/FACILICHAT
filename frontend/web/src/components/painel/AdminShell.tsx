'use client'

// AdminShell — casca do painel administrativo (sidebar + navegação + guarda de sessão).
// Extraído de painel/layout.tsx para virar componente reutilizável por todas as telas do
// painel do Gestor (Milestone 3). Comportamento idêntico ao layout anterior: protege as
// rotas (redireciona ao /login sem sessão), monta a sidebar e renderiza o conteúdo da página.

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { auth } from '@/lib/auth'
import styles from './AdminShell.module.css'

// Marca oficial do FaciliChat (mesma arte usada no protótipo comercial) — quadrado azul
// arredondado com o checkmark em branco. Mantida como SVG inline (sem libs extras).
function LogoMark() {
  return (
    <svg className={styles.logoMark} viewBox="0 0 1200 1200" aria-hidden="true">
      <path fill="#148AF5" d="M780.23,311.51h-360.45c-67.19,0-121.65,54.47-121.65,121.65v267.89c0,.93.05,1.84.07,2.77h-.07v156.2c0,15.71,12.74,28.45,28.45,28.45,6.4,0,12.61-2.16,17.63-6.12l75.57-59.65h360.45c67.19,0,121.65-54.47,121.65-121.65v-267.89c0-67.19-54.47-121.65-121.65-121.65Z" />
      <path fill="#fff" d="M566.14,687.93c-9.96,0-19.51-3.96-26.54-11.01l-78.59-78.76c-14.63-14.66-14.6-38.4.06-53.03,14.66-14.63,38.4-14.6,53.03.06l51.74,51.85,119.76-122.78c14.46-14.82,38.2-15.12,53.02-.66,14.82,14.46,15.12,38.2.66,53.02l-146.3,149.98c-7.01,7.18-16.6,11.26-26.63,11.31h-.21Z" />
    </svg>
  )
}

// Ícones de linha (estilo Line Awesome) usados na navegação — inline para não depender de libs extras.
const IconChamados = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 11l3 3L22 4" />
    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
  </svg>
)

// Deriva as iniciais do nome para o avatar circular do rodapé (ex.: "Edson Gestor" → "EG")
function iniciais(nome: string): string {
  const partes = nome.trim().split(/\s+/)
  const primeiras = partes.slice(0, 2).map(p => p[0]?.toUpperCase() ?? '')
  return primeiras.join('') || '?'
}

export function AdminShell({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()

  // Estado da sessão lido no cliente — NUNCA durante o render/SSR (onde localStorage não existe).
  // `carregado` evita o flash do painel e a divergência de hidratação (server x client).
  const [carregado, setCarregado] = useState(false)
  const [nome, setNome] = useState<string | null>(null)
  const [empresaNome, setEmpresaNome] = useState<string | null>(null)
  useEffect(() => {
    // Sem sessão ativa → manda para o login e não revela o painel
    if (!auth.autenticado()) {
      router.push('/login')
      return
    }
    // Com sessão: carrega os dados do usuário para o estado
    setNome(auth.nome())
    setEmpresaNome(auth.empresaNome())
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
        <div className={styles.logo}>
          <LogoMark />
          FaciliChat
        </div>

        <nav className={styles.nav}>
          <Link
            href="/painel/chamados"
            className={pathname?.startsWith('/painel/chamados') ? styles.linkAtivo : styles.link}
          >
            <span className={styles.navIcone}><IconChamados /></span>
            Chamados
          </Link>
        </nav>

        {/* Rodapé da sidebar com identificação do usuário e botão de logout */}
        <div className={styles.rodape}>
          <div className={styles.usuario}>
            <span className={styles.avatar}>{nome ? iniciais(nome) : '?'}</span>
            <div className={styles.usuarioInfo}>
              <span className={styles.nomeUsuario}>{nome}</span>
              {empresaNome && <span className={styles.empresaUsuario}>{empresaNome}</span>}
            </div>
          </div>
          <button onClick={sair} className={styles.botaoSair}>Sair</button>
        </div>
      </aside>

      {/* Área de conteúdo principal — renderiza a página atual */}
      <main className={styles.conteudo}>{children}</main>
    </div>
  )
}
