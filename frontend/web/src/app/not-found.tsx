// not-found.tsx — página 404 global do web (App Router)
// Exibida quando a rota não existe ou quando notFound() é chamado em uma página.
// Server component simples: só apresenta a mensagem e um link de volta ao início
// (a raiz "/" redireciona para o login ou painel conforme a sessão).

import Link from 'next/link'
import styles from './erro.module.css'

export default function NotFound() {
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <p className={styles.codigo} aria-hidden="true">404</p>
        <h1 className={styles.titulo}>Página não encontrada</h1>
        <p className={styles.descricao}>
          O endereço que você tentou acessar não existe ou foi movido.
        </p>
        <Link href="/" className={styles.botao}>
          Voltar ao início
        </Link>
      </div>
    </div>
  )
}
