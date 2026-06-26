# Procure Copilot — Sprint 3 patch (sibling repo)

Apply in **`procure-copilot`** when `cli-market-world` Sprint 3 is deployed.

**Prereqs (Railway / API):**

- `PROCURE_MAGIC_SECRET` — 32+ byte secret (must match API)
- `PROCURE_APP_URL` — e.g. `https://procurecopilot.com/dashboard`

**API contract:**

```
POST https://cli-market-production.up.railway.app/auth/procure-magic-exchange
Content-Type: application/json

{ "token": "<signed token from email URL>" }

→ 200 { "ok": true, "username": "...", "api_key": "sk-...", "tier": "procure_pro" }
→ 400 token expired / already used / invalid
```

---

## 1. `app/procure/page.tsx` — CTA "Suscribir"

Replace sales-led "Agendar" primary CTAs with subscribe deep links:

```tsx
const SUBSCRIBE_URLS = {
  starter: "https://cli-market.dev/?audience=procure&plan=starter&checkout=open#pricing",
  pro: "https://cli-market.dev/?audience=procure&plan=pro&checkout=open#pricing",
  builder: "https://cli-market.dev/?audience=procure&plan=builder&checkout=open#pricing",
} as const;

// Per plan card:
<a href={SUBSCRIBE_URLS[plan.slug]} className="btn-primary">
  Suscribir →
</a>
```

Keep "Agendar demo" as secondary link if needed for enterprise.

---

## 2. `app/dashboard/page.tsx` — Magic link handler

On mount, read `?token=` from URL and exchange:

```tsx
"use client";

import { useEffect, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_CLI_MARKET_API ||
  "https://cli-market-production.up.railway.app";

export default function DashboardPage() {
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (!token) {
      setStatus("ready");
      return;
    }

    (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/procure-magic-exchange`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        // Persist per your existing auth module (sessionStorage / cookie)
        sessionStorage.setItem("cli_market_api_key", data.api_key);
        sessionStorage.setItem("cli_market_username", data.username);
        sessionStorage.setItem("cli_market_tier", data.tier);
        // Strip token from URL
        const url = new URL(window.location.href);
        url.searchParams.delete("token");
        window.history.replaceState(null, "", url.pathname + url.search);
        setStatus("ready");
      } catch {
        setStatus("error");
      }
    })();
  }, []);

  if (status === "loading") return <p>Conectando tu cuenta…</p>;
  if (status === "error") {
    return (
      <p>
        Enlace expirado o ya usado. Revisa tu email o escribe a hello@cli-market.dev
      </p>
    );
  }
  // … existing dashboard
}
```

---

## 3. `lib/auth.ts` — Read stored key

Ensure dashboard API calls read `sessionStorage.getItem("cli_market_api_key")` (or your vault pattern) before prompting manual paste.

---

## 4. Env (Cloudflare Workers)

```bash
NEXT_PUBLIC_CLI_MARKET_API=https://cli-market-production.up.railway.app
```

CORS: `procurecopilot.com` (and legacy `procure-copilot.contacto-8e4.workers.dev`) are in API `CORS_ORIGINS`.

---

## 5. QA checklist

- [ ] `/procure` Compare/Ops/Scale → "Suscribir" opens cli-market with correct plan + modal
- [ ] After MP/PayPal activation email → magic link opens dashboard with sk- bound
- [ ] Second click on same link → error message (one-time)
- [ ] Link after 15 min → expired message
