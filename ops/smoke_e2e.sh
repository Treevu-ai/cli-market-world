#!/usr/bin/env bash
# Quick smoke test before first client — run from repo root.
set -euo pipefail
API="${MARKET_API_URL:-https://cli-market-api.fly.dev}"

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

echo "→ Product search (business-logic canary, not just uptime)"
# Catches what uptime/route-mounted checks can't: a deploy where the code
# that actually computes search results silently regressed (confirmed live
# 2026-07-21 — a require_all fix landed in cli-market-core but the sibling
# change in this repo's routers/search.py was never committed; CI, the
# import sanity check, and the old health-only smoke test all stayed green
# because nothing here exercised search *behavior*, only that the process
# was up). Uses the public demo-session token so no CI secret is needed.
_retry python3 - <<PY
import json
import urllib.error
import urllib.request

api = "$API".rstrip("/")


def http_json(path, *, method="GET", body=None, token=None):
    url = api + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        return exc.code, json.loads(raw) if raw else {}


status, session = http_json("/public/demo/session", method="POST", body={})
assert status == 200, (status, session)
token = session.get("token") or session.get("demo_token")
assert token and token.startswith("demo-"), session

status, result = http_json(
    "/products/search",
    method="POST",
    body={"query": "iphone 11", "store": "grintek_pe", "require_all": True, "limit": 5},
    token=token,
)
assert status == 200, (status, result)
names = [r.get("name", "") for r in result.get("results", [])]
assert result.get("total") == 1 and any("iPhone 11" in n for n in names), (
    f"require_all search canary failed — expected exactly 1 result containing "
    f"'iPhone 11', got total={result.get('total')} names={names}"
)
print(f"  ok: 1 result, '{names[0]}'")
PY

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
assert url and str(url).startswith(("http://", "https://", "yape://", "plin://")), data

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

# affordability — 200 (public), 401 (auth required), or 422 (missing param) all confirm route mounted
_status=$(curl -s -o /dev/null -w "%{http_code}" "$API/v1/intel/affordability?country=PE")
[ "$_status" = "200" ] || [ "$_status" = "401" ] || [ "$_status" = "422" ] || { echo "✗ /v1/intel/affordability → $_status (want 200/401/422)"; exit 1; }
echo "  affordability: $_status (route mounted)"

# affiliate-click requires auth (401 means route is mounted)
_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API/v1/action/affiliate-click" \
  -H "Content-Type: application/json" -d '{"store":"wong","product_id":"smoke","url":"https://example.com"}')
[ "$_status" = "401" ] || [ "$_status" = "422" ] || { echo "✗ /v1/action/affiliate-click → $_status (want 401/422)"; exit 1; }
echo "  affiliate-click: $_status (route mounted)"

echo "✓ Smoke OK — see ops/E2E_CLIENT_JOURNEY.md for full journey"
