#!/usr/bin/env python3
"""PayPal live E2E gate — GO-LIVE-CHECKOUT.md §5.

Automates register → export 403 → /billing/paypal (approve_url).
Manual step: open approve_url in browser, approve with live PayPal, then --poll or --verify.

Usage:
  python3 ops/paypal_live_e2e.py --prepare
  python3 ops/paypal_live_e2e.py --prepare --json
  python3 ops/paypal_live_e2e.py --poll --api-key sk-...
  python3 ops/paypal_live_e2e.py --verify --api-key sk-...
  python3 ops/paypal_live_e2e.py --full --timeout 600

Env:
  MARKET_API_URL — default production Railway API
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

OPS = Path(__file__).resolve().parent
sys.path.insert(0, str(OPS))

from payments_e2e import DEFAULT_API, http_json, register_user  # noqa: E402

STATE_PATH = OPS / ".paypal-e2e-state.json"


def _base() -> str:
    return os.getenv("MARKET_API_URL", DEFAULT_API).rstrip("/")


def _save_state(data: dict) -> None:
    STATE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def export_status(base: str, api_key: str) -> int:
    status, _, _ = http_json(
        base,
        "POST",
        "/v1/data/export",
        token=api_key,
        body={},
    )
    return status


def subscription_tier(base: str, api_key: str) -> str | None:
    status, data, _ = http_json(base, "GET", "/auth/subscription", token=api_key)
    if status != 200 or not isinstance(data, dict):
        return None
    sub = data.get("subscription") or data
    if isinstance(sub, dict):
        return sub.get("tier")
    return data.get("tier")


def prepare(*, write_state: bool = True) -> dict:
    base = _base()
    username, api_key = register_user(base)

    free_export = export_status(base, api_key)
    if free_export != 403:
        raise SystemExit(f"FAIL: export on free tier expected 403, got {free_export}")

    status, data, _ = http_json(base, "POST", "/billing/paypal", token=api_key)
    if status != 200 or not isinstance(data, dict) or not data.get("ok"):
        raise SystemExit(f"FAIL: /billing/paypal — {status} {data}")

    approve_url = data.get("approve_url") or ""
    if not approve_url:
        raise SystemExit(f"FAIL: missing approve_url in {data}")

    out = {
        "phase": "awaiting_paypal_approval",
        "api_base": base,
        "username": username,
        "api_key": api_key,
        "subscription_id": data.get("subscription_id"),
        "request_id": data.get("request_id"),
        "approve_url": approve_url,
        "free_export_status": free_export,
        "prepared_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if write_state:
        _save_state(out)
    return out


def poll_tier(api_key: str, *, timeout_sec: int = 300, interval_sec: int = 5) -> str:
    base = _base()
    deadline = time.time() + timeout_sec
    last: str | None = None
    while time.time() < deadline:
        last = subscription_tier(base, api_key)
        if last == "pro":
            return last
        time.sleep(interval_sec)
    raise SystemExit(f"FAIL: tier still not pro after {timeout_sec}s (last={last!r})")


def verify(api_key: str) -> dict:
    base = _base()
    tier = subscription_tier(base, api_key)
    export_code = export_status(base, api_key)
    ok = tier == "pro" and export_code == 200
    return {
        "ok": ok,
        "tier": tier,
        "export_status": export_code,
        "username": _load_state().get("username"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="PayPal live E2E (GO-LIVE §5)")
    parser.add_argument("--prepare", action="store_true", help="Register + 403 export + billing/paypal")
    parser.add_argument("--poll", action="store_true", help="Wait until tier=pro after manual approval")
    parser.add_argument("--verify", action="store_true", help="Assert tier=pro and export=200")
    parser.add_argument("--full", action="store_true", help="prepare → poll → verify")
    parser.add_argument("--api-key", default="", help="sk- key (default: state file)")
    parser.add_argument("--timeout", type=int, default=300, help="Poll timeout seconds")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--no-state", action="store_true", help="Do not write ops/.paypal-e2e-state.json")
    args = parser.parse_args()

    if not any((args.prepare, args.poll, args.verify, args.full)):
        parser.error("one of --prepare, --poll, --verify, --full required")

    api_key = (args.api_key or "").strip() or _load_state().get("api_key", "")

    if args.full:
        prep = prepare(write_state=not args.no_state)
        if args.json:
            print(json.dumps({**prep, "next": "open approve_url in browser"}, indent=2))
        else:
            print(f"User: {prep['username']}")
            print(f"Approve: {prep['approve_url']}")
            print("Complete PayPal approval, then re-run with --poll or --verify")
        print("Waiting for PayPal webhook...", file=sys.stderr)
        poll_tier(prep["api_key"], timeout_sec=args.timeout)
        result = verify(prep["api_key"])
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"VERIFY tier={result['tier']} export={result['export_status']}")
        return 0 if result["ok"] else 1

    if args.prepare:
        prep = prepare(write_state=not args.no_state)
        if args.json:
            print(json.dumps(prep, indent=2))
        else:
            print(f"PASS prepare — user {prep['username']}")
            print(f"  export (free): {prep['free_export_status']}")
            print(f"  subscription: {prep['subscription_id']}")
            print(f"  approve_url: {prep['approve_url']}")
            print(f"  state: {STATE_PATH}")
            print("\nNext: open approve_url → approve live PayPal → python3 ops/paypal_live_e2e.py --verify")
        return 0

    if not api_key:
        raise SystemExit("api-key required (or run --prepare first)")

    if args.poll:
        tier = poll_tier(api_key, timeout_sec=args.timeout)
        if args.json:
            print(json.dumps({"tier": tier}, indent=2))
        else:
            print(f"PASS poll — tier={tier}")
        return 0

    if args.verify:
        result = verify(api_key)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "PASS" if result["ok"] else "FAIL"
            print(f"{status} verify — tier={result['tier']} export={result['export_status']}")
            if result["ok"]:
                print("Cancel test subscription in PayPal → expect tier free (webhook)")
        return 0 if result["ok"] else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
