#!/usr/bin/env bash
# Quick smoke test before first client — run from repo root.
set -euo pipefail
API="${MARKET_API_URL:-https://cli-market-production.up.railway.app}"

echo "→ API health"
curl -sf "$API/" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('status')=='running', d"

echo "→ Pro request (no SMTP ok — expects payment_link)"
curl -sf -X POST "$API/billing/request-pro" \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke+'"$(date +%s)"'@cli-market.dev","lang":"es"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok') and d.get('payment_link'), d; print('  ref:', d.get('request_id'))"

echo "→ Landing llms.txt"
curl -sfI "https://cli-market.dev/llms.txt" | head -1

echo "✓ Smoke OK — see ops/E2E_CLIENT_JOURNEY.md for full journey"
