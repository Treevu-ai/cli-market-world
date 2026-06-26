# Procure Copilot — Hero background patch

Replaces the hero terminal GIF with a **supermarket aisle background image**. Removes `demo.gif` and related components.

## What changes

| Before | After |
|--------|-------|
| `demo.gif` in hero | Removed |
| `ProcureDemo` terminal | Returns `null` (no UI) |
| Plain hero | `hero-supermarket.webp` full-bleed background + gradient overlay |

## Apply (PowerShell, from `~\procure-copilot`)

```powershell
cd ~\procure-copilot
$base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-hero"
Invoke-WebRequest "$base/install-hero.ps1" -OutFile install-hero.ps1
.\install-hero.ps1
```

## Manual edits if apply cannot patch automatically

1. Copy `public/hero-supermarket.webp` and `components/ProcureHeroBackground.tsx`
2. In **`components/ProcureLanding.tsx`** (primary — hero lives here), inside `#hero`:

```tsx
import ProcureHeroBackground from "@/components/ProcureHeroBackground";

<section id="hero" className="landing-section relative z-10 animate-fade-in overflow-hidden">
  <ProcureHeroBackground />
  <div className="proc-container-wide ... relative z-10">
    ...
  </div>
</section>
```

3. If hero also exists in `app/procure/page.tsx`, apply the same pattern and remove `<ProcureDemo />` columns there.

3. Replace `components/ProcureDemo.tsx` with the stub from this patch (returns `null`)
4. Delete `public/demo.gif` and `components/ProcureHeroTerminal.tsx` if present

## Deploy

```powershell
Remove-Item -Recurse -Force .next, .open-next -ErrorAction SilentlyContinue
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
git add -A
git commit -m "Hero: supermarket background, remove demo gif"
git push origin main
```

## Verify

```powershell
(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'demo\.gif|155%|272px'
# False

(Invoke-WebRequest https://procurecopilot.com/hero-supermarket.webp).StatusCode
# 200

(Invoke-WebRequest https://procurecopilot.com/procure).Content -match 'hero-supermarket'
# True — background component mounted in HTML
```
