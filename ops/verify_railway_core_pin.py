#!/usr/bin/env python3
"""Fail fast if requirements-railway.txt pins a cli-market-core version not on PyPI."""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ = ROOT / "requirements-railway.txt"
PYPI = "https://pypi.org/pypi/cli-market-core/json"


def _pinned_version() -> str:
    text = REQ.read_text(encoding="utf-8")
    match = re.search(r"^cli-market-core==(\d+\.\d+\.\d+)\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit("verify_railway_core_pin: no cli-market-core== pin in requirements-railway.txt")
    return match.group(1)


def _pypi_versions() -> set[str]:
    with urllib.request.urlopen(PYPI, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return set((data.get("releases") or {}).keys())


def _version_on_pypi(version: str) -> bool:
    url = f"https://pypi.org/pypi/cli-market-core/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.status == 200
    except OSError:
        return False


def main() -> int:
    pin = _pinned_version()
    if _version_on_pypi(pin):
        print(f"OK: cli-market-core=={pin} available on PyPI")
        return 0
    available = _pypi_versions()
    if pin not in available:
        latest = max(available, key=lambda v: tuple(int(x) for x in v.split(".")))
        print(
            f"ERROR: requirements-railway.txt pins cli-market-core=={pin} "
            f"but PyPI latest is {latest}.\n"
            f"  Publish core first: Actions → Publish cli-market-core (patch) → version {pin}\n"
            f"  Or hotfix pin to {latest} until publish completes.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: cli-market-core=={pin} available on PyPI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
