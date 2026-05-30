#!/usr/bin/env python3
"""Incremental sync: tools/content-repo-template → cli-market-content.

Preserves generated assets, daily briefings, and existing Day-*.md unless forced.

Usage:
  export CLI_MARKET_CONTENT_DIR=../cli-market-content
  python3 ops/sync_content_template.py
  python3 ops/sync_content_template.py --dry-run
  python3 ops/sync_content_template.py --force-days   # overwrite Day-*.md from template
  python3 ops/sync_content_template.py --only metrics,linkedin/data-gate.md
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ops"))

from content_paths import content_root, template_dir  # noqa: E402

SKIP_PREFIXES = (
    "linkedin/assets/",
    "generated/",
)

DAY_GLOB = "linkedin/Day-"


def _should_skip(rel: Path, *, force_days: bool) -> bool:
    rel_posix = rel.as_posix()
    for prefix in SKIP_PREFIXES:
        if rel_posix.startswith(prefix):
            return True
    if not force_days and rel_posix.startswith(DAY_GLOB) and rel.suffix == ".md":
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync content template to content repo")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force-days",
        action="store_true",
        help="Overwrite linkedin/Day-*.md from template (keeps assets/)",
    )
    parser.add_argument(
        "--only",
        help="Comma-separated path prefixes to sync (e.g. metrics,linkedin/data-gate.md)",
    )
    args = parser.parse_args()

    template = template_dir()
    target = content_root()
    if not template.is_dir():
        print(f"Missing template: {template}", file=sys.stderr)
        return 1

    only_prefixes = [p.strip() for p in (args.only or "").split(",") if p.strip()]

    copied = 0
    skipped = 0
    for src in sorted(template.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(template)
        if only_prefixes and not any(rel.as_posix().startswith(p) for p in only_prefixes):
            continue
        if _should_skip(rel, force_days=args.force_days):
            skipped += 1
            continue
        dest = target / rel
        if dest.exists() and dest.read_bytes() == src.read_bytes():
            skipped += 1
            continue
        if args.dry_run:
            print(f"would copy: {rel.as_posix()}")
            copied += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied += 1

    env_hint = os.getenv("CLI_MARKET_CONTENT_DIR", "").strip()
    print(f"Content root: {target}")
    if env_hint:
        print(f"CLI_MARKET_CONTENT_DIR={env_hint}")
    print(f"Sync: {copied} file(s) {'planned' if args.dry_run else 'copied'}, {skipped} skipped")
    if copied and not args.dry_run:
        print("Next: python3 ops/generate_all_linkedin_assets.py --patch")
        print("      python3 ops/slack_cli.py campaign sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
