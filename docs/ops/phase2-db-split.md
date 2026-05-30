# Fase 2 — Split de capa DB

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase2-db-split-f414`

Continúa `docs/ops/phase1-debt-cleanup.md`. Extrae la capa de conexión y DDL de `market_core.py` a `market_db.py`.

---

## Completado

| # | Tarea | Resultado |
|---|-------|-----------|
| 1 | Split `market_db.py` | Conexión (`_DB`, `_PgCursor`, `get_db`) + DDL (`init_db_pg`, `_SQLITE_DDL`, `_migrate_price_snapshots_pg`) |
| 2 | Packaging | `Dockerfile.collector`, `railway.collector.toml`, `pyproject.toml` incluyen `market_db.py` |
| 3 | Copy 13K → 43K restante | `ops/HN_POST.md`, `docs/cli-market-prd-v2.md` |

`market_core.py`: 1264 → 775 líneas.

---

## Diseño — por qué el estado se queda en `market_core`

El estado (`USE_PG`, `DATABASE_URL`, `DB_FILE`) y el ciclo de vida (`init_db`,
`ensure_db_initialized`, `_db_initialized`) **permanecen en `market_core`**.
Solo la conexión y el DDL se movieron.

Razones:

1. **Mutación de `USE_PG` en fallback.** `ensure_db_initialized()` reasigna
   `market_core.USE_PG = False` cuando PostgreSQL no responde. `market_db._DB`
   lee `market_core.USE_PG` en tiempo de conexión → fuente única, sin copias stale.
2. **Tests.** `tests/test_regression.py` parchea `market_core.USE_PG`,
   `DB_FILE`, `_db_initialized`. Mantenerlos en `market_core` preserva esos hooks.

`market_db` hace `import market_core` y referencia los atributos en runtime
(mismo patrón que `market_billing`). Sin ciclo de import porque el acceso es
siempre dentro de funciones, nunca a nivel de módulo. El entrypoint siempre es
`market_core` (collector, server, CLI, MCP lo importan), nunca `market_db` directo.

Re-exports en `market_core` (`# noqa: F401`): `_DB`, `_PgCursor`, `get_db`,
`init_db_pg`, `_SQLITE_DDL`, `_migrate_price_snapshots_pg`.

---

## Verificación

- `ruff check .` ✅
- `pytest tests/ -q -m "not integration"` — 124 passed ✅
- Import chain: `market_core/db/billing/collect_prices/server/mcp` ✅
- **Fallback PG→SQLite** probado con host inalcanzable: `USE_PG` pasa a `False`
  y `_DB` cae a SQLite sin crash ✅

```bash
ruff check .
MARKET_DATA_DIR=/tmp/market-test-data pytest tests/ -q -m "not integration"
python3 -c "import market_core, market_db; assert market_core.get_db is market_db.get_db; print('ok')"
```

---

## Pendiente Fase 3+

| Item | Notas |
|------|-------|
| PayPal «Agotado» | Fix en panel PayPal Business (externo); landing ya tiene CTA verde |
| ~~Copy LinkedIn restante~~ | ✅ Fase 3 — ver `docs/ops/phase3-content-sync.md` |
| Content repo privado | `campaign sync` tras merge de template (acción local, repo `cli-market-content`) |
| Checkout autónomo | Roadmap Build — no prometer en copy comercial |
