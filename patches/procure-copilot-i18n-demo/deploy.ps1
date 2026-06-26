# Procure Copilot — OpenNext + Cloudflare deploy (Windows)
# Usage: cd ~\procure-copilot; .\deploy.ps1
# Or download from cli-market-world patch folder.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path "package.json")) {
    # Allow running from patch dir with target = parent
    if (Test-Path "..\package.json") { Set-Location .. }
    elseif (Test-Path "..\..\package.json") { Set-Location ..\.. }
}
if (-not (Test-Path "package.json")) {
    Write-Error "Run from procure-copilot root (package.json missing)."
}

Write-Host "==> procure-copilot deploy preflight" -ForegroundColor Cyan
Write-Host "    cwd: $(Get-Location)"

Write-Host "`n==> 1/5 Clean .next and .open-next" -ForegroundColor Cyan
Remove-Item -Recurse -Force .next, .open-next -ErrorAction SilentlyContinue

Write-Host "`n==> 2/5 npm run build" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error "npm run build failed — fix TypeScript/Next errors before deploy."
}

Write-Host "`n==> 3/5 opennextjs-cloudflare build" -ForegroundColor Cyan
npx opennextjs-cloudflare build
if ($LASTEXITCODE -ne 0) {
    Write-Error "opennext build failed — .open-next\worker.js was not created."
}

if (-not (Test-Path ".open-next\worker.js")) {
    Write-Error "Missing .open-next\worker.js — opennext build did not complete. Do NOT run wrangler deploy yet."
}
Write-Host "    OK: .open-next\worker.js exists" -ForegroundColor Green

Write-Host "`n==> 4/5 copy public assets" -ForegroundColor Cyan
if (Test-Path "scripts\copy-public-assets.mjs") {
    node scripts/copy-public-assets.mjs
    if ($LASTEXITCODE -ne 0) { Write-Error "copy-public-assets.mjs failed." }
} else {
    Write-Warning "scripts\copy-public-assets.mjs not found — skip (add from procure-copilot-seo patch if assets 404)."
}

Write-Host "`n==> 5/5 opennextjs-cloudflare deploy" -ForegroundColor Cyan
npx opennextjs-cloudflare deploy
if ($LASTEXITCODE -ne 0) {
    Write-Error "Deploy failed. If you see UV_HANDLE_CLOSING on Windows, ignore it after fixing the worker.js error above."
}

Write-Host "`nDeploy complete. Verify:" -ForegroundColor Green
Write-Host '  (Invoke-WebRequest https://procurecopilot.com/procure).Content -match ''cli-market.dev/contact'''
