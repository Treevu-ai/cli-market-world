# Changelog

All notable changes to the CLI Market ecosystem.

## [2026-08-01] — source-health recovery and coordinated Core 1.12.4 release

Production health was blocking deploys with three `dead` sources:
`smartnutrition_pe`, `thegreenkiss_ca`, and `simplynaturalcanada_ca`.
Their public product APIs were verified from non-datacenter egress, but each
blocks the Fly.io collector IP with a WAF or ModSecurity response. This is an
egress restriction, not evidence that the retailers or their catalogs are
offline.

- **Core 1.12.4:** quarantines the three sources from the active catalog with
  a store-specific `disabled_reason` and a regression test. They can be
  re-enabled only after a proxy or retailer allowlist has been validated.
- **World:** pins `cli-market-core==1.12.4`; the Telegram quotation flow and
  API now consume the same released catalog definition.
- **Production:** the automatic deploy was initially skipped because its CI
  smoke measured the old container. A manual `Deploy Fly.io` workflow retained
  import checks, post-deploy smoke and automatic rollback. It completed
  successfully; `ops/doctor_prod_gate.py` reported `314 ok · 0 dead` and
  `golden linkage 68.1%`.
- **Backend, Index and Content:** no API contract, Golden Record or public
  claim changed. Backend's compatible `cli-market-core>=1.12.3` range resolves
  1.12.4; Index remains pinned identically between World and Backend; Content
  receives no coverage-count or availability claim from this operational
  change.

The release record, evidence and reactivation criteria are in
`docs/RELEASE-SYNC-2026-08-01.md`.

## [2026-07-30] — bump cli-market-core pin to 1.12.0 (also disable igardi_pe, to unblock deploys now)

`requirements.txt` pin bumped to `cli-market-core==1.12.0`. On explicit
request to unblock deploys immediately, `igardi_pe` is now disabled too
(not a confirmed hard block like `wisqaperu_pe` — production 403s vs. a
clean residential-IP response minutes later — but disabled anyway
rather than wait out the ambiguous IP-reputation issue).

**This alone likely still won't turn CI green**: the 3 stores fixed by
1.11.98 use a lifetime-cumulative success_pct that needs several
collector cycles to climb back above the dead threshold — right after
this deploys, `doctor_prod_gate.py` may still see them as dead. To
actually get code live *now*, use one of:
- `gh workflow run deploy-fly.yml` (documented in that workflow as the
  manual emergency bypass — skips the CI gate entirely), or
- temporarily raise `DOCTOR_MAX_DEAD_SOURCES` in the CI gate step.

## [2026-07-30] — bump cli-market-core pin to 1.11.99 (disable wisqaperu_pe, confirmed Cloudflare Turnstile)

`requirements.txt` pin bumped to `cli-market-core==1.11.99`. Closes the
dead-store investigation: `wisqaperu_pe` confirmed as a genuine,
unconditional Cloudflare Turnstile/JS-challenge (blocks every request,
including from a fresh residential IP) — disabled, same class as
Deltron/Efe, no code fix possible. `igardi_pe` investigated but left
active: production got 403s, but the identical request from a
residential IP returned clean JSON minutes later with no challenge at
all — looks like Fly.io IP reputation with Cloudflare rather than a
hard block, monitor rather than disable. See `cli-market-core`'s own
changelog for the full writeup.

With `wisqaperu_pe` disabled, `doctor_prod_gate.py`'s dead-store count
should drop by one immediately; the 3 stores fixed by 1.11.98 need a
fresh collector cycle to recover their lifetime success_pct back above
the "dead" threshold (cumulative ratio, not a rolling window — will take
several cycles, not instant). `igardi_pe` may or may not still show
dead depending on whether the IP-reputation issue has cleared.

## [2026-07-30] — bump cli-market-core pin to 1.11.98 (fix 3/5 dead-store collector failures)

`requirements.txt` pin bumped to `cli-market-core==1.11.98`. Root-caused
why `ops/doctor_prod_gate.py` (`MAX_DEAD_SOURCES=0`) has been failing CI
— and blocking every Fly.io deploy — since 2026-07-29 21:19 UTC: 5 dead
stores (`thegreenkiss_ca`, `simplynaturalcanada_ca`, `wisqaperu_pe`,
`smartnutrition_pe`, `igardi_pe`). Fixed 3 of 5: some WAFs return HTTP
200 with an HTML block page instead of JSON to the collector's IP
specifically — both the Shopify and WooCommerce connectors only treated
non-2xx status as "blocked, try the fallback," so `resp.json()` raised
uncaught and neither connector's existing fallback ever ran. See
`cli-market-core`'s own changelog for the full root-cause writeup and
the 2 stores (`wisqaperu_pe`, `igardi_pe`) still unresolved (genuine
403s that need production-side investigation, not a further guess from
a local checkout).

**Still blocking deploys**: this fix needs a fresh collector cycle to
flip the 3 recovering stores back from `dead`, and even then 2 stores
remain genuinely dead — so `doctor_prod_gate.py` will likely keep CI red
until either those 2 are fixed or `DOCTOR_MAX_DEAD_SOURCES` is raised
temporarily. Decision pending.

## [2026-07-30] — bump cli-market-core pin to 1.11.97 (fix items_resolved/breakdown SKU mismatch — GLORIA report Hallazgo 3)

`requirements.txt` pin bumped to `cli-market-core==1.11.97`. Closes the
last open finding from `docs/reports/p0-glo-basket-pe-enterprise-blockers.md`:
`market_optimize_purchase` could resolve the same requested item to
different SKUs across `items_resolved`, `product_links`, and
`sections.compare.breakdown` in a single response ("yogurt gloria" → 3
different GLORIA products in one real production response). Now
`items_resolved` is reconciled against the leader store's breakdown, so
it always describes the exact product/price actually priced into the
shown total. See `cli-market-core`'s own changelog for the full
root-cause writeup. With this, all 5 findings from that report are
closed.

## [2026-07-30] — bump cli-market-core pin to 1.11.96 (fix market_optimize_purchase wrong-category matches)

`requirements.txt` pin bumped to `cli-market-core==1.11.96`. Fixes a bug
surfaced by a 15-exercise PE diagnostic run: `market_optimize_purchase`
returned an invalid S/154 plan (vs S/958 validated by hand) because its
basket-total computation resolved "queso" to "Tequeños de Queso" (a fried
snack) and "mantequilla" to "Mantequilla de Maní" (peanut butter) — both
literal word-overlap false positives, cheaper than the real dairy
staple, so they won the per-store "best price" pick. Fixed at the
matching layer (`market_food_match.py`/`market_spread.py` exclusion
lists) in `cli-market-core`; see that repo's changelog for the full
root-cause writeup and the known, intentional limit (a separate "leche"
→ "leche light" observation from the same report was NOT touched —
insufficient evidence to tell a real mismatch from a working-as-intended
diet-variant substitution).

## [2026-07-30] — bump cli-market-core pin to 1.11.95 (register deltron_pe, disabled)

`requirements.txt` pin bumped to `cli-market-core==1.11.95`, which adds
`deltron_pe` (Deltron, PE wholesale tech distributor) to the `STORES`
registry. Registered `disabled=True` / `enable_with_credentials=True` —
the site runs a custom PHP storefront (not VTEX/WooCommerce/Magento/
Shopify) whose product search returns server-rendered HTML with every
price hidden behind "Precios - solo para usuarios logueados" (B2B
wholesale login required). No collector changes possible until account
credentials are available. See `cli-market-core`'s own changelog for the
full investigation notes.

## [2026-07-30] — bump cli-market-index pin to v0.2.2 (ship the DANLAC variety-fingerprint fuzzy-match fix to production)

Found while auditing ecosystem-wide alignment: `cli-market-index` had
already fixed and backfilled the bug behind "same commercial SKU, different
`canonical_product_id`" (DANLAC yogurt showing under different ids across
retailers — see `cli-market-index/CHANGELOG.md`'s 2026-07-30 entry for the
full root-cause writeup: `_fuzzy_search` matched candidates on
brand+category+unit+qty only, never checking the variety fingerprint that
distinguishes real product variants), but this repo's pin was still 10
commits behind that fix — `829b15a`, pre-dating both the `BRAND_MAP` entry
and the `_fuzzy_search` fix. The one-time production backfill already run
against `cli-market-api`'s DB only cleaned up existing rows; without this
pin bump, newly ingested variants (DANLAC or any other brand) could keep
silently merging into an existing bare-variety golden record the same way.

- `requirements.txt`: `cli-market-index` pin moved from commit `829b15a`
  to tag `v0.2.2` (commit `66e6c7e`) — full 174-test suite confirmed green,
  independent code-reviewer pass on the fix itself: APPROVE, 0 findings.
- No `cli-market-world` code changes needed — this is purely a dependency
  pin bump; the resolver logic lives entirely in `cli-market-index`.

**Deployed**: `flyctl deploy --app cli-market-api --build-secret
github_token=$(gh auth token)` run same session — Docker rebuilds the
`git+https` pin unconditionally on this layer (no cache-bust needed, the
commit SHA in `requirements.txt` changed). Verified healthy post-deploy.

## [2026-07-30] — expose stores_resolved on search/compare + bump cli-market-core pin to 1.11.94 (relevance-ranked search candidates)

Closes the last two code-fixable findings from the tool-performance
diagnostics for this round:

- `routers/search.py`: `/products/search` and `/products/compare` now
  include `stores_resolved` (the pre-filter store count) in their
  response — turns "0 stores matched your country/line/store filters"
  into a diagnosable signal instead of looking identical to "candidates
  existed but none passed the relevance filter" (both previously just an
  empty list). New tests confirm `stores_resolved == 0` for an unknown
  country on both endpoints.
- `requirements.txt` pin bumped to `cli-market-core==1.11.94`, which ranks
  search candidates by token-match-count before the recency-ordered
  candidate cap — closes the "exact vs broad" search gap (a broad
  `market_search` finding a Sapolio 4L pack that a stricter search
  missed). Same class of bug as the 2026-07-20 "pollo" incident. See that
  repo's own changelog for the known, intentional limits of this fix
  (single-token queries and `require_all=True` wording mismatches are
  unaffected).

With this, all 3 code-fixable findings from
`Diagnostico_desempeno_tools_CLI_Market_2026-07-29.md` are closed.
`canonical_product_id` drift across retailers remains out of reach —
owned entirely by `cli-market-index` (external repo).

**Deployed**: PyPI publish of `cli-market-core` 1.11.94 confirmed via tag
`v1.11.94`. `flyctl deploy --app cli-market-api --build-secret
github_token=$(gh auth token)` and the same for `cli-market-collector`
(`--config fly.collector.toml`) run same session — both apps rebuilt
against the new pin, both healthy post-deploy.

## [2026-07-30] — flag cross-retailer product_id collisions in /analytics/price-history + bump cli-market-core pin to 1.11.93

Closes a finding from `Diagnostico_desempeno_tools_CLI_Market_2026-07-29.md`:
`product_id` is each retailer platform's own raw catalog ID (VTEX
`productReference`, Shopify/WooCommerce numeric ID), never globally
namespaced. `GET /analytics/price-history?product_id=...` without `store=`
queried by `product_id` alone across every retailer's catalog, silently
merging unrelated products that happen to reuse the same small numeric ID
— confirmed in production: `product_id=468` returned both a Cafetal coffee
and an unrelated basil oil from a different retailer.

- `routers/analytics.py`: when `product_id` is given without `store` and the
  matched rows span more than one distinct store, the response now includes
  `stores_matched` and a `warning` telling the caller to pass `store=` to
  disambiguate. `snapshots` stays the same flat list — no shape break.
- New test reproduces the exact repro (two stores, same `product_id`,
  unrelated products) and confirms `store=` suppresses the warning.
- `requirements.txt` pin bumped to `cli-market-core==1.11.93`, which also
  ships 2 other fixes from the same diagnostic — see that repo's own
  changelog: a bundle-contamination guard for `market_basket` (an aceite
  vegetal request resolving to an arroz+aceite pack) and disambiguation of
  `meta.confidence`'s meaning (`confidence_basis` field).

**Deployed**: `cli-market-core` 1.11.93 built and published to PyPI via
`.github/workflows/publish-pypi.yml` (triggered by pushing tag `v1.11.93`),
confirmed live on PyPI. `flyctl deploy --app cli-market-api --build-secret
github_token=$(gh auth token)` and `flyctl deploy --app cli-market-collector
--config fly.collector.toml --build-secret github_token=$(gh auth token)`
both run same day — both apps rebuilt against the new `requirements.txt`
pin (Docker's layer cache invalidates automatically since the file content
changed). Verified live: `cli-market-api` 2 machines healthy;
`cli-market-collector` active machine healthy (+ 1 standby, by design).
`curl https://cli-market-api.fly.dev/analytics/price-history?product_id=1`
and `curl -X POST https://cli-market-api.fly.dev/v1/basket/compare -d
'{"items":[{"name":"leche"}]}'` both return `401` (auth required) — not
`404`/`500` — confirming the new code is live, not just the pin bump.

## [2026-07-30] — wire 4 intel MCP tools into the HTTP transport + bump cli-market-core pin to 1.11.92 (basket-stress, commerce-pulse, price-forecast, arbitrage — 404/"Unknown tool" since 2026-07-17)

Closes the code-fixable findings from `docs/reports/p0-glo-basket-pe-enterprise-blockers.md`
(Cursor-reported enterprise playbook run against the GLORIA dairy canasta).
`market_basket_stress`, `market_commerce_pulse`, `market_price_forecast`, and
`market_arbitrage` were registered as MCP tools since `0f539d3` (2026-07-17)
but had **two** independent gaps, both now closed:

1. `cli-market-core` never implemented the backing REST routes (404 in prod)
   — fixed in `cli-market-core` 1.11.92 (see that repo's own changelog for the
   4 new `@router.get` handlers + `market_price_forecast.py`/
   `market_arbitrage.py`).
2. **This repo's `routers/mcp_http.py`** (the production HTTP MCP transport —
   separate surface from `cli-market-core`'s stdio server, see the
   two-MCP-surface architecture note in `9083a59d`) had **no dispatch case at
   all** for these 4 tool names — they fell through to `{"error": "Unknown
   tool"}` regardless of what `cli-market-core` did. Fixing only the core
   package would not have fixed what Cursor (an HTTP MCP client) actually
   sees. Added the 4 missing `elif name ==` branches in `_call_tool()`, same
   `client.get(f"{_API_BASE}/v1/intel/...", params=...)` pattern as their
   neighbors, and gated all 4 as `pro` tier in `_PRE_CHECK_TIER` (same
   structural gap as `market_procurement_signal`/`market_price_risk`: the
   `cli-market-core` endpoint only checks `Depends(_require_v1_auth)`, no
   billing tier concept, so this repo must self-enforce).

Also closes 3 P1 correctness findings from the same investigation, all fixed
upstream in `cli-market-core` 1.11.92: `market_optimize_purchase` resolving
one requested SKU to 3 different products across response sections;
substitutes crossing dairy subcategory (mantequilla → queso crema,
`confidence: "ok"`); and a 500 (should be 422) on malformed
`procurement-bulk` input. Full detail in `cli-market-core/CHANGELOG.md`'s
2026-07-30 entry.

**Deployed** (superseded by 1.11.93 above, but confirming this specific
release reached production first): `cli-market-core` 1.11.92 published to
PyPI via tag `v1.11.92`, `cli-market-api` redeployed same session. Verified
live: `curl https://cli-market-api.fly.dev/v1/intel/basket-stress?country=PE`
(and `/pulse`, `/forecast`, `/arbitrage`) all returned `401` — not `404` —
confirming the 4 routes exist in production.

## [2026-07-29] — chore(deps): bump cli-market-core pin to 1.11.91 (WooCommerce full-catalog Playwright fallback, fixes 2/5 `doctor_prod_gate.py` dead stores)

Follow-up to today's dashboard-OOM incident's "not yet done" list
(`ops/doctor_prod_gate.py` failing on 5 dead stores, `MAX_DEAD_SOURCES=0`).
Root-caused in `cli-market-core`: `igardi_pe` and `granjaorganicabudi_cl`
WAF-block plain `httpx` on the WooCommerce full-catalog batch endpoint with
a flat 403, and the connector's Playwright fallback (already working for
`search()`) was never wired into that path — silently returning 0 products
every cycle. Fixed upstream (`cli-market-core` 1.11.91, full writeup in that
repo's own changelog), verified live: `granjaorganicabudi_cl` 0 → 84
products, `igardi_pe` 0 → 100.

The remaining 3 dead stores (`smartnutrition_pe`, `simplynaturalcanada_ca`,
`thegreenkiss_ca`) all succeeded when queried directly from a non-Fly.io IP
— looks like Fly.io's datacenter IP range gets blocked more aggressively
than a residential/office one, not a code bug. Left open, not fixed here.

**Deployed**: `flyctl deploy --app cli-market-collector --config
fly.collector.toml --build-secret github_token=$(gh auth token)` run same
day (same gap as the 2026-07-27/07-28 incidents — a git-side pin bump alone
doesn't reach the running Fly machine). Confirmed via `pip show
cli-market-core` on the live machine: `Version: 1.11.91`. Both machines
healthy post-deploy.

**Status when this session ended — pick up here next time:**
- `ops/doctor_prod_gate.py` still reported `5 dead stores` immediately
  after the redeploy — **expected, not a failure**: the fix only takes
  effect on the collector's *next* full-catalog cycle
  (`COLLECT_CATALOG_INTERVAL`, default 60 min), which hadn't run yet.
- Even once `igardi_pe`/`granjaorganicabudi_cl` start succeeding every
  cycle, `doctor_prod_gate.py`'s "dead" classification
  (`source_health.store_health_state()` in `cli-market-core`) is a
  **lifetime** success ratio, not a recent window — months of accumulated
  0%-success history means the average will climb slowly, not flip to
  "ok" after one good cycle. Don't read a still-red gate a day from now as
  "the fix didn't work" without checking whether `granjaorganicabudi_cl`/
  `igardi_pe` individually show recent successes via
  `GET /v1/sources/health` (`last_success`, `consecutive_failures` reset
  to 0) even while `success_pct` is still climbing.
- **To verify**: `GET https://cli-market-api.fly.dev/v1/sources/health`,
  check `igardi_pe` / `granjaorganicabudi_cl` for `last_success` newer than
  this deploy and `consecutive_failures: 0`. Full gate green requires their
  lifetime `success_pct` to climb back above 30% (dead threshold) — will
  take multiple cycles, not one.
- **Separate, not-yet-scoped follow-up**: `store_health_state()`'s
  lifetime-average design is the same "buries recent reality" failure
  mode already flagged twice for `coverage_7d_pct` (2026-07-27 entry
  below, and `cli-market-core`'s own changelog) — worth considering a
  recent-window (e.g. 7d) variant for the dead/ok classification too,
  not done here.
- The 3 IP-reputation-blocked stores (`smartnutrition_pe`,
  `simplynaturalcanada_ca`, `thegreenkiss_ca`) are still unaddressed —
  no code fix attempted, since the working theory (Fly.io datacenter IP
  blocked, not a connector bug) doesn't have an obvious fix without
  routing those specific stores through the Playwright fallback too (or
  a proxy/residential-IP path), which is a larger change.

## [2026-07-29] — `/dashboard/data` OOM fix (root cause of the 0%-coverage Command & Control report)

Investigating "is the collector operational?" (it was — 325/325 stores, ~4h
fresh data) surfaced the real problem: `GET /dashboard/data` was 502'ing and
a `cli-market-api` Fly machine got OOM-killed (`Out of memory: Killed process
659 (python)`) — full incident writeup in
[`docs/incident-2026-07-29-dashboard-oom.md`](docs/incident-2026-07-29-dashboard-oom.md).

- `routers/dashboard.py` fetched the full `price_snapshots` table (150K+
  rows) into Python memory **3 times** per request (`spread_rows`,
  `price_rows`, and a second dict-list conversion for outliers) — collapsed
  into a single fetch (`spread_products`) reused across dispersion, P25/P50/P75
  percentiles, and outlier detection.
- Added `pg_advisory_lock` around the shared-cache-miss compute path
  (`_compute_dashboard_data_locked()`) so the app's 2 Fly machines can't both
  pay the full recompute cost in parallel on cache expiry — the likely trigger
  for the exact OOM moment (one machine timed out waiting on the endpoint
  while the other died from OOM ~50s later).
- `fly.toml`: VM memory `1024mb → 2048mb` as immediate headroom.
- Hit the same circular CI gate as the 2026-07-25 incident (`smoke-production`
  checks `/dashboard/data` against the live, still-broken prod, blocking the
  auto-deploy that would fix it) — resolved with a manual `flyctl deploy` from
  this repo, then verified live: `coverage_7d_pct` 0% → 88.3%,
  `collector_stale: false`, `market_dashboard` MCP tool responds cleanly.
- Full suite green (1070/1071; the 1 failure is pre-existing/unrelated,
  `test_canonical_copy.py`).
- **Not fixed here** (separate, pre-existing issue): CI's `doctor_prod_gate`
  still fails on 5 dead stores + Golden linkage at 71.8% (matches the linkage
  regression already flagged in today's Command & Control report) — see
  Follow-ups in the incident doc.

## [2026-07-28] — chore(deps): bump cli-market-core pin to 1.11.90 (Shopify variant-title fix for organix_pe unit-normalization)

Follow-up to yesterday's stale-collector-deploy incident (below): pins
the fix for `organix_pe`'s ~3% unit-normalization (Shopify catalogs that
put pack size only on the variant selector, never the product title —
see `cli-market-core`'s own changelog for the full writeup). After
merging this pin, redeploy `cli-market-collector` on Fly.io
(`fly deploy --app cli-market-collector --config fly.collector.toml
--build-secret github_token=...`) — a git-side pin bump alone does not
reach the running machine, exactly the gap that caused yesterday's
incident.

## [2026-07-27] — `cli-market-collector` Fly.io deploy was 3 days stale, silently missing the entire 217-store batch

Routine ask ("did the collector finish its run and are stats updated?")
surfaced a real production gap: `market_stats` looked healthy
(110 tracked stores, snapshot from minutes ago), but `market_stores`
listed 325 registered retailers and `market_coverage_matrix` showed
`supermercados`/`hogar` freshness stuck at 43–57% instead of the ~90%+
seen on other lines.

**Investigation, narrowed store by store:**
- Cross-referencing `market_stores` against the coverage matrix's
  `supermercados×PE` cell (13 tracked) found 15 registered stores —
  `delcampoatucasaperu_pe` and `organix_pe` had zero price snapshots
  ever (`market_retailer_scorecard` → `insufficient_data` on every
  section).
- Ruled out "site is down": `WebFetch` against both stores' live
  catalog endpoints (`delcampoatucasaperu.com/wp-json/wc/store/v1/products`,
  `organix.pe/products.json`) returned well-formed product JSON,
  right now, from both.
- Ruled out "stale PyPI pin": `cli-market-world/requirements.txt` was
  already pinned to `cli-market-core==1.11.89`, current as of this
  session.
- Also found and ruled out as the direct cause (but worth a separate
  fix): the "coverage_7d_pct" per-store metric in
  `cli-market-core`'s `source_health.py` (surfaced through
  `market_retailer_scorecard`) is `snapshots_7d ÷ store's all-time
  total_snapshots` — a ratio that reads low for old/high-volume stores
  (wong, metro, plazavea all showed 44–50% despite `success_pct: 100%`
  and a `last_success` from minutes earlier) purely because of
  accumulated history, not actual staleness. This is the same
  ambiguous-name problem already fixed once today in
  `health_stats.py`'s *different* `coverage_7d_pct` (see the tier-gating
  entry above and cli-market-core's own changelog) — the rename never
  reached this second, store-level copy of the metric. Follow-up:
  apply the same `active_stores_coverage_7d_pct`-style rename here.
- **Root cause found via `flyctl`, not code inspection**:
  `flyctl releases -a cli-market-collector` showed the last deploy
  (v45) was `2026-07-24 20:52` — 3 days before the 217-store batch
  (`cli-market-core` 1.11.76 → 1.11.85) merged on 2026-07-26.
  `flyctl ssh console -a cli-market-collector -C "pip show
  cli-market-core"` confirmed the running container had
  `Version: 1.11.76` — the exact version the batch started from. The
  git-side dependency pin was correct and up to date; nobody had
  redeployed the Fly machine since. Every one of the 217 new stores
  across all rounds was invisible to the live collector, not just the
  two caught here.

**Fix**: `flyctl deploy --app cli-market-collector --config
fly.collector.toml --build-secret github_token=$(gh auth token)` from
a fresh clone (the checked-out working copy in use was missing
`Dockerfile.collector`/`fly.collector.toml` due to sparse-checkout).
New release v46 confirmed via `pip show cli-market-core` →
`Version: 1.11.89`. Machine healthy post-deploy
(`Machine ... is now in a good state` on both the primary and standby).

**Also found, not yet fixed**: `db-lock-monitor.yml`'s
`ops/db_lock_monitor.py --slack` run fails with `Slack API error:
channel_not_found` (`SLACK_CHANNEL_ALERTAS` misconfigured/empty) on
every run, which trips `exit code 1` and surfaces `##[warning]DB lock
or collector staleness detected` in the Actions UI — even on runs
where the actual check result was `collector: fresh`. This has been
crying wolf on every ~25-min run; worth fixing the Slack channel
config before anyone trusts that warning again.

**Follow-up (pending)**: verify after the collector's next few 4h
cycles (`COLLECT_INTERVAL_HOURS=4`) that `market_stats` /
`market_coverage_matrix` / `market_retailer_scorecard` show snapshots
for `delcampoatucasaperu_pe`, `organix_pe`, and the rest of the
217-store batch.

## [2026-07-27] — Real tier gating for 12 MCP tools (a live Starter-account smoke test found the [Pro]/[Enterprise] labels were purely aspirational)

A real Starter-tier account (registered + email-verified for this
purpose, revoked after) got `HTTP 200` from every single `[Pro]`-labeled
tool tested via `/mcp` — both the tools added earlier today and several
pre-existing ones (`market_favorites`, `market_add`, `market_ecosystem_radar`).
Investigated whether this was intentional (generous trial?) — it isn't.
`require_pro`/`require_starter`/`require_export` are real, actively-used
gates elsewhere (`routers/intel.py`, `routers/analytics.py`,
`routers/data_export.py`); the endpoints backing these 12 tools just
never called them.

- `routers/brand_intel.py` — swapped `require_api_key` → `require_pro`
  on all 4 Brand Monitor endpoints (world-native, fixed directly at
  the source).
- `routers/mcp_http.py` — new `_pre_check_tier()`, enforced in
  `_call_tool()` before the backend request, for the 7 tools backed by
  `cli-market-core`'s shared `api_routes.py` (`Depends(_require_v1_auth)`
  only — that package has no billing/tier concept, so it structurally
  can't self-enforce: `market_receipts`, `market_quality_scores`,
  `market_quality_flagged`, `market_dispersion`, `market_coverage_matrix`,
  `market_prices`, `market_basket_snapshot`) plus `market_procurement_bulk`
  (enterprise). Real per-endpoint tier checks elsewhere are untouched.
- New tests simulate a real non-admin Starter caller (the "admin" test
  identity always bypasses tier checks via `is_platform_admin`, which
  only reads a real `MARKET_API_TOKEN` env var in production — not in
  tests, so most existing tests needed a `db_set_subscription("admin",
  "enterprise")` fixture to keep working now that these paths actually
  check tier). Full suite green (1054 passed; 8 pre-existing unrelated
  failures).
- **Verified live**: registered a second real Starter account against
  production, called `market_prices`/`market_brand_monitor`/
  `market_procurement_bulk` through `/mcp` — all three now correctly
  return `isError: true` with the right message (`pro_required` for the
  first two, `enterprise_required` — not `pro_required` — for the last).
  Revoked the test account afterward.

**Deliberately NOT touched**: `market_favorites`, `market_add`/`cart`,
`checkout`, `market_ecosystem_radar`, and other older tools found to
have the same gap during the investigation — those sit on live
revenue/checkout paths and need explicit product sign-off before
changing tier requirements, separate from this fix.

**`MARKET_USER_TOKEN` fixed** — the PAM `user` phase was failing `401`
across the board (`user.whoami`, `user.search`, `user.v1_prices`, etc.)
because the GitHub Actions secret held a stale/invalid `sk-...` key,
unrelated to this session's `MARKET_API_TOKEN` (admin) rotation.
Registered a fresh account (`hello+pam@cli-market.dev`, real email +
OTP verification, kept — not a throwaway), stored its key as the new
`MARKET_USER_TOKEN` secret. First local re-run surfaced a second real
issue: `user.intel_brief` / `user.intel_inflation` (pre-existing
`require_pro`-gated routes, untouched by this fix) returned `403`
because the fresh account only had a default Starter trial — the PAM
matrix's `expect: status 200` assumes a Pro-tier account. Granted Pro
via `POST /v1/admin/set-tier` (admin-only, `MARKET_API_TOKEN`).
Re-ran `ops/production_acceptance.py --phase user --tier 1` locally:
**15/15 PASS**. `MARKET_API_TOKEN` re-synced to GitHub Actions after
being regenerated for this admin call (same write-once-then-delete
handling as the rest of this session's token rotations).

## [2026-07-27] — Gap analysis + fixes on the HTTP MCP transport: 3 tier-gating bugs fixed, 8 new tools (6 here + 2 shared), full dispatch-table test coverage (12% → 100%)

Follow-up to the same-day entry below, which only mirrored the wave-5
tools into `routers/mcp_http.py`. This entry covers a dedicated gap
analysis of that file (never analyzed on its own before) plus fixes.

**Tier-gating bugs fixed (`routers/mcp_http.py`)**
- `market_procurement_bulk` was tagged `[Enterprise]` in its description
  but gated in `_PRO_TOOLS` — a caller below Enterprise got a Pro-plan
  upsell message that wouldn't actually unlock the tool. Moved to a new
  `_ENTERPRISE_TOOLS` set with its own `_ENTERPRISE_UPGRADE_MSG`.
- `market_intel_refresh` / `market_enrichment_refresh` were tagged
  `[Admin]` (same as `market_scan`) but were still in `_PRO_TOOLS`,
  contradicting the file's own docstring ("Admin... no upgrade prompt
  applies"). Removed from `_PRO_TOOLS` — matches `market_scan`.
- `market_household_get` was tagged `[Starter]` but wasn't in any
  gated set, so a 403 from insufficient tier reached the caller as a
  raw `HTTP 403` instead of a friendly message. Added a new
  `_STARTER_TOOLS` set with `_STARTER_UPGRADE_MSG`.

**8 new MCP tools** (2 shared with `cli-market-core` 1.11.87, 6 world-only):
- `market_prices` (`GET /v1/prices`), `market_basket_snapshot`
  (`GET /v1/basket`) — same REST endpoints exposed in
  `cli-market-core`'s registry this same day (see that repo's
  CHANGELOG). Pro tier.
- `market_brand_monitor`, `market_brand_monitor_promos`,
  `market_brand_monitor_config`, `market_brand_monitor_alerts` — a
  complete, previously-unexposed product surface:
  `routers/brand_intel.py` (490 lines, cross-store SKU/competitor
  monitoring, promo history, PVP deviation alerts), world-only (no
  cli-market-core equivalent — the feature isn't in the shared
  package). Pro tier.

**Dispatch-table test coverage: 7/59 (12%) → 71 tests covering all 65
tools (100%)** — the same class of gap that let `market_discover`,
`market_price_risk`, and `market_price_alerts` ship broken silently
before (see file docstring). Added:
- Parametrized dispatch tests for every simple GET/POST tool.
- Dedicated tests for tools with non-trivial dispatch logic:
  `market_basket` (include_tco default), `market_exchange` (payload
  field remapping), `market_household_update` (PUT vs PATCH),
  `market_dashboard` (slim param logic), `market_discover`
  (3-request composition), `market_cart_update`/`market_alert_delete`
  (PUT/DELETE), `market_ticket`/`market_voice`.
- Tier-gating regression tests for all three new upgrade-message paths.
- `test_all_tools_have_dispatch_and_all_dispatch_branches_are_registered`
  — a structural test using `inspect.getsource` + regex to diff
  `_TOOLS` names against every `elif name ==` branch in `_call_tool`,
  in both directions. This is the actual regression guard against the
  historical bug class — future drift between the schema list and the
  dispatch table now fails CI immediately instead of shipping silently.

Full local suite run before push; PyPI 1.11.87 published, pin bumped,
`ops/sync_market_stats.py` re-run (legacy 74→76, full 71→73).

**Verified live** — commit `0d0849a9` pushed → CI green (1041 passed,
9 pre-existing unrelated failures) → Deploy Fly.io green → confirmed
directly against production: `POST /mcp` (`tools/list`) now returns
59 → 65 tools with all 6 new names present; `GET /.well-known/mcp.json`
returns `profiles.legacy.tool_count: 76`.

## [2026-07-27] — 5 new MCP tools (quality/receipts/coverage), and a discovered architecture split: two independently-maintained MCP tool surfaces

A gap analysis of the MCP tool registry found 5 REST endpoints
(`/v1/receipts`, `/v1/quality/scores`, `/v1/quality/flagged`,
`/v1/dispersion`, `/v1/coverage/matrix`) that already had real handlers
in `cli-market-core/market_core/api_routes.py` but no MCP tool exposing
them. Implementing them surfaced a bigger fact worth recording: **there
are two separate, independently-maintained MCP tool surfaces**, not one.

- `cli-market-core/market_core/market_mcp_registry.py` — the canonical
  registry used by the **stdio MCP server** (the `cli-market-core` PyPI
  package, used by local CLI/agent integrations). Profile-based
  (`default`=44, `legacy`/`full`/`admin`), generic lambda dispatch.
- `cli-market-world/routers/mcp_http.py` — a fully independent,
  hand-maintained **HTTP MCP transport** (`POST /mcp` on
  `cli-market-api.fly.dev`, used by claude.ai, Cursor, VS Code, Kiro,
  Codex, Gemini). Does NOT import the cli-market-core registry at all.
  This is intentional, not tech debt: it originated in
  `cli-market-backend` (`routers/mcp_http.py`, ported over in #298,
  2026-06-22, "consolidate backend-only features into world") because
  the HTTP transport needs per-tool subscription-tier gating
  (free/Pro/Admin), funnel-event logging, and per-tool timeout tuning
  that don't fit the registry's generic dispatch pattern. It currently
  exposes more tools (54, pre-this-change) than the stdio default
  profile (44), including some with no registry equivalent at all
  (`market_macro`, `market_dashboard`, `market_alert_create/delete`).

Net effect: a new MCP tool added only to `market_mcp_registry.py` does
**not** reach the production HTTP endpoint — it must be added to both
surfaces separately. Did that for this batch:

- cli-market-core 1.11.85 → 1.11.86: added `market_receipts`,
  `market_quality_scores`, `market_quality_flagged`,
  `market_dispersion`, `market_coverage_matrix` to
  `market_mcp_registry.py` (bundle `advanced`, hidden from `default`
  profile — stays at 44) and `market_mcp.py` dispatch. `TOOLS` 69→74,
  `ORIGINAL_TOOL_NAMES` 63→68. Full suite green (706 passed, 3
  skipped). Published to PyPI.
- `cli-market-world/requirements.txt` and `cli-market-backend/requirements.txt`
  pins bumped to 1.11.86 (backend repo is frozen/deprecated but kept in
  sync for history — do not deploy from it).
- `cli-market-world/routers/mcp_http.py`: same 5 tools added to `_TOOLS`,
  `_PRO_TOOLS` (gated Pro, consistent with similar niche intel tools
  like `market_retailer_scorecard`/`market_promo_detector`), and
  `_call_tool` dispatch. New parametrized tests in `tests/test_mcp_http.py`.
  This is the file that actually matters for production — deployed via
  `deploy-fly.yml` (workflow_run after CI green).

**Verified live** — full local suite green before push (978 passed; the
9 failures seen were pre-existing and reproduce identically with these
changes stashed out: an untracked local `Clippings/` dir tripping the
stale-copy-text test, `test_playwright_fallback.py`'s async fixtures,
one `test_market_observatory_local.py` flake, and an `e2e_test.py`
error needing a live server — none touch MCP code). Commit `8d9c692f`
pushed → CI green → Deploy Fly.io green → confirmed directly against
`POST https://cli-market-api.fly.dev/mcp` (`tools/list`): tool count
54 → 59, all 5 new names present.

**Discovery docs sync (commit `e9caa4df`)** — `mcp.json` (root +
`landing/public/`), `glama.json`, `landing/public/mcp-tools-registry.csv`,
and `landing/lib/marketStats.ts` were still describing the
`market_mcp_registry.py` counts from before this batch. Ran
`ops/sync_market_stats.py` to regenerate all of them against the
already-live `cli-market-core` 1.11.86: legacy 69→74, full 66→71 (the
curated default profile correctly stays 44 — the 5 new tools are
deliberately hidden from it). Verified live at
`https://cli-market.dev/mcp.json`.

**Docker image gap found + fixed (commit `02d4c3fd`)** — while
verifying the API's own `/.well-known/mcp.json`, found it always
served the generic inline fallback from `routers/discovery.py`
instead of the real, richer `mcp.json` — the `Dockerfile` only ever
`COPY`ed `*.py` and `pyproject.toml`, never `mcp.json`, so the file
was never present in the deployed image regardless of how well-synced
the git-tracked copy was. Pre-existing, unrelated to this session's
tool addition — just surfaced while checking the fix end-to-end. Added
`mcp.json` to the `COPY` line; verified live at
`https://cli-market-api.fly.dev/.well-known/mcp.json` now returns the
full `profiles`/`bundles`/`tools_legacy` payload (legacy tool_count 74)
instead of the stripped-down fallback.

## [2026-07-26] — 217 new stores across 30 countries + a critical STORES import regression found and fixed in production (cli-market-core 1.11.76→1.11.85, cli-market-world, cli-market-backend, cli-market-index, procure-copilot, cli-market-content)

Started as "index more organic-product retailers in Argentina" and grew
into four store-indexing rounds (organic food, non-food organic,
leather goods, dedicated Bsale research) across 30 countries, plus a
full ecosystem sync-and-verify pass that surfaced a production-breaking
regression nobody had caught. `cli-market-core` STORES went 103 → 360;
version 1.11.76 → 1.11.85 (skipping 1.11.83, see below).

**Store indexing, four rounds (cli-market-core 035081d, 889fb8f, a9d74fb)**
- Round 1 — organic/natural food retailers: AR, BR, UY, PY, CO, EC, CL,
  MX, US, ES. 78 stores added (WooCommerce/Shopify/VTEX/magento_graphql),
  each verified end-to-end via the real connector's `search()` (not
  curl) — a real product name + correct price in local currency, not
  just "the platform string appears in the HTML." New Garden AR added
  via the existing `magento_graphql` connector (its REST API needs an
  integration token, but `/graphql` is public) instead of writing a new
  connector. Venezuela and most of Paraguay yielded ~0 candidates —
  confirmed there's essentially no e-commerce there on a supported
  platform (WhatsApp/social dominate instead).
- Round 2 — non-food "organic line" retailers (cosmetics, apparel,
  home/cleaning) in the same 10 countries, at the user's explicit
  request to distinguish these from food/grocery. 49 stores added, kept
  on `line=belleza/moda/hogar` instead of `supermercados` so they don't
  pollute basic-basket searches (precedent: `valorable_co`, Colombian
  organic-cotton apparel).
- Round 3 — 11 more countries (BO, PE-organic-specific, PA/CR/GT, CA,
  GB, DE, FR, IT, NL): 51 stores across food + non-food in one pass.
  Bolivia yielded 0.
- Round 4 — leather goods (consumer → `moda`, B2B tanneries/hide
  suppliers → `industrial`) across all 20 countries already covered:
  74 stores, 58 moda + 16 industrial. Two cross-country corrections
  caught during verification: a store surfaced in a Venezuela search
  but its Store API returned ARS (filed under AR instead); a Peru
  candidate's API returned CLP (filed under CL).
- Consistent finding across every round: initial research always
  produces false positives (Tiendanube/PrestaShop/Wix/Jumpseller/
  Ecwid mentioning a supported platform's name only in a third-party
  script) and a handful of real failures research alone can't catch
  (price=0 across an entire catalog on wholesale-only stores, wrong
  currency, catalogs that turn out to be B2B raw materials not finished
  consumer goods). Every store in this session was verified against the
  actual connector's `search()`/`normalize()`, not just curl.

**Dedicated Bsale platform research (cli-market-core a9d74fb)**
- Every earlier Bsale candidate in every round above was a false
  positive (Wix/Shopify/Tiendanube mentioning "bsale" only in a
  third-party payment/analytics script) — the platform had exactly 1
  registered store (`datilerabiomarket_pe`) despite being originally
  Chilean. Sourced candidates from Bsale's own published client list
  (`bsale.cl/sheet/clientes`) instead of generic search, which is what
  finally cut through the noise. 4 new Chilean stores confirmed against
  the connector's actual endpoint (`GET {base}/collection/details/
  {slug}` → JSON with `window.INIT.collections.push(...)`): tactical
  gear, collectible rubber ducks, women's footwear, dried fruit/nuts.
  Platform now has 5 stores, not 1.

**BigCommerce connector theme-variant fix (cli-market-core a9d74fb)**
- `market_connectors/bigcommerce.py` only parsed one Stencil theme
  variant (ssa-peru.com's "with-tax" pricing, href-first `<a>` tags).
  A second real variant (maggiesorganics.com) puts other attributes
  before `href` and uses tax-exclusive pricing markup — the original
  regexes silently returned zero tiles on stores using this variant.
  Both regexes now tolerate attribute order and the with/without-tax
  class variants; verified this doesn't regress the original
  ssa-peru.com fixture. Added `maggiesorganics_us`.
- Documented but explicitly not fixed: `buckleguy.com` and other
  Makeswift-hydrated BigCommerce stores have no product markup in the
  server-rendered HTML at all (client-side JS hydration) — needs a
  headless-browser fallback, not a parsing fix.

**Critical regression: `from market_core import STORES` broken since 1.11.7x (cli-market-core e01845e, 955276c)**
- Found while running `cli-market-backend`'s test suite after the store
  batch: 25 test modules failed collection with `ImportError: cannot
  import name 'STORES' from 'market_core'`. Root cause: commit
  `2529d54` ("remove duplicate store_color/currency defs shadowing
  canonical exports") dropped the actual duplicate definitions but also
  deleted the one working `from .market_stores import STORES`
  re-export alongside them — collateral damage in an otherwise correct
  cleanup. Confirmed via a fresh venv install from PyPI: every published
  version from ~1.11.7x through 1.11.83 was broken for any consumer
  importing `STORES` at the package level, which `cli-market-backend`
  does directly in `routers/agent.py`, `market_server.py`, and
  `routers/search.py`.
- Restored the re-export with a comment explaining why it must not be
  removed again. **1.11.83 was tagged and published to PyPI *before*
  this fix landed** (fix came in a follow-up commit after the tag), so
  that specific published version still has the bug — republished as
  **1.11.84** with the fix actually included. Confirmed via
  `cli-market-world`'s CI, which failed with the exact same error
  against 1.11.83 and passed clean against 1.11.84.
- Net effect: any clean deploy of `cli-market-backend` (not relying on
  a stale cached wheel from before `2529d54`) would have failed to
  start. `cli-market-world`'s automated Fly.io pipeline had also been
  silently skipping deploys (gated on CI, which was failing on the same
  import) — confirmed the full pipeline (sanity-check imports → deploy
  → post-deploy smoke test) went green end-to-end once 1.11.84 was
  live, and the production API (`cli-market-api.fly.dev`) is confirmed
  serving all 360 stores.

**`e2e_test.py` bit-rot, 4 separate bugs (cli-market-world 555b06b5)**
- Not wired into any CI workflow, so nothing had caught these. Found
  while re-running it after the stats sync: (1) `cmd_compare`'s test
  call was missing `store=None` in its `Namespace` — the one crash
  originally reported; (2) the fixed 3-second server-startup sleep was
  too short now that DB init time scales with catalog size (355+ stores
  took ~7s cold-start, was ~103-150 stores when the constant was
  chosen) — replaced with a 30×1s poll loop; (3) that poll loop needed
  to catch `httpx.TransportError`, not just `ConnectError` — a bound
  socket that isn't fully serving yet can time out instead of refuse;
  (4) `market_cli.API = "..."` silently did nothing — `api()`/`cli_api()`
  live in `market_core.market_core` and read that module's own `API`
  global (populated from `MARKET_API_URL` once at import time), never
  `market_cli`'s — every "local" run of this script was actually
  hitting production for every authenticated call. Fixed by setting
  `MARKET_API_URL` before the first `market_core` import instead. All
  11 steps now pass end-to-end with zero unintended production traffic.

**Stats sync across the ecosystem (cli-market-world f5636bcd, cli-market-index f92997d, procure-copilot 2eb6abb, cli-market-content b1066b8)**
- Ran `ops/sync_market_stats.py` to propagate the new store/country
  counts everywhere they're quoted: `marketStats.ts`, README, MCP
  registry (`server.json`/`mcp.json`), social-preview assets, LinkedIn/
  HN content templates, and `cli-market-index`'s `canasta_data.py`
  (formatting-only diff, no data change).
- Caught a test-fixture contaminating live stats: a leftover dev-DB row
  (`test_gd_peer2`, name "X", created 2026-07-22 by an unrelated
  session) was merging into `get_all_stores()`'s DB-primary read and
  showing up in the public WooCommerce-store-count list. Deleted.
- `procure-copilot` was badly stale (82 retailers / 9 countries vs. the
  real 355 at time of sync) — its `stats-sync.yml` CI only triggers on
  push/PR touching `lib/market-stats.ts` itself, so with nothing else
  ever touching that file, drift went undetected indefinitely. Added a
  weekly `schedule` cron (+`workflow_dispatch`) so the existing
  validation now runs proactively instead of only reacting to a change
  nobody was making.
- `cli-market-content`'s marketing copy sync also propagated a Pro
  price correction ($49 → $39) that wasn't new — `cli-market-core`
  fixed that stale default back in `708a98e` (#157), this repo just
  hadn't been re-synced since; same source of truth
  (`PUBLIC_PRO_PRICE_USD`) now consistent across GTM-Hub,
  revenue-architecture, one-pagers, and email templates.

**`tests/test_andean_panel.py` false failure, not a regression (cli-market-core 889fb8f)**
- The test hardcoded Ecuador as `macro_only` in the CAF Andean
  affordability panel. Round 1's new EC `supermercados` stores made
  `_country_has_retail_channel` correctly report EC as
  `retail_and_macro` — updated the assertions to match reality instead
  of leaving a real behavior change failing CI.

**Known follow-ups (not done this session)**
- Tiendanube support: evaluated and explicitly declined. No public
  unauthenticated API (`api.tiendanube.com` 401s without a per-store
  OAuth token, unlike the WooCommerce Store API / Shopify
  `products.json` every existing connector relies on) — the only path
  is per-product HTML scraping via the storefront sitemap, no bulk JSON,
  much heavier than any existing connector. Would unlock a meaningful
  number of stores excluded this session (mostly AR/UY/BR organic and
  leather retailers — Tiendanube dominates small/mid retail in the
  Southern Cone), but the maintenance cost was judged disproportionate.
  Revisit only if the calculus changes (e.g. Tiendanube ships a public
  read API).
- `cli-market-backend` is frozen/deprecated as of 2026-07-25 (one day
  before this session) — confirmed via its `fly.toml`, which
  deliberately uses a fake app name to block accidental deploys. Still
  received the version-pin bump for correctness/dependency-graph
  reasons, but the real production path is `cli-market-world`'s
  automated Fly.io pipeline.

## [2026-07-21] — Pricing-tier repricing review → full auth/security audit of the Intelligence catalog (cli-market-world)

Started as a pricing/revenue review of the 9 market-intelligence tools
(inflation, cost-of-living, scores, dashboard) sitting in the Base/free
tier while Pro was mostly consumer-transactional. Checking why
`market_whoami` was orphaned surfaced that several "Pro" tools returned
raw HTTP errors instead of upgrade prompts — pulling that thread found
the real root cause: multiple backend endpoints had no authentication
at all. Widened into a full audit of the 54-tool MCP catalog. 8 commits,
`683bedbb..75bccd2b`, all pushed to `main`; full suite green (964
passed) at every step. Full writeup: `docs/reports/SECURITY-AUDIT-2026-07-21.md`.

**Unauthenticated `cli-market-core` data endpoints (18 routes, commits `683bedbb`, `ee5d0926`, `dab77652`)**
- `market_server.py` mounts the pip-installed `cli-market-core` router at
  `/v1`; several of its handlers ship without `Depends(_v1_auth)` —
  plain public functions. A pre-existing workaround
  (`_CORE_INTEL_AUTH_PATHS` + `core_intel_api_key_gate` middleware)
  covered only 3 of them. Extended it to the other 15: `/v1/intel/{affordability,alerts,informal-signal,promo-detector,retailer-scorecard,andean-panel}`,
  `/v1/basket/{compare,tco}`, `/v1/products/substitutes`,
  `/v1/ecosystem/launches`, `/v1/quality/scores`, `/v1/health/slas`,
  `/v1/health/slas-summary`, and `/v1/receipts/{receipt_id}` (prefix
  match, not exact-path).
- Worst single finding: `GET /v1/receipts/{receipt_id}` returned
  `username` + `image_url` + full OCR line items for any guessable
  8-hex-char id, with **no ownership check** in `get_receipt()` — a real
  IDOR, not just a missing-auth gap.
- Also fixed: the gate middleware was registered *after*
  `CORSMiddleware` (Starlette makes the last-registered middleware the
  outer layer), so a browser's `OPTIONS` preflight to any gated path got
  a bare 401 with no CORS headers before `CORSMiddleware` ever answered
  it — added an `OPTIONS` bypass.
- Verified by a dedicated `security-reviewer` pass (not just self-review)
  before shipping; that pass is what surfaced the receipts IDOR and the
  CORS ordering bug.
- Root cause lives upstream, not in this repo — filed
  [`Treevu-ai/cli-market-core#160`](https://github.com/Treevu-ai/cli-market-core/issues/160)
  asking for `Depends(_v1_auth)` at the source plus a receipt-ownership
  check, so the hand-maintained path list in `market_server.py` (which
  already drifted once) can be deleted once the pin bumps.

**Dependency CVE (commit `41b4a03f`)**
- Dependabot alert #62: `sharp` (npm, `landing/package-lock.json`,
  transitive via Next.js image optimization) — libvips CVEs
  (GHSA-f88m-g3jw-g9cj, high). Pinned to `0.35.3` via `overrides`. Alert
  auto-closed on push.

**MCP catalog Free/Pro documentation mismatch (10 tools, commits `defbef22`, `6ebf6243`)**
- `routers/mcp_http.py`'s `_PRO_TOOLS` set controls whether a backend
  402/403 gets rewritten into a friendly upgrade message. 10 tools were
  documented as Free (no `[Pro]` tag) while their backend actually calls
  `require_pro()`, so free/trial callers got a raw passthrough error
  instead: `market_promo_detector`, `market_retailer_scorecard`,
  `market_informal_signal`, `market_inflation`, `market_scores`,
  `market_macro`, `market_intel_brief`, `market_indicators`,
  `market_trending`, `market_affordability`. Found by cross-referencing
  every untagged tool's dispatch endpoint against its real backend auth
  requirement in `routers/intel.py` / `routers/analytics.py`. All 10
  added to `_PRO_TOOLS` and tagged `[Pro]`.
- Surfaced by a real GTM artifact: a sales-demo script opened on
  `market_promo_detector` as the hook step — before this fix, that step
  would have shown a raw HTTP error at the exact moment meant to hook a
  prospect.

**Unauthenticated compute-abuse vector + a mislabeled admin tool (commit `75bccd2b`)**
- `/v1/ticket/scan(-url)` and `/v1/voice/transcribe(-url)` ran
  `tesseract`/`whisper` subprocesses (up to 60s) for any unauthenticated
  caller — a free-compute/cost-abuse vector, not a data leak (SSRF was
  already mitigated via `validate_public_http_url`). Gated all four with
  `require_api_key`, matching the rest of the API's baseline. Updated
  `tests/test_media.py` / `tests/test_security.py` accordingly.
- `market_scan` sat in `_PRO_TOOLS` despite its backend requiring
  `require_admin` (`MARKET_API_TOKEN`), not a paid tier — description
  was already correctly `[Admin]`-tagged, so this was dead/misleading
  bookkeeping, not a live bug. Removed from `_PRO_TOOLS`.

**GTM narrative cross-check (commit `7d1611f6`)**
- Cross-checked three sales narratives (B2C, Fintech, Enterprise) against
  actual tool tiers. Headline: the B2C "free copilot" pitch is built
  almost entirely on `[Pro]`-gated tools (`optimize_purchase`, `basket`,
  `alert_create`, `household_update`) — should be marketed as Pro
  ($39/mo), not as a free hook. Full narrative-by-narrative breakdown in
  `docs/reports/GTM-NARRATIVES-B2C-FINTECH-ENTERPRISE.md`.

**Known follow-ups (not done this session)**
- Upstream fix for the 18 `cli-market-core` endpoints —
  [`cli-market-core#160`](https://github.com/Treevu-ai/cli-market-core/issues/160),
  not yet actioned by that repo.
- Repricing decision (business call, not a code fix): whether the 9
  intelligence tools — now correctly gated as Pro — should instead sit
  in a separate Intelligence tier ($300–500/mo) above Pro ($39/mo).
  Analysis in `docs/reports/PRICING-INTELLIGENCE-TIER-REVIEW.md`.
- GTM copy update (marketing call): reposition the B2C narrative as
  Pro-tier rather than a free hook.
- `docs/reports/` sits outside this repo's sparse-checkout cone by
  design — new docs there need `git add --sparse` to commit; left
  un-added to the cone on explicit instruction.

## [2026-07-21/22] — Grintek onboarding, require_all root-cause chain, shared-token rotation, security headers, search-logic dedup, Growth plan made real (cli-market-world, cli-market-core 1.11.51–1.11.58)

Long session spanning retailer onboarding, a multi-repo relevance-matching
bug chain, infra hygiene, and a full audit-driven fix pass. Grouped by
theme below; cli-market-core went 1.11.50 → 1.11.58 over the course of it.

**Grintek onboarding (grintek.pe / corp.grintek.pe, WooCommerce)**
- Researched both the retail (`grintek.pe`) and wholesale (`corp.grintek.pe`)
  WooCommerce stores, confirmed the connection protocol (WooCommerce Store
  API / REST API v3 with consumer key/secret — no HTML scraping or
  sitemap crawling involved, contrary to a later question from the
  retailer's contact about whether `sitemap.xml` mattered; it doesn't).
- Submitted and approved both retailer applications
  (`grintek_pe`, `grintek_corp_pe`, `line=electro`) via
  `POST /v1/retailers/apply` → `POST /admin/retailer-applications/{id}/approve`.
  Catalog confirmed live in production (iPhone 11 and others discoverable).
- Diagnosed and messaged the retailer's contact with fix instructions for a
  Hostinger WAF (`hcdn`) that was blocking `corp.grintek.pe`.

**require_all / relevance-matching bug chain (cli-market-core 1.11.51–1.11.56)**
- Root cause: `market_search(query='iphone 11')` without word-boundary
  AND-matching returned toys/cookware/car batteries sharing only a bare
  `'11'` token. Added a `require_all` param (default `false`, `true` for
  agent tool calls with no human filtering results) across
  `routers/search.py`, `routers/mcp_http.py`, and cli-market-core's
  `data_v1_service.py`, `market_intel_agent.py`, `market_mcp.py`,
  `market_mcp_registry.py`.
- Found and fixed a second-order bug in the same area: the SQL-level
  candidate fetch stayed OR-only even when `require_all=true` at the
  Python filter, so the candidate cap filled with irrelevant noise before
  relevance filtering ever ran — fixed by making the SQL joiner and
  `ORDER BY` conditional on `require_all` too.
- Fixed a recurring static-`STORES`-dict anti-pattern (6+ instances this
  chain alone) where dynamically-approved retailers (e.g. `grintek_pe`)
  were silently excluded from country filters, live-search line/currency
  lookups, and basket-compare store resolution, because those code paths
  checked only the static built-in `STORES` dict and not
  `store_credentials`/`get_store_profile`.
- `market_cli.py`: removed `choices=list(STORES.keys())` from 4 argparse
  definitions — it permanently locked out any dynamically-approved store
  from the CLI, rejecting `--store grintek_pe` before any code ran.
- Added a business-logic canary to `ops/smoke_e2e.sh` (search for
  `iphone 11` with `require_all=true`, assert exactly 1 result) after a
  deploy shipped a `cli-market-core` fix without its `cli-market-world`
  counterpart and the old health-only smoke test stayed green throughout.

**Shared API token rotation**
- Rotated the personal API token shared across 11 local IDE/CLI MCP
  configs (Cursor, Kiro, Windsurf, Codex, Cline, Devin, Grok, Zed, Kilo
  Code, Kimi Code, VS Code) plus Clay.com. Documented the rotation
  (old/new token IDs) in a gitignored `.env.local`. Verified end-to-end
  post-rotation; confirmed Grintek reachable and the 4 paying users
  unaffected.

**Read-only product/code/security audit**
- Full pass across cli-market-world, cli-market-core, cli-market-index,
  cli-market-content, and public landing pages: code quality, security,
  harness/CI validation, static-vs-dynamic architecture gaps, and
  tool/logic duplication. Produced the priority list this session's later
  work (below) executed against.

**Mistral AI Studio + LangSmith Fleet reconfiguration**
- User deleted the CLI Market MCP connector in Mistral AI Studio and the
  MCP server entry in LangSmith Fleet; both needed rebuilding after the
  token rotation. Mistral: recreated the custom MCP connector
  (`https://cli-market-api.fly.dev/mcp`, API-token auth), added the
  rotated token as a named credential, verified — all 54 MCP tools
  fetched successfully, confirming the live `require_all` fix. LangSmith
  Fleet turned out to be a separate product at `langchain.com/fleet`
  (not under `smith.langchain.com`); deprioritized by explicit user
  instruction ("olvida lang") in favor of the audit fix-list below.

**Landing page security headers**
- Added a `/*` catch-all block to `landing/public/_headers` (Cloudflare
  Pages' native header mechanism — `next.config.ts`'s `headers()` is inert
  under the site's `output: "export"` static build): CSP, HSTS,
  X-Frame-Options, X-Content-Type-Options, Referrer-Policy,
  Permissions-Policy. `script-src` keeps `'unsafe-inline'` since Next's
  static export emits inline RSC hydration payloads
  (`self.__next_f.push(...)`) with no per-request nonce available.
- Found and fixed a pre-existing, unrelated build break blocking this
  from ever deploying: `landing/tsconfig.json`'s broad `**/*.ts` include
  was sweeping `intel-latam/` (a standalone Vite/Express sub-app with its
  own `package.json`/Dockerfile/`fly.toml`, deployed separately) into the
  Next.js typecheck, failing on missing `express`/`vite` types. The
  Cloudflare Pages deploy had been silently failing since 2026-07-20.
  Excluded `intel-latam` from the tsconfig.

**Search-logic consolidation (cli-market-core 1.11.57)**
- `routers/search.py` (this repo's HTTP API) and cli-market-core's
  `data_v1_service.query_product_search` (used by the MCP intel agent)
  carried independent, byte-for-byte-duplicated copies of the
  tokenize/word-boundary-relevance/SQL-candidate-selection logic. They had
  already drifted: `data_v1_service.py`'s candidate ordering was always
  freshness-based (fixed 2026-07-20 for a "pollo" starvation bug — cheap
  derivatives filling the candidate cap before a pricier-but-relevant
  whole chicken could be considered), while `routers/search.py`'s fix only
  covered `require_all=True`.
- Extracted the shared logic into a new `market_core.product_search`
  module (`normalize_text`, `word_set`, `query_tokens`, `is_relevant`,
  `order_col_for`, `candidate_cap_for`, `build_search_sql`); both callers
  now import from it, so `routers/search.py` gets the more complete
  freshness-ordering fix too.

**Retailer Growth plan ($9/mo) made real (cli-market-core 1.11.58)**
- Found: the Growth checkout (`POST /billing/retailer-growth-checkout` →
  Mercado Pago → webhook → Slack notification) worked end to end, but
  none of the 4 promised features (priority search placement, price-vs-
  competitors dashboard, faster refresh, verified badge) existed in code,
  and there was no DB flag or admin action to mark a store as Growth once
  paid — money could be collected for a product that couldn't be
  delivered.
- Added `is_growth` / `growth_dashboard_token` / `growth_activated_at`
  columns to `store_credentials`.
- New admin endpoints `POST /admin/stores/{store_id}/activate-growth` and
  `GET .../growth-status` (mirrors the existing retailer-application
  approve pattern) — the team's manual action once a paid checkout is
  matched to a `store_id`.
- Search priority: growth stores win **exact price ties only**, in both
  `/products/search` and `/products/compare` (including the per-product
  `best_store` selection inside `_fuzzy_compare`) — never outranks a
  genuinely cheaper competitor, preserving "cheapest first" trust.
- `collect_prices.py`: growth stores get a scoped mid-cycle refresh
  (default 60 min vs. the global multi-hour interval) via the daemon's
  existing 30s trigger-poll loop — no restructuring of the main cycle.
- New `GET /v1/retailers/{store_id}/dashboard?token=...`: opaque-token-
  gated "your prices vs. competitors" view for the store's own line/
  country, reusing the store-resolution pattern from `_resolve_search_stores`.
- **Found and fixed while wiring the badge**: `GET /stores` and
  `GET /lines` — read by the `market_stores`/`market_discover` MCP tools
  and `/v1/basket/compare`'s store resolution — only ever iterated the
  static built-in `STORES` dict. Every dynamically-approved retailer,
  **including Grintek**, was invisible to both endpoints despite being
  fully onboarded. Same anti-pattern as the require_all chain above,
  found again in a part of the codebase that chain hadn't reached.
  Confirmed live: `grintek_pe` now appears in both `/stores` and
  `/lines`.
- Caught (and fixed) a real bug in code review before shipping: the new
  growth-refresh staleness check compared `datetime.isoformat()`
  (`...THH:MM:SS.ffffff+00:00`) against SQLite's `datetime('now')`
  (`YYYY-MM-DD HH:MM:SS`, space separator) — since space (0x20) sorts
  below `'T'` (0x54), every stored timestamp compared as "older" than the
  cutoff regardless of actual freshness, so every growth store looked
  permanently stale. Caught by the test written for this exact function.
  Fixed by formatting the cutoff to match SQLite's own output.

**Known follow-ups (not done this session)**
- `~/.claude`-adjacent: the `GH_TOKEN` Windows user environment variable
  is set to a non-GitHub secret (a leftover from the token-rotation work),
  which was silently breaking `gh auth`/git push all session. Left for the
  user to clear (`[System.Environment]::SetEnvironmentVariable("GH_TOKEN", $null, "User")`)
  since it's a persistent system-level setting outside repo scope.
- Store-resolution divergence between `routers/search.py`'s
  `_resolve_search_stores` and `data_v1_service.py`'s inline
  `get_custom_store_ids()` country filter — unverified whether they
  actually produce different results; flagged, not touched.
- Growth checkout collects free-text `email`/`store_name`, not a
  validated `store_id` — the team currently has to manually match a paid
  checkout to a `store_id` before calling the new activate-growth
  endpoint. Same manual-match effort as retailer-application approval
  already requires, so left as-is; a landing-page form change would be
  needed to remove the manual step.
- `landing/public/_headers`' CSP keeps `script-src 'self' 'unsafe-inline'`
  (required by Next static export's inline RSC hydration payloads); a
  nonce/hash-based CSP would need a build-time header-generation step,
  not currently in place.

## [2026-07-21] — Telegram UX redesign, search-agent hallucination root cause, market_brands quality pass (cli-market-world, cli-market-core 1.11.49/1.11.50)

Started from a live bug report: the Telegram/WhatsApp bot answered real
product queries ("café", "leche evaporada", "Nescafé en Wong") with
"no encontré resultados" or a fabricated price range, despite the
underlying data being real and directly queryable. Root-caused and fixed
end to end, then used the same investigation loop to harden `market_brands`
and drop two dead inline buttons.

**Telegram: inline buttons, editMessageText, typing indicator**
- Webhook now acks immediately with a "🔍 Buscando..." placeholder +
  `sendChatAction: "typing"`, does the `/v1/intel/ask` call in a
  `BackgroundTasks` job (mirrors `whatsapp.py`'s existing pattern), then
  edits the placeholder in place with the real answer — fixes both the
  silent-until-done UX and a latent webhook-timeout risk.
- Added a `callback_query` branch handling inline-keyboard button presses.
  Buttons dispatch directly against the session's `last_query`/
  `last_country` (new columns on `messenger_sessions`) instead of routing
  back through the LLM — sidesteps the tool-selection ambiguity entirely
  for the most common follow-ups.
- Dropped the "📈 ¿Va a subir?" and "🔔 Avisarme si baja" buttons: neither
  had a real forecasting or persistent-alert backend behind them, just a
  one-off LLM question dressed up as a feature that didn't exist. Only
  "🔄 Comparar tiendas" (backed by real `search_products` data) remains.
  Button follow-ups now send a new message instead of editing the original
  in place, after a second button press was found to silently erase the
  first button's answer.
- `**bold**` markdown from `ask_intel` answers wasn't rendered — Telegram
  was sent `parse_mode: "HTML"` (needs `<b>`) and WhatsApp needed
  single-asterisk bold; neither bridge converted it, so users saw literal
  asterisks. Both fixed.
- Rewrote both bots' welcome messages to state mission, capabilities, and
  explicit limits (no purchases/payments, coverage gaps possible, prices
  refresh periodically not real-time) instead of just a usage example.

**Root cause: get_prices vs. search_products tool-selection bug**
- Confirmed via a raw `/v1/intel/ask` call with `tools_used` inspection:
  Haiku was calling `get_prices` (an unfiltered country/store sample, no
  name matching) instead of `search_products` for named-product questions,
  getting a random sample that didn't happen to contain the product, and
  truthfully-but-wrongly reporting "no encontré nada."
- Hardened the system prompt and `get_prices`' tool description with an
  explicit rule + few-shot example; added a structural fallback — when
  `get_prices` is called with no store/line filter (the shape of a
  misrouted product lookup), it now also runs a name-matching search
  against the original question and surfaces it as
  `possible_product_matches`, giving the model a chance to self-correct
  even when it picks the wrong tool. Shipped as cli-market-core 1.11.49
  (PR #158, merged with the previously-unmerged `search_products` tool
  addition it depended on).

**A second, subtler hallucination: pagination mistaken for absence**
- Found while testing "pollo": whole-chicken products (San Fernando,
  Avinka) are real, but 100+ cheaper derivative matches (nuggets, patés,
  embutidos) filled `search_products`' default 20-result page first — a
  cheapest-first page can legitimately never include a pricier-but-relevant
  product, and `ask_intel` was concluding "no existe" from a page with no
  signal that it was partial.
- `query_product_search` now returns `truncated: bool`; the system prompt
  tells the agent to say "puede haber más" instead of "no existe" when
  true. Also fixed an independent issue in the same function: the SQL
  candidate fetch was ordered by price ASC and capped (`limit*20`) *before*
  the word-boundary relevance filter ran, so with enough matching rows,
  relevant candidates could be excluded from consideration entirely rather
  than merely ranked low — candidates are now fetched ordered by freshness
  (price-neutral); the final page is still sorted by price. Shipped as
  cli-market-core 1.11.50 (PR #159).

**market_brands (`GET /v1/analytics/brands`) quality pass**
- Merges casing ("Gloria"/"GLORIA"), accent ("Nescafe"/"NESCAFÉ"), hyphen
  ("Fisher-Price"/"FISHER PRICE"), and spacing ("Valle Norte"/"VALLENORTE")
  variants of the same brand into one row instead of fragmenting counts —
  8 such pairs found live in Peru's top-500 brands alone before the fix.
- Keeps store-name-as-brand values (e.g. `brand="Wong"`) as-is: several
  retailers sell private-label ("marca blanca") products under their own
  store name, so that's real brand data, not a scraping artifact — a
  correction from the user after an earlier pass would have wrongly
  filtered these out.
- Filters genuine placeholder junk ("—", "n/a", and "generic"/"genérico" in
  either language/accent — the Spanish accented form was already filtered
  but the unaccented and English spellings weren't).
- New optional `query` param scopes brands to a specific product category
  (e.g. `query=cafe`) instead of every brand in the line, word-boundary
  matched against product name.
- New `is_new` field per brand when `country` is given: true the first time
  a brand has ever been seen for that country (tracked in a new
  `known_brands` table) — a discovery signal for a new market entrant.
- Bundled in the same commit at the user's request: `/analytics/trending`
  and `/analytics/indicators` now require Pro (an already-in-progress,
  unrelated fix that was sitting uncommitted — they return the same
  live-computed values their `/v1/intel/*` equivalents already charge Pro
  for; was `require_api_key`, an unintended paywall bypass).

Verified end to end against production for both bots (Telegram inline
buttons + editMessageText; a real Twilio-signed WhatsApp webhook call) after
every deploy, plus `market_brands` across all 6 countries with a live
fuzzy-duplicate scan to confirm no further systematic fragmentation
patterns remained.

## [2026-07-19] — WhatsApp/Telegram bridge fix + dedicated bot account (cli-market-world)

Both messenger bridges were silently broken: every real question (anything
past the "hola"/"ayuda" greeting menu) fell back to the generic error
message, because they called a non-existent endpoint.

- **Fixed the endpoint bug** in `routers/integrations/whatsapp.py` and
  `routers/integrations/telegram.py`: both called
  `POST {MARKET_API_URL}/v1/shop/ask` with `{"query", "country", "user_tier"}`
  — that route has never existed. The real Data Moat Q&A endpoint is
  `POST /v1/intel/ask`, which takes `{"question": str}`. Also added
  response-body logging on non-200 so a future break fails loudly instead of
  silently degrading to the fallback string.
- **Found a bigger issue while fixing it**: `MARKET_API_TOKEN` — the only
  token either bridge had — resolves to the platform `"admin"` account in
  `server_deps.auth_user`, with unlimited quota via `is_platform_admin`.
  Once the endpoint bug was fixed, *every* WhatsApp/Telegram sender would
  have gotten unrestricted admin-tier backend access, not just the operator.
- **Added `WHATSAPP_ADMIN_NUMBERS` allowlist** (WhatsApp only, per explicit
  request — Telegram doesn't have an equivalent admin concept yet): a
  comma-separated list of Twilio `From` numbers (e.g.
  `whatsapp:+51902126765`) that get `MARKET_API_TOKEN` (admin/unlimited).
  Every other sender now gets `MARKET_BOT_API_TOKEN` instead.
- **Created a dedicated bot service account** (`bot-whatsapp-telegram`,
  `hello@cli-market.dev`) with a *permanent* Starter subscription (no trial
  expiry — `db_set_subscription(..., "starter")` with no `expires_days`) and
  issued its API key as `MARKET_BOT_API_TOKEN`. Had to create it directly
  against production Postgres via `flyctl proxy 15432:5432 -a cli-market-db`
  (the normal `/auth/register` flow needs a live inbox for the OTP code,
  impractical for a service account) rather than the usual registration
  endpoint.
- Deployed to `cli-market-api` (`fly deploy --app cli-market-api --config
  fly.toml --build-secret github_token=...`); both new secrets
  (`WHATSAPP_ADMIN_NUMBERS`, `MARKET_BOT_API_TOKEN`) set via
  `flyctl secrets set ... -a cli-market-api`.
- Documented all three new/changed env vars in `ops/SECRETS_INVENTORY.md`.

## [2026-07-18] — Banco Central do Brasil connector: first gov source outside Peru (cli-market-index)

Fifth gov connector overall, first one covering a country other than Peru.
Same shape, same `gov_price_observations` table, same read path — no new
plumbing needed on the backend or MCP side (`market_gov_observations` is
already source-agnostic).

- **BCB connector** (`bcb_br`) — USD/BRL exchange rate (venda, série 1) +
  IPCA monthly variation (série 433) + Selic daily rate (série 11), daily,
  via the Banco Central do Brasil SGS API. **No API key required** — the
  lowest-friction gov source so far (BCRP/WTO/Comtrade all need a
  registered key or portal subscription). Verified live 2026-07-18:
  `GET api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/5` returns
  real same-day data.
- **Real-world catch found during verification, not documented anywhere
  public:** the SGS endpoint returns HTTP 400 from a Ministério da Fazenda
  WAF page (not a JSON error) when the request has no browser-like
  `User-Agent` — a bare `curl`/`httpx` default gets blocked outright. The
  connector sends an explicit UA header; without it, the daily cron would
  fail every single run with an error unrelated to the series code or
  params. Same category of gotcha as SISAP's datacenter-IP block, just
  worked around instead of blocking the connector.
- `POST /admin/cron/gov-bcb` (backend) + `gov-bcb-refresh` cron job
  (morning-ops-chain), same non-fatal-on-failure pattern as the other four
  gov sources.
- Série 11 (Selic) shipped same-day as a third series (originally deferred
  to avoid scope creep before initial review) — same same-day-extension
  pattern BCRP used when it grew from FX+IPC to include trade balance.
  Slug `selic_bcb_br`, verified live: `{"data":"17/07/2026","valor":"0.052531"}`.

## [2026-07-18] — UN Comtrade connector: third independent trade-data source (cli-market-index)

Fourth gov connector overall, third independent export/import figure
alongside BCRP's balance-of-payments series and WTO's SITC3 monthly series.
Same shape, same `gov_price_observations` table, same read path — no new
plumbing needed on the backend side, just another source key.

- **UN Comtrade connector** (`comtrade_pe`) — Peru total merchandise
  exports/imports (HS classification, national totals), via the UN Comtrade
  Data API (free API-portal key, `subscription-key` query param — unlike
  WTO's header-based auth). Verified live: Peru reports to UN Comtrade
  **annually only** (a monthly query returns `count: 0` for every period
  tried), so the connector queries a rolling 6-year window and resolves to
  whichever year is newest (2024 at ship time); each period also fans out
  into several `motCode` (mode-of-transport) rows server-side, and the
  parser keeps only the `motCode == 0` ("all modes") aggregate row.
  Commodity slugs namespaced `*_comtrade_pe`.
- `POST /admin/cron/gov-comtrade` (backend) + `gov-comtrade-refresh` cron job
  (morning-ops-chain), same non-fatal-on-failure pattern as the other three.
- Verified live in production 2026-07-18: `{"ok":true,"source":"comtrade_pe","fetched":2,"resolved":2,"errors":0}`.

## [2026-07-18] — Official government data: BCRP trade balance, SISAP, WTO (cli-market-index, cli-market-core 1.11.47/48)

New capability: CLI Market's own indicators (Macro Gap, Affordability Score,
etc.) were entirely shelf-price-derived — no independent, official-source
validation. This ships the first three government/international data
connectors feeding a new `gov_price_observations` table in the semantic
index, read via `GET /v1/intel/gov-observations` (source-agnostic) and the
`market_gov_observations` MCP tool.

### cli-market-index (semantic index)
- **BCRP connector** (`bcrp_pe`) — USD/PEN exchange rate (venta/compra) +
  Lima IPC, daily. Extended same-day with Peru's monthly total merchandise
  **exports/imports/trade balance** (FOB, national totals) — the PRD's
  original department-level series turned out discontinued (last update
  Dec.2022/2023), so the connector uses BCRP's actively-maintained national
  series instead.
- **SISAP connector** (`sisap_pe`) — MIDAGRI canasta básica retail prices
  (arroz, aceite, azúcar, huevos, leche) across Lima + Piura, Lambayeque, La
  Libertad, Cajamarca. Required real reverse-engineering: the PRD's
  documented URL no longer resolves (ministry migrated `minagri.gob.pe` →
  `midagri.gob.pe`), that domain's TLS cert expired 2021-12-14 (plain HTTP
  only), and there's no JSON API — the actual GET parameters for its
  2010-era jQuery form were recovered by driving the real form in a browser
  and reading the resulting network request, not by reading the client JS.
  **Cron paused**: `sistemas.midagri.gob.pe` silently drops TCP connections
  from cloud/datacenter IP ranges (confirmed via raw socket connect from a
  Fly machine) — the connector is correct and tested against real data from
  a residential IP, but the daily unattended job can't reach it. Manual
  runs of `POST /admin/cron/gov-sisap` from a non-datacenter network still
  work.
- **WTO connector** (`wto_pe`) — Peru total merchandise exports/imports,
  monthly, via the WTO Timeseries API (free developer-portal key). Kept
  deliberately separate from BCRP's own export/import figures (commodity
  slugs namespaced `*_wto_pe`) since the two use different classifications
  and are expected to diverge somewhat — cross-validation signal, not a
  duplicate.
- Evaluated and passed on: SUNAT Aduanas (static annual yearbooks from a
  mid-2000s CMS, less fresh than BCRP's monthly series), Global Trade Alert.
  UN Comtrade was wired the same day — see the entry above.

### cli-market-core (MCP)
- `index_resolve` / `index_lookup` / `index_stats` — the semantic index's
  HTTP endpoints (`/resolve`, `/index/lookup/{id}`, `/index/stats`) had no
  MCP tool mapping despite cli-market-index's own README claiming they did.
- `market_gov_observations` — read path for all gov connectors above.
- Default MCP profile: 40 → 44 tools.

### Ops
- Rotated: production Postgres password, `MARKET_API_TOKEN` (admin + GitHub
  Actions secret), and two workshop participants' API keys — all had been
  sitting in plaintext in local, never-committed ops notes. Redacted those
  files in place; nothing was ever pushed to git.
- `index_gate.enrich_list` now batches through `IndexService.enrich_batch`
  instead of one DB round trip per item (perf fix, was silently degraded to
  the slow path because the local `cli-market-index` install was stale).

## [2026-07-17] — Price alert security hardening (cli-market-core 1.11.45)

### cli-market-core (shared package, PyPI)
- **Security fix:** `notify_email` on price alerts (`POST /v1/alerts`, both
  cli-market-backend and cli-market-world) is now locked to the caller's
  own OTP-verified `app_users.email` — previously any Pro+ user could set
  an arbitrary third-party address and use price alerts as an SMTP relay
  (harassment/phishing risk against the address, reputational risk to CLI
  Market's sending domain). Fixed in both repos' `routers/alerts.py`.
- **Security fix:** `notify_webhook` is now actually gated to Enterprise
  tier (was documented but unenforced in cli-market-backend) and validated
  against SSRF (`market_security.validate_public_http_url`) both at alert
  creation and again at send time in `market_alerts._send_webhook` —
  closes a DNS-rebinding gap where a domain validated at creation could be
  re-pointed to a private/metadata IP before the webhook fires (alerts can
  fire up to `cooldown_hours=720` / 30 days later, repeatedly). Also
  disables redirect-following on the outbound webhook POST.

### cli-market-backend
- `GET /analytics/stats` now returns `unique_brands_on_shelf` (distinct
  brands with a priced snapshot in the last `STATS_BRAND_FRESHNESS_DAYS`,
  default 30d) and `brands_on_shelf_window_days`.
- `POST /products/search` results now include a `confidence` field
  (`"ok"` / `"suspect"`) — reuses the discount-scrape-error check
  `save_price_snapshot` already ran, previously only visible in the
  internal ops dashboard.
- README retailer/country counts corrected (had drifted from 81/41/8 to
  the current 82/37/9) and pointed at `GET /analytics/stats` as the live
  source instead of hand-maintained numbers.

## [2026-07-17] — cli-market-core 1.11.46: 5 new intel MCP tools

### cli-market-core (shared package, PyPI)
- **New MCP tools:** `market_basket_stress`, `market_commerce_pulse`,
  `market_price_forecast`, `market_arbitrage`, `market_ecosystem_traction`
  — these HTTP endpoints (`/v1/intel/basket-stress`, `/pulse`, `/forecast`,
  `/arbitrage`, `/analytics/observatory`) existed but had no MCP tool
  mapping, so an agent using the MCP interface (Claude, ChatGPT, etc.)
  couldn't reach them. Default profile grows from 35 to 40 curated tools.
  `market_ecosystem_traction` in particular surfaces the public,
  no-PII adoption telemetry (`/analytics/observatory`) partner/press
  conversations want as a proof-of-traction signal.

## [2026-07-14] — Market Console live bug sweep, brand-monitor endpoint, subcategory-scoped scores + cross-brand substitutes

### cli-market-world (Market Console — `/dashboard/pricing`, `/dashboard/household`)
- **Fixed:** `/v1/brand-monitor` fetch never checked `response.ok` — a 404
  body (`{"detail":"Not Found"}`, the endpoint didn't exist yet) got stored
  as monitor state anyway, and rendering then spread
  `[...monitor.my_skus, ...monitor.competitor_skus]` on a body with neither
  field, throwing mid-render. This was the "page froze / reload or back"
  bug reported live — it fired automatically within ~1s of a brand
  auto-selecting.
- **Fixed:** `/analytics/brands` fetch also skipped the `response.ok` check
  — an expired/invalid key returned 401, silently read as "0 brands,"
  rendering as "Sin marcas para este scope" with no indication it was an
  auth failure, not an empty result. Matches the "dashboard doesn't offer
  brand/SKU selection" report exactly.
- **Fixed:** `InflationResponse` type declared `avg_rpv_7d_pct`, but the
  real `/v1/intel/inflation` response field is `avg_inflation_pct` — the
  "Inflación de góndola" card always showed `NaN%`. Also added `days=7` to
  the fetch so the "7d rolling" label matches what's actually requested
  (was defaulting to the endpoint's 30d).
- **Fixed:** the household and pricing dashboards' API-key gate used
  `type="password"`, which some browser/password-manager autofill paths
  set directly via the DOM without dispatching the input event React
  listens to — the field visibly showed the pasted key, but React's state
  (and the "Entrar" button's disabled check) never updated. Switched to
  `type="text"` with `autoComplete="off"` and per-vendor ignore attributes
  (1Password/LastPass/Bitwarden), keeping the value visually masked via
  `-webkit-text-security` instead of relying on the input type.
- **Fixed (residual gap, found via live adversarial testing):** the fix
  above stopped most autofill desyncs, but a targeted browser test —
  setting the input's `.value` via the raw DOM setter with zero events
  dispatched, simulating an autofill that ignores every opt-out attribute
  — still left `apiKey` React state stale, and the button's native
  `disabled` attribute silently swallowed the click entirely (no error,
  no feedback, same symptom as the original report). `handleAuth` now
  reads the live DOM value through a `ref` as the source of truth instead
  of trusting `apiKey` state alone; the button switched from `disabled` to
  `aria-disabled` (styling only) so a click always gets a chance to
  self-heal, and `onBlur` resyncs state as soon as focus leaves the field.
  Re-ran the exact same adversarial test against production after
  deploying — the click now succeeds and the dashboard renders.

### cli-market-backend (deployed to `cli-market-api`, Fly)
- **Added:** `GET /v1/brand-monitor` — was referenced by the frontend but
  never implemented anywhere in the backend (confirmed via live curl: 404).
  Returns cross-store SKU snapshots for a brand + competitors, read
  directly from `price_snapshots`. `product_id` in each row is
  `COALESCE(canonical_product_id, product_id)` so the comparator table can
  actually align the same product across stores; `promo_active`/`discount`
  read straight off existing columns rather than reimplementing
  `/v1/intel/promo-detector`'s per-product authenticity check.
- **Fixed:** `/analytics/brands` accepted a `country` query param and
  never applied it to the query — brand rankings silently mixed every
  country together. Found while reusing this endpoint's query shape for
  brand-monitor's competitor auto-selection.
- **Added:** `dispersion_score` (per-canonical-product cross-store price
  variance) now excludes any canonical group whose internal price spread
  exceeds 3x max/min — confirmed live against production gasificadas data
  that ~14% of canonical links were bundle listings whose price tracks
  promo state, not real retailer pricing (`Gaseosa Inca Kola 1.5L Pack de
  2 unid` ranged S/6.9–54.9 under one canonical id). Reporting a
  dispersion number off one of these would present a scrape/linking
  artifact as a genuine pricing signal.

### cli-market-core (PyPI `1.11.43`) — subcategory-scoped scores + brand-agnostic substitutes
- **Added:** optional `subcategory` param threading through
  `compute_price_dispersion` → `_compute_snapshot_kpis` →
  `refresh_internal_indicators` → `compute_composite_scores`/`get_scores`,
  so callers can ask "how aggressive is pricing in *gasificadas*
  specifically" instead of only the whole-line blend. Reuses
  `market_spread.infer_subcategory` rather than reimplementing bucketing.
  `get_latest_values` now isolates on the full `scope` string
  (`"PE:supermercados:gasificadas"` vs `"PE:supermercados"`) instead of
  just the `country`/`line` columns they share — otherwise a
  subcategory-scoped row would silently leak into line-level queries.
- **Added:** same >3x-internal-spread exclusion as the backend fix above,
  applied inside `compute_price_dispersion` so the composite score itself
  isn't pulled around by the same bundle-listing artifacts.
- **Added:** `category_equivalent_products()` in `golden_taxonomy.py` —
  `find_substitutes()` could only ever return same-brand, cross-store
  matches (`canonical_product_id` bakes brand into the id by construction,
  so exact-id equality can never surface a different brand). The new path
  groups by subcategory + comparable pack size (qty tolerance mirrors
  cli-market-index's resolver `_qty_close` default of 0.15) and extends a
  thin same-product pool with cross-brand candidates, each entry tagged
  `substitution_type` (`same_product_cross_store` /
  `cross_brand_category_match` / `fuzzy_name_match`) so callers can tell a
  verified same-SKU link from a genuinely different product.
- **Fixed:** pre-existing version-marker drift — `pyproject.toml` said
  `1.11.42` while `market_stats.py`'s `PACKAGE_VERSION` said `1.11.33`.
  Both now consistently `1.11.43`.
- Full suite: 564 passed, 3 skipped, 3 pre-existing failures confirmed
  identical on `main` before this change (clock/timezone drift in a
  rate-limit test, a stale delivery-quote assertion, a flaky live-network
  test) — not caused by this session's work.
- Published to PyPI and backend pin bumped (`cli-market-core==1.11.43`);
  `/v1/intel/scores` and `/analytics/indicators` gained an optional
  `subcategory` param passthrough. Live-verified on production: PE
  supermercados line-level `retail_aggression` is 86.8 (promo_intensity
  43.4%), `subcategory=bebidas` alone comes back 100 (promo_intensity
  52.5%) — confirms gasificadas genuinely runs hotter on promos than the
  line-wide blend, not just a hunch. Cross-brand substitutes verified too:
  querying "big cola" now returns Pepsi/Kola Real/Guaraná/Oro tagged
  `cross_brand_category_match` alongside the real Metro same-product match
  tagged `same_product_cross_store` — previously impossible.

### Investigation — pricing report validation (no code, live production queries)
- Reviewed an internal "Poder de Precio e Innovación — Bebidas Gasificadas
  (PE)" report against live data. The flagship Big Cola 46% cross-retailer
  gap (S/1.30 Plaza Vea vs S/1.90 Metro) verified as a real, same-moment,
  canonically-linked comparison — but not representative of the category
  (the same brand's 355ml can showed ~3% spread across the same stores).
  The report's 14-SKU category map covered roughly 14/44 (~32%) of
  distinct canonical gasificadas products actually in production — likely
  a first-page sample, not a census. This surfaced the >3x-spread bundle
  artifact documented above as a side effect.

## [2026-07-13] — Light landing palette, cross-repo MCP tool bugs, canonicalization root cause + data backfill

### cli-market-world (landing) — Fase 1 + Fase 2 craft pass
- **Changed:** Full palette swap from black/orange to light piedra-salvia theme
  across `globals.css` tokens, `.brand-mode-operations`, and hardcoded hex in 6
  components — validated against an Artifact prototype before touching the
  real site.
- **Fixed:** `Navbar.tsx` had an inline `rgba(0,0,0,...)` background bypassing
  the token system entirely, staying black after the swap.
- **Fixed:** `HeroBackground.tsx` gradient wash and image saturation tuned down
  — the retail-aisle photo read too heavy/dark against the new light canvas.
- **Fixed:** Hydration mismatch in `usePricingBillingFootnote` — the initial
  `useState` used the geo-aware footnote (reads `Intl` timezone, unavailable
  during SSR) instead of a static default, causing server/client HTML to
  differ on `/build`'s pricing section.
- **Changed:** Pill buttons (`--cm-radius-pill: 10px → 999px`), larger card
  radius (`--cm-radius-lg: 16px → 20px`), bigger hero typography
  (`.hero-garamond-headline` clamp ceiling 4rem → 5.5rem), and a solid-color
  featured pricing tier — one token/component change fans out to 23+ buttons
  and 30+ cards without touching each call site.
- **Changed:** Hero content (home + all spoke pages) left-aligned — centered
  hero copy is out of style for SaaS marketing pages.
- **Fixed:** Hero pricing chips advertised a nonexistent "Free" tier —
  `Pricing.tsx`'s real tiers are Starter/Pro/Enterprise. Caught during a live
  MCP tool test.

### cli-market-core (PyPI `1.11.42`)
- **Fixed:** `resolve_canonical_id`'s taxonomy-registry fallback used a raw
  bidirectional substring match with no word boundaries, returning the first
  hit in arbitrary dict order — a short/generic registry name could match
  inside an unrelated product name. Replaced with `\b`-bounded regex,
  preferring the longest (most specific) match.

### cli-market-backend (deployed to `cli-market-api`, Fly)
- **Fixed:** `market_discover` was wired to `/analytics/trending` (a
  `market_trending` copy-paste) — now composes `/lines` + `/stores` +
  `/countries` in parallel, matching cli-market-core's own reference
  implementation.
- **Fixed:** `market_price_history` was entirely absent from `/mcp`'s tool
  dispatch, falling through to `"Unknown tool"` despite its REST endpoint
  (`/analytics/price-history`) already existing.
- **Fixed:** `market_price_risk` was wired to `/v1/intel/alerts`
  (`market_price_alerts`' endpoint, which requires a `product` param
  `market_price_risk`'s own schema doesn't have) — every call 422'd. Retargeted
  to `/v1/intel/price-risk`.
- **Added:** `market_informal_signal`, `market_promo_detector`,
  `market_retailer_scorecard` — registered as MCP tools in cli-market-core but
  never implemented on this backend's REST layer. cli-market-core already
  ships the `compute_*` business logic; wired directly rather than mounting
  core's whole optional router (would collide with paths this backend already
  implements independently).
- **Fixed:** `Dockerfile`'s GitHub PAT build-arg was echoed verbatim into
  BuildKit's own progress log for any `ARG`-interpolated `RUN` command,
  regardless of shell flags — migrated to `RUN --mount=type=secret`, which
  BuildKit never logs or persists into an image layer. Two PATs and one OAuth
  token were exposed and rotated during this investigation.
- **Changed:** Pinned `cli-market-core==1.11.42`, `cli-market-index@7bc582d`.

### cli-market-index
- **Fixed (root cause):** `Resolver._fuzzy_search` matched candidate products
  on brand + package size alone, with no category check — a brand selling
  unrelated product lines in an identical container size (e.g. BELL'S: 3L
  cooking oil and 3L soda) collided into one Golden Record. This was the
  actual mechanism behind the cross-category substitute bugs surfaced via live
  agent testing of `market_optimize_purchase` and `market_substitutes`; the
  cli-market-core `resolve_canonical_id` fix above only hardened its own
  fallback and never touched how this index assigns `canonical_product_id` in
  the first place. Added `category_hint` as a required match dimension.

### Data backfill (production `price_snapshots`)
- **Fixed:** 6,314 rows had `canonical_product_id` corrected after the
  `_fuzzy_search` fix landed. Scope was arrived at through two discarded
  broader attempts (a brand-blind recompute, then an unscoped per-row
  recompute) that would have introduced *new* miscategorizations for
  personal-care products (`infer_category`'s keyword fallback misreads scent/
  flavor words like "leche" in shampoo names) — the executed backfill only
  touched `canonical_product_id` values current shared by 2+ products that
  compute distinct categories today (direct evidence of a real collision),
  and explicitly excluded any row naming a personal-care product. ~5,000
  singleton mismatches and 475 personal-care rows were left untouched,
  documented as a separate follow-up (`infer_category`'s keyword fallback
  needs its own fix, not a data patch).


### cli-market-world (landing) — Market Console v1
- **Added:** Explorer (`/dashboard/explorer`) and Developer (`/dashboard/developer`)
  consoles — session persisted via `localStorage` (no new login flow), reusing
  `BasketOptimizer` instead of rebuilding it. Deployed and verified live.
- **Fixed:** `DashboardNav`'s "Salir" button was unclickable — each dashboard page's own
  fixed `Navbar` rendered on top of it (`app/dashboard/layout.tsx`).
- **Fixed:** `BasketOptimizer`'s own country selector was silently overwritten whenever
  an unrelated parent control changed country (Explorer's search chips, saving the
  household profile) — found via a `click-path-audit` pass over the Console.

### cli-market-world (ops) — agent pipelines
- **Fixed:** `ops/price_pulse_agents.py`'s external `agency-agents` dependency
  (`~/Proyectos/agency-agents`) was missing locally — cloned
  [`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents);
  `--prepare` now runs end-to-end again.
- **Added:** `ops/growth_pulse_agents.py` — wires the 6 previously-unused design/
  marketing/sales agency-agents personas (brand-guardian, ui-designer, ux-architect,
  ux-researcher, content-creator, sales-engineer) to real signals (live site copy,
  PyPI/GitHub, `/health/stats`) instead of leaving them as dead context files.
- **Added:** `docs/agents/growth-pulse-workflow.md`, `ops/python-mcp-patterns.md`
  (Python translation of the `mcp-server-patterns` skill against the real
  `market_mcp.py` JSON-RPC loop), `ops/x402-payment-adr.md` (x402 payment research —
  no payment code touched; includes a real read-only simulation against production
  Procure Copilot data: 91/92 historical procurements were Tier A, 63/92 under a $20
  cap — $20 cap adopted).

### Cross-tool MCP config
- **Fixed:** `${MARKET_API_TOKEN}` placeholder (never expanded — TOML/JSON configs don't
  interpolate env vars) was silently sent as the literal token, causing 401s, in Codex,
  Cursor, Claude Code, Gemini CLI, Kiro, Kilo Code, Kilo, Devin, and Cline. Replaced with
  the real key/token in all 9 configs.

### cli-market-core v1.11.41 (PyPI)
- **Added:** `budgets` table (PG+SQLite) + `check_budget()` / `db_get_budget()` /
  `db_set_budget()` in `market_billing.py` — opt-in per-user spend cap for checkout, no
  row means no limit. Reuses `app_orders` for live spend totals instead of a new ledger
  table; counts `pending`+`paid` so several pending orders can't collectively exceed the
  cap before any settle.
- **Added:** `market_connectors/CONNECTOR_PATTERN.md` — documents the real connector
  interface/auth/error-handling/test conventions for the next platform integration.

### cli-market-backend
- **Added:** Budget gate wired into `_prepare_pending_order()` (shared by all 4 payment
  gateways), right after `pre_checkout_validate` and before order creation — same 409
  shape convention. Idempotent retries skip the check (already-counted spend). New
  `GET`/`POST /checkout/budget` endpoints.
- **Changed:** Pin `cli-market-core==1.11.41`; deployed to `cli-market-api` (Fly).

### Also this session (outside the 3 core repos)
- `~/Proyectos/cli-market-langchain-agent` — example LangGraph ReAct agent using
  `langchain-mcp-adapters` against the real `market-mcp` server (31 tools), verified
  live with real search/compare queries.

---

## [2026-06-18] — CLI fixes: --version, i18n, Win UTF-8, onboarding, demo nag

### cli-market-world v1.9.42
- **Added:** `--version` flag to CLI parser with `cli-market-world {PACKAGE_VERSION}`
- **Added:** Mini-tutorial onboarding for new users without session (`market_cli_hello.py`)
- **Added:** Demo account nag after 5 searches suggesting `market init`
- **Fixed:** Windows cp1252 terminal encoding — force UTF-8 stdout
- **Fixed:** `ModuleNotFoundError` for `market_cli_i18n` via full extraction from `market_cli.py`
- **Changed:** `argparse` description now includes live stats (retailers, countries, indicators)

---

## [2026-06-13] — Core 1.9.35 observatory_snapshot_streak (T-173)

### cli-market-core v1.9.35 (PyPI)
- **Added:** `observatory_snapshot_streak()` in `market_core/market_observatory.py`
- **Added:** core test `test_observatory_snapshot_streak`
- **Changed:** git tags `v1.9.34` (backport on main) + `v1.9.35`

### cli-market-world (post-PyPI via `ops/after_core_1.9.35_published.sh`)
- **Changed:** Pin `cli-market-core==1.9.35`; remove shim streak fallback

## [2026-06-12] — World 1.9.34 + Observatory P0 prod closure

### cli-market-world v1.9.34
- **Changed:** Pin `cli-market-core==1.9.34`; Railway prod OpenAPI **1.9.34**
- **Fixed:** Dockerfile `GITHUB_TOKEN` / `GH_PAT` fallback for private `cli-market-index` clone
- **Added:** `publish-core-pypi.yml` workflow; release scripts for core backport
- **Changed:** OpenAPI version from `pyproject.toml`; Railway verify uses Observatory P0 gate

### cli-market-core v1.9.34 (PyPI)
- **Changed:** Observatory backport — tool normalization, internal filter, sqlite3.Row DAA fix
- **Fixed:** `PACKAGE_VERSION` aligned with wheel version (was 1.9.30 in 1.9.33)

---

## [2026-06-12] — Force Railway redeploy (1.9.33 + core pin)

### cli-market-world v1.9.33
- **Changed:** `requirements-railway.txt` pin `cli-market-core>=1.9.33`
- **Changed:** Dockerfile `CACHE_BUST` bump to force image rebuild on Railway
- **Fixed:** `compute_daily_observatory_metrics` sqlite3.Row `.get` crash in nightly job
- **Fixed:** CI lint (ruff) blockers on `main`

---

## [2026-06-12] — Observatory P0 closure: mirror-first telemetry (Railway prod)

### cli-market-world v1.9.33
- **Added:** Full `market_observatory.py` in world (mirror/prod deploy before core PyPI backport)
- **Fixed:** Extract `retailer` / `country` from JSON body; skip `/index/*`; normalize tool names
- **Fixed:** Filter internal tools (`index_stats`, etc.) from public aggregates; `weekly_agent_growth`
- **Added:** `market_agent_id.py` — `X-Agent-ID` + `MARKET_AGENT_ID` for MCP setup
- **Changed:** Command-control panel order (semáforo → prioridades → scoreboard → tracción)
- **Changed:** Adoption Index — top-level `maa`, `maa_proxy`, `mcp_retention_7d` in signals

### cli-market-core (pending PyPI)
- Observatory fixes + `get_agent_id()` queued for core v1.9.34 after mirror deploy verified

---

## [2026-06-11] — Health stats on prod + golden linkage visibility

### cli-market-core v1.9.30
- **Added:** `market_core.health_stats` — `build_health_stats()`, `compute_linkage_metrics()`, shared `derive_collector_status()`
- **Added:** `GOLDEN_LINKAGE_PCT` in `market_stats` (live from `GET /health/stats`)
- **Added:** Tests for sources health ok/partial/dead classification (ticket 3.1)

### cli-market-backend
- **Added:** `GET /health/stats` on production API — moat KPIs, `golden_linkage_pct`, `sources_summary`

### cli-market-world v1.9.30
- **Changed:** `/health/stats` uses shared core builder + index `registry_size`
- **Changed:** `market doctor` — sources health + golden linkage rows
- **Changed:** Landing `goldenLinkagePct` via `ops/sync_market_stats.py`
- **Fixed:** PyPI installs chip — consolidated total from `/analytics/pypi` (legacy + core + world), clearer layout in hero Build card

---

## [2026-06-11] — Indicator cron + Phase 2 composite scores

### cli-market-core v1.9.29
- **Added:** 6 Phase 2 composite scores — `commodity_pressure`, `wage_affordability`, `producer_pressure`, `search_momentum`, `monetary_shelf_gap`, `commodity_transmission`
- **Fixed:** `refresh_after_collection` aggregates `phase2_written`

### cli-market-backend
- **Added:** `POST /admin/cron/indicators-refresh` — nightly macro + Phase 2 refresh
- **Changed:** `cli-market-core>=1.9.29`

### cli-market-world v1.9.29
- **Added:** `.github/workflows/indicators-nightly.yml` (05:00 UTC), `ops/indicators_daily.py`
- **Added:** Mirror `POST /admin/cron/indicators-refresh`
- **Changed:** Index pin `9d05013`, landing `packageVersion: 1.9.29`

### cli-market-index @ `9d05013`
- **Fixed:** mypy type args on `export_taxonomy_registry`

---

## [2026-06-10] — Data moat Phase 2: commodity, CEPAL, Trends (44 indicators)

### cli-market-core v1.9.28
- **Added:** 6 Phase 2 indicators — `commodity_input_pressure`, `real_wage_basket_ratio`, `ipp_food_co`, `gtrends_search_momentum`, `bcrp_shelf_gap`, `commodity_transmission_lag`
- **Added:** External fetchers in `market_enrich_sources` — CEPAL salary/basket, World Bank food production index, Google Trends RSS
- **Changed:** `compute_price_dispersion` and `compute_staple_price_momentum` prefer golden `canonical_product_id` + taxonomy cache
- **Changed:** Catalog **38 → 44** indicator definitions

### cli-market-backend
- **Changed:** `requirements.txt` → `cli-market-core>=1.9.28`
- **Fixed:** Docker build — `CACHE_BUST` invalidates pip layer; accepts `GITHUB_TOKEN` or `GH_TOKEN` for private index clone

### cli-market-world v1.9.28
- **Changed:** Pins, contract parity, landing `indicatorsCount: 44`, `packageVersion: 1.9.28`
- **Added:** `docs/PYPI-PACKAGE-MODEL.md`, `ops/RELEASE-DISPERSION.md`, `ops/smoke_phase2_prod.py`
- **Changed:** Landing TSX uses `MARKET_STATS.pipInstallCmd` (no hardcoded `pip install`)

### cli-market-index @ `9c8f74d`
- **Added:** Canasta registry + golden record attributes (`export_taxonomy_registry`, `infer_category` canasta paths)

---

## [2026-06-09] — Data moat Phase 0+1: golden taxonomy + regional macro (38 indicators)

### cli-market-core v1.9.27
- **Added:** Golden taxonomy bridge — `canonical_price_buckets()`, `staple_price_deltas_golden()` in `golden_taxonomy.py`
- **Added:** 4 Phase 1 macro indicators — `fx_ars_blue_gap`, `bcrp_inflation_expectation_12m`, `bcrp_reference_rate`, `fuel_price_index_pe`
- **Changed:** Basket/dispersion reads prefer `canonical_product_id` when taxonomy cache is present

### cli-market-backend
- **Added:** Post-certify taxonomy export hook; pin `cli-market-core>=1.9.27`
- **Changed:** `requirements-private.txt` — full 40-char `cli-market-index` pin

### cli-market-world v1.9.27
- **Changed:** Mirror parity for taxonomy bridge; CI index pin `9c8f74d`
- **Changed:** `docs/DATA-MOAT-INDICATORS.md` — Phase 0/1 catalog

---

## [2026-06-09] — Observatory P0: MCP telemetry layer

### cli-market-core v1.9.17
- **Added:** `market_core.market_observatory` — `agent_events`, `agents`, `daily_observatory_metrics`, MAA, retention, `ObservatoryMiddleware`
- **Added:** `X-Agent-ID` identity resolution priority chain

### cli-market-backend
- **Added:** Observatory middleware + `GET /analytics/observatory`, `/dashboard/observatory`
- **Changed:** `requirements.txt` → `cli-market-core>=1.9.17`

### cli-market-world v1.9.17
- **Added:** Mirror Observatory API, `ops/observatory_daily.py`, nightly workflow
- **Added:** Landing `/stats` (data-gate público) + bloque Observatory en command-control
- **Fixed:** `sync_market_stats.py` — URLs PyPI ya no duplican `-world`
- **Changed:** Adoption Index `real_usage` uses MAA when telemetry active
- **Changed:** `cli-market-core>=1.9.17`

---

## [2026-06-09] — P0 onboarding: tutorial + mcp-setup

### cli-market-core v1.9.16
- **Changed:** `PACKAGE_VERSION` bump (aligned with world release)

### cli-market-world v1.9.16
- **Added:** `market tutorial` — 3-step guided onboarding (search, compare, export) with `tutorial_completed` funnel event
- **Added:** `market mcp-setup --ide {cursor|claude|windsurf|vscode}` — one-liner MCP config, API ping, project-dir detection
- **Added:** Funnel events `tutorial_completed` and `mcp_setup_completed`
- **Changed:** Adoption Index multi-PyPI Pepy rollup (core + world)

---

## [2026-06-08] — CLI intel namespace + billing touchpoints

### cli-market-world v1.9.7
- **Changed:** Intelligence CLI under `market intel` (`inflation`, `indicators`, `enrichment`, `scores`); legacy top-level shims kept
- **Changed:** Public `--help` slimmed — `about`/`share` hidden; `upgrade` Pro-only; `tools --profile` without `admin`
- **Fixed:** `market intel inflation` table matches API `line` / `avg_*` schema
- **Changed:** Touchpoints use `market account` (not `market keys`) and `market upgrade` (not `--plan starter`)
- **Added:** `ops/CLIENT_PAYMENT_JOURNEY.md` — client payment flow (Build + Procure)

---

## [2026-06-07] — MCP bundle alignment (PR5)

### cli-market-core v1.9.6
- **Changed:** `MCP_TOOL_PROFILE` defaults to `default` (24 curated tools) instead of `legacy` (46)
- **Changed:** Invalid profile env falls back to `default`

### cli-market-world v1.9.6
- **Changed:** `market tools` reads registry bundles (Shop/Intel/Account) with `--profile` flag
- **Changed:** `market_ui` MCP catalog driven by `market_mcp_registry` (canonical tools marked ★)
- **Changed:** `market hello`, `market about`, help copy use default/legacy tool counts
- **Changed:** `mcp.json` env includes `MCP_TOOL_PROFILE=default`

---

## [2026-06-05] — Ecosystem rearchitecture

### cli-market-index v0.1.0
- **Fixed:** `{} or {}` bug in `Resolver.__init__` — empty dict was falsy, causing registry divergence
- **Changed:** Imports dropped `src.` prefix — now installable as `pip install -e .`
- **Changed:** `infer_category` extracted as standalone public function
- **Changed:** `build-backend` fixed from `setuptools.backends.legacy` to `setuptools.build_meta`
- **Changed:** `pyproject.toml` now includes `[tool.setuptools.packages.find] where = ["src"]`
- **Added:** CI workflow (GitHub Actions) — runs integration tests on push to `treevu-ai-main`
- **Added:** README ecosystem table with precise roles for all 4 repos
- **Added:** `.gitignore`

### cli-market-backend v1.0.0
- **Changed:** `index_gate.py` refactored — removed 120 lines of inline normalizers, now imports from `cli-market-index` as single source of truth
- **Changed:** README updated with semantic enrichment pipeline diagram
- **Added:** CI workflow (GitHub Actions) — runs `pytest tests/`
- **Added:** `.gitignore`

### cli-market-core v1.8.0
- **Added:** README.md — module catalog, ecosystem architecture, version
- **Added:** CI workflow (GitHub Actions) — smoke test importing all modules
- **Added:** `.gitignore`

### cli-market-world
- **Added:** Ecosystem architecture section in README with pipeline SVG
- **Added:** `docs/assets/ecosystem-pipeline.svg` — 4-layer architecture diagram
- **Added:** `docs/use-cases.md` — AI agent builders, data scientists, retailers
- **Added:** `docs/demo-walkthrough.md` — 8-step terminal demo
- **Added:** Footer links to demo, use cases, architecture
- **Added:** HowItWorks link to full demo walkthrough

---

## [2026-06-04] — Repository split

- **Split:** `cli-market-world` monorepo separated into 4 repositories
- `cli-market-backend` — scrapers, FastAPI server, data ingestion
- `cli-market-index` — entity resolution engine, Golden Records
- `cli-market-core` — intelligence, indicators, billing, MCP tools
- `cli-market-world` — landing page, docs, deployment configs

---

## [2026-06-02] — Platform baseline

- 45,000+ verified shelf prices
- 66 retailers (36 verified active), 8 countries
- 43 MCP tools, 34 market indicators
- Checkout via PayPal + QR (Yape/Plin)
- PyPI packages: `pip install cli-market-world` (+ `cli-market-core` intelligence layer)
- Production API on Railway
