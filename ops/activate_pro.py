#!/usr/bin/env python3
"""Activate Pro tier after manual payment confirmation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from market_core import (
    db_find_subscription_request,
    db_mark_subscription_request_activated,
    db_set_subscription,
    ensure_db_initialized,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Activate CLI Market Pro after payment")
    p.add_argument("username", nargs="?", help="CLI username (from market login)")
    p.add_argument("--email", help="Lookup latest Pro request by subscriber email")
    p.add_argument("--request-id", dest="request_id", help="Pro request ref (PRO-XXXXXXXX)")
    args = p.parse_args()

    ensure_db_initialized()

    username = (args.username or "").strip()
    request_id = (args.request_id or "").strip()
    req = None

    if request_id:
        req = db_find_subscription_request(request_id=request_id)
        if not req:
            print(f"✗ Request not found: {request_id}", file=sys.stderr)
            return 1
        if not username:
            username = req["username"]

    if args.email and not username:
        req = db_find_subscription_request(email=args.email)
        if req:
            username = req["username"]
            if not request_id:
                request_id = req["id"]

    if not username:
        p.error("Provide username, --email, or --request-id")

    result = db_set_subscription(username, "pro")
    print(f"✓ Pro activated for {result['username']}")

    if not request_id and req:
        request_id = req.get("id", "")
    if request_id:
        db_mark_subscription_request_activated(request_id, username)
        print(f"✓ Request {request_id} marked activated")

    print("\nNext: ask customer to run `market whoami` — tier should show pro.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
