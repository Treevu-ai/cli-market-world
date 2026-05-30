# Database — SQLite vs PostgreSQL

**Fecha:** 2026-05-30 · **Owner:** `market_core.py` + `market_billing.py`

Guía para desarrollo local, CI, producción (Railway) y migraciones idempotentes.

---

## Matriz de entornos

| Entorno | `DATABASE_URL` | Backend | Archivo / host |
|---------|----------------|---------|----------------|
| Dev local | vacío o unset | SQLite | `{MARKET_DATA_DIR}/market.db` |
| pytest / CI | `""` (forzado en `tests/conftest.py`) | SQLite | `/tmp` o `MARKET_DATA_DIR` |
| Railway prod | `${{Postgres.DATABASE_URL}}` | PostgreSQL | Managed Postgres |
| Fallback runtime | PG unreachable | SQLite | Mismo path local tras log warning |

Selección en `market_core.py`:

```python
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_PG = bool(DATABASE_URL) and _pg_host_reachable(DATABASE_URL)
```

Si PostgreSQL falla al iniciar, `ensure_db_initialized()` reasigna `USE_PG = False` y reintenta con SQLite.

---

## Fuente única de DDL

**Regla:** solo `market_core.init_db()` / `ensure_db_initialized()` crean tablas.

| Módulo | Rol |
|--------|-----|
| `market_core.py` | DDL base (`init_db_pg`, `_SQLITE_DDL`), usuarios, carrito, órdenes, snapshots |
| `market_billing.py` | Migraciones billing (`subscription_requests`, `billing_pending`, columnas PayPal) |
| `store_credentials.py` | Runtime credentials (no DDL duplicado en collector) |
| `collect_prices.py` | **No define DDL** — llama `ensure_db_initialized()` antes de escribir |

Violación detectada en CI: `tests/test_regression.py` valida single-source-of-truth.

---

## Inicialización

Cada entrypoint debe llamar `ensure_db_initialized()` antes de operaciones DB:

- `market_server.py` — lifespan startup
- `collect_prices.py` — `main()`
- Tests — `conftest.py` / fixtures
- Ops scripts — `ops/activate_pro.py`, `ops/approve_retailer.py`

`ensure_db_initialized()` es idempotente y aplica `_migrate_payment_schema()` en cada arranque (deploys incrementales).

---

## Migraciones idempotentes

| Función | Tablas / columnas |
|---------|-------------------|
| `_migrate_payment_schema` | `subscription_requests`, `billing_pending`, `app_orders.gateway_ref`, `subscriptions.paypal_subscription_id` |
| `_migrate_store_credentials` | `store_credentials`, columnas review en `retailer_applications` |
| `_migrate_price_snapshots_pg` | Índice UNIQUE upsert en PG para `price_snapshots` |

Todas usan `CREATE IF NOT EXISTS` / `ALTER ADD COLUMN IF NOT EXISTS` (PG) o try/except (SQLite legacy).

---

## Migración legacy JSON → SQLite

`db_migrate_from_json()` (en `market_core`) importa datos históricos JSON al primer arranque del server. Solo aplica si existen archivos legacy; idempotente.

---

## Verificación

### Local / CI

```bash
MARKET_DATA_DIR=/tmp/market-test-data pytest tests/ -q -m "not integration"
```

### Producción (API)

```bash
curl -s https://cli-market-production.up.railway.app/health/db | jq
```

Respuesta esperada en prod:

- `backend`: `"postgresql"`
- `tables`: incluye `price_snapshots`, `subscriptions`, `subscription_requests`, `store_credentials`
- `price_snapshots_upsert_ready`: `true` (PG)

### Collector

```bash
curl -s https://cli-market-production.up.railway.app/health/collector | jq
```

---

## Pasar de SQLite local a Postgres (Railway)

1. Provisionar Postgres en Railway; enlazar `DATABASE_URL` al servicio API.
2. Redeploy — `ensure_db_initialized()` crea schema en PG vacío.
3. **Datos:** no hay migración automática SQLite→PG hoy. Opciones:
   - Arrancar PG limpio (collector repuebla snapshots en horas)
   - Export manual: `price_snapshots` CSV + import psql (ops ad-hoc)
4. Verificar `/health/db` post-deploy.
5. Collector en Railway debe compartir la misma `DATABASE_URL`.

---

## Billing schema

Lógica extraída a `market_billing.py`. Imports existentes desde `market_core` siguen funcionando (re-export).

Tablas billing:

- `subscriptions` — tier free/pro/enterprise
- `subscription_requests` — flujo Pro manual (`PRO-xxxxxxxx`)
- `billing_pending` — webhooks PayPal/Stripe pendientes

Ver `ops/BILLING_MANUAL.md` y `ops/E2E_CLIENT_JOURNEY.md`.

---

## Referencias

- `docs/ops/phase0-mitigation.md` — métricas y GTM
- `docs/ops/phase1-debt-cleanup.md` — deuda Fase 1
- `routers/health.py` — `/health/db`, `/health/collector`
- `tests/test_regression.py` — guards DDL
