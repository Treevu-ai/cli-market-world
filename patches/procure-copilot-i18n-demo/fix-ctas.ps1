# Fix Agendar demo mailto links → cli-market.dev contact form, then build + deploy.
# Usage: cd ~\procure-copilot; .\fix-ctas.ps1

$ErrorActionPreference = "Stop"
$PatchBranch = "cursor/procure-i18n-demo-fix-7bb5"
$Base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/$PatchBranch/patches/procure-copilot-i18n-demo"
$Contact = "https://cli-market.dev/contact?topic=procure#contact-procure"

if (-not (Test-Path "package.json")) {
    Write-Error "Run from procure-copilot root."
}

Write-Host "==> 1/5 Download latest apply.py" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path patches\procure-copilot-i18n-demo | Out-Null
@("apply.py", "repair.py", "lib/procureCta.ts", "lib/i18n.ts", "lib/LanguageContext.tsx", "lib/procureLocale.ts", "components/LangToggle.tsx", "deploy.ps1") | ForEach-Object {
    $dest = Join-Path "patches\procure-copilot-i18n-demo" $_
    $dir = Split-Path $dest -Parent
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Invoke-WebRequest "$Base/$_" -OutFile $dest
}

Write-Host "`n==> 2/5 Patch CTAs (remove all mailto:hello@cli-market.dev)" -ForegroundColor Cyan
python patches\procure-copilot-i18n-demo\apply.py

$hits = @()
Get-ChildItem -Path lib, components -Recurse -Include *.ts,*.tsx -ErrorAction SilentlyContinue | ForEach-Object {
    if ((Get-Content $_.FullName -Raw) -match 'mailto:hello@cli-market\.dev\?') {
        $hits += $_.FullName
    }
}
if ($hits.Count -gt 0) {
    Write-Host "    PowerShell fallback on remaining files..." -ForegroundColor Yellow
    foreach ($f in $hits) {
        $raw = Get-Content $f -Raw
        $fixed = $raw -replace 'mailto:hello@cli-market\.dev\?[^"''\s>]*', $Contact
        if ($fixed -ne $raw) { Set-Content $f $fixed; Write-Host "    fixed $f" -ForegroundColor Green }
    }
}

$still = @()
Get-ChildItem -Path lib, components -Recurse -Include *.ts,*.tsx -ErrorAction SilentlyContinue | ForEach-Object {
    if ((Get-Content $_.FullName -Raw) -match 'mailto:hello@cli-market\.dev\?') {
        $still += $_.FullName
    }
}
if ($still.Count -gt 0) {
    Write-Error "Demo mailto still in: $($still -join ', ')"
}

Write-Host "`n==> 3/5 Build" -ForegroundColor Cyan
Remove-Item -Recurse -Force .next, .open-next -ErrorAction SilentlyContinue
npm run build
if ($LASTEXITCODE -ne 0) { Write-Error "npm run build failed" }

Write-Host "`n==> 4/5 OpenNext build + deploy" -ForegroundColor Cyan
$deploy = "patches\procure-copilot-i18n-demo\deploy.ps1"
if (-not (Test-Path $deploy)) {
    Invoke-WebRequest "$Base/deploy.ps1" -OutFile deploy.ps1
    $deploy = ".\deploy.ps1"
}
& $deploy

Write-Host "`n==> 5/5 Verify production" -ForegroundColor Cyan
$ok = (Invoke-WebRequest "https://procurecopilot.com/procure").Content -match 'cli-market\.dev/contact\?topic=procure'
if ($ok) {
    Write-Host "SUCCESS — Agendar demo uses contact form" -ForegroundColor Green
} else {
    Write-Host "Still False — wait 2 min for CDN cache or paste deploy output in Cursor" -ForegroundColor Yellow
}
