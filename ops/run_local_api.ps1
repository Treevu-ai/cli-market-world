# Start CLI Market API locally with .env loaded (Railway secrets).
#
#   .\ops\run_local_api.ps1
#   .\ops\run_local_api.ps1 -Pull          # refresh .env from Railway first
#   .\ops\run_local_api.ps1 -Port 8765
#
# Requires: Python + .env (run: python ops/pull_railway_env.py)

param(
    [switch]$Pull,
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Import-DotEnv {
    param([string]$Path)
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $name = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        if (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        ) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        Set-Item -Path "env:$name" -Value $value
    }
}

if ($Pull) {
    Write-Host "Pulling variables from Railway..."
    python ops/pull_railway_env.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$envFile = Join-Path $Root ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Host ""
    Write-Host "No .env found. Run one of:" -ForegroundColor Yellow
    Write-Host "  python ops/pull_railway_env.py"
    Write-Host "  .\ops\run_local_api.ps1 -Pull"
    Write-Host ""
    Write-Host "Starting with SQLite fallback (no Railway Postgres)." -ForegroundColor Yellow
} else {
    Import-DotEnv -Path $envFile
    if ($env:DATABASE_URL) {
        $dbHost = if ($env:DATABASE_URL -match "@([^/:]+)") { $matches[1] } else { "?" }
        Write-Host "Loaded .env — DATABASE_URL host: $dbHost"
    } else {
        Write-Host "Loaded .env (no DATABASE_URL — SQLite fallback)"
    }
}

$env:PORT = "$Port"
$hostAddr = if ($env:HOST) { $env:HOST } else { "127.0.0.1" }

Write-Host ""
Write-Host "API:        http://${hostAddr}:$Port"
Write-Host "Docs:       http://${hostAddr}:$Port/docs"
Write-Host "Collector:  http://${hostAddr}:$Port/health/collector"
Write-Host "Ctrl+C to stop"
Write-Host ""

python market_server.py