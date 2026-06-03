# Go-Live Runbook — PayPal Checkout + Pro Activation

This is the step-by-step to turn on **paid Pro subscriptions** in production.
The API gating is already live (PR #78): data endpoints require an `sk-` key and
free/Pro tiers have different rate limits. What's left is wiring PayPal so a real
payment flips a user to `pro`.

> The whole loop is: user subscribes on PayPal → PayPal sends
> `BILLING.SUBSCRIPTION.ACTIVATED` to our webhook → we run
> `db_set_subscription(username, "pro")`. If the webhook isn't wired, customers
> get charged but never receive Pro. **Do not announce paid plans until step 5
> passes.**

---

## 1. Environment variables (Railway → API service → Variables)

Set these on the **API** service (the one serving HTTP, with `PORT=8080`):

| Variable | Where to get it | Notes |
|----------|-----------------|-------|
| `PAYPAL_CLIENT_ID` | PayPal Developer Dashboard → My Apps & Credentials → **Live** app | Live, not Sandbox |
| `PAYPAL_CLIENT_SECRET` | same app → "Secret" → Show | Keep secret; never commit |
| `PAYPAL_SANDBOX` | set to `false` | Defaults to `true`; **must be `false`** for real money |
| `PAYPAL_WEBHOOK_ID` | created in step 3 below | Required in production — webhook returns 503 without it |
| `PAYPAL_PLAN_ID` | the Pro billing plan id (`P-xxxxx`) | The $49/mo subscription plan |
| `CHECKOUT_WEBHOOK_SECRET` | any strong random string | Guards the legacy `/checkout/webhook` |

Leave the collector service alone — it doesn't serve HTTP and needs no PayPal vars.

> ⚠️ Sanity check from the past incident: the API service `PORT` must be `8080`
> (or unset), **never** `5432`. `5432` is Postgres; binding Uvicorn there made the
> app fall back to an empty SQLite and serve 0 prices.

---

## 2. Create the Live subscription plan (one-time)

If `PAYPAL_PLAN_ID` doesn't exist yet, create a $49/mo plan under the Live app
(PayPal Dashboard → Pay & Get Paid → Subscriptions → Plans, or via API). Copy the
resulting `P-...` id into `PAYPAL_PLAN_ID`.

---

## 3. Register the webhook at PayPal

PayPal Developer Dashboard → your **Live** app → **Add Webhook**:

- **Webhook URL:**
  ```
  https://cli-market-production.up.railway.app/checkout/paypal-webhook
  ```
- **Event types to subscribe:**
  - `BILLING.SUBSCRIPTION.ACTIVATED`   ← flips user to Pro
  - `BILLING.SUBSCRIPTION.CANCELLED`
  - `BILLING.SUBSCRIPTION.EXPIRED`
  - `BILLING.SUBSCRIPTION.SUSPENDED`   ← these three downgrade to free
  - `PAYMENT.CAPTURE.COMPLETED`        ← marks one-off orders paid
  - `CHECKOUT.ORDER.APPROVED`
  - `CHECKOUT.ORDER.COMPLETED`

After saving, PayPal shows a **Webhook ID** — copy it into `PAYPAL_PLAN_ID`'s
neighbor `PAYPAL_WEBHOOK_ID` (step 1) and redeploy.

---

## 4. Verify configuration (no charge yet)

After the redeploy, hit the status endpoint (browser or curl from your machine —
the CI sandbox can't reach the host):

```bash
curl -s "https://cli-market-production.up.railway.app/paypal-status?test=1" | jq
```

Expect:
```json
{
  "configured": true,
  "sandbox": false,
  "live": true,
  "webhook_configured": true,
  "plan_id_configured": true,
  "api_url": "https://api-m.paypal.com",
  "auth_test": { "ok": true }
}
```

If any of `live`, `webhook_configured`, `plan_id_configured` is `false`, the
matching env var from step 1 is missing or wrong.

---

## 5. End-to-end test purchase (the real gate)

1. Register a throwaway account and grab its `sk-` key:
   ```bash
   curl -s -X POST https://cli-market-production.up.railway.app/auth/register | jq
   # note "username" and "api_key"
   ```
2. Confirm it's **free** today — export must be blocked:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" \
     -X POST https://cli-market-production.up.railway.app/v1/data/export \
     -H "Authorization: Bearer sk-YOURKEY" -H "Content-Type: application/json" -d '{}'
   # expect 403
   ```
3. Start the Pro subscription for that username via `/billing/paypal`, complete
   the PayPal approval with a **real** funding source (small charge — you can
   refund/cancel after).
4. Within a few seconds, PayPal fires `BILLING.SUBSCRIPTION.ACTIVATED`. Verify
   the user is now Pro:
   ```bash
   curl -s https://cli-market-production.up.railway.app/auth/subscription \
     -H "Authorization: Bearer sk-YOURKEY" | jq '.subscription.tier'
   # expect "pro"
   ```
5. Re-run the export from step 2 — it should now return **200**.
6. Cancel the test subscription in PayPal. Confirm
   `BILLING.SUBSCRIPTION.CANCELLED` arrives and the tier drops back to `free`.

If the tier doesn't flip in step 4, check the API logs for the webhook line
(`PayPal webhook processed: ...`). The most common causes:
- `custom_id` not carrying the username → the code falls back to the
  `billing_pending` table keyed by subscription id; make sure `/billing/paypal`
  recorded the pending row.
- Webhook signature failing → `PAYPAL_WEBHOOK_ID` mismatch.

---

## 6. Email confirmations (optional but recommended)

Pro activation / receipts go out over SMTP if configured. Set on the API service:

| Variable | Example |
|----------|---------|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | sender address |
| `SMTP_PASS` | app password |
| `SMTP_FROM` | `CLI Market <no-reply@…>` |

Without these, the app still activates Pro — it just won't send the email.

---

## Quick reference — tiers enforced today (PR #78)

| Tier | req/min | req/day | Export / refresh |
|------|---------|---------|------------------|
| free | 60 | 1,000 | ❌ 403 |
| pro  | 300 | 10,000 | ✅ |

Public (no key): `/health/*`, `/dashboard/*`, `/lines`, `/stores`, `/countries`,
`/categories/{store}`, `/products/barcode/*`, `/products/enrich`.
