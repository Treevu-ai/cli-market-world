# Fase 7 — Performance, confidence DB y billing ops

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase7-performance-confidence-f414`

Continúa `docs/ops/phase6-intelligence-api.md`. Cierra el backlog de **confidence persistida**, **índices `/v1/prices`**, **sync template → repo privado** y runbook **PayPal live**.

---

## Problema

| Área | Síntoma |
|------|---------|
| `/v1/prices?clean=1` | Carga **toda** la tabla en memoria para filtrar outliers en cada request |
| Dashboard | `confidence` calculada en SQL ad hoc (`'suspect' as confidence`), no persistida |
| Content GTM | `init_content_repo.py --force` sobrescribe todo; no hay sync incremental post-F5 |
| Billing | PayPal Hosted Button puede mostrar **Agotado**; activación Pro sigue manual |

---

## Completado en esta fase

| # | Tarea | Archivos |
|---|-------|----------|
| 7.1 | Columna `price_snapshots.confidence` (`ok` / `suspect`) | `market_db.py`, migración `_migrate_price_snapshots_v7` |
| 7.2 | Confidence en ingest (collector + `save_price_snapshot`) | `market_core.py`, `collect_prices.py`, `price_confidence.py` |
| 7.3 | Backfill batch (discount + median outliers) | `ops/backfill_confidence.py` |
| 7.4 | `/v1/prices?clean=1` usa `confidence='ok'` + paginación SQL | `data_v1_service.py` |
| 7.5 | Índices compuestos query `/v1/prices` | `idx_ps_store_line_queried`, `idx_ps_line_currency`, `idx_ps_confidence` |
| 7.6 | Sync incremental template → content repo | `ops/sync_content_template.py` |
| 7.7 | Tests | `tests/test_price_confidence.py`, `tests/test_data_v1.py`, `tests/test_sync_content_template.py`, `tests/test_market_basket.py` ✅ todos merged |

### Valores `confidence`

| Valor | Origen |
|-------|--------|
| `ok` | Precio dentro de reglas publicables |
| `suspect` | `discount_pct >= 90` o outlier ±5× mediana del grupo |

`crit` queda en dispersion/spread (nivel subcategoría), no fila individual.

---

## Deploy producción (Railway)

```bash
# 1. Merge PR → redeploy API (migración automática en ensure_db_initialized)
# 2. Backfill una vez contra prod (local):
pip install psycopg2-binary
export DATABASE_URL='postgresql://...'   # Railway → Postgres → Connect (no commitear)
python3 ops/backfill_confidence.py

# 3. Verificar
curl -s '$BASE/v1/prices?clean=1&country=MX&limit=5' | jq '.total, .items[0].confidence'
curl -s '$BASE/v1/quality/flagged?limit=3' | jq '.total'
```

Tras backfill, `/v1/prices?clean=1` deja de escanear 43K filas en Python por request.

---

## Content repo — sync incremental

```bash
export CLI_MARKET_CONTENT_DIR=/home/acuba/Proyectos/cli-market-content

# Sync métricas + data-gate sin tocar Day-*.md ni PNG
python3 ops/sync_content_template.py --only metrics,linkedin/data-gate.md

# Sync completo (preserva assets/ y Day-*.md)
python3 ops/sync_content_template.py

# Forzar refresh de posts desde template
python3 ops/sync_content_template.py --force-days

python3 ops/generate_all_linkedin_assets.py --patch
python3 ops/slack_cli.py campaign sync
```

Push al repo privado:

```bash
cd $CLI_MARKET_CONTENT_DIR
git add -A && git commit -m "sync template Fase 7" && git push
```

Ver también `docs/CONTENT.md`.

---

## PayPal live + «Agotado» (externo — checklist)

No requiere código; acciones en PayPal Business + Railway env:

| Paso | Acción |
|------|--------|
| 1 | PayPal Business → **Payment links & buttons** → botón `B6YVFTG4MA73J` |
| 2 | Inventario **ilimitado** o stock > 0 (evita «Sold out / Agotado») |
| 3 | Railway: `PRO_PAYMENT_URL=https://www.paypal.com/ncp/payment/B6YVFTG4MA73J` |
| 4 | Probar: `curl -X POST $BASE/billing/request-pro -d '{"email":"test@example.com"}'` |
| 5 | Tras pago: `python3 ops/activate_pro.py USERNAME --email cliente@email.com` (≤24 h hábiles) |

Documentación: `ops/BILLING_MANUAL.md`, `ops/E2E_CLIENT_JOURNEY.md`, sandbox opcional `ops/PAYPAL_SANDBOX.md`.

---

## Verificación CI

```bash
pytest tests/test_price_confidence.py tests/test_data_v1.py tests/test_sync_content_template.py tests/test_market_basket.py -q
pytest tests/test_regression.py -q -k "dashboard or prices"
ruff check .
```

---

## Pendiente Fase 8+

| Item | Notas |
|------|-------|
| Checkout autónomo PayPal REST | `/billing/paypal` + `/checkout/paypal-webhook` — código + tests en prod; go-live: `docs/ops/GO-LIVE-CHECKOUT.md` |
| `inventory_daily[]` | Dashboard Fase 4 — serie temporal |
| Gráfica inflación por tienda | Requiere 2ª captura histórica |
| Cron post-collector | `backfill_confidence.py` tras cada run collector |
| Materialized view outliers | Si backfill no basta a escala 100K+ |
