# Audit: historical-series data moat + a silently broken Postgres CI gate

**Date:** 2026-08-05
**Status:** Partially resolved — collector/price-history fixes deployed; test-pg triage in progress (2 of N passes done)
**Trigger:** Asked to verify we're actually generating and saving historical price series in production.

## Summary

What started as "confirm price history is being collected" turned up two
unrelated, real production/CI gaps:

1. The scheduled collector (`collect_prices.py`, Postgres path) had never
   once written to `price_history` in the file's entire history — only
   incidental `live=true` `/search` calls did. The real historical series
   depended on accidental traffic, not the collector that runs every 4–6h.
2. `tests/conftest.py` has unconditionally blanked `DATABASE_URL` at pytest
   collection time since 2026-05-28 — which also silently defeated CI's
   `test-pg` job (added 2026-06-01 specifically to catch Postgres-only
   regressions). That job has been running the full suite against SQLite
   under a Postgres-container costume for ~2 months.

Both are fixed at the mechanism level and deployed/pushed. #2 uncovered a
long tail of real, previously-invisible Postgres-only bugs; one triage pass
landed, more remain.

## Part 1 — Collector / price_history / data-moat fixes (deployed to prod)

### Findings

- `price_snapshots` is an upsert table (1 row per product+store, overwritten
  every cycle) — **not** a historical series, despite `GET
  /analytics/price-history`'s name and summary implying one.
- `price_history` (the real append-only, change-triggered series) had gone
  stale for ~11 days (last row 2026-07-24) despite `price_snapshots`
  refreshing every cycle. Root cause: `collect_prices.py`'s Postgres write
  path (`pg_insert()`) only ever wrote `price_snapshots` + `stock_history`,
  never `price_history`. `price_history` was only ever populated by
  `save_price_snapshot()` on live `/search?live=true` calls.
  - Downstream effect: indicators computed from `price_history` (e.g.
    `staple_price_momentum` / "Retail Price Velocity") had been frozen
    since 2026-07-29.
- `run_collection()`'s Postgres path could leave a `collector_runs` row
  stuck at `finished_at = NULL` forever if anything failed between
  `pg_run_start()` and `pg_run_end()` outside the per-store `gather()` —
  confirmed 51 of the last 855 production runs orphaned this way.
- `stock_history` (749K+ rows, written every cycle) had zero readers
  anywhere in the codebase — write-only since it was added.
- `routers/brand_intel.py`'s `days` query param (free range 1–90) built its
  freshness filter as the SQLite-literal `datetime('now', '-{days}
  days')`. `_DB.execute()`'s SQLite→Postgres translator only rewrites a
  fixed whitelist of literal intervals (7/14/30 days, 1 day, 24 hours) — any
  other `days` value reached Postgres as raw SQLite syntax and errored.

### Fixes (commits, in order, all on `main`)

| Commit | Change |
|---|---|
| `05f19bb6` | `run_collection()`: wrap the PG batch loop in try/except/finally so `pg_run_end()` always runs, closing out the run instead of leaving it orphaned. `pg_insert()`: capture the pre-upsert price via a `WITH old AS (...)` CTE on the same `INSERT ... ON CONFLICT` statement, append to `price_history` only on a real price change (mirrors `market_core.append_price_history()`'s dedup semantics, wired to the actual recurring collector). |
| `7f70ae7c` | New `GET /analytics/price-history/series` (reads `price_history` for real per-product curves; old endpoint left as-is for compat). New `GET /analytics/stock-availability` (the "% time in stock" aggregate `stock_history`'s docstring always promised but nothing built). `market_server.py` lifespan now also calls `ensure_stock_history_table()` — it was previously only ever created lazily by the collector daemon, so a fresh deploy serving requests before the collector's first cycle could 500 on the new endpoint. |
| `8b9faa4e` | `routers/brand_intel.py`: both `/v1/brand-monitor` and `/v1/brand-monitor/promos` now compute the freshness cutoff in Python and bind it as a parameter instead of relying on the SQLite-literal translator. Added `days=2/45/60` regression tests (values outside the translator's whitelist). |

### Also done directly in production (not a commit)

- Backfilled the 51 pre-fix orphaned `collector_runs` rows: `finished_at =
  started_at`, `errors` set to an explanatory marker, so they stop
  distorting cadence metrics. Verified no run was in-flight before running
  the `UPDATE`.

### Verification

- Rollback-only transactions against real production Postgres (via `fly ssh
  console`) validated the CTE upsert logic (`old_price` correctly reflects
  the pre-update value; dedup skips a same-price rewrite) before any of it
  was committed to code.
- Each commit: full local test suite green, pushed, CI green, `deploy-fly.yml`
  auto-deployed with its built-in smoke test + auto-rollback-on-failure —
  no rollback triggered on any of these.
- Post-deploy: `/health/collector` and `/health/db` checked after each
  deploy (325/325 stores, `runs_total` advancing, Postgres backend
  confirmed).
- A wakeup was scheduled ~1h after the `price_history` fix landed to
  confirm the next collector cycle actually appended new rows; not yet
  confirmed as of this write-up (queued, not blocking).

### Not done / explicitly deferred

- `staple_price_momentum` and related `price_history`-fed indicators need
  a few collector cycles (≥3 paired snapshots per store in a 7-day window)
  to start producing values again — not something to verify same-day.

## Part 2 — `tests/conftest.py` silently defeating `test-pg` CI (in progress)

### Finding

`tests/conftest.py:40` did `os.environ["DATABASE_URL"] = ""` unconditionally
at collection time (added 2026-05-28, `3cd94f05`, to stop a real production
`DATABASE_URL` leaking in from a developer's local `.env` from ever being
hit by tests). CI's `test-pg` job (added 2026-06-01, explicit purpose: *"catch
PG-specific regressions (datetime translation, ON CONFLICT, type
mismatches)"*) sets `DATABASE_URL` to its own throwaway `localhost` Postgres
service container — but conftest's blanket override ran first and wiped
that out too, before any test module ever imported `market_core`.

Proof: `test-pg`'s own CI log showed `market_db.py:167: DeprecationWarning:
The default datetime adapter is deprecated... see the sqlite3
documentation` — a warning that can only fire from the `sqlite3` module.
It had been running the full suite against SQLite under the `test-pg` name
for ~2 months. This is exactly the bug class (`datetime` literal
translation, see `routers/brand_intel.py` above) the job exists to catch,
and exactly why it went undetected for 2 months.

### Fix (`d54a0ac3`)

Only blank `DATABASE_URL` when it doesn't already point at
`localhost`/`127.0.0.1` — a real prod DB is never there, so this preserves
the original leak protection while letting a deliberately-provided
local/CI Postgres through. Verified all three cases locally (no URL → still
blanked; CI-style `localhost` URL → preserved, `USE_PG=True`; a simulated
stray real prod URL → still blanked).

Pushed deliberately expecting `test-pg` to go red — its job here is to make
the backlog visible, not fix it. Confirmed isolated: `lint`, `secret-scan`,
`test`, `test-connectors`, `smoke-production` all stayed green; only
`test-pg` failed (29 failed, 1087 passed, 56 errors at that point).
`deploy-fly.yml` correctly skipped (overall CI failed; this commit doesn't
touch production code anyway).

### Triage pass 1 (`845fe073`)

Two real, independent bugs found and fixed, both invisible until `test-pg`
actually started hitting Postgres:

1. **`market_vault.py`** did `from market_core import USE_PG` at module
   level — a value-copy snapshot frozen at first import. `market_core.USE_PG`
   is designed to flip at runtime (PG outage → SQLite fallback →
   self-healed recovery via `market_core.recover_pg_if_needed()`); a frozen
   snapshot silently stops matching the live connections `get_db()` hands
   out. This is what caused `test_vault.py`'s `sqlite3.OperationalError:
   near "(": syntax error` — `ensure_vault_schema()` picked the Postgres DDL
   branch off a stale `True` while the actual connection had already
   fallen back to SQLite. Fixed by reading `market_core.USE_PG` live at
   every call site. **10 other files in this repo have the same
   `from market_core import USE_PG` pattern** — not fixed, flagged for a
   future pass (see below).
2. **`tests/test_checkout_payments.py`**'s autouse `clean_payment_tables`
   fixture deleted `app_orders` before `app_order_items` (which references
   `app_orders(order_id)` via FK). SQLite doesn't enforce FKs by default —
   silently "worked" there. Postgres always enforces it, so the DELETE threw
   `ForeignKeyViolation`, swallowed by a bare `except: pass` — but that left
   the connection in an aborted-transaction state for the rest of the
   fixture, and since this fixture runs `autouse` before *every* test in
   the file (which runs first in CI's pytest invocation), it poisoned the
   very next unguarded statement (`DELETE FROM app_users`) on every single
   test. This was the primary driver of the wider cascade across the suite.
   Fixed: delete children before parents, plus a defensive `rollback()` on
   any future per-table delete failure.

**Verified in real CI** (not just local Docker): `test-pg` went from 29
failed / 56 errors (pre-triage) to **28 failed / 42 errors** (post-triage) —
15 more tests passing, 14 fewer errors, confirmed via the actual GitHub
Actions log, not just a local approximation.

### Triage pass 2 (`e90bbd66`)

The `market_funnel.py:829` `IndexError: tuple index out of range` flagged
above was **mis-diagnosed** in pass 1 — it's not row-indexing at all.
Reproduced directly against real Postgres: `_DB.execute()` hands the whole
SQL string to psycopg2 as a `%`-format string whenever params are given
(that's the mechanism behind its `%s` placeholder substitution) — a literal
`%` inlined in the query text (`id LIKE 'PRO-%'`) collides with that
substitution and psycopg2 raises `IndexError`, one frame before any
application code runs. SQLite's driver doesn't do `%`-substitution, so this
was invisible until `test-pg` actually started hitting real Postgres —
same root shape as the `datetime('now', ...)` literal-translation bugs in
part 1, different mechanism.

Grepped the repo for the same shape (a `LIKE '...%...'` literal combined
with a non-empty params tuple on the same `.execute()` call) and found two
more real instances, both reproduced and fixed the same way (bind the LIKE
pattern as a parameter instead of inlining it):

- `market_funnel.py`'s `activation_summary()`
- `ops/observatory_audit.py`'s noise-heuristic query (4 LIKE patterns)
- `ops/pro_payment_reminder.py`'s pending-request lookup

Two lookalikes were checked and left alone —
`migrations/run_migration.py` and `ops/mcp_credential_guard.py` both call
`.execute()` with no params tuple at all, so `%`-substitution never
triggers. `routers/health.py`'s `ILIKE` queries are hand-written Postgres
SQL, also called without params.

**Verified in real CI:** `test-pg` went from 28 failed / 42 errors
(pass-1 baseline) to **24 failed / 42 errors**. Errors count unchanged —
this pass targeted the `failed` (assertion-reachable) bugs, not the
`test_vault.py`-class errors, which are a separate, still-open,
intermittent issue (see below).

### Not done — remaining backlog

- **24 failed + 42 errors remain untriaged** in `test-pg` as of `e90bbd66`.
  Local full-suite runs against a fresh Postgres container keep showing a
  *different* mix of failures/counts between runs (e.g. `test_vault.py`'s
  errors reappeared in one local run after being confirmed fixed in
  another) — this points to a real, intermittent ordering/isolation issue
  in the suite itself (see next item), separate from the specific bugs
  already fixed one at a time.
- **Non-deterministic PG→SQLite fallback mid-run, still unexplained.**
  Across ~6 full local runs against fresh Postgres containers today, error
  counts varied (79 → 46 → 64 → 42-ish) and *which* tests hit
  `sqlite3.OperationalError`/`database is locked` varied between runs of
  the identical code. No `psycopg2.errors.*` or connection-exhaustion
  message found in the Postgres container's own logs at the times this
  happens. Checked and ruled out: Postgres-side `FATAL`/`too many clients`
  (none found). Not yet checked: client-side `connect_timeout` (10s, see
  `_DB.__init__`) tripping under this Windows/Docker-Desktop local setup
  specifically — may or may not reproduce the same way on GitHub Actions'
  Linux runners; real CI's own numbers (28→24 failed, steady 42 errors
  across two pushes) look more stable than local, so this might be more of
  a local-environment artifact than a CI-relevant bug. Needs a dedicated
  investigation before spending more triage time chasing symptoms that
  might not even reproduce in real CI.
- **The 10-file `from market_core import USE_PG` stale-snapshot pattern**
  (same class as the `market_vault.py` fix) is unaudited elsewhere:
  `audit_funnel.py`, `collector_schema.py`, `market_adoption.py`,
  `market_adoption_index.py`, `market_audit.py`, `market_brand_registry.py`,
  `market_funnel.py`, `market_server.py`, `procure_magic.py`,
  `routers/health.py`. Not all of these necessarily matter in practice
  (e.g. a one-time startup check vs. a function called repeatedly across
  the process lifetime) — needs a per-file judgment call, not a blind
  find-replace.

## Files touched today

- `collect_prices.py` — zombie-run fix, `price_history` write path
- `routers/analytics.py` — `/price-history/series`, `/stock-availability`
- `market_server.py` — `ensure_stock_history_table()` in lifespan
- `routers/brand_intel.py` — `days` cutoff computed in Python
- `tests/test_analytics.py`, `tests/test_brand_intel.py` — new/fixed tests
- `tests/conftest.py` — stop defeating `test-pg`
- `market_vault.py` — dynamic `USE_PG` read
- `tests/test_checkout_payments.py` — FK-safe delete order
- `market_funnel.py`, `ops/observatory_audit.py`, `ops/pro_payment_reminder.py` — LIKE patterns bound as params, not inlined
