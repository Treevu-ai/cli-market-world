#!/usr/bin/env python3
"""Verify (and optionally close) a Pro billing request in production DB."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

API_SERVICE_ID_DEFAULT = "6e74bc38-bbf2-4815-bac4-38092067d3b1"

from market_core import (  # noqa: E402
    db_find_subscription_request,
    db_get_subscription,
    db_mark_subscription_request_activated,
    ensure_db_initialized,
    get_db,
)


def _load_railway_database_url() -> str:
    railway = "railway.cmd" if sys.platform == "win32" else "railway"
    token = (os.getenv("RAILWAY_TOKEN") or os.getenv("RAILWAY_PROJECT_TOKEN") or "").strip()
    if not token:
        return ""
    env = os.environ.copy()
    env.pop("RAILWAY_API_TOKEN", None)
    env["RAILWAY_TOKEN"] = token
    service_id = (
        os.getenv("RAILWAY_API_SERVICE_ID", API_SERVICE_ID_DEFAULT).strip()
        or API_SERVICE_ID_DEFAULT
    )
    proc = subprocess.run(
        [railway, "variables", "--json", "--service", service_id],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
        timeout=90,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "railway variables failed")
    vars_map = json.loads(proc.stdout)
    return (vars_map.get("DATABASE_PUBLIC_URL") or vars_map.get("DATABASE_URL") or "").strip()


def main() -> int:
    p = argparse.ArgumentParser(description="Check Pro subscription request status")
    p.add_argument("request_id", help="PRO-XXXXXXXX")
    p.add_argument(
        "--fix-pending",
        action="store_true",
        help="If user tier is pro but request still pending, mark request activated",
    )
    args = p.parse_args()

    request_id = args.request_id.strip().upper()
    if not request_id.startswith("PRO-"):
        print(f"Invalid ref: {request_id}", file=sys.stderr)
        return 1

    if not os.getenv("DATABASE_URL"):
        db_url = _load_railway_database_url()
        if db_url:
            os.environ["DATABASE_URL"] = db_url
        else:
            print("DATABASE_URL not set and Railway token unavailable", file=sys.stderr)
            return 1

    ensure_db_initialized()
    req = db_find_subscription_request(request_id=request_id)
    if not req:
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

    db = get_db()
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
