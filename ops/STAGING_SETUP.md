# CLI Market — Staging Environment Setup

## Railway Staging (recommended)

### 1. Create staging environment
```bash
# In Railway dashboard → Project → Environments → New Environment
# Name: staging
# Source branch: staging (or main for mirror)
```

### 2. Required variables (copy from production, override these)
```
RAILWAY_ENVIRONMENT=staging
DATABASE_URL=<staging-postgres-url>  # Separate Postgres instance
PAYPAL_SANDBOX=true
MERCADOPAGO_SANDBOX=true
MARKET_ENV=staging
```

### 3. Staging-specific behavior

The server auto-detects staging via `RAILWAY_ENVIRONMENT` or `MARKET_ENV`:

| Feature | Production | Staging |
|---|---|---|
| SQLite fallback | **Blocked** (crashes) | Allowed (for quick tests) |
| PayPal | Live credentials | Sandbox |
| MercadoPago | Live credentials | Sandbox |
| Webhook verification | Required | Optional |
| Slack notifications | All channels | `#staging-alerts` only |

### 4. Deploy
```bash
# Railway auto-deploys from the staging branch
git push origin main:staging
```

### 5. Healthcheck
```bash
curl https://<staging-domain>.up.railway.app/health/deep
# Expected: {"status": "healthy", "checks": {...}}
```

### 6. Smoke test
```bash
# Basic API
curl https://<staging-domain>.up.railway.app/health
curl https://<staging-domain>.up.railway.app/stores
curl https://<staging-domain>.up.railway.app/v1/search?q=leche&country=PE

# Deep health
curl https://<staging-domain>.up.railway.app/health/deep

# MCP discovery
curl https://<staging-domain>.up.railway.app/.well-known/mcp.json
```
