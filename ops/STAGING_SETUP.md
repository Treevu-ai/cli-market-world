# CLI Market — Staging Environment Setup

## Fly.io Staging (recommended)

### 1. Create staging app
```bash
# Separate Fly app, same org — Fly has no built-in "environments" like Railway,
# so staging is just a second app (e.g. cli-market-api-staging).
fly apps create cli-market-api-staging
fly postgres create --name cli-market-db-staging --region gru --vm-size shared-cpu-1x --volume-size 1
fly postgres attach cli-market-db-staging --app cli-market-api-staging
```

### 2. Required variables (copy from production, override these)
```
DATABASE_URL=<staging-postgres-url>  # Separate Postgres instance (auto-injected by `fly postgres attach`)
PAYPAL_SANDBOX=true
MERCADOPAGO_SANDBOX=true
MARKET_ENV=staging
```

### 3. Staging-specific behavior

The server auto-detects staging via `MARKET_ENV` (Fly does not inject an environment-name var):

| Feature | Production | Staging |
|---|---|---|
| SQLite fallback | **Blocked** (crashes) | Allowed (for quick tests) |
| PayPal | Live credentials | Sandbox |
| MercadoPago | Live credentials | Sandbox |
| Webhook verification | Required | Optional |
| Slack notifications | All channels | `#staging-alerts` only |

### 4. Deploy
```bash
fly deploy --app cli-market-api-staging --config fly.toml
```

### 5. Healthcheck
```bash
curl https://cli-market-api-staging.fly.dev/health/deep
# Expected: {"status": "healthy", "checks": {...}}
```

### 6. Smoke test
```bash
# Basic API
curl https://cli-market-api-staging.fly.dev/health
curl https://cli-market-api-staging.fly.dev/stores
curl https://cli-market-api-staging.fly.dev/v1/search?q=leche&country=PE

# Deep health
curl https://cli-market-api-staging.fly.dev/health/deep

# MCP discovery
curl https://cli-market-api-staging.fly.dev/.well-known/mcp.json
```
