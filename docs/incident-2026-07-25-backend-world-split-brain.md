# Incident: cli-market-backend / cli-market-world split-brain deploy

**Date:** 2026-07-25
**Status:** Resolved
**Severity:** High (production ran deprecated code for 2+ days; a real security fix sat undeployed the whole time)

## Summary

`cli-market-backend` and `cli-market-world` are two separate GitHub repos that both
target the same Fly.io app, `cli-market-api` (and, for the collector, the same
`cli-market-collector` app). `cli-market-backend` was declared deprecated in its own
README in June 2026 — "consolidated into cli-market-world... new development should
happen in cli-market-world" — but nothing prevented `flyctl deploy` from that
directory from still landing on the real, live app.

During an unrelated work session, an entire cycle of feature work (custom Twilio
WhatsApp webhook, Shopify tokenless-Storefront-API fallback, VTEX store additions,
a price-constant bugfix in `mcp_http.py`) was done against `cli-market-backend` and
manually deployed to `cli-market-api` repeatedly — without realizing that repo was
the deprecated one. Meanwhile `cli-market-world`'s own CI-driven `deploy-fly.yml`
(gated on CI passing) had been silently failing to deploy for **2+ days**, so its
own queued-up security fixes never reached production.

## How it was found

The user shared a Cursor-agent PR (`#519`, security fix for an account-takeover path
and a Telegram admin-token fallback) filed against `cli-market-world`. Locating it
required checking multiple repos, which surfaced that `cli-market-world` has its own
`routers/`, `market_server.py`, `collect_prices.py`, etc. — a near-complete duplicate
of `cli-market-backend`'s app layer, but with materially different code (different
commit history, different feature sets, different MCP tool tiering).

Both repos' `fly.toml` pointed `app` at `cli-market-api`. Fly's own release history
showed continuous deploys through the session — all from manual `flyctl deploy`
runs out of `cli-market-backend` — while `cli-market-world`'s `deploy-fly.yml` runs
showed `skipped` since 2026-07-23, because the workflow only fires when its `CI`
workflow completes successfully, and CI had been red since that date.

## Root cause chain

1. `cli-market-backend/README.md` already documented the June 2026 deprecation, but
   its `fly.toml` / `fly.collector.toml` still pointed at the real app names, so a
   manual deploy from that checkout had no guardrail.
2. `cli-market-world`'s CI had been failing since 2026-07-23 on a trivial `ruff`
   error (`F541`, f-strings without placeholders) in a stray, already-committed
   analysis script (`analysis/golden_records/get_golden_records_flyio.py`).
3. Because `deploy-fly.yml` only deploys on a successful `CI` run
   (`workflow_run: ["CI"], types: [completed]`, gated on `conclusion == 'success'`),
   the broken lint silently blocked every deploy for two days — no alert, just
   `skipped` runs.
4. `cli-market-world` also runs `ops/contract_parity.py` in CI, which checks that
   its `cli-market-core` / `cli-market-index` pins match `cli-market-backend`'s (a
   deliberate migration safety net — `cli-market-backend` is treated as the
   "production backend" reference until `cli-market-world`'s mirror is proven
   equivalent). Because `cli-market-backend`'s pins had been bumped ahead
   (`cli-market-core` 1.11.58 → 1.11.76, plus a newer `cli-market-index` commit)
   during the unrelated session, this check also started failing.
5. Once lint + pins were fixed, `deploy-fly.yml`'s own post-deploy smoke test
   (`ops/doctor_prod_gate.py`) failed on `MAX_DEAD_SOURCES` — 6 stores were
   classified `"dead"`. Root cause: `store_health_state()` (in `cli-market-core`)
   classifies on **lifetime cumulative** `success_pct`
   (`total_successes / total_requests` since the store was first tracked), not a
   recent window. Those 6 stores (Shopify DTC brands: magicmind, glossier, fenty,
   allbirds, colourpop, kylie) had been broken for months before a same-session fix
   (tokenless Storefront API fallback) started working again — but their
   historical failure volume meant the lifetime ratio would take weeks/months to
   climb back over the 30% "dead" threshold even with 100% success going forward.

## Resolution

1. Fixed the blocking `ruff` lint error on `cli-market-world`'s tracked files.
2. Bumped `cli-market-world/requirements.txt`'s `cli-market-core` pin to 1.11.76 and
   its `cli-market-index` git pin to match `cli-market-backend`'s (both already
   verified safe in production); synced the same SHA across the 4 GitHub workflow
   files `ops/check_index_pin.py` cross-checks.
3. Ported the `SEED_QUERIES` fix (10 previously-uncovered business lines:
   suplementos, flores_regalos, industrial, belleza, papeleria, equipos_cocina,
   musical_instruments, restaurantes, pet, licores) from
   `cli-market-backend/collect_prices.py` into `cli-market-world`'s copy.
4. Reset `store_health.total_requests` / `total_successes` to `1/1` for the 6
   recovered Shopify stores directly in production Postgres (via `flyctl ssh
   console`) — a one-time, defensible correction now that the underlying
   connector fix was independently verified working, not a way to hide a real
   problem. `store_health_state()`'s lifetime-window design is worth revisiting
   separately (see Follow-ups).
5. Triggered `deploy-fly.yml` via `workflow_dispatch` (bypasses the CI gate,
   intended for exactly this kind of manual/emergency deploy) once the smoke gate
   was green. `cli-market-world` is now live on `cli-market-api` (confirmed via
   `flyctl status`, no auto-rollback).
6. Froze `cli-market-backend`'s deploy configs: `fly.toml` / `fly.collector.toml`
   now point `app` at nonexistent names (`cli-market-api-DO-NOT-DEPLOY-FROZEN`,
   `cli-market-collector-DO-NOT-DEPLOY-FROZEN`) so any future `flyctl deploy` from
   that checkout fails fast instead of landing. **Note:** both files are
   `.gitignore`d in that repo, so this only protects the local machine/checkout
   where the edit was made — it does not propagate to a fresh clone.
7. Reviewed and merged `cli-market-world#519` (the security PR), catching and
   fixing two real issues before merge (see below).

## Security fix (PR #519) — what it does, and what was wrong with it

The PR fixed two real vulnerabilities in `cli-market-world`:

1. **Account takeover via unauthenticated `procure-subscribe` username binding.**
   `POST /billing/procure-subscribe` accepted any `username` + attacker-controlled
   `email`. After a Mercado Pago payment, activation emailed the victim's magic
   link (with an API key) to the attacker's address. Fixed by prioritizing the
   registered account email over the request-supplied email when sending
   activation mail, and by adding `_assert_username_email_binding()`, which
   rejects the checkout (403) when the resolved username belongs to an existing
   account whose registered email doesn't match the request email.

2. **Telegram bridge falling back to the platform admin API token.** When
   `MARKET_BOT_API_TOKEN` was unset, `_process_message` / `_process_callback`
   fell back to `MARKET_API_TOKEN`, granting any Telegram user admin-tier
   `/v1/intel/ask` access. Fixed by removing that fallback entirely for public
   traffic; `TELEGRAM_ADMIN_CHAT_IDS` opts specific chats into the admin token,
   `TELEGRAM_ALLOWED_CHAT_IDS` is an optional general allowlist, and `_ask_intel`
   now degrades gracefully (a "not configured" message) instead of using no token
   or a wrong one.

**Gap found during review, fixed before merge:** `_assert_username_email_binding()`
originally only checked `db_get_user_email(username)`, which reads the
`subscription_requests` table — populated only after a user's *first* checkout
attempt. A victim who registered an account (`app_users`) but never subscribed
before would read back `None` there, silently skipping the block — exactly the ATO
scenario the fix exists to prevent. Reproduced locally (created a user via
`db_save_user` only, confirmed the 403 never fired). Fixed by also checking the
real account record via `db_get_users().get(username, {}).get("email")`.

Also found and fixed: 3 pre-existing Telegram tests
(`test_callback_query_reuses_last_query_without_retyping`,
`test_llm_answer_with_html_special_chars_is_escaped`,
`test_llm_answer_markdown_bold_is_rendered_as_html_bold`) broke under the new
no-admin-fallback behavior because they never set `MARKET_BOT_API_TOKEN`, so their
test chat IDs resolved to no token and `_ask_intel` short-circuited before ever
reaching the mocked HTTP call the tests assert against. Production already had
`MARKET_BOT_API_TOKEN` configured (verified via `flyctl secrets list`), so this was
a test-only gap, not a live regression — fixed by patching the env var into those
3 tests.

## Follow-ups / not yet done

- `store_health_state()`'s lifetime-cumulative classification (in `cli-market-core`)
  should probably use a recent rolling window instead — the current design means
  any store that was broken for a long time before a real fix will read as "dead"
  for a long time afterward regardless of current behavior. This needs a
  `cli-market-core` change + PyPI release, out of scope for this incident.
- `cli-market-backend`'s frozen `fly.toml` / `fly.collector.toml` edits are local
  to the machine they were made on (both files are gitignored in that repo). If
  another machine/session has its own checkout of `cli-market-backend` with the
  real app names still in `fly.toml`, the same risk exists there until that
  checkout is separately frozen.
- `tests/test_market_observatory_local.py::test_compute_daily_observatory_metrics_sqlite_row`
  fails on a clean `cli-market-world` main independent of anything in this
  incident (confirmed via a baseline run) — pre-existing, unrelated, not fixed
  here.
- No decision has been made yet on whether `cli-market-backend` should be archived
  outright (GitHub "Archive this repository") to make the deprecation
  unmissable, versus leaving it as-is with the frozen deploy configs.
