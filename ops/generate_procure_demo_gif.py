#!/usr/bin/env python3
"""Render Procure Copilot hero demo.gif (920×520, orange theme)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT.parent / "cli-market-core"
for p in (ROOT, CORE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from terminal_gif_render import ScriptLine, build_frames, write_gif  # noqa: E402

PATCH_OUT = ROOT / "patches" / "procure-copilot-hero" / "public" / "demo.gif"
OPS_OUT = ROOT / "ops" / "procure-demo.gif"

# Fallbacks when cli-market-core is not checked out (cloud agent / sparse clone).
_FALLBACK = {
    "rv": 40,
    "countries": 8,
    "prices": "63,000+",
}


def _stats() -> dict[str, int | str]:
    try:
        from market_core import market_stats as stats  # noqa: WPS433

        return {
            "rv": stats.RETAILERS_VERIFIED,
            "countries": stats.COUNTRIES,
            "prices": stats.PRICES_VERIFIED_LABEL,
        }
    except ImportError:
        return _FALLBACK


def _script() -> list[ScriptLine]:
    s = _stats()
    rv = s["rv"]
    countries = s["countries"]
    prices = s["prices"]
    return [
        ("dim", 'OPS: "Canasta horeca PE — arroz, aceite, leche."', 10),
        ("dim", "", 2),
        ("prompt", "procure run --country PE", 6),
        ("out", f"✓ 3 ítems · {rv} retailers · data-gate OK", 8),
        ("dim", "", 2),
        ("prompt", 'procure compare "arroz aceite leche"', 8),
        ("out", "Metro S/124.10 ← mejor · ahorro 6.2%", 10),
        ("dim", "", 2),
        ("prompt", "procure approve ORD-PE-0042", 6),
        ("out", "✓ pending → approved · gerente@empresa", 8),
        ("dim", "", 2),
        ("prompt", "procure checkout --payment yape", 6),
        ("out", "✓ checkout_ready · handoff CLI Market", 8),
        ("dim", "", 2),
        ("head", "────────────────────────────", 2),
        ("out", f"Cobertura: {rv} retailers · {countries} países", 4),
        ("out", f"Precios: {prices} · refresh 4h", 4),
        ("out", "Tiempo: 12s · trazabilidad completa", 6),
        ("head", "────────────────────────────", 2),
        ("dim", "procurecopilot.com · desde $29/mes", 20),
    ]


def main() -> int:
    frames = build_frames(
        _script(),
        title="PROCURE-COPILOT · DEMO",
        theme="procure",
    )
    write_gif(frames, PATCH_OUT)
    shutil.copy2(PATCH_OUT, OPS_OUT)
    print(f"Wrote {PATCH_OUT} ({len(frames)} frames, {len(frames) * 72 / 1000:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
