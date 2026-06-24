#!/usr/bin/env python3
"""CLI Market — Price Pulse Client Report (B2B).

Generates a polished, client-ready markdown report from /dashboard/data.
Suitable for Intelligence Pilot (USD 300–500/mes) deliverables.

Usage:
  python3 ops/price_pulse_client.py                # full report, saves to generated/reports/
  python3 ops/price_pulse_client.py --country PE   # filter by country
  python3 ops/price_pulse_client.py --json         # output raw JSON (for further processing)

Env vars:
  DASHBOARD_DATA_URL   default: https://cli-market-production.up.railway.app/dashboard/data
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from market_intel_v2 import (
    PROMO_DISCOUNT_THRESHOLD,
    _RPV_DISCLAIMER_ES,
    build_coverage_table_rows,
    coverage_partial_label,
)

DASHBOARD_URL_PRODUCTION = "https://cli-market-production.up.railway.app/dashboard/data"
DASHBOARD_URL_LOCAL = "http://127.0.0.1:8765/dashboard/data"

OUTPUT_DIR = Path(__file__).resolve().parent / "generated" / "reports"

# ── IPC taxonomy (from market_spread.py — imported at runtime) ─────────────────
try:
    from market_spread import CANASTA_ITEMS, CANASTA_IPC_MAP
except ImportError:
    CANASTA_ITEMS = ["leche", "arroz", "aceite", "azucar", "huevos", "pan", "cafe", "pollo", "queso", "jabon"]
    CANASTA_IPC_MAP: dict[str, dict[str, str]] = {}


def fetch_data(local: bool = False) -> dict[str, Any]:
    """Fetch dashboard data, trying production first, falling back to localhost.

    Set `local=True` or env var `MARKET_API_URL` to use localhost directly.
    """
    custom_url = os.getenv("DASHBOARD_DATA_URL", "")
    urls: list[tuple[str, str]] = []

    if custom_url:
        urls.append(("custom", custom_url))
    elif local:
        urls.append(("local", DASHBOARD_URL_LOCAL))
    else:
        urls.append(("production", DASHBOARD_URL_PRODUCTION))
        urls.append(("local", DASHBOARD_URL_LOCAL))

    errors: list[str] = []
    for label, url in urls:
        try:
            r = httpx.get(url, timeout=15)
            if r.status_code == 200:
                if errors:
                    print(f"  ⚠️  {'; '.join(errors)} — using {label}: {url}")
                else:
                    print(f"  ✅ {label}: {url}")
                return r.json()
            errors.append(f"{label} returned {r.status_code}")
        except Exception as e:
            errors.append(f"{label} error: {e}")

    raise RuntimeError(
        f"Could not fetch dashboard data.\n"
        f"  Production: {DASHBOARD_URL_PRODUCTION}\n"
        f"  Local:      {DASHBOARD_URL_LOCAL}\n"
        f"  Errors: {', '.join(errors)}\n"
        f"  Hint: Start the local server with `python market_server.py` or set DASHBOARD_DATA_URL."
    )


def _fmt(n: int | float | None) -> str:
    if n is None:
        return "—"
    return f"{int(n):,}".replace(",", ".")


def _pct(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.1f}%"


def _emoji_delta(delta: float) -> str:
    if delta > 0:
        return f"📈 +{delta:.1f}%"
    elif delta < 0:
        return f"📉 {delta:.1f}%"
    return "➡️ 0.0%"


def build_client_report(data: dict, *, country: str | None = None) -> str:
    """Generate a client-facing Price Pulse markdown report."""
    now = datetime.now(timezone.utc)
    ds = now.strftime("%Y-%m-%d")
    week = f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"

    k = data.get("kpis", {})
    moat = data.get("moat_summary", {})
    coll = data.get("collector", {})
    dashboard_view = data.get("dashboard_view", {})

    lines: list[str] = []

    # ── Header ─────────────────────────────────────────────────────────────
    lines += [
        "# CLI Market Price Pulse",
        f"**Semana {week} · {ds}**",
        "",
        "*Reporte generado automáticamente desde datos de góndola verificados.*",
        "*CLI Market Intelligence — Piloto comercial · Confidencial*",
        "",
        "---",
        "",
    ]

    # ── Resumen Ejecutivo ──────────────────────────────────────────────────
    total = k.get("total_indexed", 0)
    snapshots = k.get("snapshots_24h", 0)
    active = k.get("stores_indexed", 0)
    coverage = k.get("coverage_7d_pct", 0)
    fresh_pct = k.get("fresh_24h_pct", 0)
    moat_age = moat.get("moat_age_hours")
    partial = coverage_partial_label(coverage)

    lines += [
        "## 1. Resumen Ejecutivo",
        "",
    ]
    if partial:
        lines.append(f"**{partial}** — cobertura agregada {_pct(coverage)} (<60% umbral publicación).")
        lines.append("")
    lines += [
        f"- **{_fmt(total)}** precios indexados en el data moat",
        f"- **{_fmt(snapshots)}** precios actualizados en las últimas 24 horas",
        f"- **{active}** tiendas con datos activos",
        f"- **{_pct(coverage)}** de cobertura del catálogo activo (7 días)",
        f"- **{_pct(fresh_pct)}** de precios con menos de 24 horas de antigüedad",
    ]
    if moat_age is not None:
        age_text = f"{moat_age:.0f} horas" if moat_age < 48 else f"{moat_age/24:.1f} días"
        lines.append(f"- Antigüedad del último snapshot: **{age_text}**")

    collector_status = coll.get("status", "unknown")
    status_emoji = {"ok": "✅", "stale": "⚠️", "running": "🔄", "unknown": "❓"}.get(collector_status, "❓")
    lines += [
        f"- Estado del collector: {status_emoji} **{collector_status}**",
        "",
    ]

    # ── Retail Price Velocity (RPV) ─────────────────────────────────────────
    inflation = data.get("inflation", [])
    lines += [
        "---",
        "",
        "## 2. Retail Price Velocity (RPV — 7 días)",
        "",
        f"_{_RPV_DISCLAIMER_ES}_",
        "",
    ]
    if inflation and any(i.get("delta_pct", 0) != 0 for i in inflation):
        lines.append("| Línea | Moneda | Precio promedio (7d) | Precio promedio (14d) | Variación |")
        lines.append("|-------|--------|----------------------|-----------------------|-----------|")
        for i in inflation:
            delta = i.get("delta_pct", 0) or 0
            lines.append(
                f"| {i.get('line', '?')} | {i.get('currency', '')} | "
                f"{i.get('avg_now', 0):.2f} | {i.get('avg_before', 0):.2f} | "
                f"{_emoji_delta(delta)} |"
            )

        # Aggregate signal
        deltas = [i.get("delta_pct", 0) or 0 for i in inflation]
        avg_delta = sum(deltas) / len(deltas) if deltas else 0
        lines += [
            "",
            f"**Señal agregada (RPV):** variación promedio de **{avg_delta:+.1f}%** en {len(inflation)} líneas.",
        ]
    else:
        lines.append("_Serie histórica insuficiente (se requieren ≥7 días de datos). El piloto incluye acumulación progresiva._")
    lines.append("")

    # ── Canasta Básica ─────────────────────────────────────────────────────
    canasta = data.get("canasta_basica", [])
    dashboard_blocks = dashboard_view.get("blocks", {}) if dashboard_view else {}
    _canasta_block = dashboard_blocks.get("canasta", {})

    lines += [
        "---",
        "",
        "## 3. Canasta Básica",
        "",
    ]

    if canasta:
        lines.append("| Tienda | Ítems | Total | Moneda |")
        lines.append("|--------|-------|-------|--------|")
        for c in canasta:
            items = c.get("items", 0)
            total_val = c.get("total", 0)
            note = ""
            if items < 6:
                note = " ⚠️"
            lines.append(
                f"| {c.get('store_name', '?')} | {items}/10{note} | "
                f"{total_val:.2f} | {c.get('currency', '')} |"
            )
        lines.append("")

        # IPC taxonomy annotation
        if CANASTA_IPC_MAP:
            lines += [
                "### Trazabilidad metodológica — Categorías IPC (INEI, base 2021=100)",
                "",
                "| Ítem canasta | División IPC | Subclase IPC | Ponderación INEI |",
                "|-------------|-------------|-------------|------------------|",
            ]
            for item in CANASTA_ITEMS:
                ipc = CANASTA_IPC_MAP.get(item, {})
                lines.append(
                    f"| {item} | {ipc.get('division', '—')} | "
                    f"{ipc.get('subclass', '—')} | {ipc.get('ponderacion', '—')} |"
                )
            lines += [
                "",
                "*Ponderaciones referenciales INEI (base 2021=100). La canasta de CLI Market "
                "cubre productos de consumo diario en retail formal urbano. No pretende replicar "
                "la canasta completa del IPC nacional.*",
                "",
            ]

        # Spreads from block
        spreads_block = dashboard_blocks.get("canasta_spreads", {})
        if spreads_block:
            spread_highlights = spreads_block.get("highlights", "")
            if spread_highlights:
                lines.append(f"**Spreads destacados:** {spread_highlights}")
                lines.append("")
    else:
        lines.append("_Sin datos de canasta para este período._")
        lines.append("")

    # ── Dispersión de precios (CV) ───────────────────────────────────────────
    marketing_spreads = data.get("marketing_spreads", [])
    indicator_values = data.get("indicator_values") or data.get("indicators_latest") or []
    dispersion_cv = None
    for iv in indicator_values if isinstance(indicator_values, list) else []:
        if isinstance(iv, dict) and iv.get("key") == "price_dispersion":
            dispersion_cv = iv.get("value")
            break
    if marketing_spreads or dispersion_cv is not None:
        lines += [
            "---",
            "",
            "## 4. Dispersión de Precios",
            "",
        ]
        if dispersion_cv is not None:
            lines += [
                f"- **Coeficiente de variación (CV) agregado:** **{dispersion_cv:.1f}%**",
                "  _(Fórmula: σ/μ × 100 por grupo comparable — ver docs/methodology.md §5)_",
                "",
            ]
        seen: set[str] = set()
        shown = 0
        for s in marketing_spreads:
            if s.get("marketing_ready") and shown < 10:
                label = s.get("seed") or s.get("subcategory", "?")
                if label in seen:
                    continue
                seen.add(label)
                ratio = s.get("spread_ratio", 0) or 0
                cv_item = s.get("cv_pct") or s.get("dispersion_cv")
                cv_note = f" · CV **{cv_item:.1f}%**" if cv_item is not None else ""
                lines.append(
                    f"- **{label}** ({s.get('line', '')}, {s.get('currency', '')}): "
                    f"spread legacy **{ratio:.1f}x**{cv_note} — "
                    f"{s.get('stores', '?')} tiendas "
                    f"(min {s.get('currency', '')} {s.get('min_price', 0):.2f} / "
                    f"max {s.get('currency', '')} {s.get('max_price', 0):.2f})"
                )
                shown += 1
        if shown == 0 and dispersion_cv is None:
            lines.append("_Sin spreads marketing-ready en este corte._")
        lines += [
            "",
            "_`spread_ratio` (max−min)/min es métrica legacy — no usar en publicaciones v2._",
            "",
        ]

    # ── Calidad del dato ────────────────────────────────────────────────────
    quality = data.get("quality_funnel", {})
    lines += [
        "---",
        "",
        "## 5. Calidad del Dato",
        "",
    ]
    if quality:
        lines.append(f"- **Capturados**: {_fmt(quality.get('captured', 0))} precios")
        lines.append(f"- **Flagged (descuentos >90%)**: {_fmt(quality.get('flagged_discounts', 0))}")
        lines.append(f"- **Flagged (outliers 5x)**: {_fmt(quality.get('flagged_outliers', 0))}")
        lines.append(f"- **Citables (marketing-ready)**: {_fmt(quality.get('citable', 0))}")
        lines.append("")
        lines.append(
            "*El funnel clean → flagged → citable documenta cada paso de filtrado. "
            "Solo se entregan datos 'citables' en exports y reportes B2B.*"
        )
    lines.append("")

    # ── Cobertura y frescura ─────────────────────────────────────────────────
    cov_rows = build_coverage_table_rows(data, limit=12)
    lines += [
        "---",
        "",
        "## 6. Cobertura y Frescura",
        "",
        f"| Retailer | País | Éxito % | Cobertura 7d | Último snapshot |",
        f"|----------|------|---------|--------------|-----------------|",
    ]
    for row in cov_rows:
        succ = row.get("success_pct")
        cov7 = row.get("coverage_7d_pct")
        lines.append(
            f"| {row.get('store', '?')} | {row.get('country', '—')} | "
            f"{succ:.0f}% | {cov7:.0f}% | {row.get('last_snapshot', '—')} |"
            if succ is not None and cov7 is not None
            else f"| {row.get('store', '?')} | {row.get('country', '—')} | — | — | {row.get('last_snapshot', '—')} |"
        )
    lines += [
        "",
        f"**Cobertura agregada:** {_pct(coverage)} · **Umbral publicación:** ≥60%",
        "",
    ]

    # ── Metodología ─────────────────────────────────────────────────────────
    lines += [
        "---",
        "",
        "## 7. Metodología",
        "",
        "- **Documento canónico:** `docs/methodology.md` (CLI Market Intelligence v2).",
        "- **RPV:** `shelf_price_momentum_7d` — Retail Price Velocity, no inflación oficial.",
        f"- **Promo intensity:** SKUs con descuento ≥ **{int(PROMO_DISCOUNT_THRESHOLD * 100)}%** sobre list_price.",
        "- **Price dispersion:** coeficiente de variación (CV) entre retailers por producto comparable.",
        "- **BSI:** canasta hoy / mediana 30d — ortogonal a dispersión cross-retailer.",
        "- **Fuente:** APIs públicas de retailers VTEX/Shopify/Magento (sin scraping de páginas web).",
        "- **Frecuencia:** Collector programado cada 4–8 horas.",
        "- **Cobertura geográfica:** Perú, Colombia, Argentina, Brasil, México, Chile + Europa.",
        "- **Normalización:** Precios por kg/L cuando la unidad es parseable.",
        "- **Filtros de calidad:** Descuentos >90% marcados como 'suspect'. Outliers >5x mediana excluidos de canasta.",
        f"- **Disclaimer:** {_RPV_DISCLAIMER_ES}",
        "",
        "---",
        "",
        f"*Generado el {ds} · CLI Market Intelligence · hello@cli-market.dev*",
        "*Dashboard público: https://cli-market-production.up.railway.app/dashboard*",
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate B2B Price Pulse client report")
    parser.add_argument("--country", default=None, help="Filter by country code (e.g. PE)")
    parser.add_argument("--json", action="store_true", help="Output raw dashboard JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print report only, don't save")
    parser.add_argument("--local", action="store_true", help="Use localhost server (http://127.0.0.1:8765)")
    args = parser.parse_args()

    print("Fetching dashboard data...")
    try:
        data = fetch_data(local=args.local)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    report = build_client_report(data, country=args.country)

    if args.dry_run:
        print(report)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ds = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = OUTPUT_DIR / f"price-pulse-client-{ds}.md"
    path.write_text(report, encoding="utf-8")
    print(f"Client report written: {path}")
    print(f"  Convert to PDF:  pandoc {path} -o {path.with_suffix('.pdf')} --pdf-engine=xelatex")
    print(f"  Lines: {len(report.splitlines())}")


if __name__ == "__main__":
    main()
