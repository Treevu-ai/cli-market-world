# PayPal live E2E gate — GO-LIVE-CHECKOUT.md §5 (Windows)
#
#   .\ops\paypal_live_e2e.ps1 --prepare
#   .\ops\paypal_live_e2e.ps1 --verify
#   .\ops\paypal_live_e2e.ps1 --status
#
# Uses `py -3` or `python` — avoids the broken Microsoft Store `python3` alias.

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Passthrough
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Resolve-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Exe = "py"; Prefix = @("-3") }
        }
    }
    foreach ($name in @("python", "python3")) {
        if (Get-Command $name -ErrorAction SilentlyContinue) {
            & $name -c "import sys" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return @{ Exe = $name; Prefix = @() }
            }
        }
    }
    return $null
}

$py = Resolve-PythonCommand
if (-not $py) {
    Write-Host ""
    Write-Host "Python not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Install: https://www.python.org/downloads/ — enable 'Add python.exe to PATH'"
    Write-Host "2. Or disable Store alias: Settings > Apps > Advanced app settings >"
    Write-Host "   App execution aliases — turn OFF python.exe and python3.exe"
    Write-Host ""
    Write-Host "Then retry: .\ops\paypal_live_e2e.ps1 --prepare"
    exit 1
}

$scriptPath = Join-Path $Root "ops\paypal_live_e2e.py"
& $py.Exe @($py.Prefix + $scriptPath) @Passthrough
exit $LASTEXITCODE
