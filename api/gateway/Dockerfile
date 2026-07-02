# ============================================================
# Stage 1: deps — production node_modules only
# ============================================================
FROM node:20-alpine AS deps

WORKDIR /app

COPY api/gateway/package*.json ./
RUN npm ci --only=production

# ============================================================
# Stage 2: builder — full install + transpile/bundle
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY api/gateway/package*.json ./

RUN npm ci --omit=dev

COPY api/gateway/ .
RUN npm run build

# ============================================================
# Stage 3: runner — lean production image
# ============================================================
FROM node:20-alpine AS runner

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid API Gateway"
LABEL org.opencontainers.image.description="Node.js Express API gateway routing to backend services"

RUN addgroup --system --gid 1005 gateway \
    && adduser --system --uid 1005 --ingroup gateway gateway

WORKDIR /app

COPY --from=deps    /app/node_modules ./node_modules
COPY --from=builder /app/dist         ./dist

# Copy package.json for runtime metadata
COPY api/gateway/package.json ./

ENV NODE_ENV=production \
    PORT=3001

USER gateway

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:3001/health || exit 1

CMD ["node", "dist/server.js"]
