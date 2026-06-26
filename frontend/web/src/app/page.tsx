// Página raiz (/) — redireciona automaticamente para a tela de login
// O Next.js executa este redirect no servidor antes de qualquer renderização

import { redirect } from 'next/navigation'

export default function Home() {
  redirect('/login')
}
