# Fase 1 — Limpieza de deuda técnica

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase1-debt-cleanup-f414`

Continúa `docs/ops/phase0-mitigation.md`. Objetivo: reducir deuda sin romper imports ni CI.

---

## Completado en esta fase

| # | Tarea | Resultado |
|---|-------|-----------|
| 1 | Componentes landing huérfanos | Eliminados 11 archivos (~985 líneas) superseded por `ScaleCoverageSection`, `UseCasesSection`, etc. |
| 2 | Template content 13K → 43K | `tools/content-repo-template/` — Day-03/06/07, GTM-Hub, content/reddit strategy |
| 3 | Doc SQLite/Postgres | `docs/ops/database-migration.md` |
| 4 | Split billing | `market_billing.py` — subscriptions, Pro requests, payment migrations; re-export en `market_core` |

---

## Archivos eliminados (landing)

`AnimatedSphere`, `AgentDispatch`, `CoverageSection`, `DataSection`, `Features`, `FinalCTA`, `Lines`, `QualitySection`, `StatsSection`, `TerminalSection`, `UseCases`

---

## `market_billing.py`

Extraído de `market_core.py`:

- `TIERS`, `_migrate_payment_schema`
- `db_get/set_subscription`, order gateway helpers
- `db_*billing*`, `db_*subscription_request*`
- `user_can_checkout`

**Compatibilidad:** todo sigue importable desde `market_core` (re-export). Nuevo código puede usar `from market_billing import ...`.

---

## Pendiente Fase 2

| Item | Notas |
|------|-------|
| PayPal «Agotado» | Fix en panel PayPal Business (inventario ilimitado); landing ya tiene CTA link verde |
| `market_db.py` split | Extraer `_DB`, `init_db_pg`, `_SQLITE_DDL` — mayor riesgo |
| Sync content repo privado | `CLI_MARKET_CONTENT_DIR=../cli-market-content` + `campaign sync` tras merge template |
| Checkout autónomo | Roadmap Build — no prometer en copy comercial |

---

## Verificación

```bash
cd landing && npm run build
MARKET_DATA_DIR=/tmp/market-test-data pytest tests/ -q -m "not integration"
python3 -c "from market_core import TIERS, db_get_subscription; from market_billing import user_can_checkout; print('ok')"
```
