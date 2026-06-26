# Procure Copilot — Hero terminal GIF patch

Fixes the hero demo on `/procure`:

| Issue | Fix |
|-------|-----|
| Line across GIF / cropped terminal | Remove `width:155%` + `margin-left:-27.5%` hack |
| Frame too narrow | `aspect-[920/520]` + `object-contain` |
| Old CLI Market gif (820×480) | New Procure gif 920×520, orange theme |

## Apply (from procure-copilot root)

### PowerShell (no sparse checkout)

```powershell
cd ~\procure-copilot
irm https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-hero/install-hero.ps1 -OutFile install-hero.ps1
.\install-hero.ps1
```

### Local clone

```powershell
cd ~\procure-copilot
python ~\cli-market-world\patches\procure-copilot-hero\apply.py --target $PWD --patch ~\cli-market-world\patches\procure-copilot-hero
```

## Regenerate demo.gif (from cli-market-world)

```bash
cd cli-market-world/ops
python3 generate_procure_demo_gif.py
```

Copies to `patches/procure-copilot-hero/public/demo.gif`.

## Deploy

```powershell
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx wrangler deploy
```

Verify: open https://procurecopilot.com/procure — full terminal visible, no horizontal line artifact.
