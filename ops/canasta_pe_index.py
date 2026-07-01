#!/usr/bin/env python3
"""Generate public Índice Canasta Perú markdown from production dashboard data.

Usage:
  python3 ops/canasta_pe_index.py
  python3 ops/canasta_pe_index.py --write landing/public/indice-canasta-pe.md
  python3 ops/canasta_pe_index.py --remote --write landing/public/indice-canasta-pe.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_URL = os.getenv(
    "DASHBOARD_DATA_URL",
    "https://cli-market-api.fly.dev/dashboard/data",
)
OUT_PATH = ROOT / "landing/public/indice-canasta-pe.md"


def _fetch(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=45) as resp:
        return json.loads(resp.read().decode())


def _pe_canasta_rows(data: dict) -> list[dict]:
    rows = []
    for row in data.get("canasta_basica") or []:
        if (row.get("currency") or "").upper() == "PEN":
            rows.append(row)
    rows.sort(key=lambda r: float(r.get("total") or 0))
    return rows


def render_markdown(data: dict, *, generated_at: str) -> str:
    pe_rows = _pe_canasta_rows(data)
    moat = data.get("moat_summary") or {}
    kpis = data.get("kpis") or {}
    freshness = moat.get("freshness_pct") or kpis.get("freshness_pct")
    coverage = moat.get("coverage_7d_pct") or kpis.get("coverage_7d_pct")

    lines = [
        "# Índice Canasta Perú",
        "",
        f"**Actualizado:** {generated_at} (UTC) · Fuente: [CLI Market dashboard](https://cli-market-api.fly.dev/dashboard/data)",
        "",
        "Canasta básica comparable (10 ítems) en cadenas peruanas con cobertura activa. "
        "Señal pública del data moat — ver [`docs/gtm/pitch-agentic-protocols.md`](../docs/gtm/pitch-agentic-protocols.md).",
        "",
        "## Resumen",
        "",
        f"- **Cadenas PE en canasta:** {len(pe_rows)}",
        f"- **Freshness (&lt;24 h):** {freshness}%" if freshness is not None else "- **Freshness:** ver dashboard",
        f"- **Cobertura 7d:** {coverage}%" if coverage is not None else "",
        "",
        "## Totales por cadena (PEN)",
        "",
        "| Cadena | Ítems | Total canasta |",
        "|--------|------:|--------------:|",
    ]
    for row in pe_rows:
        name = row.get("store_name") or "?"
        items = int(row.get("items") or 0)
        total = float(row.get("total") or 0)
        lines.append(f"| {name} | {items}/10 | S/ {total:.2f} |")

    if len(pe_rows) >= 2:
        cheapest = pe_rows[0]
        priciest = pe_rows[-1]
        ratio = float(priciest["total"]) / float(cheapest["total"]) if cheapest.get("total") else 0
        lines.extend(
            [
                "",
                "## Spread",
                "",
                f"- Más barata: **{cheapest.get('store_name')}** (S/ {float(cheapest.get('total', 0)):.2f})",
                f"- Más cara: **{priciest.get('store_name')}** (S/ {float(priciest.get('total', 0)):.2f})",
                f"- Ratio max/min: **{ratio:.2f}×**",
            ]
        )

    lines.extend(
        [
            "",
            "## Metodología",
            "",
            "- Ítems: leche, arroz, aceite, azúcar, huevos, pan, café, pollo, queso, jabón (canasta CLI Market)",
            "- Precios de góndola online, normalizados cuando aplica; actualización collector cada **4 h**",
            "- Solo cadenas con ≥60% ítems encontrados en el snapshot",
            "",
            "## API",
            "",
            "```bash",
            "pip install cli-market-world",
            'market basket "arroz:1 aceite:1 leche:1" --country PE',
            "```",
            "",
            "*CLI Market · datos verificables · [cli-market.dev](https://cli-market.dev)*",
        ]
    )
    return "\n".join(line for line in lines if line is not None) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Índice Canasta Perú generator")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--write", type=Path, default=None, help="Write markdown path")
    parser.add_argument("--remote", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    data = _fetch(args.url)
    if data.get("error"):
        print(data.get("error"), file=sys.stderr)
        return 1

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    md = render_markdown(data, generated_at=generated_at)
    out = args.write or OUT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {out} ({len(_pe_canasta_rows(data))} PE chains)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
