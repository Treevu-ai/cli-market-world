#!/usr/bin/env python3
"""Quantitative Observatory audit — PRD P0 §13 acceptance helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

OPS = Path(__file__).resolve().parent
ROOT = OPS.parent
sys.path.insert(0, str(OPS))
sys.path.insert(0, str(ROOT))

from load_env import load_repo_env  # noqa: E402

load_repo_env()


def _audit_events(*, days: int = 30) -> dict:
    from market_core import get_db
    from market_core.market_observatory import _since_sql, ensure_observatory_schema

    ensure_observatory_schema()
    days = max(1, min(days, 90))
    since = _since_sql(days)
    db = get_db()
    try:
        total_row = db.execute(
            "SELECT COUNT(*) AS n FROM agent_events WHERE occurred_at >= ?",
            (since,),
        ).fetchone()
        null_agent = db.execute(
            """
            SELECT COUNT(*) AS n FROM agent_events
            WHERE occurred_at >= ?
              AND (agent_id IS NULL OR TRIM(agent_id) = '')
            """,
            (since,),
        ).fetchone()
        noise_row = db.execute(
            """
            SELECT COUNT(*) AS n FROM agent_events
            WHERE occurred_at >= ?
              AND (agent_id LIKE 'smoke%' OR agent_id LIKE 'pam-%'
                   OR agent_id LIKE 'test-%' OR agent_id LIKE 'user-%')
            """,
            (since,),
        ).fetchone()
    finally:
        db.close()

    total = int(total_row["n"] or 0) if total_row else 0
    null_n = int(null_agent["n"] or 0) if null_agent else 0
    noise_n = int(noise_row["n"] or 0) if noise_row else 0
    instrumented_pct = 100.0 if total == 0 else round(100.0 * (total - null_n) / total, 2)
    return {
        "window_days": days,
        "events_total": total,
        "events_null_agent_id": null_n,
        "events_noise_heuristic": noise_n,
        "agent_id_resolvable_pct": instrumented_pct,
        "agent_id_target_pct": 100.0,
        "agent_id_ok": null_n == 0,
    }


def run_audit(*, days: int = 30, streak_days: int = 7) -> dict:
    from market_observatory import observatory_snapshot_streak

    events = _audit_events(days=days)
    streak = observatory_snapshot_streak(days=streak_days)
    ok = events["agent_id_ok"] and streak.get("ok")
    return {
        "ok": ok,
        "events": events,
        "daily_snapshot_streak": streak,
        "notes": [
            "instrumentation_pct requires route-level audit (future)",
            "noise_heuristic is approximate — see is_noise_agent in core",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Observatory quantitative audit")
    p.add_argument("--days", type=int, default=30, help="Event window")
    p.add_argument("--streak-days", type=int, default=7, help="Daily metrics streak window")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    report = run_audit(days=args.days, streak_days=args.streak_days)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        ev = report["events"]
        st = report["daily_snapshot_streak"]
        print(f"Events ({ev['window_days']}d): {ev['events_total']}")
        print(f"NULL agent_id: {ev['events_null_agent_id']} ({ev['agent_id_resolvable_pct']}% resolvable)")
        print(
            f"Daily snapshots: {st['snapshots_found']}/{st['target']} "
            f"(cutoff {st['cutoff_date']}) — {'OK' if st.get('ok') else 'FAIL'}"
        )
        print(f"Overall: {'PASS' if report['ok'] else 'NEEDS WORK'}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
