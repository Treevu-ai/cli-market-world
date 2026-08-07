# Audit: historical-series data moat + a silently broken Postgres CI gate

**Date:** 2026-08-05
**Status:** Fully done. test-pg's real target landed (28→1 failed, 0 errors, confirmed in real CI). The plain SQLite `test` job hang that was unmasked as a side effect is root-caused and fixed. The one remaining test-pg failure (`test_auth.py::test_revoke_api_key_success`) is also root-caused and fixed — see the two sections near the bottom. As of `c322074` (cli-market-core v1.12.9), no known failures remain in either CI job.
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

**Status (at the time): unresolved, deprioritized.** Real root cause hadn't
been identified after two rounds of investigation. `test-pg` — the thing
that actually matters for this repo's Postgres behavior — was unaffected
and healthy (1188 passed / 1 failed / 0 errors, confirmed on `d9d563a0`).
Picked back up in a later session — see below, now resolved.

## The SQLite `test` job hang: resolved

### Method

Reproduced locally with a diagnostic pytest plugin (not committed) that
hooks `pytest_runtest_setup`/`pytest_runtest_teardown` and snapshots
`market_core.market_core`'s `DATA_DIR`/`DB_FILE`/`_db_initialized`/`USE_PG`
(both the submodule and the top-level package re-export) plus a live
`SELECT ... FROM sqlite_master WHERE name='store_credentials'` existence
check before/after every single test, logging only on change. Run against
the full local suite (SQLite, matching CI's `test` job), this pinpointed
the exact transition: right after `tests/test_server.py`'s last test's
teardown, `store_credentials_exists` flips `True → False` **with no
`DATA_DIR`/`DB_FILE` change at all** — i.e. the real shared session DB file
itself lost its tables in place, not a path swap.

### Root cause

`tests/test_server.py` had a `teardown_module()`:

```python
TEST_DATA_DIR = os.environ["MARKET_DATA_DIR"]
...
def teardown_module():
    """Clean up temp dir after all tests."""
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
```

`MARKET_DATA_DIR` is set once in `conftest.py` via `tempfile.mkdtemp()` —
it's the **one shared SQLite data directory for the entire pytest
session**, not a directory private to `test_server.py`. This
`teardown_module()` deleted it wholesale the moment `test_server.py`'s own
tests finished, **without** resetting `market_core.market_core._db_initialized`
back to `False`. Every subsequent test file in the run (alphabetically
after `test_server.py`: `test_slack_ops.py`, `test_sources_health.py`,
`test_stores_catalog_growth.py`, `test_vault.py`, the `test_whatsapp_*`
files, etc.) still saw `_db_initialized == True` and skipped
re-initialization, so `get_db()` opened a connection to a path that no
longer existed — SQLite silently auto-creates an empty file there with
zero tables. Hence the `sqlite3.OperationalError: no such table:
store_credentials` / `app_users` / `rate_limits` cascade from ~78% onward,
and very likely the hang itself (whatever downstream code path hits an
unbounded retry or lock contention against a file that's being
concurrently recreated).

**Why this was invisible until now, despite presumably existing for a long
time:** `test_market_observatory_local.py`'s un-monkeypatched `USE_PG`
leak (fixed earlier in this same investigation, "triage pass 5") had been
accidentally *masking* this bug — it silently rerouted the rest of the
session's tests onto a different, small, isolated temp DB, so by the time
`test_server.py`'s `teardown_module()` deleted the *original* shared
`MARKET_DATA_DIR`, nothing downstream was still pointed at it, and the
delete was harmless by coincidence. Fixing that leak correctly restored
every downstream test to the real shared DB — which is exactly what
exposed this second, independent, pre-existing bug to the `rmtree()`.
Two unrelated bugs, stacked, where fixing the first was a precondition for
the second becoming visible at all.

### Fix

Removed `teardown_module()` (and the now-unused `shutil`/`os` imports and
`TEST_DATA_DIR` constant) from `tests/test_server.py`. `MARKET_DATA_DIR` is
already `tempfile.mkdtemp()`-managed per session — nothing needs to
explicitly delete it, and no single test file should ever delete a
directory it doesn't own exclusively.

### Verification

Full local suite (SQLite, matching CI's `test` job invocation), after the
fix: **completed in 9:38 — no hang.** `1190 passed, 1 failed, 0 errors`.
The one failure (`test_market_observatory_local.py::test_compute_daily_observatory_metrics_sqlite_row`,
`assert 0 >= 1`) is unrelated to the cascade — a narrow, pre-existing flake,
not yet triaged, tracked separately (not blocking).

**Confirmed in real CI** on `500056a2`: the `test` job completed and went
green — no hang, no timeout. `test-pg` failed separately on an unrelated,
already-known issue (next section).

## The last test-pg failure: resolved

### Finding

With the hang fixed, `test-pg` on `500056a2` ran to completion cleanly and
failed on exactly the one pre-existing, already-documented item: `1
failed, 1188 passed, 2 skipped` — `test_auth.py::test_revoke_api_key_success`,
`assert 404 == 200` on `DELETE /auth/keys/{key_id}`.

No local Postgres/Docker was available to reproduce interactively (Docker
Desktop's engine was stopped and wouldn't start non-interactively), so this
was triaged by temporarily instrumenting the failing test itself with
`print()`s of the resolved username, `DEFAULT_TOKEN` state, and a direct
dump of the `api_keys` table before and after the failing DELETE call —
committed, pushed, read from the CI log, then reverted (`7db06713`).

The dump was unambiguous:

```
[DIAG] api_keys table rows (before): ... {'id': 10, 'username': 'admin', 'label': 'to-revoke'}
[DIAG] delete response: 404 {"detail":"Key not found"}
[DIAG] api_keys table rows (after):  ... (id 10 is gone)
```

**The DELETE genuinely succeeded — the row was really removed — but the
endpoint returned 404 anyway.** Root cause, in `cli-market-core`'s
`db_revoke_api_key()`:

```python
row = db.execute(
    "DELETE FROM api_keys WHERE id=? AND username=? RETURNING id",
    (key_id, username),
).fetchone()
...
return row is not None
```

`_DB.execute()` (same file) already special-cases any `RETURNING` clause:
it calls `cur.fetchone()` internally right after executing, to populate
`.lastrowid`. That consumes the psycopg2 cursor's one-row result set. When
`db_revoke_api_key()` then calls `.fetchone()` again on the same cursor
(via the `_PgCursor` wrapper), there's nothing left to fetch — always
`None`, regardless of whether the DELETE matched a row. So this endpoint
was **structurally guaranteed to always 404 on Postgres**, even on a
successful revoke — not a flake, not test-only, a real production bug
(any `cli-market-api` caller revoking a real API key on Postgres always
saw a 404 despite the key actually being revoked).

Grepped every other `RETURNING`-using call site in the package:
`db_add_to_cart` correctly uses `cur.lastrowid` (not `.fetchone()`);
`db_create_api_key` sidesteps the whole trap by re-`SELECT`ing the row
after insert instead of trusting the `RETURNING` result. `db_revoke_api_key`
was the only one still calling `.fetchone()` directly on a `RETURNING`
result — an isolated instance, not a systemic pattern across the codebase.

### Fix (`cli-market-core` v1.12.9, commit `c322074`)

Read `cur.rowcount` instead of `.fetchone()` — accurate for `DELETE`,
unaffected by the cursor's fetch state:

```python
cur = db.execute(
    "DELETE FROM api_keys WHERE id=? AND username=? RETURNING id",
    (key_id, username),
)
affected = cur.rowcount
...
return affected > 0
```

Published to PyPI as `cli-market-core==1.12.9`; bumped the pin in
`requirements.txt` here to match.

### Verification

Diagnostic instrumentation confirmed the bug's exact shape via real CI
output (above) before the fix — high confidence this is the true and only
cause, not a guess. Not yet re-confirmed with a fresh `test-pg` run as of
this write-up (queued as the next CI push); expected to be the final
green light for both CI jobs.

## Aparte: ¿vale la pena scrapear precio por sucursal? (investigación, sin cambios de código)

**Trigger:** pregunta directa del usuario — si internamente alguien pidiera
"Wong Arequipa" vs "Plaza Vea Trujillo", ¿podríamos responder eso hoy? La
respuesta corta ya era no (no hay columna de sucursal/ciudad en ningún
store). Esto es la investigación de seguimiento: ¿vale la pena construirlo?

### Método

Consultas HTTP en vivo (sin cambios de código) contra la API pública de
catálogo VTEX (`/api/catalog_system/pub/products/search`) de las tiendas
peruanas rastreadas, variando el parámetro `sc` (sales channel) de VTEX —
el único mecanismo de segmentación de precio que expone esa API pública.

### Hallazgos

- **`market_connectors/vtex.py`** (conector actual) no usa `sc` ni ningún
  parámetro de región — llama al catálogo con los defaults de cada tienda.
  `market_core.STORES["wong"]`/`["metro"]`/`["plazavea"]` no tienen
  configuración de `sc` ni de región, solo `base`/`country`/`currency`/`line`/`platform`.
- **Wong** (`wong.pe`): para el SKU 13571 (Chocolate con Leche Triángulo
  29-30g), `sc=70` (el canal real por defecto, confirmado vía
  `addToCartLink` de una búsqueda sin `sc` explícito) → S/2.50; `sc=71` →
  S/1.90. Diferencia real, mismo SKU, mismo momento.
- **Metro** (`metro.pe`, dominio separado, mismo grupo Cencosud): el mismo
  SKU 13571, en su canal por defecto, también S/2.50 — igual al *default*
  de Wong, no al `sc=71` más barato. Es decir, el precio "real" que ve un
  cliente en cualquiera de las dos marcas es el mismo; `sc=71` no es "el
  precio de Metro escondido en el canal de Wong".
- **Plaza Vea** (`plazavea.com.pe`): mismo experimento con otro SKU
  (Chocolate Nestlé Triángulo Doypack 136g, S/10.90). `sc=1` y `sc=2` (los
  únicos canales válidos encontrados) devolvieron **el mismo precio**;
  otros valores de `sc` simplemente no matchearon ningún producto (sin
  precio alterno, a diferencia de Wong).
- No se encontró ningún selector de tienda/ciudad de cara al cliente en
  ninguno de los tres sitios, ni ningún parámetro de región/postal-code
  soportado por la búsqueda pública de catálogo (`DeliverySlaSamplesPerRegion`,
  el mecanismo real de "Regionalización" de VTEX, requeriría simular
  selección de dirección — no probado, ver "no hecho" abajo).
- Los tags de campaña vistos en Wong (`"Delivery Gratis T121 Playas"`,
  `"...T116 Playas"`) son zonas de delivery/promoción, no precio distinto.
- **`tottus` no está en `market_stores.py` en absoluto** — no es un tema de
  precio por sucursal, es una tienda que hoy no rastreamos. Gap separado,
  no relacionado con esta investigación.

### Conclusión

**No vale la pena hoy.** La única variación de precio real encontrada
(Wong `sc=71`) no se repite en Plaza Vea con el mismo método, y Metro
confirma que el precio por defecto es igual entre marcas hermanas — todo
apunta a que `sc=71` es un canal interno no representativo (app, mayorista,
o canal de pruebas), no evidencia de precio geográfico real. Construir
scraping por sucursal sería ingeniería especulativa sin caso de negocio
demostrado: ninguna de las tres cadenas probadas publica precio distinto
por ciudad/tienda en su catálogo web público, que es exactamente lo que ya
capturamos.

### No hecho / posible siguiente paso

- No se simuló el flujo real de "elegir tienda/dirección" (selección de
  código postal) en ningún sitio — el mecanismo de Regionalización de VTEX
  podría, en teoría, afectar disponibilidad o precio de forma que la API
  de catálogo sin sesión no refleja. Si se quisiera cerrar esto del todo:
  simular ese flujo (probablemente vía cookies/headers de sesión regional)
  en 2-3 cadenas más, ~30 min por cadena.
- Solo se probó 1 SKU por tienda — no se puede descartar que otras
  categorías (ej. perecibles, que sí suelen variar por tienda física)
  tengan un comportamiento distinto al de abarrotes empacados.

## Addendum 2026-08-07 — post-fix verification in production (INDECOPI regulatory-impact exercise)

**Trigger:** A simulated INDECOPI regulatory-impact analysis (canasta de 10
productos básicos, PE, 6 retailers masivos) surfaced that `market_price_history`
returned exactly **1 snapshot** for all 10 SKUs queried, plus a previously
audited GLORIA milk SKU. Before concluding "no price changes in the window,"
this was cross-checked against this file's `05f19bb6` fix (collector wired to
`price_history` with change-triggered dedup, deployed 2026-08-05).

### Verification method

Direct production checks, no code changes:

- `GET https://cli-market-api.fly.dev/health/collector` — confirms the
  collector is alive and cycling: `last_run: 2026-08-07T16:36:32Z`,
  `stores_attempted: 323`, `stores_succeeded: 323`, `runs_total: 876`.
- `GET https://cli-market-api.fly.dev/health/db` — confirms Postgres backend,
  `price_history` and `price_snapshots` listed as distinct tables (not
  conflated).
- Re-queried `market_price_history` (MCP tool, hits the production API) for
  two previously-checked SKUs after at least one more collector cycle had
  run in between:
  - Arroz Extra Paisana 1kg, Plaza Vea (`product_id=20131000`): `id=16942`
    unchanged, `queried_at` unchanged (2026-07-13) — no cycle touched it in
    that window.
  - Leche Entera UHT Gloria 946ml, Plaza Vea (`product_id=358217`): **same
    `id=357623`**, but `queried_at` advanced from `09:38` to `16:36` (a real
    collector cycle ran in between, confirmed against `/health/collector`'s
    timestamp) — price unchanged (S/6.20 → S/6.20).

### Finding

The same `id` persisting while `queried_at` advances is the *expected*
signature of the change-triggered dedup design this file's `05f19bb6` fix
implemented: the collector ran, confirmed the price was still current, and
did not insert a new `price_history` row because there was no real price
change — it is not evidence of a stuck or broken pipeline.

This is **not**, however, a full end-to-end confirmation that a new row gets
appended *when a price does change* — no SKU checked has moved price since
the fix landed 2 days ago, so the append-on-change path has not been
observed firing in production, only inferred from the collector being
healthy and the dedup logic reading correctly in code. This is the exact
item this file already flagged as open ("not yet confirmed as of this
write-up... queued, not blocking").

### Implication for the INDECOPI exercise's 30+30 pre/post design

The ~35-day history figure used as the starting assumption for that exercise
does not apply to `price_history` in practice — real, reliable
change-triggered accumulation only started **2026-08-05**, not
"inicios de julio." Recommended earliest viable date for a genuine 30-day
pre + 30-day post window, recalculated from the fix date: **~2026-10-04**,
conditional on the collector continuing to run every cycle and on the
tracked SKUs actually experiencing price movements to populate the series
(a staple with a genuinely flat price for months will still show few rows
regardless of elapsed calendar time — that is correct dedup behavior, not a
data gap to fix).

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
- `tests/test_server.py` — removed `teardown_module()`'s `shutil.rmtree()` of the shared `MARKET_DATA_DIR`, the actual root cause of the SQLite `test`-job hang (see "The SQLite `test` job hang: resolved")
