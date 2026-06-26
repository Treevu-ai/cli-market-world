# Wire Procure EN toggle to page copy + deploy.
# Usage: cd ~\procure-copilot; .\fix-i18n.ps1

$ErrorActionPreference = "Stop"
$Base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/cursor/landing-hero-procure-i18n-7bb5/patches/procure-copilot-i18n-demo"

if (-not (Test-Path "package.json")) { Write-Error "Run from procure-copilot root." }

Write-Host "==> Download i18n patch" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path patches\procure-copilot-i18n-demo\lib | Out-Null
@(
  "apply.py",
  "lib/procureCta.ts", "lib/i18n.ts", "lib/LanguageContext.tsx", "lib/procureLocale.ts",
  "lib/procureEnStrings.ts", "lib/procureI18n.ts", "components/LangToggle.tsx"
) | ForEach-Object {
  $dest = "patches\procure-copilot-i18n-demo\$_"
  $dir = Split-Path $dest -Parent
  if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  Invoke-WebRequest "$Base/$_" -OutFile $dest
}

Write-Host "==> Apply patch" -ForegroundColor Cyan
python patches\procure-copilot-i18n-demo\apply.py

Write-Host "==> Build + deploy" -ForegroundColor Cyan
Remove-Item -Recurse -Force .next, .open-next -ErrorAction SilentlyContinue
npm run build
if ($LASTEXITCODE -ne 0) { Write-Error "npm run build failed" }
npx opennextjs-cloudflare build
if (Test-Path scripts\copy-public-assets.mjs) { node scripts\copy-public-assets.mjs }
npx opennextjs-cloudflare deploy

$html = (Invoke-WebRequest "https://procurecopilot.com/procure").Content
if ($html -match 'Your purchases') {
  Write-Host "SUCCESS — EN hero visible in HTML" -ForegroundColor Green
} else {
  Write-Host "Deploy OK — toggle EN in browser to verify hero reads 'Your purchases.'" -ForegroundColor Yellow
}
