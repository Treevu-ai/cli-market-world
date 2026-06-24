"""Intelligence v2 helpers — world repo (methodology-defensible P1).

Overrides and report enrichments that do not require a core PyPI release.
See docs/methodology.md and docs/prd-intelligence-v2-methodology.md.
"""

from __future__ import annotations

from typing import Any

from market_core import STORES
from market_core.market_basket import build_canasta_snapshot
from market_core.market_intel_products import compute_affordability

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
}


def _canasta_totals_by_store(db, country: str) -> dict[str, Any]:
    """Min / promedio / max canasta totals across retailers (same moment)."""
    cc = country.strip().upper()
    stores = [k for k, v in STORES.items() if v.get("country") == cc and not v.get("disabled")]
    if not stores:
        return {"stores": 0, "method": "no_stores"}

    snap = build_canasta_snapshot(db, min_items=3, store_filter=set(stores))
    rows = snap.get("stores") or []
    totals = [float(r["total"]) for r in rows if r.get("total") and float(r["total"]) > 0]
    if not totals:
        return {"stores": 0, "method": "snapshot_empty"}

    return {
        "best": round(min(totals), 2),
        "average": round(sum(totals) / len(totals), 2),
        "worst": round(max(totals), 2),
        "stores": len(totals),
        "method": "canasta_snapshot",
        "currency": _CURRENCY_BY_COUNTRY.get(cc, rows[0].get("currency", "")),
    }


def _affordability_headline_v2(
    *,
    cc: str,
    currency: str,
    canasta_avg: float | None,
    canastas_per_wage_avg: float | None,
    rpv_pct: float | None,
) -> str:
    """Titular sin brecha IPC (PRD 4.2). Usa canasta promedio (PRD 4.4)."""
    parts: list[str] = []
    if canasta_avg is not None:
        parts.append(f"Canasta promedio observada ~{canasta_avg:.0f} {currency} en {cc}")
    if canastas_per_wage_avg is not None:
        parts.append(f"equivale a {canastas_per_wage_avg:.1f} canastas por salario mínimo (promedio)")
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
    """Affordability OS v2 — titular con canasta promedio; best/worst en components."""
    base = compute_affordability(db, country=country, line=line, days=days)
    cc = base.get("country") or "PE"
    components = dict(base.get("components") or {})
    totals = _canasta_totals_by_store(db, cc)
    currency = totals.get("currency") or components.get("canasta_currency") or _CURRENCY_BY_COUNTRY.get(cc, "")

    canasta_avg = totals.get("average")
    canasta_best = totals.get("best")
    canasta_worst = totals.get("worst")
    min_wage = components.get("minimum_wage_local")

    canastas_per_wage_avg = None
    canastas_per_wage_best = None
    canastas_per_wage_worst = None
    if min_wage and min_wage > 0:
        if canasta_avg:
            canastas_per_wage_avg = round(min_wage / canasta_avg, 2)
        if canasta_best:
            canastas_per_wage_best = round(min_wage / canasta_best, 2)
        if canasta_worst:
            canastas_per_wage_worst = round(min_wage / canasta_worst, 2)

    components.update(
        {
            "canasta_average": canasta_avg,
            "canasta_best": canasta_best,
            "canasta_worst": canasta_worst,
            "canasta_stores_compared": totals.get("stores") or components.get("canasta_stores_compared"),
            "canasta_method": totals.get("method") or components.get("canasta_method"),
            "canasta_currency": currency,
            "canastas_per_minimum_wage_average": canastas_per_wage_avg,
            "canastas_per_minimum_wage_best": canastas_per_wage_best,
            "canastas_per_minimum_wage_worst": canastas_per_wage_worst,
            # Titular principal = promedio; min queda como contexto best-case
            "canastas_per_minimum_wage": canastas_per_wage_avg,
        }
    )
    # Legacy field retained for backward compat
    if canasta_best is not None:
        components["canasta_min"] = canasta_best

    rpv = components.get("internal_inflation_pct") or components.get("staple_momentum_7d_pct")
    base["headline_es"] = _affordability_headline_v2(
        cc=cc,
        currency=currency,
        canasta_avg=canasta_avg,
        canastas_per_wage_avg=canastas_per_wage_avg,
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
