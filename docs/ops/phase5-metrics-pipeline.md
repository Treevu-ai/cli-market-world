# Fase 5 — Pipeline de métricas GTM unificado

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase5-metrics-pipeline-f414`

Continúa `docs/ops/phase4-i18n-landing.md`. Cierra el backlog de **regenerar price-pulse** y unifica el sync de métricas para data-brags LinkedIn.

---

## Problema

Tres comandos fragmentados escribían métricas en rutas distintas:

| Script | Escribía | No escribía |
|--------|----------|-------------|
| `sync_linkedin_metrics.py` | `data-gate.md`, Day-07/08/10/14 | price-pulse |
| `monday.py` | price-pulse, reporte semanal | data-gate |
| `daily_briefing.py` | price-pulse (si dashboard OK) | data-gate |

Además:
- `slack_cli campaign status` apuntaba a `docs/linkedin/` (legacy)
- `content_paths` no resolvía al template del monorepo sin repo privado
- Patches solo cubrían era 19K, no 41K
- Tabla «Posts» en `data-gate.md` se corrompía con regex parcial

---

## Completado en esta fase

| # | Tarea | Archivos |
|---|-------|----------|
| 1 | `sync_linkedin_metrics.py` escribe **price-pulse + data-gate + Day-*** en un comando | `ops/sync_linkedin_metrics.py` |
| 2 | Fallback `content_paths` → `tools/content-repo-template/` | `ops/content_paths.py` |
| 3 | `campaign status` usa `content_paths.linkedin_dir()` | `ops/slack_cli.py` |
| 4 | Patches era 41K → cifras live; rebuild tabla Posts en data-gate | `ops/sync_linkedin_metrics.py` |
| 5 | Regenerado snapshot W22 con prod (2026-05-30) | `metrics/price-pulse-2026-W22.md`, `linkedin/data-gate.md`, Day-07/08/10/14 |
| 6 | Tests pipeline | `tests/test_sync_linkedin_metrics.py` |

### Cifras verificadas (prod 2026-05-30)

| Métrica | Valor |
|---------|-------|
| Precios indexados | **43,415** |
| Refresh 24h | **37,731** |
| Tiendas fresh | **35** |
| Coverage 7d | **97.2%** |

Mensaje agregado LinkedIn: **37K+ fresh / 43K+ indexados** (no confundir con product stats canónicos **43,000+** de `marketStats.ts` — redondeo marketing OK).

---

## Comando único (pre-publicar data-brags)

```bash
python3 ops/slack_cli.py campaign sync
# equivalente:
python3 ops/sync_linkedin_metrics.py

python3 ops/slack_cli.py campaign status
python3 ops/generate_all_linkedin_assets.py --patch   # opcional PNG
```

Con repo privado montado:

```bash
export CLI_MARKET_CONTENT_DIR=../cli-market-content
python3 ops/init_content_repo.py --force
python3 ops/slack_cli.py campaign sync
```

---

## Dos sistemas de métricas (sin cambio)

1. **Product stats** — `ops/sync_market_stats.py` → `landing/lib/marketStats.ts` (43K+, 60/30 retailers)
2. **Price-pulse semanal** — snapshot fechado desde `/dashboard/data` (43,415 indexados hoy)

No editar price-pulse a mano salvo notas de marketing/producto.

---

## Verificación

```bash
python3 ops/sync_linkedin_metrics.py --dry-run
python3 ops/slack_cli.py campaign status
pytest tests/test_sync_linkedin_metrics.py -q
rg "41,856|36,935" tools/content-repo-template/linkedin/Day-0[78].md  # debe quedar vacío o solo histórico
```

---

## Pendiente Fase 6+

| Item | Notas |
|------|-------|
| PayPal live + «Agotado» | Panel PayPal Business (externo) |
| Dashboard API `/v1/*` | Intelligence enablers — ver `docs/dashboard-redesign.md` Fase 3 |
| Propagar template → repo privado | `init_content_repo.py --force` local |
| Checkout autónomo | Roadmap Build |
