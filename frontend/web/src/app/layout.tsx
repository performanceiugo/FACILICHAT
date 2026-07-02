// Layout raiz da aplicação Next.js — envolve todas as páginas
// Define fonte global, metadados da aba do navegador e idioma padrão

import type { Metadata } from 'next'
import { Figtree } from 'next/font/google'
import './globals.css'

// Carrega a fonte Figtree (fonte oficial do design system) com os 6 pesos usados no branding.
// `variable` expõe a família como a CSS var --font-figtree, consumida por --font-sans no globals.css.
const figtree = Figtree({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-figtree',
})

// Metadados exibidos na aba do navegador e em mecanismos de busca
export const metadata: Metadata = {
  title: 'FaciliChat',
  description: 'Plataforma de atendimento para gestão de condomínios',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // A classe da variável da fonte fica no <html> para valer em todo o documento
    <html lang="pt-BR" className={figtree.variable}>
      <body>{children}</body>
    </html>
  )
}
