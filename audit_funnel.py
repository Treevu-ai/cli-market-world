#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
out = []

try:
    from market_core import USE_PG, get_db
    from market_funnel import ensure_funnel_schema

    out.append(f"USE_PG={USE_PG}")
    ensure_funnel_schema()
    db = get_db()

    rows = db.execute(
        "SELECT event, username, meta, created_at FROM funnel_events ORDER BY created_at"
    ).fetchall()
    out.append(f"funnel_events={len(rows)}")
    for r in rows:
        d = dict(r)
        out.append(f"  {d['event']} | {d.get('username')} | {d.get('meta')} | {d.get('created_at')}")

    reqs = db.execute(
        "SELECT id, username, email, status, created_at FROM subscription_requests ORDER BY created_at"
    ).fetchall()
    out.append(f"subscription_requests={len(reqs)}")
    for r in reqs:
        d = dict(r)
        out.append(f"  {d['id']} | {d['email']} | {d['username']} | {d['status']} | {d.get('created_at')}")

    users = db.execute("SELECT username, created_at FROM users ORDER BY created_at").fetchall()
    out.append(f"users={len(users)}")
    for r in users:
        out.append(f"  {dict(r)}")

    subs = db.execute("SELECT username, tier FROM subscriptions ORDER BY username").fetchall()
    out.append(f"subscriptions={len(subs)}")
    for r in subs:
        out.append(f"  {dict(r)}")

    db.close()
except Exception:
    out.append(traceback.format_exc())

Path("audit_funnel_out.txt").write_text("\n".join(out), encoding="utf-8")
