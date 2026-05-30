# Landing (cli-market.dev)

Static Next.js export → Cloudflare Pages.

## Dev (local)

Desde la **raíz del repo** o desde `landing/`:

```bash
# Opción A — raíz del repo (recomendado)
cp landing/.env.example landing/.env.local
# Editar landing/.env.local → NEXT_PUBLIC_HERO_AB=1
npm run dev
# → http://localhost:3000/?hero=b

# Opción B — solo landing/
cd landing
cp .env.example .env.local
npm install
npm run dev
```

`.env.local` va en **`landing/.env.local`**, no en la raíz.

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
| `NEXT_PUBLIC_HERO_VARIANT` | Hero H1 fixed variant `a`–`f` when AB off (default `a`) |
| `NEXT_PUBLIC_HERO_AB` | Set `1` for runtime sticky split via cookie (`cm_hero_variant`) |
| `HERO_AB` | Cloudflare Pages only — set `1` to enable edge middleware cookie |

## Pro flow components

- `components/ProSubscribeButton.tsx` — pricing tier CTA
- `components/PayPalHostedButton.tsx` — embed after request
- `components/ContactForm.tsx` — `#contact` with Pro path

See [../ops/E2E_CLIENT_JOURNEY.md](../ops/E2E_CLIENT_JOURNEY.md).
