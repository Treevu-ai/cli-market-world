#!/usr/bin/env python3
"""Render landing demo.gif (terminalizer-style) from live market_stats."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT.parent / "cli-market-core"
for p in (ROOT, CORE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from market_core import market_stats as stats  # noqa: E402
from market_core.market_mcp_registry import public_tool_count  # noqa: E402

from terminal_gif_render import ScriptLine, build_frames, write_gif  # noqa: E402

OUT_PATHS = [
    ROOT / "landing" / "public" / "demo.gif",
    ROOT / "ops" / "demo.gif",
]


def _script() -> list[ScriptLine]:
    pkg = stats.PYPI_PACKAGE_NAME
    ver = stats.PACKAGE_VERSION
    rv = stats.RETAILERS_VERIFIED
    rd = stats.RETAILERS_DEFINED
    countries = stats.COUNTRIES
    mcp = public_tool_count("default")
    mcp_legacy = public_tool_count("legacy")
    return [
        ("dim", '🤖 AGENT: "Compara arroz en Perú y arma una canasta."', 10),
        ("dim", "", 2),
        ("prompt", "pip install cli-market-world", 8),
        ("out", f"✓ {pkg} {ver}", 8),
        ("dim", "", 2),
        ("prompt", "market init", 6),
        ("out", f"✓ {rd} retailers · {rv} verificados · {mcp} MCP · {countries} países", 12),
        ("dim", "", 2),
        ("prompt", 'market compare "arroz" --country PE', 8),
        ("dim", "", 2),
        ("out", "Metro S/2.90 · Wong S/3.10 · Plaza Vea S/2.95 · normalizado/kg", 10),
        ("dim", "", 2),
        ("prompt", 'market basket "arroz:1 leche:1" --country PE', 8),
        ("dim", "", 2),
        ("out", "Mejor: Metro S/12.40 · ahorro S/1.20 vs promedio", 10),
        ("dim", "", 2),
        ("prompt", "market tools", 6),
        ("out", f"Shop · Intel · Account · {mcp} tools ({mcp_legacy} legacy)", 8),
        ("dim", "", 4),
        ("head", "─────────────────────────────────────────", 2),
        ("head", "🧾  AGENT RECEIPT", 4),
        ("head", "─────────────────", 2),
        ("out", f"Comparado:  {rv} retailers verificados · PE", 4),
        ("out", "Canasta:    Metro · S/12.40", 4),
        ("out", f"MCP:        {mcp} curated ({mcp_legacy} legacy)", 4),
        ("out", "Tiempo:     <15 segundos", 4),
        ("head", "─────────────────", 2),
        ("dim", "cli-market.dev  ·  MIT  ·  pip install cli-market-world", 22),
    ]


def main() -> int:
    frames = build_frames(_script(), title="CLI Market — Agent Receipt")
    out = OUT_PATHS[0]
    write_gif(frames, out)
    for dest in OUT_PATHS[1:]:
        shutil.copy2(out, dest)
    print(f"Wrote {out} ({len(frames)} frames, {len(frames) * 72 / 1000:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
