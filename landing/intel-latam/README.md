# CLI Market Intelligence — intel-latam

Standalone Node/Express + Vite/React app, originally scaffolded in Google AI
Studio and since rewired to run entirely on real CLI Market infrastructure —
no simulated/Gemini-generated data anywhere in this app.

Live at: https://cli-market.dev/intel-latam (reverse-proxied via a
Cloudflare Worker in `cli-market-world/workers/intel-latam-proxy` to
`https://cli-market-intelligence.fly.dev`, deployed separately on Fly.io).

## What's real here

- Chat (`ConversationalBridge.tsx`) calls `POST /api/chat` → the server
  proxies to the real Data Moat (`POST /v1/intel/ask` on `cli-market-api`).
- Checkout (`CheckoutModal.tsx`, wired from `Pricing.tsx`) calls
  `POST /api/checkout` → `POST /billing/build-checkout` (real PayPal flow).
- The footer's "Activar Pro" panel (`ActivateProPanel.tsx`) calls
  `POST /api/activate` → `POST /admin/activate-pro-request`, gated by a
  local passphrase checked server-side before the real admin token is used.

## Run locally

**Prerequisites:** Node.js

1. `npm install`
2. Copy `.env.example` to `.env.local` and fill in the real values (see
   comments in that file for what each one does and how to get it).
3. `npm run dev`

## Deploy

Deployed to Fly.io as the `cli-market-intelligence` app:

```
flyctl deploy -a cli-market-intelligence --ha=false
```

`vite.config.ts` sets `base: '/intel-latam/'` because the app is served
under that path prefix in production — if you add new client-side
`fetch()` calls, prefix them with `import.meta.env.BASE_URL` or they'll
bypass the Cloudflare Worker's routing once deployed.

This folder is not (yet) a git repository — there is no commit history to
check for past changes here.
