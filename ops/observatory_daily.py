#!/usr/bin/env python3
"""Daily Observatory metrics snapshot.

Usage:
  python3 ops/observatory_daily.py
  python3 ops/observatory_daily.py --json
  python3 ops/observatory_daily.py --dry-run

Writes daily_observatory_metrics row (Postgres/SQLite via market_observatory).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

from market_observatory import compute_daily_observatory_metrics, observatory_summary  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market Observatory daily snapshot")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--dry-run", action="store_true", help="Summary only; skip DB upsert")
    args = parser.parse_args()

    if args.dry_run:
        payload = observatory_summary(days=30)
        payload["dry_run"] = True
    else:
        payload = compute_daily_observatory_metrics()

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Observatory snapshot OK — MAA={payload.get('unique_agents', '—')} date={payload.get('date', '—')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
