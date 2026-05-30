# Fase 6 — Intelligence API `/v1/*`

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase6-intelligence-api-f414`

Continúa `docs/ops/phase5-metrics-pipeline.md`. Implementa endpoints granulares del dashboard (Fase 3 en `docs/dashboard-redesign.md`) para equipos Intelligence.

---

## Completado

| Ticket | Endpoint | Módulo |
|--------|----------|--------|
| 3.1 ✅ (previo) | `GET /v1/sources/health` | `routers/health.py` |
| 3.2 | `GET /v1/quality/flagged` | `routers/data_v1.py` |
| 3.3 | `GET /v1/prices?clean=1` | `routers/data_v1.py` |
| 3.4 | `GET /v1/dispersion?clean=1` | `routers/data_v1.py` |
| 3.5 | `GET /v1/basket` | `routers/data_v1.py` + `market_basket.py` |
| 3.5b | `POST /v1/basket/compare` → `"source": "live"` | `routers/search.py` |
| 3.6 | `GET /v1/coverage/matrix` | `routers/data_v1.py` |
| 3.7 | `dashboard_view.blocks.portada.acceso` + spec `1.2` | `dashboard_view_model.py` |

Lógica compartida: `data_v1_service.py` · canasta extraída de dashboard → `market_basket.py`.

---

## Contratos rápidos

```bash
export BASE=https://cli-market-production.up.railway.app

curl -s $BASE/v1/quality/flagged?limit=5 | jq '.total,.items[0].reason'
curl -s '$BASE/v1/prices?clean=1&country=PE&limit=5' | jq '.total'
curl -s '$BASE/v1/dispersion?clean=1&limit=5' | jq '.items[0].status'
curl -s $BASE/v1/basket | jq '.source,.stores[0]'
curl -s $BASE/v1/coverage/matrix | jq '.gaps[:3]'
```

### Snapshot vs live

| Endpoint | Fuente |
|----------|--------|
| `GET /v1/basket` | Snapshots DB (`source: snapshot`) |
| `POST /v1/basket/compare` | Live scrape VTEX (`source: live`) |

---

## Calidad / flagged

- `reason=discount` — SQL `discount_pct >= 90`
- `reason=outlier` — `find_median_outliers` (banda ±5x)
- `reason=spread` — grupos dispersion `status=crit` (>10x)
- `count_flagged_outliers()` en dashboard usa conteo DB completo (no muestra cap 10)

---

## Verificación

```bash
pytest tests/test_data_v1.py tests/test_sources_health.py -q
pytest tests/test_dashboard_view_model.py -q
MARKET_DATA_DIR=/tmp/m pytest tests/test_regression.py -q -k dashboard
```

---

## Pendiente Fase 7+

Ver `docs/ops/phase7-performance-confidence-billing.md`:

| Item | Estado |
|------|--------|
| PayPal live + «Agotado» | Runbook ops (externo) |
| Propagar content template → repo privado | ✅ `ops/sync_content_template.py` |
| Índices SQL para `/v1/prices` | ✅ Fase 7 |
| `confidence` persistida en DB | ✅ Fase 7 + `ops/backfill_confidence.py` |
| Checkout autónomo | Roadmap Fase 8 |
