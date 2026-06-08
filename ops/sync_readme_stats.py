#!/usr/bin/env python3
"""DEPRECATED — use ops/sync_market_stats.py (includes sync_readme)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    print("sync_readme_stats.py is deprecated. Use: python ops/sync_market_stats.py", file=sys.stderr)
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "ops" / "sync_market_stats.py")]))