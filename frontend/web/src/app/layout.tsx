// Layout raiz da aplicação Next.js — envolve todas as páginas
// Define fonte global, metadados da aba do navegador e idioma padrão

import type { Metadata } from 'next'
import { Geist } from 'next/font/google'
import './globals.css'

// Carrega a fonte Geist do Google Fonts com subset latino (otimizado para produção)
const geist = Geist({ subsets: ['latin'] })

// Metadados exibidos na aba do navegador e em mecanismos de busca
export const metadata: Metadata = {
  title: 'FaciliChat',
  description: 'Plataforma de atendimento para gestão de condomínios',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={geist.className}>{children}</body>
    </html>
  )
}
