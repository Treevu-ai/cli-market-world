# Apply Procure SEO/GEO patch (PowerShell)

param(
    [string]$Target = (Get-Location).Path,
    [string]$Patch = (Join-Path $PSScriptRoot ".")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path (Join-Path $Target "package.json"))) {
    Write-Error "Not a Node project: $Target"
}

Write-Host "Applying SEO patch -> $Target"

python (Join-Path $Patch "apply.py") --target $Target --patch $Patch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nOptional verify:"
Write-Host '  (Invoke-WebRequest "https://procurecopilot.com/procure").Content -match "procurecopilot.com/procure"'
