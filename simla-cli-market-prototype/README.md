# Prototipo Simla.com + CLI Market

Middleware FastAPI que detecta intención de precios en WhatsApp (vía Simla.com) y responde con inteligencia de góndola de CLI Market.

**Estado:** prototipo local (2026-07-31). No es un deploy de producción en Fly.io del monorepo principal.

## Qué hace

1. Recibe webhook `POST /webhook/whatsapp` (payload Simla-like).
2. Detecta intención: search / compare / optimize / history / alert.
3. Llama a la **API real** de CLI Market:
   - `POST /products/search`
   - `POST /products/compare`
   - `POST /v1/basket/compare` (Pro+)
   - `GET /analytics/price-history`
4. Formatea respuesta para WhatsApp y la reenvía a Simla (o dry-run si no hay key).

## Setup

```bash
cd simla-cli-market-prototype
cp .env.example .env
# Editar .env con CLI_MARKET_API_KEY (y SIMLA_* si vas a enviar WA)

python setup.py
# o: pip install -r requirements.txt

python -m uvicorn src.simla_middleware:app --reload --host 0.0.0.0 --port 8000
```

- Health: http://localhost:8000/health  
- OpenAPI: http://localhost:8000/docs  

## Variables de entorno

Ver [`.env.example`](.env.example). **Nunca** commits de `.env`.

| Variable | Rol |
|----------|-----|
| `CLI_MARKET_API_KEY` | Bearer de CLI Market (`sk-…`) |
| `CLI_MARKET_API_URL` | Default `https://cli-market-api.fly.dev` |
| `SIMLA_API_KEY` | Tenant Simla (opcional → dry-run de envío) |
| `SIMLA_API_URL` | URL del tenant (no el marketing site genérico) |
| `SIMLA_WEBHOOK_SECRET` | Si se setea, exige header `X-Webhook-Secret` |

## Pruebas rápidas

```bash
# Intent (sin red)
curl -s -X POST http://localhost:8000/api/test-intent \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"¿Cuánto cuesta la leche?\"}"

# Search live (requiere CLI_MARKET_API_KEY)
curl -s "http://localhost:8000/api/test-search?query=leche&country=PE"

# Demo CLI
python demo_simple.py

# Unit tests intent
python -m pytest tests/ -q
```

## Estructura

```
simla-cli-market-prototype/
├── src/
│   ├── cli_market_client.py   # API CLI Market (contratos reales)
│   ├── simla_client.py        # Envío WhatsApp Simla
│   ├── intent_detector.py     # Keywords ES → intent
│   ├── whatsapp_formatter.py  # Copy WhatsApp
│   └── simla_middleware.py    # FastAPI app
├── tests/
├── docs hermanos: ../docs/integrations/
├── .env.example
└── README.md
```

## Docs de arquitectura (repo)

- [Simla](../docs/integrations/simla-cli-market-architecture.md)
- [HubSpot](../docs/integrations/hubspot-cli-market-architecture.md)
- [Zoho](../docs/integrations/zoho-cli-market-architecture.md)
- [Implementación y monitoreo](../docs/integrations/implementation-monitoring-guide.md)

## Limitaciones conocidas (revisión 2026-07-31)

| Tema | Detalle |
|------|---------|
| Simla paths | Dependen del tenant; el client usa paths configurables y dry-run sin key |
| Basket | `/v1/basket/compare` exige tier Pro en prod |
| Alertas | Solo confirma en copy; no hay backend persistente de alertas |
| Webhook auth | Opcional vía `SIMLA_WEBHOOK_SECRET`; firmar según contrato Simla real |
| NLP | Keywords regex, no LLM |
| Seguridad | Rotar cualquier key que haya estado en README/chat |

## Relación con bots nativos del monorepo

CLI Market ya tiene bridges nativos Twilio WhatsApp + Telegram en:

- `routers/integrations/whatsapp.py`
- `routers/integrations/telegram.py`

Este prototipo es la vía **Simla CRM** (middleware externo), no reemplaza esos routers.
