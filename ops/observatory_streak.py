#!/usr/bin/env python3
"""Check daily_observatory_metrics streak (PRD §13 — 7 consecutive days).

Usage:
  python3 ops/observatory_streak.py
  python3 ops/observatory_streak.py --remote --days 7
  python3 ops/observatory_streak.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

API_BASE = os.getenv(
    "MARKET_API_URL",
    "https://cli-market-api.fly.dev",
).rstrip("/")


def _fetch_remote(days: int) -> dict:
    token = os.getenv("MARKET_API_TOKEN", "")
    if not token:
        raise SystemExit("MARKET_API_TOKEN required for --remote")
    r = httpx.get(
        f"{API_BASE}/admin/observatory/streak",
        params={"days": days},
        headers={"Authorization": f"Bearer {token}"},
        timeout=25,
    )
    r.raise_for_status()
    return r.json()


def main() -> int:
    p = argparse.ArgumentParser(description="Observatory daily snapshot streak")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--remote", action="store_true", help="Query production API")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.remote:
        data = _fetch_remote(args.days)
    else:
        from market_observatory import observatory_snapshot_streak

        data = observatory_snapshot_streak(days=args.days)

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        status = "OK" if data.get("ok") else "NEEDS WORK"
        print(
            f"[{status}] Observatory snapshots: {data.get('snapshots_found')}/"
            f"{data.get('target')} in last {data.get('window_days')}d "
            f"(since {data.get('cutoff_date')})"
        )

    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
