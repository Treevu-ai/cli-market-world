# Procure Copilot — OpenNext + Cloudflare deploy (Windows)
# Usage: cd ~\procure-copilot; .\deploy.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path "package.json")) {
    if (Test-Path "..\package.json") { Set-Location .. }
    elseif (Test-Path "..\..\package.json") { Set-Location ..\.. }
}
if (-not (Test-Path "package.json")) {
    Write-Error "Run from procure-copilot root (package.json missing)."
}

Write-Host "==> procure-copilot deploy preflight" -ForegroundColor Cyan
Write-Host "    cwd: $(Get-Location)"

Write-Host "`n==> 0/6 Repair ProcureLanding if a previous patch broke quotes" -ForegroundColor Cyan
$repair = "patches\procure-copilot-i18n-demo\repair.py"
if (Test-Path $repair) {
    python $repair
} else {
    $landing = "components\ProcureLanding.tsx"
    if (Test-Path $landing) {
        $raw = Get-Content $landing -Raw
        $fixed = $raw -replace 'lang === \\"en\\"', 'lang === "en"'
        if ($fixed -ne $raw) { Set-Content $landing $fixed; Write-Host "    Fixed escaped quotes" -ForegroundColor Green }
    }
}

Write-Host "`n==> 1/6 Clean .next and .open-next" -ForegroundColor Cyan
Remove-Item -Recurse -Force .next, .open-next -ErrorAction SilentlyContinue

Write-Host "`n==> 2/6 npm run build" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "BUILD FAILED — worker.js error below is a consequence, not the root cause." -ForegroundColor Red
    Write-Host "Run fix-build.ps1 first:" -ForegroundColor Yellow
    Write-Host '  Invoke-WebRequest "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/cursor/procure-i18n-demo-fix-7bb5/patches/procure-copilot-i18n-demo/fix-build.ps1" -OutFile fix-build.ps1'
    Write-Host "  .\fix-build.ps1"
    Write-Error "npm run build failed — fix errors above before deploy."
}

Write-Host "`n==> 3/6 opennextjs-cloudflare build" -ForegroundColor Cyan
npx opennextjs-cloudflare build
if ($LASTEXITCODE -ne 0) {
    Write-Error "opennext build failed — .open-next\worker.js was not created."
}

if (-not (Test-Path ".open-next\worker.js")) {
    Write-Error "Missing .open-next\worker.js — opennext build did not complete. Do NOT run wrangler deploy yet."
}
Write-Host "    OK: .open-next\worker.js exists" -ForegroundColor Green

Write-Host "`n==> 4/6 copy public assets" -ForegroundColor Cyan
if (Test-Path "scripts\copy-public-assets.mjs") {
    node scripts/copy-public-assets.mjs
    if ($LASTEXITCODE -ne 0) { Write-Error "copy-public-assets.mjs failed." }
} else {
    Write-Warning "scripts\copy-public-assets.mjs not found — skip (add from procure-copilot-seo patch if assets 404)."
}

Write-Host "`n==> 5/6 opennextjs-cloudflare deploy" -ForegroundColor Cyan
npx opennextjs-cloudflare deploy
if ($LASTEXITCODE -ne 0) {
    Write-Error "Deploy failed. UV_HANDLE_CLOSING on Windows is noise if worker.js existed — retry deploy once build passed."
}

Write-Host "`nDeploy complete. Verify:" -ForegroundColor Green
Write-Host '  (Invoke-WebRequest https://procurecopilot.com/procure).Content -match ''cli-market.dev/contact\?topic=procure'''
