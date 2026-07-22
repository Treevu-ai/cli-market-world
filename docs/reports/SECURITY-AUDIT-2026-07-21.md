# Security & Pricing-Gate Audit — 2026-07-21

**Trigger:** starting from a pricing/tier repricing review, checking why `market_whoami` was orphaned surfaced that several "Pro" tools returned confusing raw HTTP errors instead of upgrade prompts. Pulling that thread found the actual root cause: multiple backend endpoints had no authentication at all.

**Scope:** `cli-market-world` repo only (`market_server.py`, `routers/mcp_http.py`, `routers/media.py`, `landing/`). Root cause for one class of findings lives upstream in the `cli-market-core` pip package — tracked separately, not fixed here.

**Result:** 8 commits, `683bedbb..75bccd2b`, all pushed to `main`. Full test suite green (964 passed) at each step; only pre-existing, unrelated failures deselected (`test_canonical_copy`, `test_market_observatory_local`, 3 webhook-loopback tests with a separate DB-fixture issue).

---

## 1. Unauthenticated data endpoints (`cli-market-core`, 18 routes)

`market_server.py` mounts the pip package `cli-market-core`'s router at `/v1`. That package shipped several handlers without `Depends(_v1_auth)` — plain public functions. A pre-existing workaround (`_CORE_INTEL_AUTH_PATHS` + `core_intel_api_key_gate` middleware) patched 3 of them; the rest were live, unauthenticated, in production.

**Closed (commits `683bedbb`, `ee5d0926`, `dab77652`):**

| Path | Note |
|---|---|
| `/v1/intel/affordability`, `/v1/intel/alerts` | already shadowed by a Pro-gated world-repo route; redundant-but-harmless |
| `/v1/intel/informal-signal`, `/v1/intel/promo-detector`, `/v1/intel/retailer-scorecard` | genuinely open — real holes |
| `/v1/intel/andean-panel`, `/v1/basket/compare` | shadowed but only by registration order (fragile) — now explicit |
| `/v1/products/substitutes`, `/v1/basket/tco`, `/v1/ecosystem/launches` | genuinely open |
| `/v1/receipts/{receipt_id}` (prefix match) | worst one: returned `username` + `image_url` + full OCR line items for any 8-hex-char id, **no ownership check**. IDOR, not just missing auth. |
| `/v1/quality/scores`, `/v1/health/slas`, `/v1/health/slas-summary` | no evidence of intentional public exposure (unlike `/dashboard/data`, which stayed open — documented, linked from landing, explicit `slim` mode for MCP) |

**Also fixed:** the gate middleware was registered *after* `CORSMiddleware` (outer layer, runs first), so any browser preflight `OPTIONS` to a gated path 401'd before CORS could answer — real cross-origin callers would fail silently. Added an `OPTIONS` bypass.

**Verified upstream by a dedicated `security-reviewer` pass** (not just self-review) before shipping.

**Not fixed here — filed upstream:** [`Treevu-ai/cli-market-core#160`](https://github.com/Treevu-ai/cli-market-core/issues/160). The `market_server.py` gate is a hand-maintained path list in a different repo from the routes it protects — it already drifted once. Ask: add `Depends(_v1_auth)` at the source, add an ownership check to `get_receipt()`, then delete the workaround once the pin bumps.

## 2. Dependency CVE (commit `41b4a03f`)

GitHub Dependabot alert #62: `sharp` (npm, `landing/package-lock.json`, transitive via Next.js image optimization) — libvips CVEs (GHSA-f88m-g3jw-g9cj, high). Pinned via `overrides` to `0.35.3`. Alert auto-closed (`fixed`) on push.

## 3. Free/Pro documentation mismatch in the MCP catalog (commits `defbef22`, `6ebf6243`)

`routers/mcp_http.py` has a `_PRO_TOOLS` frozenset that controls whether a backend 402/403 gets rewritten into a friendly upgrade message. 10 tools were documented as Free (no `[Pro]` tag) while their backend actually calls `require_pro()` — so a free/trial caller got a raw passthrough error instead of an upgrade prompt:

`market_promo_detector`, `market_retailer_scorecard`, `market_informal_signal`, `market_inflation`, `market_scores`, `market_macro`, `market_intel_brief`, `market_indicators`, `market_trending`, `market_affordability`.

Found by systematically cross-referencing every untagged tool's dispatch endpoint against its backend auth requirement (`routers/intel.py`, `routers/analytics.py`). All 10 added to `_PRO_TOOLS` and tagged `[Pro]` in their descriptions; the file's header docstring (a human-readable mirror of the set) updated to match.

**Surfaced by a real GTM artifact:** a sales-demo script (see §5) opened on `market_promo_detector` as the hook step — before this fix, that step would have shown a raw HTTP error at the exact moment designed to hook a prospect.

## 4. Unauthenticated compute-abuse vector + a mislabeled tool (commit `75bccd2b`)

- `/v1/ticket/scan(-url)` and `/v1/voice/transcribe(-url)` ran `tesseract`/`whisper` subprocesses (up to 60s) for **any unauthenticated caller** — a free-compute/cost-abuse vector, not a data leak (SSRF was already mitigated via `validate_public_http_url`). Gated all four with `require_api_key`, consistent with the rest of the API's baseline (no permanent anonymous tier anywhere else).
- `market_scan` sat in `_PRO_TOOLS` despite its backend requiring `require_admin` (`MARKET_API_TOKEN`), not a paid tier. Its description was already correctly tagged `[Admin]`; removed from `_PRO_TOOLS` as dead/misleading bookkeeping. Not a live bug (`require_admin` raises 401, and the upgrade-prompt path only fires on 402/403), but confusing to a reader of the code.

## 5. GTM narrative cross-check (commit `7d1611f6`)

Three sales narratives (B2C, Fintech, Enterprise) were checked against actual tool tiers. Findings and corrected tier table in [`GTM-NARRATIVES-B2C-FINTECH-ENTERPRISE.md`](GTM-NARRATIVES-B2C-FINTECH-ENTERPRISE.md). Headline: the B2C "free copilot" pitch is built almost entirely on `[Pro]`-gated tools — should be marketed as Pro ($39/mo), not as a free hook.

## Commit index

| Commit | What |
|---|---|
| `683bedbb` | 5 unauthenticated `cli-market-core` intel endpoints → gated |
| `41b4a03f` | `sharp` CVE patch (landing) |
| `ee5d0926` | 6 more unauthenticated endpoints incl. receipts IDOR + CORS/OPTIONS fix |
| `dab77652` | `quality/scores`, `health/slas*` gated |
| `defbef22` | 3 MCP tools (promo_detector, retailer_scorecard, informal_signal) tagged `[Pro]` |
| `7d1611f6` | Pricing tier review + GTM narratives docs |
| `6ebf6243` | 7 more MCP tools tagged `[Pro]` (inflation, scores, macro, intel_brief, indicators, trending, affordability) |
| `75bccd2b` | OCR/voice endpoints gated; `market_scan` declassified |

## Open items

- **Upstream:** [`cli-market-core#160`](https://github.com/Treevu-ai/cli-market-core/issues/160) — add auth at the source, delete the `market_server.py` workaround once fixed.
- **Repricing decision (not executed, business call):** see [`PRICING-INTELLIGENCE-TIER-REVIEW.md`](PRICING-INTELLIGENCE-TIER-REVIEW.md) — the 9 intelligence tools are now correctly gated as Pro, but whether they should instead sit in a separate Intelligence tier ($300–500/mo) above Pro ($39/mo) is still an open pricing decision, not a code fix.
- **GTM copy update (not executed, marketing call):** B2C narrative should be repositioned as Pro-tier, not a free hook — see §5.
