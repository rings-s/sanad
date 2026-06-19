# ── Stage 1: build the SvelteKit app as a Node SSR server ─────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies against the lockfile first for better layer caching.
COPY package.json package-lock.json ./
RUN npm ci

# VITE_API_URL is inlined into the client bundle at build time (import.meta.env),
# so it must be supplied here — a runtime env var would not take effect.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ENV ADAPTER=node

COPY . .
# build:node skips the Cloudflare-only `wrangler types --check` step.
RUN npm run build:node


# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM node:22-alpine AS production

WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOST=0.0.0.0

# Only production dependencies (the adapter-node server bundles the rest).
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force

COPY --from=builder /app/build ./build

USER node
EXPOSE 3000

# adapter-node entrypoint. ORIGIN/PORT/HOST are read from the environment.
CMD ["node", "build"]
