# Landing (cli-market.dev)

Static Next.js export → **Cloudflare Pages** (`cli-market-world` → https://cli-market.dev).

## Build

```bash
cd landing
cp .env.example .env.local   # optional — defaults work for production API
npm install
npm run build
# output: landing/out/
```

## Deploy (Cloudflare Pages)

From repo root (needs `CLOUDFLARE_API_TOKEN`):

```powershell
$env:CLOUDFLARE_API_TOKEN = "..."
.\ops\deploy_landing.ps1
```

Or from `landing/` after build:

```bash
CLOUDFLARE_API_TOKEN=... npm run deploy
```

CI: push to `main` with changes under `landing/` runs `.github/workflows/deploy-landing-cloudflare.yml`.

## Env (Cloudflare Pages)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Fly.io API base |
| `NEXT_PUBLIC_PAYPAL_CLIENT_ID` | PayPal Hosted Buttons SDK |
| `NEXT_PUBLIC_PAYPAL_HOSTED_BUTTON_ID` | Button `B6YVFTG4MA73J` |
| `NEXT_PUBLIC_PRO_PAYMENT_URL` | Fallback payment link |

## Pro flow components

- `components/ProSubscribeButton.tsx` — pricing tier CTA
- `components/PayPalHostedButton.tsx` — embed after request
- `components/ContactForm.tsx` — `#contact` with Pro path

See [../ops/E2E_CLIENT_JOURNEY.md](../ops/E2E_CLIENT_JOURNEY.md).
