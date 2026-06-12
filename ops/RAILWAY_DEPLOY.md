# Railway deploy — cli-market-world

## Por qué `git push main` no mueve Railway

Este repo **no tenía** workflow de deploy a Railway. Los pushes solo disparan:

- CI / CodeQL
- PyPI (solo con tag `v*`)
- Landing Cloudflare (solo si cambia `landing/`)

**Railway no se entera** del push salvo que:

1. Tengas la integración GitHub nativa conectada en el dashboard (repo + rama), **o**
2. Corras el workflow **Deploy Railway** (`.github/workflows/deploy-railway.yml`), **o**
3. Ejecutes `railway up` local con CLI enlazada.

Si prod sigue en **1.9.30** con `index_stats` en `/analytics/observatory`, la imagen API **no se reconstruyó** tras el merge de Observatory P0.

---

## Setup único (5 min)

### 1. Project token

Railway → proyecto CLI Market → **Settings** → **Tokens** → Create token.

GitHub → `Treevu-ai/cli-market-world` → **Settings** → **Secrets** → `RAILWAY_TOKEN` = token del paso anterior.

> Usa **Project Token**, no el API token de cuenta.

### 2. (Opcional) Service IDs — solo si el auto-detect falla

Con `RAILWAY_TOKEN` basta para el deploy API: el workflow lista servicios y elige el que no es Postgres/collector.

Si falla, añade **Variables** en GitHub:

**URL directa:** https://github.com/Treevu-ai/cli-market-world/settings/variables/actions

1. Click **New repository variable**
2. Repite para cada fila:

| Name | Value |
|------|--------|
| `RAILWAY_API_SERVICE_ID` | ver abajo cómo copiarlo en Railway |
| `RAILWAY_COLLECTOR_SERVICE_ID` | `3813265a-1862-44a7-a723-62afa8a88dcf` (opcional; hay default) |

#### Cómo copiar `RAILWAY_API_SERVICE_ID` en Railway

1. Abre https://railway.com/dashboard
2. Entra al proyecto **CLI Market** (o el que tenga `cli-market-production.up.railway.app`)
3. En el canvas, click el **servicio API** — el que tiene dominio `cli-market-production` (no Postgres, no collector)
4. Pestaña **Settings** → baja hasta **Service ID** → copiar UUID  
   **O** mira la URL del navegador:
   `https://railway.com/project/<PROJECT_ID>/service/<ESTE_ES_EL_SERVICE_ID>`
5. Pega ese UUID en GitHub como valor de `RAILWAY_API_SERVICE_ID`

### 3. Disparar deploy

```text
GitHub → Actions → Deploy Railway → Run workflow → target: both
```

O push a `main` que toque `Dockerfile`, `*.py`, `routers/`, etc.

---

## Redeploy manual (dashboard)

Sin GitHub Actions:

1. Railway → servicio **API** → **Deployments**
2. **Deploy** → branch `main` repo `Treevu-ai/cli-market-world`  
   (si no aparece el repo, reconectar GitHub en **Settings → Source**)
3. Repetir para **collector** si cambió `Dockerfile.collector` / `collect_prices.py`

---

## Verificación post-deploy

```bash
curl -s https://cli-market-production.up.railway.app/openapi.json | jq .info.version
# esperado: >= 1.9.33

curl -s "https://cli-market-production.up.railway.app/analytics/observatory?days=30" \
  | jq '[.top_tools[].name] | index("index_stats")'
# esperado: null (tool interna filtrada)
```

---

## IDs conocidos (prod)

| Recurso | ID |
|---------|-----|
| Project | `d0353d46-78c9-4949-a03f-3ecdb78f06aa` |
| Environment (production) | `036bd72a-f6d8-4c51-b2ab-50cfb261468b` |
| Collector service | `3813265a-1862-44a7-a723-62afa8a88dcf` |
| API service | **copiar del dashboard** → `RAILWAY_API_SERVICE_ID` |

---

## CLI local (alternativa)

```bash
npm i -g @railway/cli@5.2.0
railway login
railway link   # proyecto CLI Market
RAILWAY_TOKEN=<project-token> railway up --service=<API_SERVICE_ID>
```
