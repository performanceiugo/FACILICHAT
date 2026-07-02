// Layout do painel administrativo — envolve todas as páginas dentro de /painel/.
// A casca (sidebar, navegação e guarda de sessão) vive no componente reutilizável
// AdminShell, para ser compartilhada pelas telas do painel do Gestor (Milestone 3).

import { AdminShell } from '@/components/painel/AdminShell'

export default function PainelLayout({ children }: { children: React.ReactNode }) {
  return <AdminShell>{children}</AdminShell>
}
