# Build + deploy landing to Cloudflare Pages (cli-market-world project).
# Requires: CLOUDFLARE_API_TOKEN (+ optional CLOUDFLARE_ACCOUNT_ID).
#
#   $env:CLOUDFLARE_API_TOKEN = "..."
#   .\ops\deploy_landing.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

if (-not $env:CLOUDFLARE_API_TOKEN) {
    Write-Error "Set CLOUDFLARE_API_TOKEN before running."
}

if (-not $env:CLOUDFLARE_ACCOUNT_ID) {
    $headers = @{ Authorization = "Bearer $env:CLOUDFLARE_API_TOKEN" }
    $resp = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts?per_page=1" -Headers $headers
    $id = $resp.result[0].id
    if (-not $id) {
        $resp = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/user/memberships?per_page=1" -Headers $headers
        $id = $resp.result[0].account.id
    }
    if (-not $id) {
        Write-Error "Could not resolve CLOUDFLARE_ACCOUNT_ID. Set it explicitly or fix token permissions."
    }
    $env:CLOUDFLARE_ACCOUNT_ID = $id
    Write-Host "Resolved Cloudflare account ID from API token"
}

Push-Location landing
npm ci
npm run build
Pop-Location

npx wrangler pages deploy landing/out --project-name=cli-market-world --branch=main --account-id=$env:CLOUDFLARE_ACCOUNT_ID
Write-Host "Deployed. Check: https://cli-market.dev/account"