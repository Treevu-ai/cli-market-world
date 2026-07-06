#!/usr/bin/env python3
"""Manage PayPal hosted payment link (NCP) for Pro manual checkout."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid

import httpx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DEFAULT_BUTTON_ID = "PLB-K47XCNUKG24P"
PRO_AMOUNT = os.getenv("PRO_PRICE_USD", "39")


async def _token() -> tuple[str, str]:
    from market_connectors.paypal_payments import PAYPAL_API, _get_access_token

    return await _get_access_token(), PAYPAL_API


async def cmd_show(button_id: str) -> int:
    token, api = await _token()
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{api}/v1/checkout/payment-resources/{button_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
    print(json.dumps({"status": resp.status_code, "body": resp.json() if resp.content else None}, indent=2))
    return 0 if resp.status_code == 200 else 1


async def cmd_update(button_id: str, amount: str) -> int:
    token, api = await _token()
    body = {
        "integration_mode": "LINK",
        "type": "BUY_NOW",
        "reusable": "MULTIPLE",
        "return_url": "https://cli-market.dev?payment=success",
        "line_items": [
            {
                "name": "CLI Market Pro",
                "description": "Pro plan — 10,000 requests/day, alerts, full MCP + checkout",
                "unit_amount": {"currency_code": "USD", "value": f"{float(amount):.2f}"},
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.put(
            f"{api}/v1/checkout/payment-resources/{button_id}",
            json=body,
            headers=headers,
        )
        out = {"status": resp.status_code}
        if resp.content:
            try:
                out["body"] = resp.json()
            except Exception:
                out["body"] = resp.text
        print(json.dumps(out, indent=2))
    return 0 if resp.status_code in (200, 204) else 1


async def cmd_verify(button_id: str) -> int:
    import re

    url = f"https://www.paypal.com/ncp/payment/{button_id}"
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        resp = await client.get(url)
    html = resp.text
    amount = None
    m = re.search(r'"amount","value":"([0-9.]+)"', html)
    if m:
        amount = m.group(1)
    print(json.dumps({"id": button_id, "url": url, "amount_usd": amount, "status_code": resp.status_code}, indent=2))
    expected = float(os.getenv("PRO_PRICE_USD", "39"))
    return 0 if amount and float(amount) == expected else 1


async def cmd_create(amount: str) -> int:
    token, api = await _token()
    body = {
        "integration_mode": "LINK",
        "type": "BUY_NOW",
        "reusable": "MULTIPLE",
        "return_url": "https://cli-market.dev?payment=success",
        "line_items": [
            {
                "name": "CLI Market Pro",
                "description": "Pro plan — 10,000 requests/day, alerts, full MCP + checkout",
                "unit_amount": {"currency_code": "USD", "value": f"{float(amount):.2f}"},
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "PayPal-Request-Id": str(uuid.uuid4()),
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            f"{api}/v1/checkout/payment-resources",
            json=body,
            headers=headers,
        )
        data = resp.json() if resp.content else {}
        payment_link = next(
            (l["href"] for l in data.get("links", []) if l.get("rel") == "payment_link"),
            None,
        )
        print(
            json.dumps(
                {
                    "status": resp.status_code,
                    "id": data.get("id"),
                    "payment_link": payment_link,
                    "amount_usd": amount,
                    "fly": (
                        f"fly secrets set PRO_PAYMENT_URL={payment_link} --app cli-market-api"
                        if payment_link
                        else None
                    ),
                    "landing_env": (
                        f"NEXT_PUBLIC_PAYPAL_HOSTED_BUTTON_ID={data.get('id')}"
                        if data.get("id")
                        else None
                    ),
                },
                indent=2,
            )
        )
    return 0 if resp.status_code in (200, 201) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="PayPal hosted payment link ops")
    sub = parser.add_subparsers(dest="command", required=True)

    p_show = sub.add_parser("show", help="GET payment resource by id")
    p_show.add_argument("--id", default=DEFAULT_BUTTON_ID)

    p_up = sub.add_parser("update", help="PUT payment resource price/details")
    p_up.add_argument("--id", default=DEFAULT_BUTTON_ID)
    p_up.add_argument("--amount", default=PRO_AMOUNT)

    p_new = sub.add_parser("create", help="Create new $39 payment link")
    p_new.add_argument("--amount", default=PRO_AMOUNT)

    p_ver = sub.add_parser("verify", help="Fetch NCP page and read amount")
    p_ver.add_argument("--id", default=DEFAULT_BUTTON_ID)

    args = parser.parse_args()
    if not os.getenv("PAYPAL_CLIENT_ID") or not os.getenv("PAYPAL_CLIENT_SECRET"):
        print("Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET.", file=sys.stderr)
        return 1

    handlers = {
        "show": lambda: cmd_show(args.id),
        "update": lambda: cmd_update(args.id, str(args.amount)),
        "create": lambda: cmd_create(str(args.amount)),
        "verify": lambda: cmd_verify(args.id),
    }
    return asyncio.run(handlers[args.command]())


if __name__ == "__main__":
    raise SystemExit(main())