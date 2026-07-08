// Middleware de autenticacao do app web.
// Executa antes do render para evitar flash de conteudo protegido nas rotas do painel/plataforma.

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { FUNCAO_KEY, TOKEN_KEY } from '@/lib/auth-storage'

function construirUrl(request: NextRequest, pathname: string) {
  return new URL(pathname, request.url)
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get(TOKEN_KEY)?.value
  const funcao = request.cookies.get(FUNCAO_KEY)?.value
  const autenticado = !!token
  const ehSuperadmin = funcao === 'Superadmin'

  if (pathname.startsWith('/painel')) {
    if (!autenticado) {
      return NextResponse.redirect(construirUrl(request, '/login'))
    }
    if (ehSuperadmin) {
      return NextResponse.redirect(construirUrl(request, '/plataforma/empresas'))
    }
  }

  if (pathname.startsWith('/plataforma')) {
    if (!autenticado) {
      return NextResponse.redirect(construirUrl(request, '/login'))
    }
    if (!ehSuperadmin) {
      return NextResponse.redirect(construirUrl(request, '/painel/chamados'))
    }
  }

  if (pathname === '/login' && autenticado) {
    return NextResponse.redirect(
      construirUrl(request, ehSuperadmin ? '/plataforma/empresas' : '/painel/chamados')
    )
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/login', '/painel/:path*', '/plataforma/:path*'],
}
