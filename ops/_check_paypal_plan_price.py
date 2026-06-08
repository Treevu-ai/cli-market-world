#!/usr/bin/env python3
"""One-off: read PayPal billing plan price vs PRO_PRICE_USD env."""
from __future__ import annotations

import asyncio
import json
import os
import sys

import httpx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


async def main() -> int:
    from market_connectors.paypal_payments import (
        PAYPAL_API,
        PAYPAL_PLAN_ID,
        PRO_PRICE_USD,
        _get_access_token,
    )

    plan_id = PAYPAL_PLAN_ID
    if not plan_id:
        print(json.dumps({"error": "PAYPAL_PLAN_ID not set"}))
        return 1

    token = await _get_access_token()
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{PAYPAL_API}/v1/billing/plans/{plan_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code != 200:
            print(json.dumps({"error": resp.text, "status": resp.status_code}))
            return 1
        data = resp.json()

    cycles = data.get("billing_cycles") or []
    paypal_price = None
    if cycles:
        paypal_price = (
            cycles[0].get("pricing_scheme", {}).get("fixed_price", {}).get("value")
        )

    out = {
        "plan_id": plan_id,
        "plan_name": data.get("name"),
        "status": data.get("status"),
        "paypal_price_usd": paypal_price,
        "PRO_PRICE_USD_env": PRO_PRICE_USD,
        "PRO_PAYMENT_URL": os.getenv("PRO_PAYMENT_URL"),
        "PRO_PRICE_LABEL": os.getenv("PRO_PRICE_LABEL"),
        "aligned": paypal_price is not None and float(paypal_price) == float(PRO_PRICE_USD),
    }
    print(json.dumps(out, indent=2))
    return 0 if out["aligned"] else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))