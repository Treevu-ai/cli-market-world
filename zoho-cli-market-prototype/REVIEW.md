# Review — Zoho CRM + CLI Market Prototype (2026-07-31)

## Scope

- `zoho-cli-market-prototype/` (middleware + clients + enrichment + tests)
- Referencia: `docs/integrations/zoho-cli-market-architecture.md`

## Tests

**46/46 passed** (sin red, sin Zoho real, sin CLI Market real):
- `tests/test_enrichment.py` — 31 tests: lead fields, market score, deal fields, product fields, stock calculation
- `tests/test_middleware.py` — 15 tests: webhook routing (lead/deal/product/delete/unknown), enrichments manuales, market intel, basket

## Decisiones vs. architecture doc

| Tema | Doc original | Implementación |
|------|-------------|----------------|
| Paths intel | `/v1/intel/price_risk`, `/v1/intel/procurement_signal` (con `_`) | Corregido: `/v1/intel/price-risk`, `/v1/intel/procurement-signal` (con `-`) |
| Basket endpoint | `/v1/optimize` (no existe) | Corregido: `/v1/basket/compare` |
| Token management | `get_access_token()` en cada request | Refresh lazy: refresca solo si vence en <60s o recibe 401; reintenta una vez |
| 401 race condition | No documentado | Auto-retry con refresh inmediato si el token expiró entre calls |
| Webhook delete | Doc no lo menciona | Explícitamente ignorado (`no_action_required`) — no enriquecer en delete |
| product.update | Doc incluye esto | Soportado: trigger Products+update → inventory optimization |
| Basket optimize | Endpoint en doc sin inputs | `GET /api/basket-optimize?products=leche,arroz` + 400 si vacío |
| Pro tier errors | Doc no lo considera | Graceful degradation: campos con "unavailable"/"unknown" + mensaje claro |

## Hallazgos

| Severidad | Hallazgo | Acción |
|-----------|----------|--------|
| HIGH | Paths intel con `_` → 404 en prod | Corregido a `-` |
| HIGH | `/v1/optimize` no existe en la API real | Corregido a `/v1/basket/compare` con payload `{items, country, live}` |
| HIGH | Token Zoho vence en 1h; doc hacía `get_access_token()` en cada request (1 extra HTTP call por operación) | Refresh lazy con cache en memoria + auto-retry en 401 |
| MED | Sin manejo de 401 en carrera (token expira entre `get_token` y la request) | Retry automático con refresh inmediato |
| MED | `calculate_recommended_stock` podía devolver valores negativos con inputs extremos | `max(recommended, current_stock)` garantiza ≥ 0 |
| MED | `calculate_market_score` no tenía cap → podía exceder 100 o bajar de 0 | `max(0, min(100, score))` |
| LOW | Doc usaba `scores.get("basket_stress")` directo | Normalizado: soporta tanto `scores["basket_stress"]` como `scores["scores"]["basket_stress"]` |

## Diferencias Zoho vs HubSpot (para el playbook)

| Aspecto | HubSpot | Zoho |
|---------|---------|------|
| Auth | Bearer token (no expira) | OAuth2 refresh_token (token expira en 1h) |
| Webhook payload | Array de eventos | Objeto único por evento |
| Update payload | `{"properties": {...}}` | `{"data": [{...campos..., "id": record_id}]}` |
| CRM objects | Contacts + Deals | Leads + Deals + Products |
| Módulo extra | — | Products (inventario — diferenciador clave) |

## Setup Zoho (antes de usar)

```bash
# 1. Crear Client ID/Secret en https://api-console.zoho.com
#    Tipo: Server-based Application
#    Scopes: ZohoCRM.modules.ALL, ZohoCRM.settings.ALL

# 2. Obtener refresh_token (una vez, flujo auth code):
#    https://accounts.zoho.com/oauth/v2/auth?response_type=code&client_id=...&scope=ZohoCRM.modules.ALL&redirect_uri=...

# 3. Intercambiar code por refresh_token:
#    POST https://accounts.zoho.com/oauth/v2/token (grant_type=authorization_code)

# 4. Configurar .env con CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, API_DOMAIN

# 5. Crear campos custom en Zoho CRM (Setup > Modules > Fields)
#    Leads: Market_Basket_Stress, Market_Inflation_Signal, Market_Price_Fairness,
#           Market_Retail_Aggression, Market_Score, Market_Data_Updated
#    Deals: Price_Risk_Level, Procurement_Signal, Market_Recommended_Action,
#           Price_Intelligence_Updated
#    Products: Market_Price_Risk, Procurement_Signal, Recommended_Stock,
#              Market_Intelligence_Updated

# 6. Crear webhook en Zoho: Setup > Automation > Workflow Rules
#    URL: https://tu-server.com/webhook/zoho
#    Payload: {module, record_id, operation, trigger}
```

## Arranque local

```bash
cd zoho-cli-market-prototype
cp .env.example .env
# Editar .env con CLI_MARKET_API_KEY y credenciales Zoho OAuth2

pip install -r requirements.txt
python -m uvicorn src.zoho_middleware:app --reload --port 8000

# Tests (sin red)
python -m pytest tests/ -v
```

## Qué no se hizo (siguiente iteración)

1. **Deploy en Fly.io** — mismo stack que Simla, puede desplegarse directamente.
2. **Persistencia de access_token** — el token en memoria se pierde al reiniciar. Para producción: cache en Redis o env var dinámica.
3. **Zoho datacenter routing** — la región (US/EU/IN/AU) afecta el `api_domain`; el cliente lo acepta por env var pero no hay lógica de routing automático.
4. **Batch enrichment** — backfill de leads/deals existentes.
5. **Webhook HMAC** — Zoho puede firmar webhooks con HMAC; implementar verificación real.
6. **Zoho Books / Inventory** — el architecture doc menciona integración con la suite; no implementado en este prototipo.

## Relación con otros repos

- Paths y tiers: `cli-market-world/server_deps.py` + `routers/intel.py`
- Arquitectura: `docs/integrations/zoho-cli-market-architecture.md`
- Patrones de referencia: `hubspot-cli-market-prototype/` (mismo stack, mismos endpoints)
