# CRM Integration Playbook — CLI Market

**Versión:** 1.0 | **Fecha:** 2026-07-31 | **Mantenido en:** `docs/integrations/`

---

## Overview

CLI Market expone inteligencia de góndola peruana (precios, inflación de estantería, señales de procurement) directamente dentro de los CRMs de los clientes. Hay 4 adaptadores listos para producción:

| # | CRM | ICP | Deploy | Puerto default |
|---|-----|-----|--------|----------------|
| 1 | **Simla.com** | Vendedores por WhatsApp | `cli-market-simla.fly.dev` | 8000 |
| 2 | **HubSpot** | PYMEs con equipo de ventas | `cli-market-hubspot.fly.dev` | 8001 |
| 3 | **Zoho CRM** | PYMEs sensibles al precio | `cli-market-zoho.fly.dev` | 8002 |
| 4 | **Kommo** | Sales conversacional LATAM | (pending deploy) | 8003 |

> **⚠️ Drift conocido — Simla:** `cli-market-simla.fly.dev` corre hoy desde
> `simla-cli-market-prototype/` (su propio `fly.toml`/Dockerfile), **no**
> desde `cli_market_integrations/adapters/simla/`. HubSpot y Zoho sí están
> desplegados desde el paquete unificado (ver sección Deploy más abajo). Si
> cambiás lógica de enriquecimiento de Simla, editá
> `simla-cli-market-prototype/src/` — tocar `cli_market_integrations/adapters/simla/`
> no tiene efecto en producción hasta que se migre ese deploy. Verificado
> 2026-08-02 comparando `fly.hubspot.toml`/`fly.zoho.toml` (apuntan a
> `cli_market_integrations/adapters/*/Dockerfile`) contra
> `simla-cli-market-prototype/fly.toml` (su propio Dockerfile, app
> `cli-market-simla`).

---

## Instalación (30 minutos por CRM)

```bash
pip install cli-market-integrations[serve]

# Local — arrancar cualquier adapter:
cli-market-integrate simla   --reload
cli-market-integrate hubspot --reload
cli-market-integrate zoho    --reload
cli-market-integrate kommo   --reload

cli-market-integrate --list   # ver todos los adapters disponibles
```

---

## Variables de entorno por CRM

### Comunes a todos

```bash
CLI_MARKET_API_KEY=sk-...          # requerido
CLI_MARKET_API_URL=https://cli-market-api.fly.dev
CLI_MARKET_TIMEOUT=30
```

### Simla.com

```bash
SIMLA_API_KEY=...                  # opcional — sin key = dry-run (no envía WA)
SIMLA_API_URL=https://TU-TENANT.simla.com
SIMLA_WEBHOOK_SECRET=...           # opcional — shared secret para auth
```

### HubSpot

```bash
HUBSPOT_ACCESS_TOKEN=pat-na1-...   # Private App token (NO API key legacy)
HUBSPOT_WEBHOOK_SECRET=...         # opcional
```

### Zoho CRM

```bash
ZOHO_CLIENT_ID=...
ZOHO_CLIENT_SECRET=...
ZOHO_REFRESH_TOKEN=...
ZOHO_API_DOMAIN=https://www.zohoapis.com   # .eu | .in | .com.au según datacenter
ZOHO_WEBHOOK_SECRET=...
```

### Kommo (ex-amoCRM)

```bash
KOMMO_SUBDOMAIN=tu-empresa         # requerido — de tu URL kommo.com
# Opción A — long-lived token (privado, recomendado):
KOMMO_LONG_LIVED_TOKEN=...
# Opción B — OAuth2 (público/multi-tenant):
KOMMO_CLIENT_ID=...
KOMMO_CLIENT_SECRET=...
KOMMO_REFRESH_TOKEN=...
KOMMO_REDIRECT_URI=https://tu-app.fly.dev/oauth/callback

# IDs de campos custom (obtener corriendo /api/setup-fields una vez):
KOMMO_FIELD_BASKET_STRESS=...
KOMMO_FIELD_INFLATION_SIGNAL=...
KOMMO_FIELD_PRICE_FAIRNESS=...
KOMMO_FIELD_RETAIL_AGGRESSION=...
KOMMO_FIELD_MARKET_SCORE=...
KOMMO_FIELD_PROCUREMENT=...
KOMMO_FIELD_PRICE_RISK=...
KOMMO_FIELD_DATA_UPDATED=...
```

---

## Tabla comparativa de capacidades

| Capacidad | Simla | HubSpot | Zoho | Kommo |
|-----------|-------|---------|------|-------|
| Búsqueda de precios en WhatsApp | ✅ | — | — | — |
| Comparación por retailer en WhatsApp | ✅ | — | — | — |
| Optimización de canasta | ✅ | — | ✅ | — |
| Lead/Contact enrichment (free) | — | ✅ | ✅ | ✅ |
| Deal enrichment | — | ✅ | ✅ | ✅ |
| Inventory optimization | — | — | ✅ | — |
| Señales Pro (procurement + price risk) | — | ✅ | ✅ | ✅ |
| Lead score delta | — | ✅ | ✅ (market score) | ✅ (market score) |
| Setup de campos/props | Auto via API | Auto via API | Manual en UI | Auto via API → guardar IDs |

---

## Endpoints por adapter

### Simla

| Endpoint | Descripción |
|----------|-------------|
| `POST /webhook/whatsapp` | Recibe mensajes de WhatsApp desde Simla |
| `GET /api/test-intent?message=...` | Test de intent detection sin red |
| `GET /api/test-search?query=leche` | Busca precios live |
| `GET /api/test-compare?product=leche` | Compara precios entre retailers |
| `GET /api/test-optimize?products=leche,arroz` | Optimiza canasta |
| `GET /health` | Status |

### HubSpot

| Endpoint | Descripción |
|----------|-------------|
| `POST /webhook/hubspot` | Webhook (array de eventos JSON) |
| `POST /api/enrich-contact/{id}` | Enriquecimiento manual de contacto |
| `POST /api/enrich-deal/{id}` | Enriquecimiento manual de deal |
| `GET /api/market-intelligence` | Brief + scores + inflation (free) |
| `GET /api/market-intelligence/pro-signals` | Procurement + price risk (Pro) |
| `GET /api/setup-properties` | Crea custom properties (idempotente) |

### Zoho

| Endpoint | Descripción |
|----------|-------------|
| `POST /webhook/zoho` | Webhook (objeto JSON por evento) |
| `POST /api/enrich-lead/{id}` | Enriquecimiento manual de lead |
| `POST /api/enrich-deal/{id}` | Enriquecimiento manual de deal |
| `POST /api/optimize-inventory/{id}` | Optimización de stock de producto |
| `GET /api/market-intelligence` | Brief + scores + inflation |
| `GET /api/market-intelligence/pro` | Procurement + price risk (Pro) |
| `GET /api/basket-optimize?products=...` | Optimización de canasta |

### Kommo

| Endpoint | Descripción |
|----------|-------------|
| `POST /webhook/kommo` | Webhook (x-www-form-urlencoded) |
| `POST /api/enrich-lead/{id}` | Enriquecimiento manual |
| `POST /api/enrich-lead/{id}?pro=true` | Enriquecimiento + señales Pro |
| `GET /api/setup-fields` | Crear custom fields (1 vez) |
| `GET /api/market-intelligence` | Brief + scores + inflation |
| `GET /api/market-intelligence/pro` | Procurement + price risk |

---

## Tier de CLI Market requerido

| Endpoint | Tier |
|----------|------|
| `/v1/intel/brief` | Starter+ |
| `/v1/intel/scores` | Starter+ |
| `/v1/intel/inflation` | Starter+ |
| `/v1/intel/macro` | Starter+ |
| `/products/search` | Starter+ |
| `/products/compare` | Starter+ |
| `/v1/intel/procurement-signal` | **Pro** |
| `/v1/intel/price-risk` | **Pro** |
| `/v1/basket/compare` | **Pro+** |

Todos los adapters manejan gracefully el tier insuficiente: escriben "unavailable"/"unknown" en el campo CRM en lugar de fallar.

---

## Deploy en Fly.io

### Simla (ya deployado)

```bash
fly status --app cli-market-simla
curl https://cli-market-simla.fly.dev/health
```

### HubSpot / Zoho

```bash
# Secrets (una vez):
fly secrets set CLI_MARKET_API_KEY=sk-... --app cli-market-hubspot
fly secrets set HUBSPOT_ACCESS_TOKEN=pat-... --app cli-market-hubspot

fly secrets set CLI_MARKET_API_KEY=sk-... --app cli-market-zoho
fly secrets set ZOHO_CLIENT_ID=... ZOHO_CLIENT_SECRET=... ZOHO_REFRESH_TOKEN=... --app cli-market-zoho

# Deploy:
fly deploy --app cli-market-hubspot --config cli_market_integrations/adapters/hubspot/fly.toml
fly deploy --app cli-market-zoho    --config cli_market_integrations/adapters/zoho/fly.toml
```

### Kommo (pending)

```bash
fly apps create cli-market-kommo
fly secrets set CLI_MARKET_API_KEY=sk-... KOMMO_SUBDOMAIN=... KOMMO_LONG_LIVED_TOKEN=... --app cli-market-kommo
fly deploy --app cli-market-kommo --config cli_market_integrations/adapters/kommo/fly.toml
```

---

## Onboarding checklist por CRM

### Simla

- [ ] `SIMLA_API_URL` apunta al tenant real (no `simla.com` genérico)
- [ ] `CLI_MARKET_API_KEY` seteada en Fly secrets
- [ ] URL del webhook configurada en panel de Simla: `https://cli-market-simla.fly.dev/webhook/whatsapp`
- [ ] Test: `GET /api/test-intent?message=cuanto+cuesta+la+leche` → `detected: true`

### HubSpot

- [ ] Private App creada (scopes: contacts.read/write, deals.read/write, schemas.write)
- [ ] `GET /api/setup-properties` ejecutado (crea propiedades custom)
- [ ] Webhook configurado en HubSpot → Events: contact.creation, deal.creation
- [ ] Test: `POST /api/enrich-contact/{id}` con un contacto real

### Zoho

- [ ] OAuth2 configurado (client_id/secret/refresh_token/api_domain)
- [ ] Campos custom creados manualmente en Zoho UI (ver arquitectura doc)
- [ ] Webhook configurado en Setup → Automation → Workflow Rules
- [ ] Test: `POST /api/enrich-lead/{id}` con un lead real

### Kommo

- [ ] Long-lived token ó OAuth2 configurado
- [ ] `GET /api/setup-fields` ejecutado → anotar field_ids → agregar a .env/secrets
- [ ] Webhook configurado en Settings → Integrations → Web hooks
- [ ] Test: `GET /health` → `kommo_api: true`
- [ ] Test: `POST /api/enrich-lead/{id}?pro=true` con lead real

---

## Documentación por CRM

- [Simla](simla-cli-market-architecture.md)
- [HubSpot](hubspot-cli-market-architecture.md)
- [Zoho](zoho-cli-market-architecture.md)
- [Kommo](kommo-cli-market-architecture.md)
- [Guía de implementación y monitoreo](implementation-monitoring-guide.md)

---

## Paquete

```
cli_market_integrations/
├── shared/
│   ├── intel_client.py      CLIMarketIntelClient (HubSpot + Zoho + Kommo)
│   └── enrichment.py        Helpers comunes + build_deal_pro_fields
├── adapters/
│   ├── simla/               WhatsApp via Simla.com — NO es lo desplegado en
│   │                        cli-market-simla.fly.dev hoy (ver aviso arriba)
│   ├── hubspot/             HubSpot CRM — esto sí es lo desplegado
│   ├── zoho/                Zoho CRM + Inventory — esto sí es lo desplegado
│   └── kommo/               Kommo (ex-amoCRM)
├── cli.py                   cli-market-integrate entry point
└── tests/                   87 tests, 87 passing
```
