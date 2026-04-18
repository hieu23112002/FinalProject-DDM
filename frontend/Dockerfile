# --- Build Stage ---
FROM node:20-slim AS builder
WORKDIR /app

# Install dependencies first (for better caching)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source and build
COPY . .
# Set environment for production build
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
RUN npm run build

# --- Production Stage ---
FROM node:20-slim AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy necessary files from builder
# We only need the standalone build (requires output: 'standalone' in next.config.ts/js)
# or just the static files + next server.
# For simplicity in this demo, let's copy common files.
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "run", "start"]
