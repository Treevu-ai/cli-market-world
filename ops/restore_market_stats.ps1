# Restore marketStats.ts from origin/main (skip sync when local core is stale).
#
#   .\ops\restore_market_stats.ps1
#
# Also restores procure-copilot/lib/market-stats.ts if sibling repo exists.

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

Write-Host "Fetching origin/main..."
git fetch origin main | Out-Null
git checkout origin/main -- landing/lib/marketStats.ts
Write-Host "Restored landing/lib/marketStats.ts from origin/main"

Select-String -Path (Join-Path $Root "landing/lib/marketStats.ts") -Pattern 'mcpTools|pricesVerifiedLabel'

$procure = Join-Path (Split-Path $Root -Parent) "procure-copilot/lib/market-stats.ts"
if (Test-Path -LiteralPath $procure) {
    Push-Location (Split-Path $procure -Parent | Split-Path -Parent)
    git fetch origin main 2>$null | Out-Null
    git checkout origin/main -- lib/market-stats.ts
    Pop-Location
    Write-Host "Restored procure-copilot/lib/market-stats.ts from origin/main"
    Select-String -Path $procure -Pattern 'mcpTools|pricesVerifiedLabel'
}

Write-Host ""
Write-Host "Done. Do NOT run sync_market_stats until cli-market-core is on main (PR #107+)."
