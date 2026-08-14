# Self-contained Procure checkout installer (sparse-checkout / wrong branch safe)
# Repo is PRIVATE — do not use raw.githubusercontent.com (404).
#
# From procure-copilot root:
#   gh auth login
#   gh api repos/Treevu-ai/cli-market-world/contents/patches/procure-copilot-checkout/install-checkout.ps1 -q .content | ForEach-Object { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_ -replace "`n","")) } | Set-Content install-checkout.ps1
#   .\install-checkout.ps1
#
# Or skip download — run the sparse-clone block in README.md "Private repo".

$ErrorActionPreference = "Stop"

$Target = Get-Location
if (-not (Test-Path "$Target\package.json")) {
    Write-Error "Run from procure-copilot root (package.json missing)"
}

$WorldRoot = Join-Path $env:TEMP "cli-market-world-checkout-patch"
$PatchDir = Join-Path $WorldRoot "patches\procure-copilot-checkout"

function Ensure-WorldCheckout {
    if ((Test-Path "$PatchDir\apply.py") -and (Test-Path "$WorldRoot\landing\components\BillingCheckoutModal.tsx")) {
        Write-Host "Reusing cached world checkout: $WorldRoot"
        return
    }

    Write-Host "Fetching cli-market-world (sparse: landing + patch)..."
    if (Test-Path $WorldRoot) {
        Remove-Item -Recurse -Force $WorldRoot
    }
    New-Item -ItemType Directory -Force -Path $WorldRoot | Out-Null

    git clone --depth 1 --filter=blob:none --sparse `
        https://github.com/Treevu-ai/cli-market-world.git $WorldRoot
    if ($LASTEXITCODE -ne 0) {
        Write-Error "git clone failed — run: gh auth login"
    }

    Push-Location $WorldRoot
    git sparse-checkout set `
        patches/procure-copilot-checkout `
        landing/components `
        landing/lib `
        landing/hooks
    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        Write-Error "git sparse-checkout failed"
    }
    Pop-Location

    if (-not (Test-Path "$PatchDir\apply.py")) {
        Write-Error "Patch missing after sparse checkout — check repo access"
    }
}

Ensure-WorldCheckout

Write-Host "Applying checkout patch to $Target"
python "$PatchDir\apply.py" --target $Target --world $WorldRoot --patch $PatchDir
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Verify before deploy ===" -ForegroundColor Cyan
@(
    "app\procure\subscribe\page.tsx",
    "components\ProcurePricingPanel.tsx",
    "components\BillingCheckoutModal.tsx",
    "lib\procureCta.ts"
) | ForEach-Object {
    $ok = Test-Path (Join-Path $Target $_)
    Write-Host "  $_ : $(if ($ok) { 'OK' } else { 'MISSING' })"
}

Write-Host ""
Write-Host "Cloudflare env (if not set):" -ForegroundColor Green
Write-Host "  NEXT_PUBLIC_PROCURE_MP_CHECKOUT=1"
Write-Host ""
Write-Host "Next:" -ForegroundColor Green
Write-Host "  npm run build"
Write-Host "  npx opennextjs-cloudflare deploy"
