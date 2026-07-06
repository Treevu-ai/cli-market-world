#!/usr/bin/env python3
"""Manual funnel digest — same payload as morning-ops-chain (08:00 PET).

Primary schedule: `.github/workflows/morning-ops-chain.yml` step `funnel-digest`.
Ad-hoc / Fly.io fallback only.

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