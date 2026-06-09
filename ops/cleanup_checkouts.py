#!/usr/bin/env python3
"""Remove smoke/E2E checkout noise from production — keep one real Pro request."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops"))

from load_env import load_repo_env

load_repo_env()

from market_core import ensure_db_initialized, get_db

CHECKOUT_EVENTS = (
    "request_pro",
    "starter_subscribe",
    "starter_request",
    "procure_subscribe",
)

KEEP_REQUEST_ID = "PRO-3E2A9E04"
KEEP_USERNAME = "acubatruweb"


def _meta_dict(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        return json.loads(raw) if isinstance(raw, str) else {}
    except json.JSONDecodeError:
        return {}


def _is_acubatruweb_yape_funnel(row: dict) -> bool:
    if (row.get("username") or "").strip() != KEEP_USERNAME:
        return False
    if row.get("event") != "request_pro":
        return False
    meta = _meta_dict(row.get("meta"))
    source = (meta.get("source") or "").lower()
    method = (meta.get("payment_method") or "").lower()
    if method == "yape":
        return True
    return "yape" in source


def _split_funnel_checkouts(db) -> tuple[list[dict], list[dict]]:
    rows = db.execute(
        f"""
        SELECT id, event, username, meta, created_at
        FROM funnel_events
        WHERE event IN ({",".join("?" * len(CHECKOUT_EVENTS))})
        ORDER BY created_at
        """,
        CHECKOUT_EVENTS,
    ).fetchall()
    keep: list[dict] = []
    delete: list[dict] = []
    for row in rows:
        d = dict(row)
        (keep if _is_acubatruweb_yape_funnel(d) else delete).append(d)
    return keep, delete


def _subscription_rows_to_delete(db) -> list[dict]:
    rows = db.execute(
        "SELECT id, username, email, status, payment_link, created_at "
        "FROM subscription_requests ORDER BY created_at"
    ).fetchall()
    out = []
    for row in rows:
        d = dict(row)
        if d["id"] == KEEP_REQUEST_ID:
            continue
        out.append(d)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Cleanup checkout noise in prod DB")
    p.add_argument("--apply", action="store_true", help="Execute deletes (default dry-run)")
    args = p.parse_args()

    ensure_db_initialized()
    db = get_db()

    funnel_keep, funnel_del = _split_funnel_checkouts(db)
    subs_del = _subscription_rows_to_delete(db)

    print("=== KEEP subscription_request ===")
    keep = db.execute(
        "SELECT id, username, status, payment_link FROM subscription_requests WHERE id=?",
        (KEEP_REQUEST_ID,),
    ).fetchone()
    print(f"  {dict(keep) if keep else 'MISSING'}")

    print(f"\n=== DELETE subscription_requests ({len(subs_del)}) ===")
    for r in subs_del[:15]:
        print(f"  {r['id']} | {r['username']} | {r['status']}")
    if len(subs_del) > 15:
        print(f"  ... +{len(subs_del) - 15} more")

    print(f"\n=== KEEP funnel checkout events ({len(funnel_keep)}) ===")
    for d in funnel_keep:
        print(f"  {d.get('event')} | {d.get('username')} | {d.get('meta')}")

    print(f"\n=== DELETE funnel checkout events ({len(funnel_del)}) ===")
    for r in funnel_del[:10]:
        print(f"  {r['event']} | {r['username']} | {r.get('meta')}")
    if len(funnel_del) > 10:
        print(f"  ... +{len(funnel_del) - 10} more")

    if not args.apply:
        print("\nDry-run. Re-run with --apply to delete.")
        db.close()
        return 0

    for r in subs_del:
        db.execute("DELETE FROM subscription_requests WHERE id=?", (r["id"],))
    for r in funnel_del:
        db.execute("DELETE FROM funnel_events WHERE id=?", (r["id"],))
    db.commit()
    db.close()

    print(f"\n✓ Deleted {len(subs_del)} subscription_requests and {len(funnel_del)} funnel_events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())