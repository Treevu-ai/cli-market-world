# Sync landing stats, MCP manifests, and procure-copilot/lib/market-stats.ts from market_stats.py.
#
#   .\ops\sync_market_stats.ps1
#
# Windows: use this instead of `python3` (Store alias often breaks that command).
# Requires: Python 3.10+ on PATH, sibling repo ../cli-market-core checked out.

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Test-PythonInvocation {
    param([string[]]$Invocation)
    & @Invocation -c "import sys; print(sys.version)" 1>$null 2>$null
    return $LASTEXITCODE -eq 0
}

function Get-PythonInvocation {
    $candidates = @(
        @("py", "-3"),
        @("python"),
        @("python3")
    )
    foreach ($inv in $candidates) {
        if (Test-PythonInvocation -Invocation $inv) {
            return $inv
        }
    }
    Write-Host ""
    Write-Host "Python 3 not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install from https://www.python.org/downloads/ and enable 'Add python.exe to PATH'."
    Write-Host "Or use the Windows launcher after install:"
    Write-Host "  py -3 ops/sync_market_stats.py"
    Write-Host ""
    Write-Host "If `python` opens the Microsoft Store, disable the stub aliases:"
    Write-Host "  Settings > Apps > Advanced app settings > App execution aliases"
    Write-Host "  Turn OFF python.exe and python3.exe"
    Write-Host ""
    exit 1
}

$coreRoot = Join-Path (Split-Path $Root -Parent) "cli-market-core"
if (-not (Test-Path -LiteralPath $coreRoot)) {
    Write-Host "Missing sibling repo: $coreRoot" -ForegroundColor Red
    Write-Host "Clone cli-market-core beside cli-market-world, then retry."
    exit 1
}

$py = Get-PythonInvocation
Write-Host ("Using: {0}" -f ($py -join " "))
Write-Host "Diagnosing market_core source..."
& @py (Join-Path $Root "ops/diagnose_sync_source.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& @py (Join-Path $Root "ops/sync_market_stats.py") @ScriptArgs
exit $LASTEXITCODE
