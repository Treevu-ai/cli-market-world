# Procure hero — fix invisible background

## Diagnosis (prod audit)

- `hero-supermarket.webp` → **200** (asset OK)
- `ProcureHeroBackground` → **not in HTML/JS** (component never mounted)
- Result: solid `--cm-background` black only

## Required: `app/procure/page.tsx`

Inside `#hero`, **first child** must be:

```tsx
import ProcureHeroBackground from "@/components/ProcureHeroBackground";

<section id="hero" className="landing-section relative z-10 animate-fade-in overflow-hidden">
  <ProcureHeroBackground />
  {/* rest of hero */}
</section>
```

`relative` + `overflow-hidden` on the section are required.

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
