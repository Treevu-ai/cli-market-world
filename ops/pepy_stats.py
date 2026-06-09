#!/usr/bin/env python3
"""Fetch cli-market PyPI stats from Pepy.tech (PEPY_API_KEY).

Usage:
  python3 ops/pepy_stats.py
  python3 ops/pepy_stats.py --json
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

from market_pepy import pepy_briefing_line, pepy_summary  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Pepy.tech PyPI stats for cli-market")
    parser.add_argument("--json", action="store_true", help="Print full JSON")
    parser.add_argument("--force", action="store_true", help="Bypass cache")
    args = parser.parse_args()

    data = pepy_summary(force=args.force)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(pepy_briefing_line() if data.get("ok") else data.get("message", "pepy unavailable"))
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())