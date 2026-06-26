# Procure Copilot — English + working demo CTAs

Fixes on **procurecopilot.com**:

1. **No English** — adds `LanguageProvider`, `LangToggle` (ES/EN), bilingual hero + final CTA via `lib/procureLocale.ts`
2. **Demo buttons broken** — replaces `mailto:hello@cli-market.dev` and dead links with:
   - **Agendar demo** → `https://cli-market.dev/contact?topic=procure#contact-procure` (web form)
   - **Probar demo** → `/dashboard?welcome=1`

## Apply (PowerShell)

```powershell
cd ~\procure-copilot
$base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-i18n-demo"
New-Item -ItemType Directory -Force -Path patches\procure-copilot-i18n-demo | Out-Null
@("apply.py", "lib/procureCta.ts", "lib/i18n.ts", "lib/LanguageContext.tsx", "lib/procureLocale.ts", "components/LangToggle.tsx", "README.md") | ForEach-Object {
  $dest = Join-Path "patches\procure-copilot-i18n-demo" $_
  $dir = Split-Path $dest -Parent
  if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  Invoke-WebRequest "$base/$_" -OutFile $dest
}
python patches\procure-copilot-i18n-demo\apply.py
```

## Manual (if apply skips ProcureLanding)

In `components/ProcureLanding.tsx`:

```tsx
import { useLang } from "@/lib/LanguageContext";
import LangToggle from "@/components/LangToggle";
import { getProcureCopy } from "@/lib/procureLocale";
import { procureBookDemoHref, procureTryDemoHref } from "@/lib/procureCta";

export default function ProcureLanding() {
  const { lang } = useLang();
  const copy = getProcureCopy(lang);
  // Use copy.hero.* and copy.tryDemoLabel / copy.bookDemoLabel for CTAs
}
```

Replace every `mailto:` demo href with `procureBookDemoHref()` and `/dashboard` demo links with `procureTryDemoHref()`.

## Deploy

```powershell
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx opennextjs-cloudflare deploy
```

## Verify

```powershell
(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'cli-market.dev/contact\?topic=procure'
# True — Agendar demo uses contact form, not mailto

(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'LangToggle|/dashboard\?welcome=1'
```

Toggle **EN** in the header — hero title should read "Your purchases."
