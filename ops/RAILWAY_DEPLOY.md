# Railway deploy — cli-market-world

## Diagnóstico (Jun 2026)

| Síntoma | Causa |
|---------|--------|
| `git push main` no mueve Railway | No había workflow de deploy; integración GitHub nativa desconectada |
| GitHub Action `RAILWAY_TOKEN` vacío | Secret mal nombrado, en Variables en vez de Secrets, o repo sin acceso |
| Project token + GraphQL | **Project tokens no pueden** `serviceInstanceDeploy` — usar `railway up` (soportado en CI) |

## Setup correcto (una vez)

Elige **una** opción (A es más rápida):

### Opción A — Project token (recomendado, 2 min)

1. Railway → tu proyecto → **Settings** → **Tokens** → **Create token**
2. GitHub → https://github.com/Treevu-ai/cli-market-world/settings/secrets/actions

| Name | Value |
|------|--------|
| `RAILWAY_TOKEN` | project token (UUID) del paso 1 |

El workflow sube el código del checkout con `railway up` — no requiere account token.

### Opción B — Account token (GraphQL, latest commit de GitHub)

1. https://railway.com/account/tokens → **Team → No team** → **Create token**
2. GitHub secret:

| Name | Value |
|------|--------|
| `RAILWAY_API_TOKEN` | account token del paso 1 |

Puedes tener **ambos** secrets; account token se usa primero, project token como fallback.

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
