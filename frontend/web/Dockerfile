# Imagem de PRODUÇÃO do painel web FaciliChat (Next.js standalone) — item S9.
# Dev não usa esta imagem (continua `npm run dev` fora do Docker, ver docs/setup.md).
#
# Build em dois estágios: o primeiro compila com todas as devDependencies; o segundo
# copia apenas o resultado standalone (server.js + node_modules mínimos), gerando uma
# imagem final pequena e sem código-fonte/toolchain.

# ---------- Estágio 1: build ----------
FROM node:22-alpine AS build
WORKDIR /app

# Dependências primeiro — camada cacheável enquanto os manifests não mudam.
# `npm ci` instala exatamente o que está no package-lock.json (reprodutível).
COPY package.json package-lock.json ./
RUN npm ci

# Código-fonte (o .dockerignore barra node_modules, .next e .env*)
COPY . .

# Origem da API que o proxy `/api/*` do Next usa como destino (rewrites do next.config.ts).
# É resolvida DURANTE o build, por isso entra como build-arg e não como env de runtime.
# O default aponta para o serviço `backend` da rede interna do compose de produção.
ARG NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Sem telemetria da Vercel no build/execução
ENV NEXT_TELEMETRY_DISABLED=1

# Gera .next/standalone (habilitado por `output: 'standalone'` no next.config.ts)
RUN npm run build

# ---------- Estágio 2: runtime ----------
FROM node:22-alpine AS runner
WORKDIR /app

# O server.js standalone lê PORT/HOSTNAME do ambiente; 0.0.0.0 expõe para a rede do compose
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# Copia só o necessário: o servidor autocontido e os assets estáticos do build.
# `--chown=node:node` porque o processo roda como o usuário não-root `node` (abaixo).
# (Quando o projeto ganhar uma pasta `public/`, copiá-la aqui também: ./public)
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static

# Usuário não-root (item S9): mesmo racional do backend — processo sem privilégio de root
USER node

EXPOSE 3000
CMD ["node", "server.js"]
