# Build + deploy landing to Cloudflare Pages (cli-market-world project).
# Requires: CLOUDFLARE_API_TOKEN (+ optional CLOUDFLARE_ACCOUNT_ID for wrangler).
#
#   $env:CLOUDFLARE_API_TOKEN = "..."
#   .\ops\deploy_landing.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

if (-not $env:CLOUDFLARE_API_TOKEN) {
    Write-Error "Set CLOUDFLARE_API_TOKEN before running."
}

Push-Location landing
npm ci
npm run build
Pop-Location

npx wrangler pages deploy landing/out --project-name=cli-market-world --branch=main
Write-Host "Deployed. Check: https://cli-market.dev/account"