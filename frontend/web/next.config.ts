// Configuração do Next.js do painel web FaciliChat
// Responsável por: proxy opcional para a API (rewrites) e headers de segurança de todas as
// respostas (item S16 do plano): CSP em Report-Only, anti-sniffing, anti-clickjacking,
// política de referrer e de permissões. HSTS fica no proxy HTTPS de produção (docs/setup.md).

import type { NextConfig } from 'next'

// Origem da API FastAPI — precisa entrar no connect-src da CSP, senão o fetch do painel é violação
const API_ORIGIN = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

// Em desenvolvimento o Next exige 'unsafe-eval' (HMR/react-refresh) e WebSocket local;
// em produção o script-src fica sem eval.
const dev = process.env.NODE_ENV !== 'production'

// Content Security Policy — uma diretiva por item para facilitar leitura e manutenção.
// 'unsafe-inline' em script/style: o Next injeta scripts/estilos inline no bootstrap da página;
// a migração para nonces (que elimina o inline) fica para a fase de enforce da CSP.
const csp = [
  "default-src 'self'",                                             // padrão: só a própria origem
  `script-src 'self' 'unsafe-inline'${dev ? " 'unsafe-eval'" : ''}`, // scripts próprios (+eval só em dev)
  "style-src 'self' 'unsafe-inline'",                               // CSS próprio + inline do Next
  "img-src 'self' data: blob:",                                     // imagens locais e data-URIs (logo SVG)
  "font-src 'self' data:",                                          // Figtree é self-hosted via next/font
  `connect-src 'self' ${API_ORIGIN}${dev ? ' ws: wss:' : ''}`,      // fetch para a API (+HMR em dev)
  "object-src 'none'",                                              // sem plugins/embeds
  "base-uri 'self'",                                                // impede sequestro de <base>
  "form-action 'self'",                                             // forms só postam na própria origem
  "frame-ancestors 'none'",                                         // ninguém pode embutir o painel em iframe
].join('; ')

const nextConfig: NextConfig = {
  // Proxy /api/* → backend (configurado desde o início; estratégia definitiva é o item M6 do plano)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${API_ORIGIN}/:path*`,
      },
    ]
  },

  // Headers de segurança aplicados a TODAS as rotas do app (S16)
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          // CSP em modo Report-Only: o navegador só REGISTRA violações no console, sem bloquear
          // nada. Depois de um período de observação sem violações legítimas, renomear para
          // 'Content-Security-Policy' (enforce) — passos em docs/setup.md.
          { key: 'Content-Security-Policy-Report-Only', value: csp },
          // Impede o navegador de "adivinhar" o MIME type de uma resposta (bloqueia sniffing)
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          // Anti-clickjacking para navegadores antigos (redundante com frame-ancestors da CSP)
          { key: 'X-Frame-Options', value: 'DENY' },
          // Em navegação para outra origem, envia só a origem (não vaza caminho/query da URL)
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          // O painel não usa câmera/microfone/geolocalização — nega para qualquer script da página
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
        ],
      },
    ]
  },
}

export default nextConfig
