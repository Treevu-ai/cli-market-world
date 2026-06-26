# Apply Procure SEO patch

From **procure-copilot** repo root:

```powershell
# Windows
..\cli-market-world\patches\procure-copilot-seo\apply.ps1

# Or Python directly
python ..\cli-market-world\patches\procure-copilot-seo\apply.py
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

## Deploy

```bash
npm install
npm run og:png
npm run build
npx wrangler deploy
```
