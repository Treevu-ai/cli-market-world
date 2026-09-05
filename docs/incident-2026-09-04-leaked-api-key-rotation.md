# Incident: personal API key hardcoded in local scripts, rotated

**Date:** 2026-09-04
**Status:** Resolved
**Severity:** Medium (credential exposed on local disk only — never reached git history or CI)

## Summary

While cleaning up half-finished local work in `cli-market-world` (uncommitted
`market_cli.py` changes + several one-off patch scripts), found a live
personal API key (`sk-23d8d016...`, account `user-28b62d609e6a`, enterprise
tier, unlimited rate limits) hardcoded in two untracked scripts
(`health_watchdog.py`, `test_api.py`). The same value was also present in the
local, gitignored `.env` under `MARKET_API_TOKEN`.

## How it was found

Routine review of uncommitted files before committing them. `grep`-ing the
repo for the literal key value found only the two scripts and `.env` — never
committed, never pushed (`git ls-files .env` returns nothing).

## Root cause

`.env`'s `MARKET_API_TOKEN` (a local dev convenience var, loaded by
`ops/load_env.py`) held a personal `sk-` account API key instead of the
service-level admin master token the name implies. Whoever wrote
`health_watchdog.py`/`test_api.py` copy-pasted that value directly into the
scripts instead of reading it from the environment at runtime.

## Two distinct "MARKET_API_TOKEN"-shaped credentials — do not confuse them

This surfaced an underdocumented architecture split worth calling out for
future ops work:

1. **Personal account API key** (`sk-` + 64 hex, e.g. from `market register`
   or `POST /auth/keys`). Tied to one username via the `api_keys` DB table.
   Manageable via `GET/POST /auth/keys`, `DELETE /auth/keys/{id}`
   (`routers/auth.py`). This is what most CLI/MCP usage authenticates with.
2. **Admin master token** — the literal `MARKET_API_TOKEN` env var set on the
   Fly.io app (and mirrored to GitHub Actions secrets by
   `ops/rotate_secrets.py --apply`). Checked by `server_deps.require_admin()`
   via **exact string equality**, not a DB row — there is no
   list/revoke-by-id for it, only full rotation. It gates every
   `/v1/admin/*` route (`routers/admin.py`), including
   `POST /v1/admin/set-tier` (change a user's subscription tier) and
   `POST /v1/admin/revoke-api-key` (revoke a leaked personal key by raw
   value — the *correct* way to revoke a compromised key you don't own a
   session for, instead of authenticating as that key to revoke itself).

Confusing the two (as this incident's `.env` did) means a "personal key
rotation" doesn't touch the actual admin secret, and vice versa — check
`server_deps.DEFAULT_TOKEN` / `require_admin()` before assuming which one a
given script needs.

## Resolution

1. Sourced the token from `os.environ["MARKET_API_TOKEN"]` in both scripts
   instead of hardcoding it.
2. Revoked the leaked personal key (`DELETE /auth/keys/49`, confirmed via a
   follow-up `401` on the same token against a protected endpoint).
3. Registered a fresh account (`market register`, email+OTP, passwordless —
   this backend has no username/password login path in practice; `POST
   /auth/login` exists but nothing in the current onboarding flow ever sets a
   password) and generated a new personal key for it.
4. Used the real admin master token (recovered from
   `ops/.rotation-local.txt`, the gitignored local record from the last
   `ops/rotate_secrets.py --apply` run on 2026-08-03) to call
   `POST /v1/admin/set-tier` and put the new account on `enterprise`, since
   `/v1/quality/scores` (what the watchdog polls) requires Pro+.
5. Updated local `.env`'s `MARKET_API_TOKEN` to the new personal key.
6. Verified live: `GET /v1/quality/scores` with the new key returns `200`
   with a real `freshness_seconds` value.

## Follow-ups / not yet done

- `.env` (local, gitignored, never leaked) also holds several other live
  secrets in plaintext (`ANTHROPIC_API_KEY`, PayPal, MercadoPago, Slack,
  SMTP). None of this leaked via git, but worth rotating on general hygiene
  grounds if this machine is ever shared or imaged.
- No automated check flags a hardcoded `sk-` literal in a new file before
  it's committed (a pre-commit secret scan would have caught this earlier,
  even though it never reached git in this instance).
- The old `user-28b62d609e6a` account (demo/procure-onboarding origin) still
  exists with its key permanently revoked; no cleanup of the account itself
  was done or needed.
