# HANDOFF — Cost-of-Living OS (Waves 1–4)

Última actualización: 2026-06-23  
Branch de trabajo: `claude/ecstatic-feynman-6lklyv`

## Estado por wave

| Wave | Feature | Prod | PR |
|------|---------|------|-----|
| 1 | `build_basket_compare` + DB basket | ✅ | core PR #78 |
| 2 | Missions (`/v1/missions/optimize-purchase`) | ✅ | world PR #330 |
| 3 | Intel affordability (`/v1/intel/affordability`) | ✅ | world PR #330 |
| 4 | `market_optimize_purchase` MCP tool + `market optimize` CLI | ✅ | world PR #327 |
| 4 | `POST /v1/action/affiliate-click` | ✅ | world PR #330 |
| 4 | `/v1/basket/compare` Wave 4 params (`include_tco`, `include_action_links`) | ✅ | world (this branch) |

## Arquitectura mount (market_server.py)

```python
# Cost-of-Living OS v1 routes from cli-market-core (Waves 1–4).
# Mounted AFTER world routers — existing handlers win on duplicate paths.
from market_core import api_routes as core_api_routes
from market_core.api_routes import router as core_v1_router
core_api_routes._auth_fn = require_api_key
app.include_router(core_v1_router, prefix="/v1")
```

Rutas **nuevas** aportadas por el mount (no existían en world):
- `POST /v1/missions/optimize-purchase`
- `POST /v1/intel/affordability`
- `POST /v1/action/affiliate-click`
- `POST /v1/canasta/snapshot`

Rutas **existentes en world** que ahora soportan Wave 4 (handler world, enriquecido):
- `POST /v1/basket/compare` — acepta `include_tco`, `include_action_links`, `include_delivery`, `payment_method`, `zipcode`, `country`; cuando alguno está activo delega a `market_core.market_basket.build_basket_compare`

## Core pin actual

```
# requirements-railway.txt
cli-market-core @ git+https://github.com/Treevu-ai/cli-market-core.git@8469854
```

SHA `8469854` = PR #78 mergeado en core (Wave 4 completo).  
**Pendiente A**: publicar `cli-market-core==1.11.0` en PyPI y actualizar pin a `==1.11.0`.

## Smoke de producción

```bash
# Requiere API key válida en $TOK
TOK="sk-..."

# Optimize-purchase (Wave 2 mission) — debe devolver 401 sin auth
curl -s -o /dev/null -w "%{http_code}" https://cli-market-production.up.railway.app/v1/missions/optimize-purchase -X POST -H "Content-Type: application/json" -d '{}'
# → 401

# Affordability (Wave 3 intel) — público
curl -s https://cli-market-production.up.railway.app/v1/intel/affordability | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('methodology','?'))"
# → affordability_index_v1

# Affiliate click (Wave 4) — 401 sin auth, 200 con auth
curl -s -o /dev/null -w "%{http_code}" https://cli-market-production.up.railway.app/v1/action/affiliate-click \
  -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"store":"wong","product_id":"test-123","url":"https://example.com"}'
# → 200 (o 422 si store no tiene affiliate configurado)

# Basket compare con TCO (Wave 4 world handler)
curl -s https://cli-market-production.up.railway.app/v1/basket/compare \
  -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"items":[{"name":"leche","qty":2}],"include_tco":true}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('methodology','no-envelope'))"
# → basket_compare_v1
```

## Affiliate — configuración en Railway

| Variable de entorno | Valor | Descripción |
|--------------------|----|-------------|
| `AFFILIATE_ENABLED` | `1` | Activa el toggle global (default: `0`) |
| `AFFILIATE_STORES` | `wong,metro` | Stores con UTM affiliate activo (comma-sep) |

Para habilitar en Railway: Settings → Environment Variables → añadir ambas variables y re-deploy.

El endpoint `POST /v1/action/affiliate-click` registra el click en DB y devuelve la URL enriquecida con UTM params cuando la store está en `AFFILIATE_STORES`.

## Basket compare — Wave 4 vs legacy

| Modo | Ruta | Data source | TCO | Action links | Envelope |
|------|------|------------|-----|-------------|--------|
| Legacy (live) | `POST /v1/basket/compare` con params por defecto | Live API (`fetch_store`) | ❌ | ❌ | ❌ |
| Wave 4 (DB) | `POST /v1/basket/compare` con `include_tco=true` o `include_action_links=true` | `price_snapshots` DB | ✅ | ✅ | ✅ |

El handler de world detecta los params Wave 4 y delega a `market_core.market_basket.build_basket_compare`.

## CLI — market optimize

```bash
market optimize "leche evaporada, arroz 5kg, azúcar" --country PE
```

Llama a `POST /v1/missions/optimize-purchase`. Requiere `market login` previo.  
Documentación completa: `cli/commands/optimize.py`.

## PyPI pendiente (Task A)

El workflow `publish-core-pypi.yml` (manual dispatch) necesita ejecutarse con `version=1.11.0`.  
Una vez publicado:
1. Actualizar `requirements-railway.txt`: reemplazar pin git → `cli-market-core==1.11.0`
2. Actualizar `ci.yml` y `morning-ops-chain.yml`: idem

**Nota**: El MCP de GitHub en esta sesión no tiene permiso para despachar workflows en `cli-market-core`. Requiere trigger manual desde GitHub Actions UI → `publish-core-pypi.yml` → Run workflow → version: `1.11.0`.
