# Audit: comprehensive security hardening pass

**Date:** 2026-08-11
**Status:** Done. 9 findings, all fixed, tested, and deployed to prod. No open items.
**Trigger:** Continued from a Cursor security scan (2026-08-07 findings already partially fixed in prior sessions); this session closed the remaining checkout price-bypass and Slack fail-open bugs, then ran a comprehensive follow-up audit (`security-reviewer` agent) across the rest of the codebase per an explicit request to harden the architecture broadly.

## Summary

Two batches of work:

1. Fixed the last two Cursor-flagged findings that were still open going into
   this session: the checkout price-bypass and the Slack Pro/Procure
   fail-open bug.
2. Ran a comprehensive security-reviewer sweep of the rest of the codebase
   (auth/authz gaps, injection, secrets handling, webhook verification, rate
   limiting, SSRF, mass assignment, token handling) and fixed everything it
   found: 1 CRITICAL, 1 HIGH, 4 MEDIUM, 2 LOW.

All 9 fixes shipped as individual commits to `main`, each with CI green and
a deploy verified successful before moving to the next.

## Findings and fixes

### CRITICAL — Checkout charged the client-supplied cart price

`routers/checkout/routes.py`'s `_prepare_pending_order()` computed the order
total by summing `cart_item["price"] * quantity` directly from the cart —
and `AddToCartRequest.price` (`routers/cart.py`) is fully client-controlled.
An authenticated Pro user could add a real catalog item to their cart with
`price=0.01` and check out at that price on every payment method (Yape,
PayPal, Wise, MercadoPago, Lemon). `pre_checkout_validate()`
(`pre_checkout_validate.py`) already existed and computed the real,
server-verified total from live `price_snapshots` — it was wired only to
the separate, optional `POST /checkout/validate` endpoint, never to the
actual charging path.

**Fix:** `_prepare_pending_order()` now calls `pre_checkout_validate()` and
charges `result.validated_total`, never the client's cart price. The same
bug existed independently in the legacy fallback path
(`routers/orders.py POST /checkout`, gated behind `MARKET_LEGACY_CHECKOUT`)
and got the same fix.

Commits: `8418f413`, `5c3cd51f` (CI test-fixture collision fix), `46fea36d`
(legacy path).

### HIGH — Slack Pro/Procure activation failed open

`routers/slack_ops.py::_slack_activation_allowed()` returned `True`
whenever `MARKET_API_TOKEN` was unset — the rest of the admin surface
(`require_admin`) fails closed (503 disabled) in that situation, but this
one path let *any* Slack user in the workspace self-activate Pro/Procure
via `block_actions` if the admin token was ever misconfigured. A redundant
`DEFAULT_TOKEN and` guard at the call site made the bug worse: it
short-circuited the check to *skipped* rather than *denied*.

**Fix:** fails closed (deny) when the token is unset; removed the
short-circuiting guard.

Commit: `4d3f6313`.

### HIGH — `/billing/hubspot-webhook` had no authentication

Despite the name, this is an internal trigger (our billing code → n8n →
HubSpot/Slack), not an inbound webhook — but it had zero auth. Any
anonymous caller could POST a fabricated `subscription_activated` event
with an arbitrary email/username/amount, landing as a real deal in HubSpot
plus a Slack "payment confirmed" notification an ops teammate might act on.

**Fix:** gated behind `require_admin`, matching the rest of the ops-trigger
surface. No internal caller was found that needed updating.

Commit: `46fea36d`.

### MEDIUM — SSRF guard had a DNS-rebinding TOCTOU

`market_security.validate_public_http_url()` resolved a hostname once to
reject private/metadata IPs (169.254.169.254 etc.), but the actual fetch
(`safe_post_json()` in `market_security.py`, `_fetch_public_url()` in
`routers/media.py`) then handed the *original hostname* to httpx, which
re-resolves independently at connect time. An attacker's nameserver can
answer the check-time lookup with a public IP and the connect-time lookup
moments later with a metadata/internal address.

**Fix:** added `pinned_request_kwargs()`, which returns a URL with the
hostname swapped for the already-validated IP, plus a `Host` header and
`sni_hostname` extension so TLS SNI/cert checks and virtual hosting still
target the real domain. Both call sites now connect to the pinned IP.

Commit: `2722a5c8`.

### MEDIUM — `/billing/request-starter` trusted a client-supplied `username`

An unauthenticated caller could POST `{"email": "<attacker's email>",
"username": "<victim's username>"}`. `username` was read from the request
body, and a `require_user()` failure on a bogus `Authorization` header was
silently swallowed whenever the body also carried a `username`. This bound
an arbitrary victim's username to the attacker's own email in a
subscription request an ops reviewer could approve with no
account-takeover signal visible. (`/v1/contact`'s starter path was checked
too — it never passes a client-supplied username through, so it wasn't
affected.)

**Fix:** `username` now comes only from a validated `Authorization` header,
or is left empty (falls back to deriving it from the caller's own email,
as the function already did by default).

Commit: `b8ee6b36`.

### MEDIUM — `vault-charge` / `card-payment` amount not tied to an order

`POST /billing/vault-charge` and `POST /checkout/card-payment` charged
whatever `amount` the client sent, against a payment token/card the caller
genuinely owns (ownership verification was already correct — no IDOR). No
live exploit today: no internal flow drives these from a real priced
order. But the shape is identical to the checkout price-bypass bug, and a
landmine for whenever a future flow (e.g. Pro checkout) gets wired through
here without revisiting this.

**Fix:** added an optional `order_id`. When passed, the endpoint looks up
a caller-owned pending order and charges its server-recorded total,
ignoring the client-supplied amount entirely. Omitting `order_id`
preserves current behavior (both remain usable as the generic "charge my
own saved method" API they're documented as).

Commit: `40f54168`.

### MEDIUM — 4 public catalog endpoints had no rate limiting

`routers/search.py`: `GET /products/delivery/{id}`, `/products/barcode/{code}`,
`/products/enrich`, `/categories/{store}` had no auth and no rate limiting.
`barcode`/`enrich` call OpenFoodFacts and `categories` calls each
retailer's VTEX API per request — an anonymous caller could generate
unbounded outbound traffic/cost.

**Fix:** added per-IP `check_rate_limit()`, matching the pattern already
used in `intelligence_web.py`/`public_demo.py`.

Commit: `30830396`.

### LOW — `subprocess.run(shell=True)` with a list `cmd`

`ops/generate_intel_report.py` called `subprocess.run(cmd, shell=True)`
where `cmd` was a list — on POSIX, `shell=True` only runs `cmd[0]`; the
rest silently become unused shell positional args (a correctness bug) and
it's a latent command-injection footgun if `query` ever stops coming from
`ops/monday.py`'s fixed `CATEGORIES` list.

**Fix:** switched to `shell=False` so `cmd` runs as real argv.

Commit: `30830396`.

### LOW — `/checkout/webhook` unauthenticated outside production

Outside `is_production_deploy()` (which already covers every Fly
deployment, staging included, via `FLY_APP_NAME` — so this only applies to
genuine local dev), a caller with no `CHECKOUT_WEBHOOK_SECRET` configured
could mark any order paid by guessing its `order_id` (8 hex chars, 32 bits
of entropy).

**Fix:** added per-IP rate limiting (slows brute-forcing the order_id) and
a warning log whenever the endpoint is hit unauthenticated, so a
misconfigured non-Fly deployment that's actually internet-reachable
doesn't fail silently.

Commit: `c398ecd0`.

## Verification

Every commit: full relevant test suite run locally before push (checkout,
security, vault, slack_ops, server, media — 190+ tests passing together
with no cross-file collisions), CI green on `main`, `deploy-fly.yml`
confirmed successful before moving to the next fix.

## Not changed (reviewed, no action needed)

- `market_security.is_production_deploy()`'s detection logic was reviewed
  as part of the `/checkout/webhook` finding — it already treats every Fly
  deployment as production via `FLY_APP_NAME`, so no change was needed
  there beyond the rate-limit/logging addition above.
- `/v1/contact`'s starter-plan path never passes a client-supplied
  `username` through to `process_starter_subscription_request` — not
  affected by the `/billing/request-starter` finding.
