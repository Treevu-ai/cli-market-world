# Landing (cli-market.dev)

Static Next.js export → Cloudflare Pages.

## Build

```bash
cd landing
cp .env.example .env.local   # optional — defaults work for production API
npm install
npm run build
# output: landing/out/
```

## Env (Cloudflare Pages)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Railway API base |
| `NEXT_PUBLIC_PAYPAL_CLIENT_ID` | PayPal Hosted Buttons SDK |
| `NEXT_PUBLIC_PAYPAL_HOSTED_BUTTON_ID` | Button `B6YVFTG4MA73J` |
| `NEXT_PUBLIC_PRO_PAYMENT_URL` | Fallback payment link |
| `NEXT_PUBLIC_HERO_VARIANT` | Hero H1 A/B: `a`–`f` (default `a`). See [../docs/landing/h1-ab-variants.md](../docs/landing/h1-ab-variants.md) |

## Pro flow components

- `components/ProSubscribeButton.tsx` — pricing tier CTA
- `components/PayPalHostedButton.tsx` — embed after request
- `components/ContactForm.tsx` — `#contact` with Pro path

See [../ops/E2E_CLIENT_JOURNEY.md](../ops/E2E_CLIENT_JOURNEY.md).
