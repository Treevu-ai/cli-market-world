#!/usr/bin/env python3
"""Cancel PayPal subscriptions stuck in APPROVAL_PENDING (smoke tests).

Usage:
  fly ssh console -a cli-market-api -C "python ops/paypal_cleanup_pending.py"
  fly ssh console -a cli-market-api -C "python ops/paypal_cleanup_pending.py I-ABC I-DEF"
"""

from __future__ import annotations

import argparse
import asyncio
import json

DEFAULT_IDS = (
    "I-XNXHUDXBHS98",
    "I-SCEW3M7JXL9M",
)


async def _cancel_one(sub_id: str) -> dict:
    from market_connectors.paypal_payments import PAYPAL_API, _get_access_token
    import httpx

    token = await _get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20.0) as client:
        detail = await client.get(f"{PAYPAL_API}/v1/billing/subscriptions/{sub_id}", headers=headers)
        if detail.status_code != 200:
            return {"id": sub_id, "ok": False, "error": detail.text}
        status = detail.json().get("status", "")
        if status != "APPROVAL_PENDING":
            return {"id": sub_id, "ok": True, "skipped": True, "status": status}
        resp = await client.post(
            f"{PAYPAL_API}/v1/billing/subscriptions/{sub_id}/cancel",
            json={"reason": "Smoke test — user did not approve"},
            headers=headers,
        )
        if resp.status_code not in (200, 204):
            if "RESOURCE_NOT_FOUND" in resp.text or "INVALID_RESOURCE_ID" in resp.text:
                return {"id": sub_id, "ok": True, "already_gone": True, "status": status}
            return {"id": sub_id, "ok": False, "status": status, "error": resp.text}
        return {"id": sub_id, "ok": True, "cancelled": True, "status": status}


async def main(ids: list[str]) -> int:
    results = []
    for sub_id in ids:
        results.append(await _cancel_one(sub_id))
    print(json.dumps(results, indent=2))
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="*", help="Subscription IDs (default: smoke-test IDs)")
    args = parser.parse_args()
    ids = args.ids or list(DEFAULT_IDS)
    raise SystemExit(asyncio.run(main(ids)))