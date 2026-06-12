# GitHub Actions secrets — cli-market-world

Secrets required for scheduled workflows. Configure in **Settings → Secrets and variables → Actions**.

| Secret | Workflows | Scope / notes |
|--------|-----------|----------------|
| `MARKET_API_TOKEN` | **morning-ops-chain**, observatory, adoption-index, indicators, command-control, funnel-digest, PAM | Admin bearer token (same as Railway `MARKET_API_TOKEN`) |
| `GH_PAT` | CI checkout (index, core, backend), morning-ops-chain (GTM steps), daily-briefing, gtm-preflight | **Read** on: world, core, index, **cli-market-content**, cli-market-backend |
| `GH_PAT_CONTENT` | morning-ops-chain, daily-briefing, gtm-preflight (optional) | **Read** on `cli-market-content` only — use if `GH_PAT` cannot include all repos |
| `GH_PAT_BACKEND_WRITE` | sync-backend-core-pin (optional) | **Write** on `cli-market-backend` only |
| `SLACK_BOT_TOKEN` | daily-briefing, command-control (via API) | Bot invited to all GTM channels |
| `DATABASE_URL` | auth-token-expiry-reminder (if used) | Postgres URL — **not** required for Observatory nightly (uses API cron) |

## cli-market-content checkout (private repo)

Repo: `https://github.com/Treevu-ai/cli-market-content` (private). CI `Not Found` means the **token in the secret** cannot see the repo — not that the repo is missing.

### Fine-grained PAT checklist

1. GitHub → Settings → Developer settings → Fine-grained tokens → **Generate**
2. Resource owner: **Treevu-ai**
3. Repository access: **Only select** → add `cli-market-content` (and other repos CI needs)
4. Permissions → Repository → **Contents: Read**
5. If org uses SSO: **Authorize** the token for Treevu-ai
6. Copy token → `cli-market-world` → Settings → Secrets → update **`GH_PAT`** (or set **`GH_PAT_CONTENT`**)
7. Actions → **Verify content PAT** → Run workflow (must show HTTP 200 + checkout OK)

**Important:** editing PAT permissions on github.com does **not** update the secret — you must paste the token value again if you regenerated it.

## Morning ops chain

Daily cron lives in **`morning-ops-chain.yml`** only. Child workflows (`adoption-index-nightly`, `gtm-preflight`, etc.) are `workflow_dispatch` for ad-hoc runs.

| Risk | Mitigation |
|------|------------|
| Any early job fails → no GTM that day | Fix upstream job; or run `gtm-preflight` + `daily-briefing` manually via dispatch |
| PAM flake blocks briefing | Re-run chain from failed job, or dispatch briefing workflows directly |
| "Re-run all jobs" on old run | Uses stale YAML — use **Run workflow** or bump `ops/gtm-ci-run.trigger` |
| `make gate` in content repo | Broken locally (`$(python3 --version)`); CI uses `scripts/check-gate.py` |

## Common failures

| Symptom | Fix |
|---------|-----|
| Observatory nightly: `DATABASE_URL secret missing` | Fixed in main — workflow calls `POST /admin/observatory/snapshot` with `MARKET_API_TOKEN` |
| Daily briefing / GTM preflight: `Not Found` on cli-market-content | PAT in secret lacks read on private repo — follow checklist above; run **Verify content PAT** |
| Sync backend core pin: `403` on push | Add `GH_PAT_BACKEND_WRITE` with write on backend, or apply PR manually |
| PAM admin cases skip | Set `MARKET_API_TOKEN` in workflow env / secrets |

## Verify locally

```bash
python3 ops/gtm_gate_remote.py
curl -sS -X POST "$MARKET_API_URL/admin/observatory/snapshot" \
  -H "Authorization: Bearer $MARKET_API_TOKEN"
```

Test PAT against content repo (replace `$GH_PAT`):

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $GH_PAT" \
  https://api.github.com/repos/Treevu-ai/cli-market-content
# Expect: 200
```
