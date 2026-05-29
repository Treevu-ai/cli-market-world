#!/usr/bin/env python3
"""Bootstrap cli-market-content from tools/content-repo-template.

Usage:
  python3 ops/init_content_repo.py
  python3 ops/init_content_repo.py --target ../cli-market-content
  CLI_MARKET_CONTENT_DIR=~/Proyectos/cli-market-content python3 ops/init_content_repo.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools" / "content-repo-template"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize cli-market-content directory")
    parser.add_argument(
        "--target",
        type=Path,
        help="Destination (default: CLI_MARKET_CONTENT_DIR or ../cli-market-content)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target = args.target
    if not target:
        env = os.getenv("CLI_MARKET_CONTENT_DIR", "").strip()
        target = Path(env) if env else ROOT.parent / "cli-market-content"
    target = target.expanduser().resolve()

    if not TEMPLATE.is_dir():
        print(f"Missing template: {TEMPLATE}", file=sys.stderr)
        return 1

    target.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in TEMPLATE.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not args.force:
            continue
        shutil.copy2(src, dest)
        copied += 1

    print(f"Content repo ready: {target}")
    print(f"  Copied/updated {copied} file(s) from template.")
    print()
    print("Next:")
    print(f"  export CLI_MARKET_CONTENT_DIR={target}")
    print("  pip install pillow httpx")
    print("  python3 ops/sync_linkedin_metrics.py")
    print("  python3 ops/generate_all_linkedin_assets.py --patch")
    print(f"  cd {target} && git init  # luego remote a repo privado cli-market-content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
