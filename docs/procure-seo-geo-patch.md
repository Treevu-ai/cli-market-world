# Procure Copilot — SEO + GEO patch (sibling repo)

Apply in **`procure-copilot`**. Audit live (Jun 2026):

| Check | Live status |
|-------|-------------|
| Title / description | ✅ Present |
| `canonical` / `og:url` | ❌ Still `procure-copilot.contacto-8e4.workers.dev` |
| `og:image` | ❌ `demo.gif` on workers.dev (LinkedIn prefers 1200×630 PNG) |
| JSON-LD Organization | ❌ Missing |
| `sitemap.xml` | ❌ 404 |
| `robots.txt` | ⚠️ Cloudflare default content-signals only |
| `llms.txt` | ❌ Missing |

**Canonical host:** `https://procurecopilot.com` (apex). `www` serves same app; canonical always apex.

**Env (build + wrangler):**

```bash
NEXT_PUBLIC_PROCURE_SITE_URL=https://procurecopilot.com
PROCURE_PUBLIC_URL=https://procurecopilot.com
```

---

## 1. `lib/site.ts` — single source of truth

```ts
/** Public site URL (apex). Override at build via NEXT_PUBLIC_PROCURE_SITE_URL. */
export const PROCURE_SITE_URL = (
  process.env.NEXT_PUBLIC_PROCURE_SITE_URL || "https://procurecopilot.com"
).replace(/\/$/, "");

export const PROCURE_SITE_NAME = "Procure Copilot";

export const PROCURE_OG_IMAGE = `${PROCURE_SITE_URL}/og.png`;

export const PROCURE_DEFAULT_TITLE =
  "Procure Copilot | AI Procurement Platform";

export const PROCURE_DEFAULT_DESCRIPTION =
  "AI-native procurement infrastructure for enterprise purchasing in Latin America. Compare shelf prices, approvals, and checkout — from $29/mo.";

/** Spanish marketing variant (existing copy) — use on /procure */
export const PROCURE_PROCURE_TITLE =
  "Procure Copilot — Procurement inteligente para empresas en LatAm";

export const PROCURE_PROCURE_DESCRIPTION =
  "Compara compras en retailers verificados (8 países). Desde $29/mes. Aprobaciones, data-gate y checkout. Sin WhatsApp. Sin Excel.";
```

---

## 2. `app/layout.tsx` — metadata + JSON-LD

Replace hardcoded `workers.dev` URLs. Pattern (merge with your existing fonts/CSS):

```tsx
import type { Metadata } from "next";
import {
  PROCURE_DEFAULT_DESCRIPTION,
  PROCURE_DEFAULT_TITLE,
  PROCURE_OG_IMAGE,
  PROCURE_SITE_NAME,
  PROCURE_SITE_URL,
} from "@/lib/site";

export const metadata: Metadata = {
  metadataBase: new URL(PROCURE_SITE_URL),
  title: {
    default: PROCURE_DEFAULT_TITLE,
    template: `%s | ${PROCURE_SITE_NAME}`,
  },
  description: PROCURE_DEFAULT_DESCRIPTION,
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: PROCURE_SITE_NAME,
    description:
      "AI-native procurement platform for LatAm — compare, approve, checkout.",
    url: PROCURE_SITE_URL,
    siteName: PROCURE_SITE_NAME,
    type: "website",
    locale: "es_PE",
    alternateLocale: ["en_US"],
    images: [
      {
        url: PROCURE_OG_IMAGE,
        width: 1200,
        height: 630,
        alt: "Procure Copilot — AI procurement for Latin America",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: PROCURE_DEFAULT_TITLE,
    description: PROCURE_DEFAULT_DESCRIPTION,
    images: [PROCURE_OG_IMAGE],
  },
};

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      name: PROCURE_SITE_NAME,
      url: PROCURE_SITE_URL,
      logo: `${PROCURE_SITE_URL}/logo.svg`,
      sameAs: [
        "https://www.linkedin.com/company/procure-copilot/",
        "https://cli-market.dev/procure",
      ],
    },
    {
      "@type": "SoftwareApplication",
      name: PROCURE_SITE_NAME,
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      url: PROCURE_SITE_URL,
      description: PROCURE_DEFAULT_DESCRIPTION,
      offers: {
        "@type": "AggregateOffer",
        lowPrice: "29",
        highPrice: "149",
        priceCurrency: "USD",
      },
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

---

## 3. `app/procure/page.tsx` — page metadata

```tsx
import type { Metadata } from "next";
import {
  PROCURE_OG_IMAGE,
  PROCURE_PROCURE_DESCRIPTION,
  PROCURE_PROCURE_TITLE,
  PROCURE_SITE_NAME,
  PROCURE_SITE_URL,
} from "@/lib/site";
// … existing imports

export const metadata: Metadata = {
  title: PROCURE_PROCURE_TITLE,
  description: PROCURE_PROCURE_DESCRIPTION,
  alternates: { canonical: "/procure" },
  openGraph: {
    title: PROCURE_PROCURE_TITLE,
    description: PROCURE_PROCURE_DESCRIPTION,
    url: `${PROCURE_SITE_URL}/procure`,
    siteName: PROCURE_SITE_NAME,
    images: [{ url: PROCURE_OG_IMAGE, width: 1200, height: 630 }],
  },
};

// … existing page component
```

---

## 4. `app/dashboard/layout.tsx` — noindex (private app)

```tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
  title: "Dashboard",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return children;
}
```

---

## 5. `public/og.png` — LinkedIn / OG

LinkedIn ignores GIF for rich previews. Add **1200×630 PNG**:

1. Copy `landing/public/og.svg` from cli-market-world as base, or design Procure-branded card (mint `#3afecf`, dark `#002118`).
2. Rasterize: `node scripts/rasterize_og.mjs public/og.svg public/og.png`
3. Verify: `https://procurecopilot.com/og.png` returns 200

**LinkedIn Post Inspector:** https://www.linkedin.com/post-inspector/ → paste `https://procurecopilot.com/procure`

---

## 6. `public/llms.txt` — GEO discovery

```text
# Procure Copilot — AI procurement for Latin America

> URL: https://procurecopilot.com
> Product: https://procurecopilot.com/procure
> Dashboard: https://procurecopilot.com/dashboard
> API (CLI Market): https://cli-market-production.up.railway.app
> Parent brand: https://cli-market.dev

## What it is

Procure Copilot is an AI-native procurement platform for restaurants, hotels, and ops teams in LatAm. Turn shopping lists into optimized purchase orders using verified shelf prices (CLI Market data). Flow: run → pending approval → approve → checkout.

## Pricing (USD/mo)

- Compare (starter): $29 — price compare and savings, no checkout
- Ops (pro): $79 — approvals, stock, delivery, integrated checkout
- Scale (builder): $149 — multi-country, ERP integrations

## Key capabilities

- Multi-retailer basket compare (PE, AR, BR, MX, CO, CL, …)
- Manager approval workflow with audit trail
- Data-gate: prices refreshed every 4 hours from CLI Market collector
- Checkout handoff via CLI Market (PayPal, Mercado Pago, Yape/Plin)

## API examples (authenticated)

POST https://procurecopilot.com/api/procurement/run
POST https://procurecopilot.com/api/procurement/approve
POST https://procurecopilot.com/api/procurement/checkout

## Subscribe

https://cli-market.dev/?audience=procure#pricing

## Organization

Name: Procure Copilot
Website: https://procurecopilot.com
Also: https://www.procurecopilot.com (same product; canonical URL is apex)
```

---

## 7. Sitemap + robots — `next-sitemap`

**package.json** — add script (mirror cli-market-world):

```json
"build": "next build && next-sitemap",
```

```bash
npm install -D next-sitemap
```

**next-sitemap.config.js:**

```js
/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: process.env.NEXT_PUBLIC_PROCURE_SITE_URL || "https://procurecopilot.com",
  generateRobotsTxt: true,
  outDir: ".open-next/assets",
  changefreq: "weekly",
  priority: 0.8,
  exclude: ["/dashboard", "/dashboard/*", "/api/*"],
  robotsTxtOptions: {
    policies: [
      { userAgent: "*", allow: "/" },
      { userAgent: "GPTBot", allow: "/" },
      { userAgent: "ChatGPT-User", allow: "/" },
      { userAgent: "ClaudeBot", allow: "/" },
      { userAgent: "PerplexityBot", allow: "/" },
      { userAgent: "Google-Extended", allow: "/" },
    ],
    additionalSitemaps: [],
  },
  transform: async (config, path) => ({
    loc: path,
    changefreq: config.changefreq,
    priority: path === "/procure" ? 1.0 : config.priority,
    lastmod: new Date().toISOString(),
    alternateRefs: [
      {
        href: `https://www.procurecopilot.com${path}`,
        hreflang: "x-default",
      },
    ],
  }),
};
```

> OpenNext: confirm `outDir` matches your asset output (`.open-next/assets` or `public/`). Run build once and verify `sitemap.xml` + `robots.txt` in deploy bundle.

Post-deploy checks:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://procurecopilot.com/sitemap.xml
curl -sS -o /dev/null -w "%{http_code}\n" https://procurecopilot.com/robots.txt
curl -sS https://procurecopilot.com/robots.txt | grep -i sitemap
```

---

## 8. Search Console + Bing (manual)

| Step | Action |
|------|--------|
| Google Search Console | Add property **both** `https://procurecopilot.com` and `https://www.procurecopilot.com` |
| Verify | DNS TXT (Cloudflare) or HTML file |
| Sitemap | Submit `https://procurecopilot.com/sitemap.xml` on **both** properties |
| Bing Webmaster | https://www.bing.com/webmasters — import from GSC or add site + sitemap |
| LinkedIn Page | Company name **Procure Copilot**, website `https://procurecopilot.com`, same `og:image` |

**Preferred domain:** set apex as primary in GSC; `www` as separate property so both get crawl stats.

---

## 9. LinkedIn auto-detect “Procure Copilot”

LinkedIn matches company pages via:

1. **Exact company page** — create/fill https://www.linkedin.com/company/procure-copilot/ (or your slug)
2. **og:site_name** = `Procure Copilot` (layout metadata above)
3. **Consistent naming** in title, JSON-LD `Organization.name`, and llms.txt
4. **Post Inspector** cache bust after deploy

Employees tagging the company in posts accelerates recognition.

---

## 10. QA checklist

- [ ] View source `/procure`: `canonical` = `https://procurecopilot.com/procure`
- [ ] `og:url` = `https://procurecopilot.com/procure`
- [ ] `og:image` = `https://procurecopilot.com/og.png` (not demo.gif)
- [ ] JSON-LD Organization in `<head>`
- [ ] `/sitemap.xml` 200, includes `/` and `/procure`
- [ ] `/robots.txt` lists Sitemap + allows AI bots
- [ ] `/llms.txt` 200
- [ ] LinkedIn Post Inspector preview OK
- [ ] `www.procurecopilot.com/procure` same canonical (apex) in HTML

---

## Deploy

```bash
# procure-copilot — apply patch from cli-market-world:
python ../cli-market-world/patches/procure-copilot-seo/apply.py
# or: ..\cli-market-world\patches\procure-copilot-seo\apply.ps1

npm install
npm run og:png
npm run build
npx wrangler deploy
```

Redeploy after setting `NEXT_PUBLIC_PROCURE_SITE_URL=https://procurecopilot.com` in CI / Cloudflare build env.
