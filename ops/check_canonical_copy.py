#!/usr/bin/env python3
"""Fail if deprecated GTM copy (pip install cli-market) appears outside allowlist."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STALE_PIP_RE = re.compile(r"pip install cli-market(?!-)")
STALE_PYPI_RE = re.compile(r"https://pypi\.org/project/cli-market(?!-)")

SKIP_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    "node_modules",
    ".coverage",
    ".wheel-check",
    "agent-tools",
    "mcps",
    "terminals",
    "cli_market_world.egg-info",
    "ops/generated",
}

SKIP_FILES = {
    "ops/sync_market_stats.py",
    "CHANGELOG.md",
    "ops/check_canonical_copy.py",
}

SCAN_SUFFIXES = {
    ".md",
    ".py",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".svg",
    ".ts",
    ".tsx",
    ".html",
}


def _should_scan(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in SKIP_FILES:
        return False
    if path.suffix.lower() not in SCAN_SUFFIXES:
        return False
    return not any(part in SKIP_DIRS for part in path.parts)


def find_stale_copy(root: Path = ROOT) -> list[tuple[str, int, str, str]]:
    hits: list[tuple[str, int, str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not _should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, pattern in (
                ("pip", STALE_PIP_RE),
                ("pypi", STALE_PYPI_RE),
            ):
                if pattern.search(line):
                    hits.append((rel, line_no, label, line.strip()[:120]))
    return hits


def main() -> int:
    hits = find_stale_copy()
    if not hits:
        print("Canonical copy OK — no stale pip install cli-market references")
        return 0
    print(f"Found {len(hits)} stale copy reference(s):", file=sys.stderr)
    for rel, line_no, label, snippet in hits:
        print(f"  [{label}] {rel}:{line_no}: {snippet}", file=sys.stderr)
    print(
        "\nFix: run python3 ops/sync_market_stats.py or replace with pip install cli-market-world",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())