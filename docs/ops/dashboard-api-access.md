# Dashboard — acceso programático (interno)

La sección `[ ACCESO ]` con curls ya **no se muestra** en el dashboard público (`/dashboard`). Los datos siguen disponibles vía API; este doc es la referencia para ops, ventas Intelligence y integraciones.

También disponible en JSON: `GET /dashboard/data` → `dashboard_view.blocks.portada.acceso` (spec 1.2+).

## Base

```bash
export BASE=https://cli-market-production.up.railway.app
```

## Intelligence API v1

| Endpoint | Uso |
|----------|-----|
| `GET /v1/sources/health` | Salud scraping por tienda |
| `GET /v1/quality/flagged?limit=50` | Anomalías paginadas (discount / outlier / spread) |
| `GET /v1/prices?clean=1&country=PE&limit=100` | Precios limpios paginados |
| `GET /v1/dispersion?clean=1&limit=50` | Brechas por subcategoría |
| `GET /v1/basket` | Canasta snapshot desde DB |
| `GET /v1/coverage/matrix` | Mapa país × línea + gaps |

```bash
curl -s $BASE/v1/sources/health | jq '.summary'
curl -s '$BASE/v1/quality/flagged?limit=5'
curl -s '$BASE/v1/prices?clean=1&country=PE&limit=10'
curl -s '$BASE/v1/dispersion?clean=1&limit=10'
curl -s $BASE/v1/basket | jq '.stores[]|{store_name,comparable,total}'
curl -s $BASE/v1/coverage/matrix | jq '.gaps'
```

**Snapshot vs live:** `GET /v1/basket` usa snapshots DB. `POST /v1/basket/compare` hace scrape en vivo (`source: live`).

Spec completa: `docs/dashboard-redesign.md` · implementación: `docs/ops/phase6-intelligence-api.md`.

## Otros comandos

| Comando | Qué devuelve |
|---------|----------------|
| `curl -s $BASE/dashboard/data \| jq '.quality_funnel,.dashboard_view.blocks'` | Payload completo + bloques render-ready |
| `curl -s $BASE/health/collector` | Estado del collector (ok / stale / dead / running) |
| `curl -s '$BASE/analytics/price-history?sku=...'` | Historial de precio por SKU |

## Nota producto

- **Build** (Free/Pro): API/MCP para builders — ver landing `#pricing-build`.
- **Intelligence** (piloto $300–500/mo): datos comerciales con capa de calidad — ver landing `#pricing-intelligence`.
