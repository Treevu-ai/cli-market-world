# Railway deploy — cli-market-world

## Diagnóstico (Jun 2026)

| Síntoma | Causa |
|---------|--------|
| `git push main` no mueve Railway | No había workflow de deploy; integración GitHub nativa desconectada |
| GitHub Action `RAILWAY_TOKEN` vacío | Secret mal nombrado, en Variables en vez de Secrets, o repo sin acceso |
| Project token no despliega | **Project tokens son read-only** — no pueden `serviceInstanceDeploy` |

## Setup correcto (una vez)

### 1. Token de cuenta (NO project token)

1. https://railway.com/account/tokens
2. **Team → No team** (o tu team) → **Create token**
3. Copia el token (suele empezar con formato distinto al UUID del project token)

### 2. GitHub Actions secret

https://github.com/Treevu-ai/cli-market-world/settings/secrets/actions

| Name | Value |
|------|--------|
| `RAILWAY_API_TOKEN` | token del paso 1 |

> Si ya creaste `RAILWAY_TOKEN` con project token, **reemplázalo** o añade `RAILWAY_API_TOKEN` con account token.

### 3. (Opcional) Cursor Cloud Agent

https://cursor.com/dashboard → Cloud Agents → Secrets:

| Name | Value |
|------|--------|
| `RAILWAY_API_TOKEN` | mismo account token |

Reinicia el agente tras añadir secrets.

### 4. (Opcional) Variables de servicio

https://github.com/Treevu-ai/cli-market-world/settings/variables/actions

Solo si auto-detect falla:

| Name | Value |
|------|--------|
| `RAILWAY_API_SERVICE_ID` | UUID del servicio API (Cmd+K → "Copy Service ID" en Railway) |
| `RAILWAY_COLLECTOR_SERVICE_ID` | `3813265a-1862-44a7-a723-62afa8a88dcf` |

## Disparar deploy

### GitHub Actions (recomendado)

https://github.com/Treevu-ai/cli-market-world/actions/workflows/deploy-railway.yml

**Run workflow** → `target: both`

### Desde terminal (agente o local)

```bash
export RAILWAY_API_TOKEN='...'
python3 ops/railway_deploy.py --list-services
python3 ops/railway_deploy.py --target both
```

### Railway dashboard (manual)

Servicio API → Deployments → Deploy latest commit from `main` on `Treevu-ai/cli-market-world`.

Verifica **Settings → Source** apunta a ese repo.

## Verificación

```bash
curl -s https://cli-market-production.up.railway.app/openapi.json | jq .info.version
# >= 1.9.33

curl -s "https://cli-market-production.up.railway.app/analytics/observatory?days=30" \
  | jq '[.top_tools[].name] | index("index_stats")'
# null
```

## IDs conocidos

| Recurso | ID |
|---------|-----|
| Project | `d0353d46-78c9-4949-a03f-3ecdb78f06aa` |
| Environment (production) | `036bd72a-f6d8-4c51-b2ab-50cfb261468b` |
| Collector service | `3813265a-1862-44a7-a723-62afa8a88dcf` |
