# Review — Simla / CRM integrations (2026-07-31)

## Scope revisado

- `simla-cli-market-prototype/` (middleware + client + demos)
- `docs/integrations/` (Simla, HubSpot, Zoho, guía de implementación)

## Hallazgos y fixes aplicados antes de subir a cloud

| Severidad | Hallazgo | Acción |
|-----------|----------|--------|
| CRITICAL | API keys reales en `README.md` y `.env` | Sacadas del README; `.env` gitignored; solo `.env.example` |
| HIGH | Cliente usaba `/v1/search`, `/v1/compare`, `/v1/optimize` (404 en prod) | Alineado a `/products/search`, `/products/compare`, `/v1/basket/compare`, `/analytics/price-history` |
| HIGH | Fallback mock de precios Gloria en error HTTP | Eliminado — no inventar precios |
| MED | Estructura rota (`setup` pedía `src/*` pero código en root) | Código en `src/`, imports `src.*` |
| MED | `format_history_result` llamaba `_format_error` inexistente | Corregido a `format_error` |
| MED | Webhook sin auth | Gate opcional `SIMLA_WEBHOOK_SECRET` |
| LOW | Logs y `__pycache__` | `.gitignore` local del prototipo |
| LOW | Tests ausentes | `tests/test_intent_detector.py` |

## Qué no se hizo (siguiente iteración)

1. Validar contrato real del tenant Simla (paths WhatsApp outbound).
2. Deploy del middleware (Fly/Railway) separado de `cli-market-api`.
3. Firmar webhooks según esquema oficial Simla (si no es shared secret).
4. Persistencia de alertas de precio.
5. Unificar con `routers/integrations/whatsapp.py` (Twilio nativo) si el ICP es solo WhatsApp sin CRM.

## Rotación de secretos

Si las keys del prototipo circularon en README o chat, rotar:

1. CLI Market: emitir nueva `sk-` y revocar la anterior.
2. Simla: regenerar API key del tenant.
