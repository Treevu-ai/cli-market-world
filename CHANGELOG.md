# Changelog

All notable changes to the CLI Market ecosystem.

---

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
- **Changed:** `MCP_TOOL_PROFILE` defaults to `default` (22 curated tools) instead of `legacy` (46)
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
