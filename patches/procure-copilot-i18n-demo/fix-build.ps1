# One-shot: fix broken ProcureLanding.tsx after a bad i18n patch, then verify build.
# Usage: cd ~\procure-copilot; .\fix-build.ps1

$ErrorActionPreference = "Stop"

if (-not (Test-Path "package.json")) {
    Write-Error "Run from procure-copilot root (package.json missing)."
}

$PatchBranch = "cursor/procure-i18n-demo-fix-7bb5"
$Base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/$PatchBranch/patches/procure-copilot-i18n-demo"

Write-Host "==> 1/4 Download latest patch + repair scripts" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path patches\procure-copilot-i18n-demo | Out-Null
@("apply.py", "repair.py", "fix-build.ps1", "deploy.ps1", "lib/procureCta.ts", "lib/i18n.ts", "lib/LanguageContext.tsx", "lib/procureLocale.ts", "components/LangToggle.tsx") | ForEach-Object {
    $dest = Join-Path "patches\procure-copilot-i18n-demo" $_
    $dir = Split-Path $dest -Parent
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Invoke-WebRequest "$Base/$_" -OutFile $dest
}

Write-Host "`n==> 2/4 Repair broken quotes in ProcureLanding.tsx" -ForegroundColor Cyan
$landing = "components\ProcureLanding.tsx"
if (Test-Path $landing) {
    $raw = Get-Content $landing -Raw
    $fixed = $raw -replace 'lang === \\"en\\"', 'lang === "en"'
    if ($fixed -ne $raw) {
        Set-Content $landing $fixed
        Write-Host "    Fixed escaped quotes in ProcureLanding.tsx" -ForegroundColor Green
    }
}
python patches\procure-copilot-i18n-demo\repair.py
python patches\procure-copilot-i18n-demo\apply.py

$mailtoLeft = Select-String -Path lib\*,components\* -Pattern 'mailto:hello@cli-market' -Recurse -ErrorAction SilentlyContinue
if ($mailtoLeft) {
    Write-Host "    WARN: mailto still in source — run fix-ctas.ps1 after build OK" -ForegroundColor Yellow
    $mailtoLeft | ForEach-Object { Write-Host "      $($_.Path):$($_.LineNumber)" }
}

Write-Host "`n==> 3/4 npm run build (must pass before deploy)" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build still failing. Paste the full error output in Cursor."
}

Write-Host "`n==> 4/4 Build OK — run deploy.ps1 next" -ForegroundColor Green
Write-Host "    .\patches\procure-copilot-i18n-demo\deploy.ps1"
Write-Host "    Or: Invoke-WebRequest '$Base/deploy.ps1' -OutFile deploy.ps1; .\deploy.ps1"
