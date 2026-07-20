# KARNADHAR war-room — production container for Google Cloud Run.
# Multi-stage: install → build → tiny runtime from Next.js standalone output.
# The app serves the pre-exported frontend/public/karnadhar.json — no backend,
# no database, no API keys needed at runtime.

# ---- deps: install exactly what package-lock pins ----
FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ---- build: produce .next/standalone ----
FROM node:20-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ---- runtime: minimal image, non-root, listens on $PORT ----
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Cloud Run injects PORT (default 8080); Next's standalone server reads it.
ENV PORT=8080
# standalone bundle carries its own traced node_modules + server.js.
# public/ and .next/static are NOT included by standalone — copy them in.
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 8080
CMD ["node", "server.js"]
