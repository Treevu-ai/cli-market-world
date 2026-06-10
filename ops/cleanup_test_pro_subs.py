#!/usr/bin/env python3
"""Demote smoke/test Pro tiers in production — keep only real paid subscribers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from market_core import db_set_subscription, ensure_db_initialized, get_db

# Confirmed smoke/test accounts (not real payments).
DEMOTE_USERNAMES = (
    "user-87db316c7763",
    "user-a8d64197d3a4",
    "user-ce7da4a4e021",
    "user-cf8b473f4e64",
)

KEEP_PRO = frozenset({"acubatruweb"})


def main() -> int:
    p = argparse.ArgumentParser(description="Demote test Pro users to free")
    p.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = p.parse_args()

    ensure_db_initialized()
    db = get_db()
    paid = db.execute(
        "SELECT username, tier FROM subscriptions WHERE tier != 'free' ORDER BY username"
    ).fetchall()
    db.close()

    print("=== CURRENT PAID ===")
    for row in paid:
        print(f"  {row['username']} | {row['tier']}")

    to_demote = [u for u in DEMOTE_USERNAMES if any(r["username"] == u for r in paid)]
    print(f"\n=== TO DEMOTE ({len(to_demote)}) ===")
    for u in to_demote:
        print(f"  {u} -> free")

    keep = [r["username"] for r in paid if r["username"] in KEEP_PRO]
    print("\n=== KEEP PRO ===")
    for u in keep:
        print(f"  {u}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to commit.")
        return 0

    for username in to_demote:
        result = db_set_subscription(username, "free")
        print(f"✓ {result['username']} -> free")

    ensure_db_initialized()
    db = get_db()
    paid_after = db.execute(
        "SELECT username, tier FROM subscriptions WHERE tier != 'free' ORDER BY username"
    ).fetchall()
    db.close()

    print("\n=== PAID AFTER ===")
    for row in paid_after:
        print(f"  {row['username']} | {row['tier']}")
    print(f"Total non-free: {len(paid_after)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())