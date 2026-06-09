#!/usr/bin/env python3
"""Evening founder cron — funnel digest to #funnel-cli-market.

Schedule (primary: GitHub Actions funnel-digest-evening.yml at 23:00 UTC):
  0 23 * * *  curl -X POST "$MARKET_API_URL/admin/cron/funnel-digest" -H "Authorization: Bearer $MARKET_API_TOKEN"

Local / Railway fallback:
  0 23 * * *  cd /app && python ops/cron_evening.py

Usage:
  python ops/cron_evening.py
  python ops/cron_evening.py --dry-run
  python ops/cron_evening.py --hours 24
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    p = argparse.ArgumentParser(description="Evening adoption cron")
    p.add_argument("--dry-run", action="store_true", help="Print digest only")
    p.add_argument("--hours", type=int, default=24)
    args = p.parse_args()

    cmd = [
        sys.executable,
        str(ROOT / "ops" / "funnel_digest_daily.py"),
        "--hours",
        str(args.hours),
    ]
    if not args.dry_run:
        cmd.append("--slack")
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())