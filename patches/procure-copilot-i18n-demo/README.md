# Procure Copilot — English + working demo CTAs

## Si el build falló con `Unterminated string` en ProcureLanding.tsx

Un parche anterior escribió comillas mal (`lang === \"en\"`). **Un solo comando** lo arregla y verifica el build:

```powershell
cd ~\procure-copilot
Invoke-WebRequest "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/cursor/procure-i18n-demo-fix-7bb5/patches/procure-copilot-i18n-demo/fix-build.ps1" -OutFile fix-build.ps1
.\fix-build.ps1
```

Cuando diga **Build OK**, despliega:

```powershell
Invoke-WebRequest "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/cursor/procure-i18n-demo-fix-7bb5/patches/procure-copilot-i18n-demo/deploy.ps1" -OutFile deploy.ps1
.\deploy.ps1
```

El error `worker.js was not found` **no es el problema real** — aparece porque el build nunca terminó. El crash `UV_HANDLE_CLOSING` en Windows es ruido de Wrangler después del error.

---

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

## Deploy (Windows — orden obligatorio)

**Error `worker.js was not found`** = saltaste el paso 3 o `npm run build` falló antes.

```powershell
cd ~\procure-copilot

# Opción A — script con preflight
Invoke-WebRequest "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-i18n-demo/deploy.ps1" -OutFile deploy.ps1
.\deploy.ps1

# Opción B — manual
Remove-Item -Recurse -Force .next, .open-next -ErrorAction SilentlyContinue
npm run build                                    # debe terminar sin error
npx opennextjs-cloudflare build                  # crea .open-next\worker.js
Test-Path .open-next\worker.js                   # True — si False, NO deploy
node scripts/copy-public-assets.mjs
npx opennextjs-cloudflare deploy
```

No ejecutes `npx opennextjs-cloudflare deploy` solo — sin `opennext build` no existe `worker.js`.

El crash `Assertion failed UV_HANDLE_CLOSING` en Windows es un bug de Node/Wrangler **después** del error real; ignóralo una vez que `worker.js` exista.

### Si `npm run build` falla

Suele ser un error de TypeScript tras el patch i18n. Revisa:

```powershell
npm run build 2>&1 | Select-String -Pattern 'error TS|Error:'
```

Si `ProcureLanding.tsx` quedó a medias, aplica de nuevo `.\install-i18n-demo.ps1` o revierte ese archivo y aplica solo los cambios de `lib/procure-content.ts` (CTAs sin mailto).


## Verify

```powershell
(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'cli-market.dev/contact\?topic=procure'
# True — Agendar demo uses contact form, not mailto

(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'LangToggle|/dashboard\?welcome=1'
```

Toggle **EN** in the header — hero title should read "Your purchases."
