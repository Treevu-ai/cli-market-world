# GitHub Actions secrets — cli-market-world

Secrets required for scheduled workflows. Configure in **Settings → Secrets and variables → Actions**.

| Secret | Workflows | Scope / notes |
|--------|-----------|----------------|
| `MARKET_API_TOKEN` | Observatory nightly, adoption-index, indicators, command-control, PAM | Admin bearer token (same as Railway `MARKET_API_TOKEN`) |
| `GH_PAT` | CI backend checkout, daily-briefing, gtm-preflight | **Read** on: world, core, index, **cli-market-content**, cli-market-backend |
| `GH_PAT_BACKEND_WRITE` | sync-backend-core-pin (optional) | **Write** on `cli-market-backend` only |
| `SLACK_BOT_TOKEN` | daily-briefing, command-control (via API) | Bot invited to all GTM channels |
| `DATABASE_URL` | auth-token-expiry-reminder (if used) | Postgres URL — **not** required for Observatory nightly (uses API cron) |

## Common failures

| Symptom | Fix |
|---------|-----|
| Observatory nightly: `DATABASE_URL secret missing` | Fixed in main — workflow calls `POST /admin/observatory/snapshot` with `MARKET_API_TOKEN` |
| Daily briefing / GTM preflight: `Not Found` on cli-market-content | Add `Treevu-ai/cli-market-content` to `GH_PAT` repositories (read). Workflows require real checkout (no template fallback). |
| Sync backend core pin: `403` on push | Add `GH_PAT_BACKEND_WRITE` with write on backend, or apply PR manually |
| PAM admin cases skip | Set `MARKET_API_TOKEN` in workflow env / secrets |

## Verify locally

```bash
python3 ops/gtm_gate_remote.py
curl -sS -X POST "$MARKET_API_URL/admin/observatory/snapshot" \
  -H "Authorization: Bearer $MARKET_API_TOKEN"
```
