#!/usr/bin/env python3
"""Create PayPal billing plans. Uses PAYPAL_* env vars."""
import asyncio
import json
import sys

from market_connectors.paypal_payments import create_billing_plan


async def main() -> int:
    plans = sys.argv[1:] or ["pro_annual"]
    out = {}
    for plan in plans:
        print(f"Creating {plan}...", file=sys.stderr)
        out[plan] = await create_billing_plan(plan)
        print(f"  -> {out[plan].get('id', out[plan])}", file=sys.stderr)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
