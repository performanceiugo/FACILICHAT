// Proxy de autenticacao do app web (renomeado de middleware.ts na migracao para o Next.js 16 — item V4/V5).
// Executa antes do render para evitar flash de conteudo protegido nas rotas do painel/plataforma.

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { COOKIE_FUNCAO, COOKIE_SESSAO } from '@/lib/auth-storage'

function construirUrl(request: NextRequest, pathname: string) {
  return new URL(pathname, request.url)
}

// O proxy existe para evitar o FLASH de conteudo protegido — nao para autorizar.
// Por decisao explicita (item S6), ele apenas CHECA A PRESENCA do cookie de sessao; nao verifica
// a assinatura do JWT, o que exigiria espalhar o `JWT_SECRET` para o servidor do Next.
// Toda autorizacao real acontece no backend, que revalida o token assinado a cada requisicao.
//
// O cookie `funcao` e legivel (logo, forjavel) e serve so para escolher a tela inicial. Forja-lo
// leva o usuario a uma tela que a API vai recusar a preencher — nao concede acesso a dado nenhum.
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const sessao = request.cookies.get(COOKIE_SESSAO)?.value
  const funcao = request.cookies.get(COOKIE_FUNCAO)?.value
  const autenticado = !!sessao
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
      return NextResponse.redirect(construirUrl(request, '/painel/visao-geral'))
    }
  }

  if (pathname === '/login' && autenticado) {
    return NextResponse.redirect(
      construirUrl(request, ehSuperadmin ? '/plataforma/empresas' : '/painel/visao-geral')
    )
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/login', '/painel/:path*', '/plataforma/:path*'],
}
