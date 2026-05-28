#!/usr/bin/env python3
"""PayPal REST sandbox setup for CLI Market (no Braintree).

Usage (from repo root, with sandbox credentials in env):

  export PAYPAL_CLIENT_ID=...
  export PAYPAL_CLIENT_SECRET=...
  export PAYPAL_SANDBOX=true

  python3 ops/paypal_sandbox_setup.py check
  python3 ops/paypal_sandbox_setup.py create-plan
  python3 ops/paypal_sandbox_setup.py register-webhook https://cli-market-production.up.railway.app/checkout/paypal-webhook
  python3 ops/paypal_sandbox_setup.py list-webhooks
  python3 ops/paypal_sandbox_setup.py test-upgrade admin

Requires: httpx (already in project deps).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


async def cmd_check() -> int:
    from market_connectors.paypal_payments import check_connection

    try:
        info = await check_connection()
        print(json.dumps(info, indent=2))
        print("\n✓ Sandbox credentials OK")
        return 0
    except Exception as e:
        print(f"✗ Auth failed: {e}", file=sys.stderr)
        print("\nGet sandbox Client ID + Secret from:")
        print("  https://developer.paypal.com/dashboard/applications/sandbox")
        return 1


async def cmd_create_plan(amount: float, currency: str) -> int:
    from market_connectors.paypal_payments import create_pro_plan

    try:
        result = await create_pro_plan(amount, currency)
        if "error" in result:
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2))
        print("\nAdd to Railway (sandbox):")
        print(f"  PAYPAL_PLAN_ID={result['plan_id']}")
        return 0
    except Exception as e:
        print(f"✗ Plan creation failed: {e}", file=sys.stderr)
        return 1


async def cmd_register_webhook(url: str) -> int:
    from market_connectors.paypal_payments import register_webhook

    try:
        result = await register_webhook(url)
        if "error" in result:
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2))
        print("\nAdd to Railway (sandbox):")
        print(f"  PAYPAL_WEBHOOK_ID={result['webhook_id']}")
        print(f"  PAYPAL_SANDBOX=true")
        return 0
    except Exception as e:
        print(f"✗ Webhook registration failed: {e}", file=sys.stderr)
        return 1


async def cmd_list_webhooks() -> int:
    from market_connectors.paypal_payments import list_webhooks

    result = await list_webhooks()
    print(json.dumps(result, indent=2))
    return 0 if "webhooks" in result else 1


async def cmd_test_upgrade(username: str) -> int:
    from market_connectors.paypal_payments import create_subscription

    try:
        result = await create_subscription(username=username)
        print(json.dumps(result, indent=2))
        if result.get("approve_url"):
            print("\n→ Open this URL in browser (log in with sandbox buyer account):")
            print(result["approve_url"])
            print("\nSandbox buyer accounts:")
            print("  https://developer.paypal.com/dashboard/accounts")
            return 0
        return 1
    except Exception as e:
        print(f"✗ Subscription create failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market PayPal sandbox setup")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Verify PAYPAL_CLIENT_ID/SECRET")

    p_plan = sub.add_parser("create-plan", help="Create Pro billing plan in sandbox")
    p_plan.add_argument("--amount", type=float, default=49.0)
    p_plan.add_argument("--currency", default="USD")

    p_wh = sub.add_parser("register-webhook", help="Register webhook URL in PayPal")
    p_wh.add_argument("url", help="Public HTTPS URL, e.g. .../checkout/paypal-webhook")

    sub.add_parser("list-webhooks", help="List webhooks in this sandbox app")

    p_up = sub.add_parser("test-upgrade", help="Create subscription + print approve URL")
    p_up.add_argument("username", nargs="?", default="admin")

    args = parser.parse_args()

    if not os.getenv("PAYPAL_CLIENT_ID") or not os.getenv("PAYPAL_CLIENT_SECRET"):
        print("Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET first.", file=sys.stderr)
        return 1

    if os.getenv("PAYPAL_SANDBOX", "true").lower() not in ("1", "true", "yes"):
        print("Warning: PAYPAL_SANDBOX is not true — this will hit LIVE PayPal.", file=sys.stderr)

    handlers = {
        "check": cmd_check,
        "create-plan": lambda: cmd_create_plan(args.amount, args.currency),
        "register-webhook": lambda: cmd_register_webhook(args.url),
        "list-webhooks": cmd_list_webhooks,
        "test-upgrade": lambda: cmd_test_upgrade(args.username),
    }
    return asyncio.run(handlers[args.command]())


if __name__ == "__main__":
    raise SystemExit(main())
