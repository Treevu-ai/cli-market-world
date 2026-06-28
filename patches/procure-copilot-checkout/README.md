# Procure subscribe checkout (Phase 2)

Host SaaS subscription checkout on **procurecopilot.com/procure/subscribe** instead of cli-market.dev.

## 1. Get the patch (PR #446 — not on `main` yet)

```powershell
cd ~\cli-market-world
git fetch origin
git checkout cursor/procure-checkout-on-site-e2d0
```

Or merge PR #446 and `git pull origin main`.

## 2. Apply (from procure-copilot repo)

```powershell
cd ~\procure-copilot
python ..\cli-market-world\patches\procure-copilot-checkout\apply.py
```

```bash
# sibling layout
python ../cli-market-world/patches/procure-copilot-checkout/apply.py

# explicit paths
python /path/to/cli-market-world/patches/procure-copilot-checkout/apply.py \
  --target . \
  --world /path/to/cli-market-world
```

Replaces the simple PayPal-only `/procure/subscribe` page with the full billing modal (PayPal + Mercado Pago · Yape · Plin).

## 3. Cloudflare build env

```bash
NEXT_PUBLIC_API_URL=https://cli-market-production.up.railway.app
NEXT_PUBLIC_PROCURE_SITE_URL=https://procurecopilot.com
NEXT_PUBLIC_PROCURE_APP_URL=https://procurecopilot.com/dashboard
NEXT_PUBLIC_PROCURE_MP_CHECKOUT=1
```

## 4. Railway (return URLs — set after Worker deploy)

```bash
PROCURE_SUBSCRIBE_RETURN_URL=https://procurecopilot.com/procure/subscribe?sub=success&audience=procure
PROCURE_SUBSCRIBE_CANCEL_URL=https://procurecopilot.com/procure/subscribe?sub=cancelled&audience=procure
PROCURE_MP_SUCCESS_URL=https://procurecopilot.com/procure/subscribe?mp=success&audience=procure&ref={ref}
PROCURE_MP_PENDING_URL=https://procurecopilot.com/procure/subscribe?mp=pending&audience=procure&ref={ref}
PROCURE_MP_FAILURE_URL=https://procurecopilot.com/procure/subscribe?mp=failure&audience=procure&ref={ref}
```

Add `https://www.procurecopilot.com` to `CORS_ORIGINS` if you serve www.

## 5. Deploy

```powershell
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx opennextjs-cloudflare deploy
```

On Windows, OpenNext warns about WSL — deploy usually still works; use WSL if build fails.

## Smoke test

1. https://procurecopilot.com/procure → Suscribirse → `/procure/subscribe?plan=pro&checkout=open`
2. Modal opens · PayPal + soles
3. Return from PayPal lands on `/procure/subscribe?sub=success&audience=procure`
