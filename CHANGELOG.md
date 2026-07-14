# Changelog

All notable changes to the CLI Market ecosystem.

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
