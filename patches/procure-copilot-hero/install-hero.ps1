# Procure hero — supermarket background (no demo.gif)
# Usage: cd ~\procure-copilot; .\install-hero.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
if (-not (Test-Path "$RepoRoot\apply.py")) {
    $RepoRoot = Join-Path $env:TEMP "procure-hero-patch"
    New-Item -ItemType Directory -Force -Path $RepoRoot | Out-Null
    $base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/cursor/procure-hero-supermarket-7bb5/patches/procure-copilot-hero"
    Write-Host "Downloading patch from GitHub..."
    @(
        "apply.py",
        "components/ProcureHeroBackground.tsx",
        "components/ProcureDemo.tsx",
        "public/hero-supermarket.webp"
    ) | ForEach-Object {
        $dest = Join-Path $RepoRoot $_
        $dir = Split-Path $dest -Parent
        if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        Invoke-WebRequest "$base/$_" -OutFile $dest
    }
}

$Target = Get-Location
if (-not (Test-Path "$Target\package.json")) {
    Write-Error "Run from procure-copilot root (package.json missing)"
}

Write-Host "Applying hero patch to $Target"
python (Join-Path $RepoRoot "apply.py") --target $Target --patch $RepoRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Next:"
Write-Host "  npm run build"
Write-Host "  npx opennextjs-cloudflare build"
Write-Host "  node scripts/copy-public-assets.mjs"
Write-Host "  git add -A"
Write-Host "  git commit -m 'Hero: supermarket background, remove demo gif'"
Write-Host "  git push origin main"
