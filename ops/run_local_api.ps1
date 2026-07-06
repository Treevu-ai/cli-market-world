# Start CLI Market API locally with .env loaded.
#
#   .\ops\run_local_api.ps1
#   .\ops\run_local_api.ps1 -Port 8765
#
# Requires: Python + .env (copy from .env.example — Fly.io secrets can't be
# read back via CLI, so there's no automated "pull from prod" here).

param(
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

$envFile = Join-Path $Root ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Host ""
    Write-Host "No .env found. Copy .env.example to .env and fill in your values." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Starting with SQLite fallback (no Postgres)." -ForegroundColor Yellow
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