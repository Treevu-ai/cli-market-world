# Dashboard — acceso programático (interno)

La sección `[ ACCESO ]` con curls ya **no se muestra** en el dashboard público (`/dashboard`). Los datos siguen disponibles vía API; este doc es la referencia para ops, ventas Intelligence y integraciones.

## Base

```bash
export BASE=https://cli-market-production.up.railway.app
```

## Comandos útiles

| Comando | Qué devuelve |
|---------|----------------|
| `curl -s $BASE/dashboard/data \| jq '.quality_funnel,.dashboard_view.blocks'` | Payload completo + bloques render-ready |
| `curl -s $BASE/health/collector` | Estado del collector (ok / stale / dead / running) |
| `curl -s '$BASE/analytics/price-history?sku=...'` | Historial de precio por SKU |

## Endpoints Intelligence (roadmap / parcial)

Ver `docs/dashboard-redesign.md` para la spec de `/v1/sources/health`, `/v1/quality/flagged`, `/v1/prices?clean=1`, etc.

## Nota producto

- **Build** (Free/Pro): API/MCP para builders — ver landing `#pricing-build`.
- **Intelligence** (piloto $300–500/mo): datos comerciales con capa de calidad — ver landing `#pricing-intelligence`.
