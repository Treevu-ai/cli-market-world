#!/usr/bin/env python3
"""List paid tiers and billing requests from production DB (DATABASE_URL in env)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from market_core import ensure_db_initialized, get_db

PAID_TIERS = frozenset({
    "pro", "builder", "enterprise", "starter",
    "procure_starter", "procure_pro", "procure_builder",
})


def main() -> int:
    ensure_db_initialized()
    db = get_db()

    counts = db.execute(
        "SELECT tier, COUNT(*) AS n FROM subscriptions GROUP BY tier ORDER BY n DESC"
    ).fetchall()
    paid = db.execute(
        "SELECT username, tier, req_limit_day FROM subscriptions "
        "WHERE tier != 'free' ORDER BY tier, username"
    ).fetchall()
    pending = db.execute(
        "SELECT id, username, email, status, payment_link, created_at "
        "FROM subscription_requests WHERE status='pending' ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    activated = db.execute(
        "SELECT id, username, email, status, payment_link, created_at "
        "FROM subscription_requests WHERE status='activated' ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    pp = db.execute(
        "SELECT username, paypal_subscription_id FROM subscriptions "
        "WHERE paypal_subscription_id IS NOT NULL AND paypal_subscription_id != ''"
    ).fetchall()
    db.close()

    print("=== SUBSCRIPTIONS BY TIER ===")
    for r in counts:
        print(f"  {r['tier']}: {r['n']}")

    print("\n=== PAID SUBSCRIBERS (tier != free) ===")
    if not paid:
        print("  (ninguno)")
    for r in paid:
        mark = "PAID" if r["tier"] in PAID_TIERS else "?"
        print(f"  [{mark}] {r['username']} | {r['tier']} | req_day={r['req_limit_day']}")
    print(f"\nTotal non-free: {len(paid)}")

    print("\n=== PENDING BILLING REQUESTS ===")
    if not pending:
        print("  (ninguno)")
    for r in pending:
        link = (r["payment_link"] or "")[:70]
        print(f"  {r['id']} | {r['username']} | {r['email']} | {link}")

    print("\n=== ACTIVATED REQUESTS (recent) ===")
    if not activated:
        print("  (ninguno)")
    for r in activated:
        link = (r["payment_link"] or "")[:70]
        print(f"  {r['id']} | {r['username']} | {r['email']} | {link}")

    print("\n=== PAYPAL AUTO-SUBSCRIPTIONS ===")
    if not pp:
        print("  (ninguna — todos los Pro son activación manual u ops)")
    for r in pp:
        print(f"  {r['username']} | {r['paypal_subscription_id']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())