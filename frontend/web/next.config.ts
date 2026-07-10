// Configuração do Next.js do painel web FaciliChat
// Responsável por: proxy opcional para a API (rewrites) e headers de segurança de todas as
// respostas (item S16 do plano): CSP em Report-Only, anti-sniffing, anti-clickjacking,
// política de referrer e de permissões. HSTS fica no proxy HTTPS de produção (docs/deploy-producao.md).

import type { NextConfig } from 'next'

// Origem da API FastAPI — destino do proxy `/api/*`. Note que ela NÃO entra no `connect-src` da
// CSP: depois do item S6 o navegador nunca fala com a API diretamente, só com este servidor Next,
// que reencaminha. Quem faz a chamada à API é o servidor, e CSP não se aplica a ele.
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
  `connect-src 'self'${dev ? ' ws: wss:' : ''}`,                    // só a própria origem: a API é alcançada pelo proxy /api/* (S6). (+HMR em dev)
  "object-src 'none'",                                              // sem plugins/embeds
  "base-uri 'self'",                                                // impede sequestro de <base>
  "form-action 'self'",                                             // forms só postam na própria origem
  "frame-ancestors 'none'",                                         // ninguém pode embutir o painel em iframe
].join('; ')

const nextConfig: NextConfig = {
  // Build "standalone" (item S9): o `next build` gera em .next/standalone um servidor Node
  // autocontido (server.js + só os node_modules realmente usados), que é o que a imagem Docker
  // de produção copia — a imagem final não precisa do node_modules inteiro nem do código-fonte.
  // Não afeta `next dev` nem o `next start` usado fora do Docker.
  output: 'standalone',

  // Por padrão o Next redireciona (308) qualquer URL terminada em "/" para a versão sem barra.
  // As rotas do backend usam barra final (`/chamados/`), então esse redirecionamento quebraria o
  // proxy: o fetch seguiria para `/api/chamados` e o método/corpo do POST se perderiam no caminho.
  // Desligar o redirecionamento faz a URL chegar intacta ao rewrite.
  skipTrailingSlashRedirect: true,

  // Proxy /api/* → backend. Estratégia definitiva escolhida no item M6 e implementada junto do S6:
  // o navegador só conversa com esta origem, o que torna o cookie de sessão first-party.
  async rewrites() {
    return [
      // A barra final precisa sobreviver ao proxy. O padrão `/api/:path*` a consome, e o backend
      // (cujas rotas são `/chamados/`) responderia 307 apontando para a ORIGEM DA API — o navegador
      // seguiria esse redirecionamento para fora do proxy, tornando o cookie de terceira parte e
      // esbarrando na CSP `connect-src 'self'`. Esta regra vem primeiro e preserva a barra.
      {
        source: '/api/:path*/',
        destination: `${API_ORIGIN}/:path*/`,
      },
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
          // 'Content-Security-Policy' (enforce) — passos em docs/deploy-producao.md.
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
