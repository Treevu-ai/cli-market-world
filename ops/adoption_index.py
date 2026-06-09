#!/usr/bin/env python3
"""Compute and persist CLI Market Adoption Index (V1).

Usage:
  python3 ops/adoption_index.py
  python3 ops/adoption_index.py --json
  python3 ops/adoption_index.py --github
  python3 ops/adoption_index.py --dry-run
  python3 ops/adoption_index.py --days 30

Writes:
  ops/metrics/adoption-index/latest.json
  ops/metrics/adoption-index/YYYY-MM-DD.json
  ops/metrics/adoption-index/history.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

from market_adoption_index import (  # noqa: E402
    adoption_index_markdown,
    compute_adoption_index,
    persist_snapshot,
)

METRICS_DIR = Path(__file__).resolve().parent / "metrics" / "adoption-index"
HISTORY_FILE = METRICS_DIR / "history.jsonl"
LATEST_FILE = METRICS_DIR / "latest.json"


def _write_artifacts(payload: dict, *, dry_run: bool) -> None:
    if dry_run:
        return
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    daily = METRICS_DIR / f"{today}.json"
    daily.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LATEST_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with HISTORY_FILE.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "date": today,
                    "score": payload.get("score"),
                    "grade": payload.get("grade"),
                    "computed_at": payload.get("computed_at"),
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market Adoption Index")
    parser.add_argument("--days", type=int, default=30, help="Funnel window (1-90)")
    parser.add_argument("--github", action="store_true", help="Include GitHub ecosystem signals")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--dry-run", action="store_true", help="Compute only; skip DB + files")
    args = parser.parse_args()

    payload = compute_adoption_index(days=args.days, include_github=args.github)
    if not args.dry_run:
        saved = persist_snapshot(payload)
        payload["snapshot"] = saved

    _write_artifacts(payload, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(adoption_index_markdown(payload))
        if not args.dry_run:
            print(f"\nSaved → {LATEST_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())