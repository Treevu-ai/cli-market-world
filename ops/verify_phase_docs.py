#!/usr/bin/env python3
"""Verify phase docs and required test manifest — reduce doc/code drift."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASE_DOCS = ROOT / "docs" / "ops"
MANIFEST = Path(__file__).resolve().parent / "tech-debt-required-tests.txt"
TEST_REF = re.compile(r"tests/test_[a-z0-9_]+\.py")


def _load_manifest() -> list[str]:
    if not MANIFEST.is_file():
        return []
    lines = []
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def check_required() -> list[str]:
    missing = []
    for rel in _load_manifest():
        if not (ROOT / rel).is_file():
            missing.append(rel)
    return missing


def audit_phase_docs() -> list[tuple[str, str]]:
    drift: list[tuple[str, str]] = []
    manifest = set(_load_manifest())
    for doc in sorted(PHASE_DOCS.glob("phase*.md")):
        for match in sorted(set(TEST_REF.findall(doc.read_text(encoding="utf-8")))):
            if match not in manifest and not (ROOT / match).is_file():
                drift.append((doc.name, match))
    return drift


def main() -> int:
    p = argparse.ArgumentParser(description="Verify required tests and optional phase doc audit")
    p.add_argument(
        "--audit-docs",
        action="store_true",
        help="Print phase doc references to missing tests (non-failing)",
    )
    args = p.parse_args()

    missing_required = check_required()
    if missing_required:
        print("Missing required tests (ops/tech-debt-required-tests.txt):", file=sys.stderr)
        for path in missing_required:
            print(f"  - {path}", file=sys.stderr)
        return 1

    drift = audit_phase_docs()
    if args.audit_docs and drift:
        print("Phase doc references to missing tests (informational):")
        for doc, test_path in drift:
            print(f"  - {doc} → {test_path}")
    elif drift and not args.audit_docs:
        print(
            f"Note: {len(drift)} phase-doc test refs missing — run with --audit-docs to list",
            file=sys.stderr,
        )

    print(f"OK — {len(_load_manifest())} required test files present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
