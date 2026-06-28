# Procure subscribe checkout (Phase 2)

Host SaaS subscription checkout on **procurecopilot.com/subscribe** instead of cli-market.dev.

## Apply (from procure-copilot repo)

```bash
# sibling layout: ../cli-market-world/patches/procure-copilot-checkout
python ../cli-market-world/patches/procure-copilot-checkout/apply.py

# or explicit paths
python /path/to/cli-market-world/patches/procure-copilot-checkout/apply.py \
  --target . \
  --world /path/to/cli-market-world
```

## Cloudflare build env

```bash
NEXT_PUBLIC_API_URL=https://cli-market-production.up.railway.app
NEXT_PUBLIC_PROCURE_SITE_URL=https://procurecopilot.com
NEXT_PUBLIC_PROCURE_APP_URL=https://procurecopilot.com/dashboard
NEXT_PUBLIC_PROCURE_MP_CHECKOUT=1
```

## Railway (return URLs — set after Worker deploy)

```bash
PROCURE_SUBSCRIBE_RETURN_URL=https://procurecopilot.com/subscribe?sub=success&audience=procure
PROCURE_SUBSCRIBE_CANCEL_URL=https://procurecopilot.com/subscribe?sub=cancelled&audience=procure
PROCURE_MP_SUCCESS_URL=https://procurecopilot.com/subscribe?mp=success&audience=procure&ref={ref}
PROCURE_MP_PENDING_URL=https://procurecopilot.com/subscribe?mp=pending&audience=procure&ref={ref}
PROCURE_MP_FAILURE_URL=https://procurecopilot.com/subscribe?mp=failure&audience=procure&ref={ref}
```

Add `https://www.procurecopilot.com` to `CORS_ORIGINS` if you serve www.

## Deploy

```bash
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx opennextjs-cloudflare deploy
```

## Smoke test

1. https://procurecopilot.com/procure → Suscribirse → `/subscribe?plan=pro&checkout=open`
2. Modal opens · PayPal + soles
3. Return from PayPal lands on `/subscribe?sub=success&audience=procure`
