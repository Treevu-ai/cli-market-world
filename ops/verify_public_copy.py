#!/usr/bin/env python3
"""CI gate: fail if stale copy appears in public-facing surfaces.

Checks for deprecated metric strings that must never appear in files
consumed directly by LLMs, agents, and the public landing.

Run: python3 ops/verify_public_copy.py
Exit 0 = clean, Exit 1 = stale references found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files that must stay clean — indexed by their repo-relative path
PUBLIC_SURFACES = [
    "landing/public/agents.json",
    "landing/public/llms.txt",
    "landing/public/llms-full.txt",
    "landing/public/server.json",
    "landing/lib/marketStats.ts",
    "landing/components/Hero.tsx",
    "landing/components/CapabilitiesSection.tsx",
    "README.md",
    "server.json",
]

# (label, pattern) — any match in a scanned file is a failure
STALE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("stale-tools-27", re.compile(r"\b27\s+(?:curated\s+)?MCP\b|MCP\s+tools[:\s]+27\b")),
    ("stale-price-61k", re.compile(r"61[,.]?000\+?")),
    ("stale-version-pre-1.11", re.compile(r'"version"\s*:\s*"1\.(9|10)\.\d+"')),
]

# Lines that are allowed to contain stale patterns (e.g., comments explaining the old value)
ALLOWLIST_RE = re.compile(r"#.*stale|//.*stale|<!--.*stale", re.IGNORECASE)


def check_file(rel: str) -> list[tuple[str, int, str, str]]:
    path = ROOT / rel
    if not path.exists():
        return [(rel, 0, "missing", f"File not found: {rel}")]
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return [(rel, 0, "read-error", str(exc))]

    hits: list[tuple[str, int, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if ALLOWLIST_RE.search(line):
            continue
        for label, pattern in STALE_PATTERNS:
            if pattern.search(line):
                hits.append((rel, line_no, label, line.strip()[:120]))
    return hits


def main() -> int:
    all_hits: list[tuple[str, int, str, str]] = []
    for rel in PUBLIC_SURFACES:
        all_hits.extend(check_file(rel))

    if not all_hits:
        print("verify_public_copy: all public surfaces clean ✓")
        return 0

    print(f"verify_public_copy: {len(all_hits)} stale reference(s) found:", file=sys.stderr)
    for rel, line_no, label, snippet in all_hits:
        loc = f"{rel}:{line_no}" if line_no else rel
        print(f"  [{label}] {loc}: {snippet}", file=sys.stderr)
    print(
        "\nFix: run python3 ops/sync_market_stats.py or update the file manually.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
