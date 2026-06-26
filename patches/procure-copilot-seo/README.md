# Apply Procure SEO patch

From **procure-copilot** repo root.

### One-liner (sparse checkout / no local patch folder)

```powershell
cd ~\procure-copilot
irm https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-seo/install-seo.ps1 -OutFile install-seo.ps1
.\install-seo.ps1
```

### With cli-market-world patch folder

```powershell
python ~\cli-market-world\patches\procure-copilot-seo\apply.py --target $PWD --patch ~\cli-market-world\patches\procure-copilot-seo
```

## What it does

1. Copies `lib/site.ts`, `lib/seo.ts`, `public/llms.txt`, `public/og.svg`, sitemap config
2. Adds `app/dashboard/layout.tsx` (noindex)
3. Patches `app/layout.tsx` — metadata + JSON-LD from `@/lib/seo`
4. Patches `app/procure/page.tsx` — page metadata
5. Updates `package.json` — `next-sitemap`, `og:png` script
6. Generates `public/og.png` if possible

## Manual merge (if apply.py misses layout)

In `app/layout.tsx`:

```tsx
import { organizationJsonLd, rootMetadata } from "@/lib/seo";

export const metadata: Metadata = rootMetadata;
```

Inside `<head>`:

```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
/>
```

In `app/procure/page.tsx`:

```tsx
import { procurePageMetadata } from "@/lib/seo";
export const metadata = procurePageMetadata;
```

Remove any hardcoded `procure-copilot.contacto-8e4.workers.dev` URLs.

## Build env

```bash
NEXT_PUBLIC_PROCURE_SITE_URL=https://procurecopilot.com
```

## Deploy (OpenNext — files must land in `.open-next/assets`)

```powershell
npm install
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx wrangler deploy
```

Verify **before** deploy:

```powershell
Test-Path public\og.png
Test-Path public\llms.txt
Test-Path .open-next\assets\og.png
```
