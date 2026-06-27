#!/usr/bin/env python3
"""Diagnose which market_core sync_market_stats.py uses (sibling vs pip)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORE = ROOT.parent / "cli-market-core"


def _bootstrap_core_path(core_root: Path) -> None:
    registry = core_root / "market_core" / "market_mcp_registry.py"
    if not registry.is_file():
        print(f"ERROR: registry not found: {registry}", file=sys.stderr)
        print("Expected sibling layout:", file=sys.stderr)
        print(f"  {core_root.parent / 'cli-market-core'}", file=sys.stderr)
        print(f"  {core_root.parent / 'cli-market-world'}", file=sys.stderr)
        print("Or set CLI_MARKET_CORE_ROOT to your core checkout.", file=sys.stderr)
        sys.exit(1)
    core_str = str(core_root.resolve())
    while core_str in sys.path:
        sys.path.remove(core_str)
    sys.path.insert(0, core_str)


def _git_short(path: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "log", "-1", "--oneline"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:
        return "(not a git repo)"


def main() -> None:
    core_root = Path(os.environ.get("CLI_MARKET_CORE_ROOT", DEFAULT_CORE)).resolve()
    print(f"world root:     {ROOT}")
    print(f"core root:      {core_root}")
    print(f"core exists:    {core_root.is_dir()}")
    print(f"core git HEAD:  {_git_short(core_root)}")
    print()

    _bootstrap_core_path(core_root)

    import market_core.market_mcp_registry as reg

    default = reg.public_tool_count("default")
    legacy = reg.public_tool_count("legacy")
    prefs_default = "market_preferences" in {t["name"] for t in reg.list_tools("default")}
    prefs_hidden = "market_preferences" in reg._DEFAULT_HIDDEN

    print(f"market_core file: {reg.__file__}")
    print(f"default tools:    {default}")
    print(f"legacy tools:     {legacy}")
    print(f"preferences in default profile: {prefs_default}")
    print(f"preferences in _DEFAULT_HIDDEN:   {prefs_hidden}")
    print()

    if default == 32 and prefs_default:
        print("DIAGNOSIS: registry still exposes market_preferences in default → count stays 32.")
        print("Fix: cd cli-market-core && git checkout main && git pull origin main")
        print("     (need commit 263de72 or later — PR #107)")
        sys.exit(2)
    if "site-packages" in str(reg.__file__).replace("\\", "/"):
        print("DIAGNOSIS: using pip-installed market_core, not sibling checkout.")
        print("Fix: clone cli-market-core beside cli-market-world OR set CLI_MARKET_CORE_ROOT.")
        sys.exit(2)

    print("OK: sibling core looks current (expect default=31 after PR #107).")


if __name__ == "__main__":
    main()
