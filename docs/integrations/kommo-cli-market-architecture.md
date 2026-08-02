# Arquitectura Técnica: Kommo CRM + CLI Market (LATAM Sales)

**Versión:** 1.0  
**Fecha:** 2026-07-31  
**Prioridad:** #4 — CRM de ventas conversacionales LATAM (ex-amoCRM)

---

## Objetivo

Integrar inteligencia de mercado de CLI Market en Kommo CRM para equipos de ventas peruanos, permitiendo:

1. **Lead scoring enriquecido** con señales macro de canasta peruana
2. **Campos custom en leads y contactos** con datos de inflación y retail aggression
3. **Señales Pro** (procurement_signal, price_risk) visibles en el pipeline de ventas
4. **Alerta automática** en stage changes: cuando un lead avanza, se re-enriquece

---

## Diferencias críticas vs HubSpot / Zoho

| Aspecto | HubSpot | Zoho | Kommo |
|---------|---------|------|-------|
| Auth | Bearer token (no expira) | OAuth2, token 1h | OAuth2 ó long-lived token |
| Custom fields | Props nombradas (snake_case) | Props CamelCase | IDs enteros — no nombres |
| Webhook format | JSON array | JSON objeto | **x-www-form-urlencoded** |
| Webhook setup | API o UI | Workflow Rules | Settings → Integrations → Webhooks |
| Token rotation | — | refresh_token estable | **refresh_token rota en cada refresh** |
| Setup fields | API idempotente | Manual en UI | API, devuelve field_ids → guardar en .env |

### ⚠️ Custom fields por ID — el paso más importante

Kommo no tiene propiedades nombradas. Para escribir datos de CLI Market hay que:

1. Correr `GET /api/setup-fields` → crea los 8 campos custom en la cuenta Kommo
2. El endpoint devuelve los `field_id` de cada campo creado
3. Copiar esos IDs a las env vars:

```bash
KOMMO_FIELD_BASKET_STRESS=123456
KOMMO_FIELD_INFLATION_SIGNAL=123457
KOMMO_FIELD_PRICE_FAIRNESS=123458
KOMMO_FIELD_RETAIL_AGGRESSION=123459
KOMMO_FIELD_MARKET_SCORE=123460
KOMMO_FIELD_PROCUREMENT=123461
KOMMO_FIELD_PRICE_RISK=123462
KOMMO_FIELD_DATA_UPDATED=123463
```

Sin estas env vars, el middleware detecta que no hay IDs y hace skip del update (sin error — solo un warning en log).

### ⚠️ Webhook payload es form-encoded, no JSON

```
POST /webhook/kommo
Content-Type: application/x-www-form-urlencoded

leads%5Badd%5D%5B0%5D%5Bid%5D=111111&leads%5Badd%5D%5B0%5D%5Bname%5D=Test+Lead
```

El middleware parsea esto con `urllib.parse.parse_qs` y extrae los IDs de leads afectados.

---

## Arquitectura General

```mermaid
graph TB
    A[Kommo CRM] -->|Webhook form-encoded| B[Middleware FastAPI]
    B --> C{CLI Market API}
    C -->|free| D[brief + scores + inflation]
    C -->|Pro| E[procurement-signal + price-risk]
    D & E --> B
    B -->|PATCH /api/v4/leads/{id}| F[Kommo API v4]
    F --> A

    G[/api/setup-fields] -->|POST /api/v4/leads/custom_fields| F
    G -->|retorna field_ids| H[.env]
```

---

## Auth: dos modos

### Modo 1 — Long-lived token (integración privada, recomendado para demos)

```bash
KOMMO_SUBDOMAIN=mi-empresa
KOMMO_LONG_LIVED_TOKEN=tu-long-lived-token
```

Ir a: Kommo → Settings → Integrations → crear integración privada → copiar token.
No vence. Ideal para un solo tenant.

### Modo 2 — OAuth2 (integración pública / multi-tenant)

```bash
KOMMO_SUBDOMAIN=mi-empresa
KOMMO_CLIENT_ID=tu-client-id
KOMMO_CLIENT_SECRET=tu-client-secret
KOMMO_REFRESH_TOKEN=tu-refresh-token
KOMMO_REDIRECT_URI=https://tu-app.fly.dev/oauth/callback
```

**⚠️ El refresh_token de Kommo rota en cada uso.** El middleware guarda el nuevo token en memoria durante la vida del proceso. Para producción persistir el nuevo refresh_token en un secret store o env var.

Token endpoint: `POST https://{subdomain}.kommo.com/oauth2/access_token`

---

## Endpoints del middleware

| Método | Path | Descripción |
|--------|------|-------------|
| `GET` | `/` | Root info |
| `GET` | `/health` | CLI Market + Kommo API |
| `POST` | `/webhook/kommo` | Webhook Kommo (form-encoded) |
| `POST` | `/api/enrich-lead/{id}` | Enriquecimiento manual |
| `POST` | `/api/enrich-lead/{id}?pro=true` | Enriquecimiento + señales Pro |
| `GET` | `/api/setup-fields` | Crear custom fields (1 vez) |
| `GET` | `/api/market-intelligence` | Brief + scores + inflation |
| `GET` | `/api/market-intelligence/pro` | Procurement + price risk |

---

## Campos custom creados en Kommo

| Campo | Tipo | Env var | Contenido |
|-------|------|---------|-----------|
| `CLI_Market_Basket_Stress` | numeric | `KOMMO_FIELD_BASKET_STRESS` | Estrés de canasta 0–1 |
| `CLI_Market_Inflation_Signal` | text | `KOMMO_FIELD_INFLATION_SIGNAL` | Señal shelf (ej: "4.3 pp below CPI") |
| `CLI_Market_Price_Fairness` | numeric | `KOMMO_FIELD_PRICE_FAIRNESS` | Justicia de precios 0–100 |
| `CLI_Market_Retail_Aggression` | numeric | `KOMMO_FIELD_RETAIL_AGGRESSION` | Agresión de retail 0–100 |
| `CLI_Market_Market_Score` | numeric | `KOMMO_FIELD_MARKET_SCORE` | Score compuesto 0–100 |
| `CLI_Market_Procurement` | text | `KOMMO_FIELD_PROCUREMENT` | buy_now / monitor / wait (Pro) |
| `CLI_Market_Price_Risk` | text | `KOMMO_FIELD_PRICE_RISK` | low / moderate / high (Pro) |
| `CLI_Market_Data_Updated` | text | `KOMMO_FIELD_DATA_UPDATED` | ISO timestamp del último update |

---

## Setup quickstart

```bash
# 1. Clonar y configurar
cd cli_market_integrations
cp .env.example .env.kommo
# Editar con KOMMO_SUBDOMAIN + token

# 2. Arrancar middleware local
cli-market-integrate kommo --port 8003

# 3. Crear campos custom en Kommo (UNA VEZ)
curl http://localhost:8003/api/setup-fields
# → copiar los field_ids al .env

# 4. Configurar webhook en Kommo
# Settings → Integrations → Web hooks
# URL: https://tu-server.com/webhook/kommo
# Eventos: lead add, lead update, contact add

# 5. Verificar
curl http://localhost:8003/health
curl http://localhost:8003/api/market-intelligence
```

---

## Pendientes (siguiente iteración)

1. **Persistencia de refresh_token** — en cada refresh Kommo rota el token; hay que persistirlo (env var dinámica, Fly secrets, Redis).
2. **OAuth callback endpoint** — `GET /oauth/callback` para el flujo de auth inicial.
3. **Webhook HMAC** — Kommo no tiene firma nativa por defecto; configurar `KOMMO_WEBHOOK_SECRET` como shared secret en la UI de Kommo.
4. **Stage change trigger** — re-enriquecer al cambiar de stage en el pipeline (útil para señales Pro justo antes de un cierre).
5. **Deploy en Fly.io** — mismo stack que Simla/HubSpot/Zoho (`cli-market-kommo`).

---

## Relación con otros docs

- Arquitectura HubSpot: `docs/integrations/hubspot-cli-market-architecture.md`
- Arquitectura Zoho: `docs/integrations/zoho-cli-market-architecture.md`
- Playbook ejecutivo: `docs/integrations/CRM-PLAYBOOK.md`
- Paquete: `cli_market_integrations/adapters/kommo/`
