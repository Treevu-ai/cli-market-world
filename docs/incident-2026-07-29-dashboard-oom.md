# Incident: `/dashboard/data` OOM-killed a cli-market-api machine

**Date:** 2026-07-29
**Status:** Resolved (deployed)
**Severity:** High (Command & Control daily report showed moat/coverage/tiendas sanas at 0% all day — looked like the collector was down; it wasn't)

## Summary

The morning Command & Control report (`ops/command_control_daily.py`) showed
`moat 0`, `coverage 0%`, `tiendas sanas 0/0` — reading as a dead collector. The
collector was actually fine (325/325 stores succeeded, ~4h old data). The
`/dashboard` aggregation endpoint itself was the failure: `GET /dashboard/data`
was returning Cloudflare `502 Bad Gateway` intermittently, and the underlying
Fly.io machine was getting OOM-killed.

## How it was found

Asked to check if the collector was operational. `market_stats` (via MCP)
returned healthy data (153,091 snapshots, `latest_snapshot_at` ~4h old);
`GET /health/collector` on `cli-market-api.fly.dev` confirmed `status: ok`,
325/325 stores. But `market_dashboard` (MCP) and `GET /dashboard/data` both
502'd. `flyctl logs -a cli-market-api` showed the real story around
13:56–13:57 UTC:

```
13:56:53  machine 080756eae444e8: httpx.ReadTimeout calling /dashboard/data
13:56:55  machine d8944e1c7e1368: health check starts failing
13:57:43  machine d8944e1c7e1368: Out of memory: Killed process 659 (python)
          total-vm:1136840kB, anon-rss:875696kB
13:57:44  machine d8944e1c7e1368 auto-reboots (exit code 137)
```

## Root cause

`routers/dashboard.py`'s `_dashboard_data()` (the function backing
`/dashboard/data`) fetched the full `price_snapshots` table (150K+ rows,
growing ~9K/4h at the current collector cadence) into Python memory **three
separate times**:

1. `spread_rows` — full `SELECT ... FROM price_snapshots WHERE price > 0 AND
   price < 999999` for dispersion/canasta/marketing-spread analytics.
2. `price_rows` — the same table, same filter, fetched again just to compute
   P25/P50/P75 percentiles per (line, currency).
3. A second `[dict(r) for r in spread_rows]` conversion later in the function
   (for outlier detection), duplicating the list-of-dicts materialization
   already done once for `build_spread_analytics`.

Each row carries text fields (`name`, `brand`, `url`, `store_name`), so the
Python `dict` object overhead multiplies the on-disk row size several times
over. With ~150K rows fetched/converted 3-4 times concurrently, this comfortably
exceeded the VM's 1024mb (`shared-cpu-1x`).

**Why it hit at that exact moment:** the dashboard has a 120s shared cache in
Postgres (`dashboard_cache_kv`, added earlier to fix a different problem —
per-machine in-memory caches meant Fly's round-robin gave a low hit rate). But
the only lock guarding a cache-miss recompute was a plain `threading.Lock()`,
which only serializes within one process. When the cache expired, requests
landing on **both** of the app's 2 Fly machines around the same moment each
independently paid the full compute cost in parallel — doubling peak memory
exactly when a single compute already strained the VM. The logs are consistent
with this: one machine timed out waiting on `/dashboard/data` at 13:56:53 while
the other died from OOM at 13:57:43.

## Resolution

1. **`fly.toml`**: bumped VM memory `1024mb → 2048mb` (immediate headroom).
2. **`routers/dashboard.py`**: single full-table fetch (`spread_products`),
   reused for dispersion/canasta/marketing spreads, the P25/P50/P75 percentile
   grouping, and outlier detection — down from 2 SQL queries + 2 dict-list
   conversions to 1 of each. `del spread_rows` right after the conversion frees
   the raw cursor rows early.
3. **`routers/dashboard.py`**: added `pg_advisory_lock` (`_DASHBOARD_COMPUTE_LOCK
   = 84957232`, distinct from `collect_prices.py`'s `COLLECTOR_ADVISORY_LOCK`)
   around the cache-miss compute path in `_compute_dashboard_data_locked()`. Only
   one Fly machine recomputes at a time; the other blocks on the Postgres
   advisory lock, then re-checks the shared cache before recomputing itself —
   the exact race above can no longer happen. No-ops on SQLite (local/tests are
   single-process, nothing to serialize against).
4. Verified: full test suite green (1070/1071 — the 1 failure is
   `test_canonical_copy.py::test_no_stale_pip_install_copy`, pre-existing,
   unrelated GTM copy in `Clippings/`).
5. Committed (`75dab43c` → rebased to `d7fe5574` on top of two unrelated
   upstream commits) and pushed to `main`.

### Deploy: hit the same circular gate as the 2026-07-25 incident

`deploy-fly.yml` only fires after `CI` completes successfully
(`workflow_run`, gated on `conclusion == 'success'`). CI's `smoke-production`
job calls `GET /dashboard/data` against the **live, still-broken** production —
so the smoke check failed *because* of the exact bug this fix addresses,
which blocked the automated deploy that would have shipped the fix. Circular.

Resolved the same way as 2026-07-25: manual `flyctl deploy --app cli-market-api
--config fly.toml --build-secret github_token=$(gh auth token)` from this
repo (the canonical one — not the split-brain risk from 2026-07-25, which was
about deploying from the wrong, deprecated repo). Both machines came up
healthy post-deploy.

**Verified live after deploy:**
- `GET /dashboard/data`: first call (cold cache) `200` in ~10s, second call
  (warm cache) `200` in ~1.6s.
- `moat_summary.coverage_7d_pct`: **88.3%** (was reporting 0% all morning).
- `moat_summary.collector_stale`: `false`.
- `market_dashboard` (MCP tool, the one that 502'd at the start of this
  investigation): clean response, `gate: "open"`, `publishable: true`.
- Re-ran the CI `smoke-production` job: the `/dashboard/data` step now passes.

## Follow-ups / not yet done

- **CI is still red**, blocking the automated `deploy-fly.yml` path for the
  *next* commit — but for a separate, pre-existing reason: `ops/doctor_prod_gate.py`
  fails on `Sources health: 5 dead stores (max 0)` and reports `Golden linkage:
  71.8%`. This matches the linkage regression already flagged in this
  morning's Command & Control report (71.9%, meta ≥85%, -24pp vs the prior
  day) — a separate investigation, out of scope here.
- The percentile/dispersion/outlier business logic itself
  (`market_spread.py`'s `compute_dispersion`, `find_median_outliers`, fuzzy
  canasta matching) still requires a full in-memory pass over `price_snapshots`
  — it can't cleanly move to SQL because of the keyword/regex subcategory
  inference and `difflib` fuzzy clustering. That logic also lives in the
  external `cli-market-core` package (`.deps/cli-market-core/`), not this repo,
  so any deeper rework needs its own PyPI release. As the table keeps growing
  (~9K rows/4h), the *single* remaining full-table fetch will keep getting
  more expensive — the 2048mb bump buys headroom, not a permanent fix.
- No automated regression test asserts on peak memory or on
  `_compute_dashboard_data_locked()`'s cross-machine behavior (hard to test
  without 2 live Postgres connections racing) — verified manually via the
  production logs and live re-check instead.
