#!/usr/bin/env python3
"""Generate LinkedIn assets for one day (wrapper).

Prefer: python3 ops/generate_all_linkedin_assets.py --day N
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, default=1)
    parser.add_argument("--json", type=Path, help="ignored; use cached docs/metrics/query-*.json")
    args, extra = parser.parse_known_args()
    cmd = [
        sys.executable,
        str(ROOT / "ops" / "generate_all_linkedin_assets.py"),
        "--day",
        str(args.day),
        "--patch",
    ]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
