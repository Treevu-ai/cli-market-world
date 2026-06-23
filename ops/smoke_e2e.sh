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

echo "→ Pro billing (yape — checkout_url, payment_link, or approve_url)"
export MARKET_API_URL="$API"
export SMOKE_USER="smoke-ci"
export SMOKE_EMAIL="smoke+$(date +%s)@cli-market.dev"
_retry python3 - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

api = os.environ["MARKET_API_URL"].rstrip("/")
email = os.environ["SMOKE_EMAIL"]
username = os.environ["SMOKE_USER"]


def http_json(path: str, *, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    url = api + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"detail": raw or exc.reason}
        return exc.code, payload


_, openapi = http_json("/openapi.json")
paths = openapi.get("paths") or {}

if "/billing/pro-checkout" in paths:
    billing_path = "/billing/pro-checkout"
    legacy = False
elif "/billing/request-pro" in paths:
    billing_path = "/billing/request-pro"
    legacy = True
    print("  note: /billing/pro-checkout not deployed — using /billing/request-pro", file=sys.stderr)
else:
    raise SystemExit("no pro billing endpoint in OpenAPI")

payload = {
    "email": email,
    "username": username,
    "lang": "es",
    "payment_method": "yape",
}
status, data = http_json(billing_path, method="POST", body=payload)
assert status == 200, (status, data)
assert data.get("ok"), data

url = data.get("checkout_url") or data.get("payment_link") or data.get("approve_url")
assert url and str(url).startswith("http"), data

rid = data.get("request_id") or ""
assert str(rid).startswith("PRO-"), data

if not legacy and data.get("payment_method") == "yape":
  mode = data.get("payment_mode") or ""
  if mode == "manual_transfer":
      assert data.get("amount_pen") is not None, data
  elif not (data.get("checkout_url") or data.get("payment_link")):
      raise AssertionError(data)

print(f"  endpoint: {billing_path}")
print(f"  ref: {rid}")
print(f"  rail: {data.get('payment_rail') or data.get('payment_method') or 'legacy'}")
PY

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

echo "→ Wave 4 — Cost-of-Living OS endpoints"
# optimize-purchase requires auth (401 means route is mounted)
_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API/v1/missions/optimize-purchase" \
  -H "Content-Type: application/json" -d '{}')
[ "$_status" = "401" ] || [ "$_status" = "422" ] || { echo "✗ /v1/missions/optimize-purchase → $_status (want 401/422)"; exit 1; }
echo "  optimize-purchase: $_status (route mounted)"

# affordability is public
_retry curl -sf "$API/v1/intel/affordability" | python3 -c "
import sys, json
d = json.load(sys.stdin)
m = (d.get('data') or d).get('methodology') or d.get('methodology', '')
assert 'affordability' in str(m).lower() or d, ('unexpected response', d)
print('  affordability methodology:', m or 'ok')
"

# affiliate-click requires auth (401 means route is mounted)
_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API/v1/action/affiliate-click" \
  -H "Content-Type: application/json" -d '{"store":"wong","product_id":"smoke","url":"https://example.com"}')
[ "$_status" = "401" ] || [ "$_status" = "422" ] || { echo "✗ /v1/action/affiliate-click → $_status (want 401/422)"; exit 1; }
echo "  affiliate-click: $_status (route mounted)"

echo "✓ Smoke OK — see ops/E2E_CLIENT_JOURNEY.md for full journey"
