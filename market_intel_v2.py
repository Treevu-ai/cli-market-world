"""Intelligence v2 helpers — world repo (methodology-defensible P1).

Overrides and report enrichments that do not require a core PyPI release.
See docs/methodology.md and docs/prd-intelligence-v2-methodology.md.
"""

from __future__ import annotations

from typing import Any

from market_core.market_intel_products import (
    compute_affordability,
    _canasta_totals_by_store as core_canasta_totals_by_store,
)

PROMO_DISCOUNT_THRESHOLD = 0.03  # 3% — docs/methodology.md §6

_AFFORDABILITY_DISCLAIMER_ES = (
    "La canasta CLI Market es un benchmark referencial de productos esenciales en "
    "canales digitales verificados. No representa el gasto mensual total de un hogar "
    "peruano, que incluye canales no digitales, servicios y mayor variedad de categorías. "
    "Precios observados en tiendas online indexadas; no reemplaza el IPC INEI ni encuestas de hogares."
)

_RPV_DISCLAIMER_ES = (
    "Retail Price Velocity (RPV): movimiento de precios observado en góndola online. "
    "No es inflación oficial ni sustituto del IPC (INEI, INDEC, IBGE, DANE, INEGI)."
)

_CURRENCY_BY_COUNTRY: dict[str, str] = {
    "PE": "PEN",
    "AR": "ARS",
    "MX": "MXN",
    "BR": "BRL",
    "CO": "COP",
    "CL": "CLP",
    "BO": "BOB",
    "EC": "USD",
}


def _affordability_headline_v2(
    *,
    cc: str,
    currency: str,
    canasta_avg: float | None,
    canastas_per_wage_avg: float | None,
    wage_band: dict[str, float | None] | None,
    rpv_pct: float | None,
) -> str:
    """Titular sin brecha IPC (PRD 4.2). Usa canasta promedio (PRD 4.4)."""
    parts: list[str] = []
    if canasta_avg is not None:
        parts.append(f"Canasta promedio observada ~{canasta_avg:.0f} {currency} en {cc}")
    if canastas_per_wage_avg is not None:
        parts.append(f"equivale a {canastas_per_wage_avg:.1f} canastas por salario mínimo (promedio)")
    if wage_band and wage_band.get("low") is not None and wage_band.get("high") is not None:
        parts.append(
            f"banda {wage_band['low']:.1f}–{wage_band['high']:.1f} canastas/SM (BM-style)"
        )
    if rpv_pct is not None:
        parts.append(f"RPV 7d {rpv_pct:+.1f}%")
    return (
        "; ".join(parts)
        if parts
        else f"Señales de affordability para {cc} con datos limitados en el moat."
    )


def compute_affordability_v2(
    db,
    *,
    country: str | None = None,
    line: str | None = None,
    days: int = 30,
) -> dict[str, Any]:
    """Affordability OS v2 — titular con canasta promedio; best/worst + bandas en components."""
    base = compute_affordability(db, country=country, line=line, days=days)
    cc = base.get("country") or "PE"
    components = dict(base.get("components") or {})

    # Core may already populate bands; refresh totals if missing (older core pin).
    if not components.get("canasta_average"):
        totals = core_canasta_totals_by_store(db, cc)
        components.update(
            {
                "canasta_average": totals.get("average"),
                "canasta_best": totals.get("best"),
                "canasta_worst": totals.get("worst"),
                "canasta_stores_compared": totals.get("stores") or components.get("canasta_stores_compared"),
                "canasta_method": totals.get("method") or components.get("canasta_method"),
                "canasta_currency": totals.get("currency") or components.get("canasta_currency"),
            }
        )

    currency = components.get("canasta_currency") or _CURRENCY_BY_COUNTRY.get(cc, "")
    canasta_avg = components.get("canasta_average")
    wage_band = components.get("canastas_per_minimum_wage_band") or {}
    canastas_per_wage_avg = wage_band.get("point") or components.get("canastas_per_minimum_wage_average")

    if canastas_per_wage_avg is not None:
        components["canastas_per_minimum_wage"] = canastas_per_wage_avg
    if components.get("canasta_best") is not None:
        components["canasta_min"] = components["canasta_best"]

    rpv = components.get("internal_inflation_pct") or components.get("staple_momentum_7d_pct")
    base["headline_es"] = _affordability_headline_v2(
        cc=cc,
        currency=currency,
        canasta_avg=canasta_avg,
        canastas_per_wage_avg=canastas_per_wage_avg,
        wage_band=wage_band,
        rpv_pct=float(rpv) if rpv is not None else None,
    )
    base["components"] = components
    base["disclaimer_es"] = _AFFORDABILITY_DISCLAIMER_ES
    base["methodology"] = "affordability_os_v2"
    return base


def build_coverage_table_rows(data: dict[str, Any], *, limit: int = 15) -> list[dict[str, Any]]:
    """Coverage & freshness rows for Price Pulse (PRD 4.7)."""
    health = data.get("store_health") or []
    rows: list[dict[str, Any]] = []
    for h in health[:limit]:
        rows.append(
            {
                "store": h.get("store") or h.get("store_key") or "?",
                "country": h.get("country") or "—",
                "line": h.get("line") or "—",
                "success_pct": h.get("success_pct"),
                "coverage_7d_pct": h.get("coverage_7d_pct"),
                "last_snapshot": h.get("last_snapshot") or h.get("last_success") or "—",
            }
        )
    return rows


def coverage_partial_label(coverage_pct: float | None) -> str:
    if coverage_pct is None:
        return ""
    if float(coverage_pct) < 60:
        return "[COBERTURA PARCIAL]"
    return ""
