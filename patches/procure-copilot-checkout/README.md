# Procure subscribe checkout (Phase 2)

Host SaaS subscription checkout on **procurecopilot.com/procure/subscribe** instead of cli-market.dev.

## Quick install (private repo — use `gh`, not raw GitHub URL)

`raw.githubusercontent.com` returns **404** on private repos. From **procure-copilot** root:

### Option A — sparse clone + apply (no script download)

```powershell
cd ~\procure-copilot
gh auth login

$WorldRoot = "$env:TEMP\cli-market-world-checkout-patch"
Remove-Item -Recurse -Force $WorldRoot -ErrorAction SilentlyContinue

git clone --depth 1 --filter=blob:none --sparse https://github.com/Treevu-ai/cli-market-world.git $WorldRoot
Set-Location $WorldRoot
git sparse-checkout set patches/procure-copilot-checkout landing/components landing/lib landing/hooks
Set-Location ~\procure-copilot

python "$WorldRoot\patches\procure-copilot-checkout\apply.py" --target . --world $WorldRoot
```

### Option B — download installer via GitHub CLI

```powershell
cd ~\procure-copilot
gh auth login
gh api repos/Treevu-ai/cli-market-world/contents/patches/procure-copilot-checkout/install-checkout.ps1 -q .content `
  | ForEach-Object { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_ -replace "`n","")) } `
  | Set-Content install-checkout.ps1 -Encoding utf8
.\install-checkout.ps1
```

## Manual apply (full cli-market-world clone on `main`)

```powershell
cd ~\cli-market-world
git checkout main
git pull origin main
git sparse-checkout add patches/procure-copilot-checkout landing/components landing/lib landing/hooks

cd ~\procure-copilot
python ..\cli-market-world\patches\procure-copilot-checkout\apply.py
```

## 3. Cloudflare build env

```bash
NEXT_PUBLIC_API_URL=https://cli-market-production.up.railway.app
NEXT_PUBLIC_PROCURE_SITE_URL=https://procurecopilot.com
NEXT_PUBLIC_PROCURE_APP_URL=https://procurecopilot.com/dashboard
NEXT_PUBLIC_PROCURE_MP_CHECKOUT=1
```

## 4. Railway (return URLs — set after Worker deploy)

```bash
PROCURE_SUBSCRIBE_RETURN_URL=https://procurecopilot.com/procure/subscribe?sub=success&audience=procure
PROCURE_SUBSCRIBE_CANCEL_URL=https://procurecopilot.com/procure/subscribe?sub=cancelled&audience=procure
PROCURE_MP_SUCCESS_URL=https://procurecopilot.com/procure/subscribe?mp=success&audience=procure&ref={ref}
PROCURE_MP_PENDING_URL=https://procurecopilot.com/procure/subscribe?mp=pending&audience=procure&ref={ref}
PROCURE_MP_FAILURE_URL=https://procurecopilot.com/procure/subscribe?mp=failure&audience=procure&ref={ref}
```

Add `https://www.procurecopilot.com` to `CORS_ORIGINS` if you serve www.

## 5. Deploy

```powershell
npm run build
npx opennextjs-cloudflare build
node scripts/copy-public-assets.mjs
npx opennextjs-cloudflare deploy
```

On Windows, OpenNext warns about WSL — deploy usually still works; use WSL if build fails.

## Smoke test

1. https://procurecopilot.com/procure → Suscribirse → `/procure/subscribe?plan=pro&checkout=open`
2. Modal opens · PayPal + soles
3. Return from PayPal lands on `/procure/subscribe?sub=success&audience=procure`
