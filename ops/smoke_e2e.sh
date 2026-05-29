#!/usr/bin/env bash
# Quick smoke test before first client — run from repo root.
set -euo pipefail
API="${MARKET_API_URL:-https://cli-market-production.up.railway.app}"

_retry() {
  local n=1 max=3 delay=5
  while true; do
    if "$@"; then
      return 0
    fi
    if (( n >= max )); then
      echo "✗ Failed after ${max} attempts: $*" >&2
      return 1
    fi
    echo "  retry $n/$max in ${delay}s..." >&2
    sleep "$delay"
    n=$((n + 1))
  done
}

echo "→ API health"
_retry curl -sf "$API/" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('status')=='running', d"

echo "→ Pro request (no SMTP ok — expects payment_link)"
_retry curl -sf -X POST "$API/billing/request-pro" \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke+'"$(date +%s)"'@cli-market.dev","lang":"es"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok') and d.get('payment_link'), d; print('  ref:', d.get('request_id'))"

echo "→ Landing llms.txt"
_retry curl -sfI "https://cli-market.dev/llms.txt" | head -1 | grep -q "200"

echo "→ Dashboard data"
_retry curl -sf "$API/dashboard/data" | python3 -c "
import sys, json
d = json.load(sys.stdin)
k = d.get('kpis', {})
assert (k.get('total_indexed') or k.get('total_snapshots') or 0) >= 1000, k
print('  indexed:', k.get('total_indexed', k.get('total_snapshots')))
"

echo "✓ Smoke OK — see ops/E2E_CLIENT_JOURNEY.md for full journey"
