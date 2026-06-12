# Security incident — erroneous Pro activation (2026-06-12)

## Summary

A user received **Pro tier and a live API key without completing payment** because the Slack **Activar Pro** button and `ops/activate_pro.py` did not distinguish PayPal/Mercado Pago checkouts from manual Yape/Plin transfers.

## Affected account

| Field | Value |
|-------|--------|
| Username | `user-f04c6042d6da` |
| Exposed API key | `sk-PYH1vu4PwNEDh4itGrGdgAe24NSPKj_TksCYdSvBE_o` (revoke) |
| Erroneous grant | Pro tier without payment |

## Root cause

1. Slack `#suscripciones-cli-pro` showed **Activar Pro** for every pending `PRO-` request.
2. `activate_pro.py` and Slack interaction upgraded tier without verifying payment rail.
3. PayPal/MP webhooks are the only automatic paths for those methods.

## Fix shipped (#167)

- `is_manual_wallet_pro_payment_link()` — only `yape:` / `plin:` links allow manual activation.
- Slack button hidden for PayPal/MP requests.
- `--force` on ops CLI and admin API for verified overrides only.

## Remediation (ops)

1. **Demote** user to `free`: `POST /v1/admin/set-tier`
2. **Revoke** leaked key: `POST /v1/admin/revoke-api-key`
3. **Verify** key invalid: `curl -H "Authorization: Bearer sk-…" …/v1/whoami` → 401

Automated one-shot: push `ops/triggers/collector-demote.trigger` (workflow `ops-collector-demote.yml`).

```bash
python3 ops/revoke_api_key.py 'sk-PYH1vu4PwNEDh4itGrGdgAe24NSPKj_TksCYdSvBE_o'
curl -X POST "$MARKET_API_URL/v1/admin/set-tier" \
  -H "Authorization: Bearer $MARKET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"user-f04c6042d6da","tier":"free"}'
```

## Prevention

- Manual activation sources must pass `payment_not_manual` guard (`routers/payments.py`).
- Audit tokens in Railway logs: `pro_activated:`, `payment_not_manual:`.
- Do not share `sk-` keys in Slack or support tickets; rotate on exposure.
