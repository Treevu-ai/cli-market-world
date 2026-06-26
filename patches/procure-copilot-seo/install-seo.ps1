# Self-contained Procure SEO installer (no sparse-checkout needed)
# Usage: cd ~\procure-copilot; irm .../install-seo.ps1 | iex
#    or: .\install-seo.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
if (-not (Test-Path "$RepoRoot\apply.py")) {
    $RepoRoot = Join-Path $env:TEMP "procure-seo-patch"
    New-Item -ItemType Directory -Force -Path $RepoRoot | Out-Null
    $base = "https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/patches/procure-copilot-seo"
    Write-Host "Downloading patch from GitHub..."
    @(
        "apply.py",
        "lib/site.ts", "lib/seo.ts",
        "public/llms.txt", "public/og.svg", "public/og.png",
        "next-sitemap.config.js",
        "scripts/rasterize_og.mjs",
        "scripts/copy-public-assets.mjs",
        "app/dashboard/layout.tsx"
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

Write-Host "Applying SEO patch to $Target"
python (Join-Path $RepoRoot "apply.py") --target $Target --patch $RepoRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Ensure copy script exists in target
$copyScript = Join-Path $Target "scripts\copy-public-assets.mjs"
if (-not (Test-Path $copyScript)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $copyScript) | Out-Null
    Copy-Item (Join-Path $RepoRoot "scripts\copy-public-assets.mjs") $copyScript
}

# Patch package.json deploy hook
$pkgPath = Join-Path $Target "package.json"
$pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json
if (-not $pkg.scripts) { $pkg | Add-Member -NotePropertyName scripts -NotePropertyValue (@{}) }

if ($pkg.scripts.deploy -notmatch "copy-public-assets") {
    $pkg.scripts."postbuild:opennext" = "node scripts/copy-public-assets.mjs"
}

if (-not $pkg.devDependencies) { $pkg | Add-Member -NotePropertyName devDependencies -NotePropertyValue (@{}) }
$pkg.devDependencies."next-sitemap" = "^4.2.3"

$pkg | ConvertTo-Json -Depth 10 | Set-Content $pkgPath -Encoding utf8

Write-Host ""
Write-Host "=== Verify these exist BEFORE deploy ===" -ForegroundColor Cyan
@("public\og.png", "public\llms.txt", "public\llms.txt", "lib\seo.ts", "next-sitemap.config.js") | ForEach-Object {
    $ok = Test-Path (Join-Path $Target $_)
    Write-Host "  $_ : $(if ($ok) { 'OK' } else { 'MISSING' })"
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  npm install"
Write-Host "  npm run build"
Write-Host "  npx opennextjs-cloudflare build"
Write-Host "  node scripts/copy-public-assets.mjs"
Write-Host "  npx wrangler deploy"
Write-Host ""
Write-Host "After deploy:" -ForegroundColor Green
Write-Host '  (Invoke-WebRequest https://procurecopilot.com/og.png -SkipHttpErrorCheck).StatusCode'
