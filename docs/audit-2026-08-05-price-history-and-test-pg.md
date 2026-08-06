# Audit: historical-series data moat + a silently broken Postgres CI gate

**Date:** 2026-08-05
**Status:** test-pg's real target is essentially done (28→1 failed, 0 errors, confirmed in real CI). A different, pre-existing problem in the plain SQLite `test` job was unmasked as a side effect and is now the open item — see bottom.
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

### Triage pass 3 (`da5395fa`)

Applied the `market_vault.py` dynamic-`USE_PG`-read fix to the rest of the
module-level occurrences flagged as unaudited: `market_audit.py`,
`procure_magic.py`, `market_funnel.py` (its schema DDL selector — separate
from the LIKE-pattern bug fixed in pass 2), `market_adoption_index.py`,
`market_brand_registry.py`. `market_audit.ensure_audit_schema()` runs
right after `market_vault.ensure_vault_schema()` in `test_vault.py`'s
autouse fixture — it was the real reason the ~44-test vault error cluster
survived pass 1's `market_vault.py`-only fix. Left alone (confirmed
function-local re-imports, safe): `market_adoption.py`, `audit_funnel.py`,
`collector_schema.py`, `routers/health.py`, `market_server.py`.

Verified against real Postgres: `test_vault.py` + `test_procure_magic_sprint3.py`
+ `test_security.py` + `test_paypal_reconcile.py` + `test_mcp_credential_guard.py`
together, 82/82 passed (all failing/erroring before).

### Triage pass 4 (`af47fc39`)

Four more independent bugs, each reproduced against real Postgres before
fixing:

1. `routers/brand_intel.py`: `brand_intel_config`'s `CREATE TABLE` used
   `INTEGER PRIMARY KEY AUTOINCREMENT` unconditionally — SQLite-only
   syntax, no Postgres branch had ever existed for this table. Added the
   missing PG DDL branch.
2. `routers/brand_intel.py`: `brand_promo_history()`'s "try `price_history`
   first, fall back to `price_snapshots`" always threw `UndefinedColumn` on
   Postgres — `price_history` deliberately lacks the `name`/`brand`/
   `store_name`/`currency` columns this query needs. That exception left
   the connection aborted, so the fallback failed too
   (`InFailedSqlTransaction`) — **`GET /v1/brand-monitor/promos` returned
   zero events on Postgres, unconditionally, in production, not just in
   tests.** Removed the dead `price_history` attempt; query
   `price_snapshots` directly.
3. `tests/test_collect_prices_growth.py` seeded a snapshot with the
   SQLite-literal `datetime('now', '-3 hours')` — outside the translator's
   whitelist, same class as pass-1's `brand_intel.py` fix. Computed in
   Python instead.
4. `tests/test_market_basket.py` asserted the exact SQLite-only SQL text
   `"LOWER(name) LIKE LOWER(?)"` — `market_core.market_db.name_like_clause()`
   correctly returns a *different* (and correct) clause per backend
   (`"name ILIKE ?"` on Postgres, GIN-trigram-index friendly there). Not a
   product bug — the assertion just assumed SQLite; now accepts either form.
5. `tests/test_brand_intel.py`'s `_seed_snapshot()` helper: the same
   swallowed-`ALTER`-poisons-the-transaction pattern as
   `test_checkout_payments.py` (pass 1) — added the same `rollback()`.

Verified against real Postgres (fresh container): `test_brand_intel.py` +
`test_market_basket.py` + `test_collect_prices_growth.py` together, 46/46
passed (all failing before).

**CI, `da5395fa` → `af47fc39`: 24 failed → 14 failed, 42 errors → 42
errors (unchanged).**

### The 42 errors are now understood — genuine Postgres connection flakiness

Pulled the actual traceback for one of the remaining `test_vault.py`
"ERROR at setup" entries directly from the `af47fc39` CI run. It's **not**
the stale-snapshot bug anymore — `market_vault.py:73` correctly evaluated
`market_core.USE_PG` as `True` and picked the Postgres DDL branch. The
failure is `market_db.py:167: OperationalError` — a genuine
`psycopg2.OperationalError` at the connection layer itself, inside CI's own
throwaway Postgres service container. `_DB.__init__()` (in the pinned
`cli-market-core` package, not this repo) opens a brand-new raw
`psycopg2.connect()` on every single `get_db()` call — no connection
pooling — and under this suite's connection churn (1000+ tests, each
opening/closing its own connection) that occasionally trips a transient
connection failure, which then permanently falls back the whole rest of
the process to SQLite via `ensure_db_initialized()`'s fallback logic
(`market_core.py:1450`), producing the cluster of DDL-branch-mismatched
errors across whatever runs next.

This **is** a real CI-relevant issue (confirmed in GitHub Actions' own log,
not just local Docker), but it isn't fixable from this repo — the missing
piece is retry/pooling in `_DB.__init__()`/`get_db()`, which lives in
`cli-market-core`. Two options for a future session: (a) a PR against
`cli-market-core` adding connection retry or pooling, or (b) a
`test-pg`-local mitigation (e.g. a `pytest` session-scoped fixture that
calls `market_core.recover_pg_if_needed()` between test modules, or
retries `ensure_db_initialized()` itself with backoff) — (b) treats the
symptom, (a) fixes the actual root cause and matters for production too
(a real prod Postgres blip has the same permanent-fallback-until-next-
opportunistic-recovery behavior).

### Not done — remaining backlog

- **14 failed + 42 errors remain untriaged** in `test-pg` as of `af47fc39`.
  The 42 errors are the connection-flakiness cluster above, not
  independent bugs to fix one-by-one — they need the `cli-market-core`-side
  fix (or a test-harness mitigation) described above, not more per-file
  triage.
- Remaining 14 failures not yet triaged: `test_analytics.py` (a real value
  mismatch, `assert 5.9 == 5.5` — looks like genuine test-order data
  bleed, not yet investigated), `test_audit.py` (2), `test_auth.py`
  (`test_revoke_api_key_success`), `test_mcp_credential_guard.py` (1 of its
  2 — the other was fixed in pass 3), `test_search.py` (canonical_product_id
  column + "database is locked" — likely downstream of the same connection
  flakiness above, not independent bugs).

## The real root cause (triage pass 5) — and cli-market-core 1.12.8

Spent a full round chasing a wrong lead first: widened `get_db()`'s Postgres
connect-retry budget in `cli-market-core` (3 attempts/~0.6s ->
5 attempts/~3s, published as **v1.12.8** on PyPI, pinned here) on the theory
that the persistent `test_vault.py` cluster was connection-churn flakiness.
Verified the retry logic works (simulated a 4-consecutive-failure outage,
recovers on attempt 5) — a real, legitimate improvement, kept — but CI's
count didn't move (still 14 failed / 42 errors), proving that wasn't the
actual trigger.

Confirmed by monitoring `pg_stat_activity` through a full local suite run:
connection count stayed at **1** the entire time — ruling out connection
exhaustion/leak entirely. Re-reading the exact traceback then found the
real bug: `tests/test_market_observatory_local.py`'s three tests each did
a raw `mc.USE_PG = False` (mc = `market_core.market_core`, the
*submodule*) — a direct attribute assignment, not wrapped in
`monkeypatch.setattr` despite `monkeypatch` already being used for
`setenv()` in the same tests. No teardown, so it permanently flipped the
submodule's live `USE_PG` to `False` for the rest of the pytest session
the moment any of the three ran.

Why that broke `market_vault.py` (and the ~9 other files fixed in passes
1/3) specifically: those all do `import market_core; ...
market_core.USE_PG` (the *top-level package* attribute) — itself a
`from .market_core import *` one-time re-export snapshot, frozen at first
import (see `cli-market-core`'s `market_core/__init__.py`). That snapshot
never updates after the observatory test's leak, so it kept reading `True`
and picking Postgres DDL, while `get_db()` (which reads the *live*
submodule attribute directly) correctly returned a SQLite connection —
the mismatch that produced `sqlite3.OperationalError: near "(": syntax
error` on every subsequent `ensure_*_schema()` call. Fixed with
`monkeypatch.setattr` for all four leaked attributes
(`USE_PG`/`_db_initialized`/`DATA_DIR`/`DB_FILE`).

That fix then surfaced `test_server.py`'s own copy of the FK-delete-order
bug (pass 1's `test_checkout_payments.py` class) — unguarded this time, so
it failed outright and took its entire ~80-test file down through the
autouse fixture. Reordered to delete children first, same as before.

**Result in real CI:** `test-pg` went from 14 failed / 42 errors to
**6 failed / 0 errors**. Pass 6 fixed four of the remaining six (all
genuine Postgres-vs-SQLite driver behavior differences — psycopg2
auto-deserializing `JSONB`/`TIMESTAMPTZ` columns into dicts/datetimes where
SQLite returns raw strings, plus a real production ordering bug in
`GET /analytics/price-history/series` where Postgres's `NOW()` returns
transaction-start time, not statement time, so two rows inserted in one
transaction could tie on `recorded_at` — added `id DESC` as a tiebreaker).
**Final confirmed CI result: 1171 passed, 1 failed, 0 errors** — down from
the pass-1 baseline of 29 failed / 56 errors. The one remaining failure
(`test_auth.py::test_revoke_api_key_success`, 404 instead of 200) is
un-triaged; plausibly fallout from the same class of issue, not yet
confirmed as independent.

## New problem, found by fixing the old one: the plain SQLite `test` job now hangs

The `test_market_observatory_local.py` fix above is correct and necessary
for `test-pg` — but it changed real behavior for every test that runs
*after* those three in the **plain SQLite** `test` job too. Before the fix,
the leaked `mc.DATA_DIR`/`DB_FILE` silently rerouted the rest of that job's
~1000 remaining tests onto a small, fresh, isolated temp SQLite file
instead of the real shared session DB (a bug, but one that happened to
keep things fast). After the fix, those tests correctly go back to
operating on the real, ever-growing shared DB — and CI's `test` job started
hanging for the full 10-minute job timeout before being cancelled, twice in
a row (reproduced identically on both the original run and a manual
rerun). Reproduced locally too (no Docker needed, SQLite-only): confirmed
by literally restoring the old broken version of the test file and
re-running the full local suite — clean, 1177 passed in 2:33 — versus the
fixed version, which reliably reproduces `FF....EE.E` failures around 91%
and then hangs.

### Follow-up round: found and fixed 7 real connection leaks — hang persists anyway

Tested the WAL-checkpoint-starvation theory directly: instrumented
`market_core.market_db._DB.__init__`/`close` with a traceback-tagged
open-connection counter (small standalone script, not committed) and ran
it against the full local suite. Found real, independent, unrelated-to-
each-other connection leaks — every one a `db = get_db()` with no
`db.close()` on some or all code paths:

- `routers/brand_intel.py` — all 4 endpoints, no close on *any* path
  (including early returns). On live Postgres this leaks one connection
  per request toward `max_connections`.
- `routers/dashboard.py` — `_dashboard_data()` (700+ lines) had a
  `db.close()` near the end on the success path only, no `try/finally`;
  `collector_trigger()` never closed at all.
- `routers/health.py` — `health_deep()`'s observatory/funnel checks only
  closed on their success path inside their own `try/except`.
- `market_vault.py` — `backfill_vault_bindings_from_audit()` closed on
  success but had no `finally`.
- **`server_deps.py`** — `get_messenger_session()`/
  `update_messenger_session()`, called on *every* conversational turn
  across telegram/whatsapp, never closed at all, on any path. By far the
  largest leak measured: 40 and 29 open connections in a single 10s
  sample, more than every other site combined.
- Two test-side instances of the same pattern
  (`tests/test_server.py`, `tests/test_whatsapp_conversation.py`).

All fixed (commit `d9d563a0`) — genuinely valuable regardless of the hang,
especially `server_deps.py`'s (a real prod connection-leak risk on
Postgres). Re-ran the diagnostic afterward: **`open=0` at process exit** —
confirmed zero leaked connections anywhere in a full suite run. That run
also happened to *complete*, in 2:42, no hang.

But a subsequent **clean run with no instrumentation, same code, hung
again** — same position, same `FF....EE.E` pattern, indistinguishable from
before the leak fixes. Confirmed in real CI too: `test` job on `d9d563a0`
still hit the full 10m15s timeout. This rules out the WAL-starvation
theory as the *sole* cause — with zero leaked connections confirmed, WAL
checkpointing has nothing blocking it. The one run that completed instead
of hanging, with identical code, points to a genuine timing-sensitive race
rather than a monotonic resource-exhaustion effect (the diagnostic
script's own overhead — a wrapping function call + `traceback.format_stack()`
per connection, running in a background thread — was apparently enough to
perturb timing past whatever the race depends on).

**Status: unresolved, deprioritized.** Real root cause is still not
identified after two rounds of investigation (~model of hours spent).
`test-pg` — the thing that actually matters for this repo's Postgres
behavior — is unaffected and healthy (1188 passed / 1 failed / 0 errors,
confirmed on `d9d563a0`). The plain SQLite `test` job hanging blocks
`deploy-fly.yml`'s automated path (CI must go fully green), but doesn't
indicate a *production* bug beyond the 7 leaks already fixed. Not
reverting `test_market_observatory_local.py` — would resurrect the
`test-pg` cluster this investigation was originally about. Next session
should try: `git bisect`-style search across which of the ~1050 tests
between position 0 and the hang is the actual trigger (binary-search the
`-k` deselect set rather than reasoning about it), or attach a debugger /
`py-spy dump` to a hung CI runner if that's feasible, since
`faulthandler.dump_traceback_later()` didn't get a chance to fire in the
one attempt made.

## Files touched today

- `collect_prices.py` — zombie-run fix, `price_history` write path
- `routers/analytics.py` — `/price-history/series`, `/stock-availability`, `id DESC` ordering tiebreaker
- `market_server.py` — `ensure_stock_history_table()` in lifespan
- `routers/brand_intel.py` — `days` cutoff computed in Python, `brand_intel_config` PG DDL branch, dead `price_history` promo-query path removed
- `tests/test_analytics.py`, `tests/test_brand_intel.py` — new/fixed tests
- `tests/conftest.py` — stop defeating `test-pg`
- `market_vault.py`, `market_audit.py`, `procure_magic.py`, `market_adoption_index.py`, `market_brand_registry.py`, `market_funnel.py` — dynamic `USE_PG` read
- `tests/test_checkout_payments.py`, `tests/test_server.py` — FK-safe delete order
- `market_funnel.py`, `ops/observatory_audit.py`, `ops/pro_payment_reminder.py` — LIKE patterns bound as params, not inlined
- `tests/test_collect_prices_growth.py`, `tests/test_market_basket.py`, `tests/test_audit.py`, `tests/test_search.py` — more literal-interval / backend-typed-value test fixes
- `tests/test_market_observatory_local.py` — the real root cause: unmonkeypatched `USE_PG` leak
- **`Treevu-ai/cli-market-core`** (separate repo): `market_core/market_db.py` — wider `get_db()` retry budget, published as v1.12.8; `requirements.txt` here bumped to match
- `routers/brand_intel.py`, `routers/dashboard.py`, `routers/health.py`, `market_vault.py`, `server_deps.py`, `tests/test_server.py`, `tests/test_whatsapp_conversation.py` — closed 7 real DB connection leaks (found chasing the SQLite `test`-job hang, which they did not fully resolve)
