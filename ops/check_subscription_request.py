#!/usr/bin/env python3
"""Verify (and optionally close) a Pro billing request in production DB."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from market_core import (  # noqa: E402
    db_find_subscription_request,
    db_get_subscription,
    db_mark_subscription_request_activated,
    ensure_db_initialized,
    get_db,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Check Pro subscription request status")
    p.add_argument("request_id", help="PRO-XXXXXXXX")
    p.add_argument("--username", default="", help="CLI username hint if ref lookup fails")
    p.add_argument(
        "--fix-pending",
        action="store_true",
        help="If user tier is pro but request still pending, mark request activated",
    )
    args = p.parse_args()

    request_id = args.request_id.strip().upper()
    username_hint = (args.username or "").strip()
    if not request_id.startswith("PRO-"):
        print(f"Invalid ref: {request_id}", file=sys.stderr)
        return 1

    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set (Fly secrets can't be read back via CLI — export it directly)", file=sys.stderr)
        return 1

    ensure_db_initialized()
    req = db_find_subscription_request(request_id=request_id)
    db = get_db()
    if not req:
        like = db.execute(
            "SELECT id, username, email, status, payment_link, created_at "
            "FROM subscription_requests WHERE id LIKE ? OR username=? ORDER BY created_at DESC LIMIT 10",
            (f"{request_id[:8]}%", username_hint or ""),
        ).fetchall()
        if like:
            print("nearby_requests:")
            for row in like:
                print(f"  {dict(row)}")
            for row in like:
                if (row["id"] or "").upper() == request_id:
                    req = dict(row)
                    break
            if not req and len(like) == 1:
                req = dict(like[0])
                request_id = req["id"]
                print(f"using_request_id={request_id}")
    if not req:
        sub_row = None
        if username_hint:
            sub_row = db.execute(
                "SELECT username, tier, req_limit_day FROM subscriptions WHERE username=?",
                (username_hint,),
            ).fetchone()
        total_reqs = db.execute("SELECT COUNT(*) AS n FROM subscription_requests").fetchone()
        print(f"subscription_requests_total={total_reqs['n'] if total_reqs else '?'}")
        if sub_row:
            print(f"subscription_row={dict(sub_row)}")
        db.close()
        if sub_row and (sub_row["tier"] or "").lower() == "pro":
            print(f"OK: {username_hint} tier=pro (billing request row missing for {request_id})")
            return 0
        print(f"NOT FOUND: {request_id}")
        return 1

    username = (req.get("username") or "").strip()
    status = (req.get("status") or "").strip().lower()
    sub = db_get_subscription(username) if username else None
    tier = (sub or {}).get("tier", "?")

    print(f"request_id={request_id}")
    print(f"username={username}")
    print(f"email={req.get('email')}")
    print(f"request_status={status}")
    print(f"subscription_tier={tier}")
    print(f"payment_link={(req.get('payment_link') or '')[:120]}")

    activated_events = db.execute(
        "SELECT event, meta, created_at FROM funnel_events "
        "WHERE username=? AND event='activated' ORDER BY created_at DESC LIMIT 3",
        (username,),
    ).fetchall()
    db.close()
    if activated_events:
        print("funnel_activated:")
        for row in activated_events:
            print(f"  {dict(row)}")

    if args.fix_pending and status == "pending" and tier == "pro":
        db_mark_subscription_request_activated(request_id, username)
        print(f"FIXED: marked {request_id} activated (tier already pro)")
        req = db_find_subscription_request(request_id=request_id)
        print(f"request_status={req.get('status')}")

    ok = status == "activated" or (args.fix_pending and tier == "pro")
    if status != "activated" and tier == "pro" and not args.fix_pending:
        print("NOTE: tier is pro but request not activated — rerun with --fix-pending")
        return 2
    if status == "activated" and tier == "pro":
        print("OK: paid Pro active and request closed")
        return 0
    if tier != "pro":
        print(f"BLOCKED: tier is {tier}, not pro — needs payment webhook or ops activation")
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
