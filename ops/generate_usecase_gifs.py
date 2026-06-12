#!/usr/bin/env python3
"""Render 5 terminalizer-style use-case GIFs for landing cards."""

from __future__ import annotations

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

OUT_DIR = ROOT / "landing" / "public" / "use-cases"


def _scripts() -> dict[str, tuple[str, list[ScriptLine]]]:
    pkg = stats.PYPI_PACKAGE_NAME
    ver = stats.PACKAGE_VERSION
    rv = stats.RETAILERS_VERIFIED
    prices = stats.PRICES_VERIFIED_LABEL
    refresh = stats.PRICES_REFRESH_HOURS
    mcp = public_tool_count("default")
    mcp_legacy = public_tool_count("legacy")
    indicators = stats.INDICATORS_COUNT
    countries = stats.COUNTRIES

    return {
        "agents": (
            "CLI Market — Agentes de compra",
            [
                ("dim", '🤖 AGENT: "Busca leche en PE y muéstrame el carrito."', 10),
                ("dim", "", 2),
                ("prompt", f"pip install {pkg}", 8),
                ("out", f"✓ {pkg} {ver}", 6),
                ("prompt", "market init", 6),
                ("out", f"✓ {rv} retailers verificados · {mcp} MCP tools", 8),
                ("prompt", 'market search "leche" --country PE', 8),
                ("out", "Metro S/4.20 · Wong S/4.50 · Tottus S/4.35", 8),
                ("prompt", "market add --from-last-search", 6),
                ("out", "✓ 1 ítem en carrito · total S/4.20", 8),
                ("prompt", "market tools", 6),
                ("out", f"Shop · Intel · Account · {mcp} curated ({mcp_legacy} legacy)", 10),
                ("dim", "cli-market.dev/tools · MCP en Cursor/Claude", 18),
            ],
        ),
        "market-data": (
            "CLI Market — Datos de mercado",
            [
                ("dim", "Analista: cobertura y salud del moat en vivo", 8),
                ("dim", "", 2),
                ("prompt", f"pip install {pkg}", 6),
                ("out", f"✓ {pkg} {ver}", 4),
                ("prompt", "market init", 6),
                ("out", "✓ cuenta free · API key sk-...", 6),
                ("prompt", "market discover --country AR", 8),
                ("out", f"✓ {rv} retailers · {countries} países · VTEX + Shopify", 10),
                ("prompt", "market stats", 6),
                ("out", f"✓ {prices} precios indexados · refresh {refresh}h", 10),
                ("prompt", "market scores --country AR", 6),
                ("out", "data_confidence: 0.94 · macro_alignment: 0.88", 10),
                ("dim", f"{indicators} indicadores · normalizado kg/L", 18),
            ],
        ),
        "basket": (
            "CLI Market — Canasta multi-retailer",
            [
                ("dim", "Comparar canasta familiar en un solo comando", 8),
                ("dim", "", 2),
                ("prompt", f"pip install {pkg}", 6),
                ("prompt", "market init", 5),
                ("prompt", 'market basket "arroz:1 aceite:1 leche:2" --country PE', 10),
                ("dim", "", 2),
                ("out", "Metro      S/24.10  ← mejor total", 6),
                ("out", "Wong       S/25.80", 5),
                ("out", "Plaza Vea  S/25.40", 5),
                ("out", "Tottus     S/26.05", 6),
                ("head", "────────────────────────────", 2),
                ("out", "Ahorro vs promedio: S/1.70 (6.6%)", 8),
                ("out", f"Cobertura: {rv} retailers verificados · PE", 8),
                ("dim", "market basket · sin abrir 3 apps", 18),
            ],
        ),
        "inflation": (
            "CLI Market — Inflación desde góndola",
            [
                ("dim", "Inflación real desde precios de góndola, no encuestas", 8),
                ("dim", "", 2),
                ("prompt", f"pip install {pkg}", 6),
                ("prompt", "market init", 5),
                ("prompt", "market inflation --country PE --line super", 8),
                ("out", "IPC góndola 30d: +2.1% · canasta básica +1.8%", 10),
                ("prompt", "market trending --country PE", 6),
                ("out", "↑ Aceite +4.2% · ↓ Arroz -0.6% · ↑ Leche +1.1%", 10),
                ("prompt", "market intel-brief --country PE", 8),
                ("out", f"✓ brief narrativo · {indicators} indicadores compuestos", 10),
                ("dim", "Intel MCP · Pro · cli-market.dev/#intelligence", 18),
            ],
        ),
        "procure": (
            "CLI Market — Compras de empresa",
            [
                ("dim", "Procure Copilot: comparar y aprobar sin Excel", 8),
                ("dim", "", 2),
                ("prompt", f"pip install {pkg}", 6),
                ("prompt", "market init", 5),
                ("prompt", 'procure compare "papel higiénico" --country PE', 8),
                ("out", "3 cotizaciones · mejor: S/18.90 / pack x12", 8),
                ("prompt", "procure approve ORD-PE-0042", 6),
                ("out", "✓ Aprobado · notificado a compras@empresa.com", 8),
                ("head", "────────────────────────────", 2),
                ("out", "Sin WhatsApp · sin hoja de cálculo", 6),
                ("out", f"Datos: {rv} retailers · {prices} precios", 8),
                ("dim", "cli-market.dev/#pricing · tab Procure", 18),
            ],
        ),
    }


def main() -> int:
    scripts = _scripts()
    for slug, (title, script) in scripts.items():
        out = OUT_DIR / f"{slug}.gif"
        frames = build_frames(script, title=title)
        write_gif(frames, out)
        print(f"Wrote {out} ({len(frames)} frames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
