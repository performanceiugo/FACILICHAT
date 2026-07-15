// error.tsx — boundary global de erro de runtime do web (App Router)
// Capta exceções não tratadas em qualquer página/segmento e mostra uma tela
// amigável em PT com opção de tentar de novo, em vez da tela técnica do Next.
// Precisa ser client component: recebe reset() para re-renderizar o segmento.
'use client'

import { useEffect } from 'react'
import styles from './erro.module.css'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  // Loga o erro no console do navegador para diagnóstico em dev/suporte —
  // o usuário final vê só a mensagem amigável abaixo, nunca o stack trace
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className={styles.container}>
      <div className={styles.card} role="alert">
        <p className={styles.codigo} aria-hidden="true">Ops!</p>
        <h1 className={styles.titulo}>Algo deu errado</h1>
        <p className={styles.descricao}>
          Ocorreu um erro inesperado ao carregar esta página. Tente novamente e,
          se o problema continuar, fale com o suporte.
        </p>
        {/* reset() tenta re-renderizar o segmento que falhou sem recarregar a página inteira */}
        <button type="button" className={styles.botao} onClick={() => reset()}>
          Tentar novamente
        </button>
      </div>
    </div>
  )
}
