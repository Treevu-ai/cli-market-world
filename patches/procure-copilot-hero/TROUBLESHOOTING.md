# Procure hero — fix invisible background

## Diagnosis (prod audit)

- `hero-supermarket.webp` → **200** (asset OK)
- `ProcureHeroBackground` → **not in HTML/JS** (component never mounted)
- Result: solid `--cm-background` black only

## Required: `components/ProcureLanding.tsx` (primary)

The live hero is in **ProcureLanding**, not `app/procure/page.tsx`. Inside `#hero`:

```tsx
import ProcureHeroBackground from "@/components/ProcureHeroBackground";

<section id="hero" className="landing-section relative z-10 animate-fade-in overflow-hidden">
  <ProcureHeroBackground />
  <div className="proc-container-wide ... relative z-10">
    {/* hero copy */}
  </div>
</section>
```

`relative` + `overflow-hidden` on the section; `relative z-10` on the inner container.

## Also check: `app/procure/page.tsx`

If your layout still renders hero here, apply the same pattern. `apply.py` patches both files when present.

## Deploy

```powershell
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx opennextjs-cloudflare deploy
```

## Verify

```powershell
(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'hero-supermarket'
# True
```
