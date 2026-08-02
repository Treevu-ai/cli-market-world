# Review — HubSpot + CLI Market Prototype (2026-07-31)

## Scope

- `hubspot-cli-market-prototype/` (middleware + clients + enrichment + tests)
- Alineado con `docs/integrations/hubspot-cli-market-architecture.md`

## Tests

**27/27 passed** (sin red, sin HubSpot real):
- `tests/test_enrichment.py` — 18 tests: contact props, deal props, lead score delta
- `tests/test_middleware.py` — 9 tests: webhook routing, enrichment manual, health, market-intelligence

## Decisiones vs. architecture doc

| Tema | Doc original | Implementación |
|------|-------------|----------------|
| HubSpot SDK | `hubspot-api-client` (SDK pesado) | `httpx` directo a HubSpot API v3 — mismo patrón que el resto del stack |
| Auth HubSpot | `api_key` (deprecado) | `HUBSPOT_ACCESS_TOKEN` (Private App token — método actual) |
| Endpoints intel | `price_risk`, `procurement_signal` (con `_`) | Paths reales: `/v1/intel/price-risk`, `/v1/intel/procurement-signal` (con `-`) |
| Tier gating | No documentado en arquitectura | Manejado explícitamente: errores 403 → valores degradados, no excepción |
| Webhook payload | Un objeto JSON | Array de eventos (comportamiento real de HubSpot) |
| Loop infinito | No documentado | Filtro: skip si `propertyName` empieza con `market_` o es prop propia |

## Hallazgos

| Severidad | Hallazgo | Acción |
|-----------|----------|--------|
| HIGH | Endpoints intel en doc usan `_` en vez de `-` (habrían dado 404) | Corregido: `/v1/intel/price-risk`, `/v1/intel/procurement-signal` |
| HIGH | HubSpot API Keys deprecadas, doc usaba `api_key` | Cambiado a `HUBSPOT_ACCESS_TOKEN` (Private App) |
| HIGH | Webhook de HubSpot envía array, no objeto único | Middleware acepta `list[HubSpotWebhookEvent]` |
| MED | Sin filtro de loop: enriquecer contacto → HubSpot notifica → re-encola infinito | Skip si `propertyName` es una prop propia (`market_*`) |
| MED | Endpoints Pro (procurement-signal, price-risk) lanzarían excepción en tier free | Manejo graceful: `{"error": "tier_insufficient"}` → props degradadas con aviso |
| LOW | `enrichment.py` separado del middleware | Facilita testear lógica de negocio sin levantar FastAPI |

## Setup HubSpot (antes de usar)

```bash
# 1. Crear Private App en HubSpot (Settings > Integrations > Private Apps)
#    Scopes: crm.objects.contacts.read/write, crm.objects.deals.read/write
#            crm.schemas.contacts.write, crm.schemas.deals.write

# 2. Copiar el Access Token al .env
HUBSPOT_ACCESS_TOKEN=pat-na1-...

# 3. Crear custom properties en HubSpot (idempotente)
curl http://localhost:8000/api/setup-properties

# 4. Configurar webhook en HubSpot > Settings > Webhooks
#    URL: https://tu-server.com/webhook/hubspot
#    Eventos: contact.creation, contact.propertyChange, deal.creation, deal.propertyChange
```

## Arranque local

```bash
cd hubspot-cli-market-prototype
cp .env.example .env
# Editar .env con CLI_MARKET_API_KEY y HUBSPOT_ACCESS_TOKEN

pip install -r requirements.txt
python -m uvicorn src.hubspot_middleware:app --reload --port 8000

# Tests (sin red)
python -m pytest tests/ -v
```

## Qué no se hizo (siguiente iteración)

1. **Deploy en Fly.io** — el prototipo es local; puede desplegarse igual que `cli-market-simla` (mismo stack).
2. **HMAC de webhook** — HubSpot firma con SHA-256 + client secret, no shared secret. Implementar verificación real antes de producción.
3. **Batch enrichment** — para backfill de contactos existentes: endpoint `POST /api/enrich-batch` con lista de IDs.
4. **Persistencia de métricas** — el código de Prometheus del architecture doc no está implementado (prototipo sin estado).
5. **Retry / dead-letter** — los background tasks de FastAPI no reintentan. Para producción: celery/arq o Fly.io cron.
6. **Validar scores reales** — los field names de `/v1/intel/scores` (`retail_aggression`, etc.) asumen la forma actual del response; confirmar contra API real con key Pro.

## Relación con otros repos

- Lógica de intel: `cli-market-world/routers/intel.py` (fuente de verdad de paths y tiers)
- Tier gating: `cli-market-world/server_deps.py` (`_CORE_V1_TIER_ROUTES`)
- Arquitectura: `docs/integrations/hubspot-cli-market-architecture.md`
