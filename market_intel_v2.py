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
    "BO": "BOB",
    "EC": "USD",
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


def _canastas_per_wage_band(
    min_wage: float | None,
    *,
    best_total: float | None,
    avg_total: float | None,
    worst_total: float | None,
) -> dict[str, float | None]:
    if not min_wage or min_wage <= 0:
        return {"low": None, "point": None, "high": None}

    def _ratio(total: float | None) -> float | None:
        if total and total > 0:
            return round(min_wage / total, 2)
        return None

    return {
        "low": _ratio(worst_total),
        "point": _ratio(avg_total),
        "high": _ratio(best_total),
    }


def _canasta_band_confidence(*, stores_compared: int, spread_pct: float | None) -> str:
    if stores_compared < 2:
        return "low"
    if stores_compared < 3:
        return "moderate"
    if spread_pct is not None and spread_pct > 50:
        return "moderate"
    return "ok"


def _affordability_headline_v2(
    *,
    cc: str,
    currency: str,
    canasta_avg: float | None,
    canastas_per_wage_avg: float | None,
    wage_band: dict[str, float | None] | None = None,
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

    totals = _canasta_totals_by_store(db, cc)
    canasta_avg = components.get("canasta_average") or totals.get("average")
    canasta_best = components.get("canasta_best") or totals.get("best")
    canasta_worst = components.get("canasta_worst") or totals.get("worst")
    min_wage = components.get("minimum_wage_local")
    currency = (
        components.get("canasta_currency")
        or totals.get("currency")
        or _CURRENCY_BY_COUNTRY.get(cc, "")
    )

    wage_band = components.get("canastas_per_minimum_wage_band")
    if not wage_band or wage_band.get("point") is None:
        wage_band = _canastas_per_wage_band(
            min_wage,
            best_total=canasta_best,
            avg_total=canasta_avg,
            worst_total=canasta_worst,
        )

    spread_pct = None
    if canasta_best and canasta_worst and canasta_best > 0:
        spread_pct = round((canasta_worst - canasta_best) / canasta_best * 100, 1)
    stores_compared = totals.get("stores") or components.get("canasta_stores_compared") or 0
    band_confidence = components.get("canasta_band_confidence") or _canasta_band_confidence(
        stores_compared=int(stores_compared),
        spread_pct=spread_pct,
    )

    canastas_per_wage_avg = wage_band.get("point")

    components.update(
        {
            "canasta_average": canasta_avg,
            "canasta_best": canasta_best,
            "canasta_worst": canasta_worst,
            "canasta_stores_compared": stores_compared,
            "canasta_method": totals.get("method") or components.get("canasta_method"),
            "canasta_currency": currency,
            "canastas_per_minimum_wage_average": canastas_per_wage_avg,
            "canastas_per_minimum_wage_best": wage_band.get("high"),
            "canastas_per_minimum_wage_worst": wage_band.get("low"),
            "canastas_per_minimum_wage_band": wage_band,
            "canasta_band_spread_pct": spread_pct,
            "canasta_band_confidence": band_confidence,
            "canastas_per_minimum_wage": canastas_per_wage_avg,
        }
    )
    if canasta_best is not None:
        components["canasta_min"] = canasta_best

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


def build_andean_panel(
    db,
    *,
    line: str = "supermercados",
    days: int = 30,
) -> dict[str, Any]:
    """CAF Andean panel — delegates to core when available, else world fallback."""
    try:
        from market_core.market_intel_products import build_andean_panel as core_build_andean_panel

        return core_build_andean_panel(db, line=line, days=days)
    except ImportError:
        from market_core.market_indicators import compute_staple_price_momentum, get_latest_values

        _MINIMUM_WAGE = {"PE": 1130.0, "BO": 2750.0, "EC": 482.0}
        countries: list[dict[str, Any]] = []
        for cc in ("PE", "BO", "EC"):
            has_retail = any(
                v.get("country") == cc and not v.get("disabled") for v in STORES.values()
            )
            latest = get_latest_values(db, country=cc, line=line, limit=50)
            latest_map = {v["key"]: v for v in latest}
            food_cpi = latest_map.get("food_cpi_yoy", {}).get("value")
            row: dict[str, Any] = {
                "country": cc,
                "currency": _CURRENCY_BY_COUNTRY.get(cc),
                "minimum_wage_local": _MINIMUM_WAGE.get(cc),
                "data_status": "retail_and_macro" if has_retail else "macro_only",
                "channel": "online_modern_retail" if has_retail else None,
                "official_food_cpi_yoy_pct": food_cpi,
                "official_food_cpi_source": "World Bank FP.CPI.FOOD.ZG",
            }
            if has_retail:
                aff = compute_affordability_v2(db, country=cc, line=line, days=days)
                components = aff.get("components") or {}
                row.update(
                    {
                        "retail_price_velocity_7d_pct": components.get("staple_momentum_7d_pct"),
                        "retail_price_velocity_promo_adjusted_7d_pct": components.get(
                            "staple_momentum_promo_adjusted_7d_pct"
                        ),
                        "shelf_vs_official_food_cpi_gap_pp": components.get(
                            "shelf_vs_official_food_cpi_gap_pp"
                        ),
                        "canasta": {
                            "best": components.get("canasta_best"),
                            "average": components.get("canasta_average"),
                            "worst": components.get("canasta_worst"),
                            "currency": components.get("canasta_currency"),
                            "stores_compared": components.get("canasta_stores_compared"),
                        },
                        "canastas_per_minimum_wage_band": components.get("canastas_per_minimum_wage_band"),
                        "canasta_band_confidence": components.get("canasta_band_confidence"),
                        "affordability_score": aff.get("affordability_score"),
                        "affordability_band": aff.get("affordability_band"),
                    }
                )
            else:
                row["note"] = (
                    "Sin canal retail indexado en CLI Market; solo benchmark macro "
                    "(World Bank FP.CPI.FOOD.ZG). No comparable con canasta/SM de Perú."
                )
                staple_mom = compute_staple_price_momentum(db, cc, days=7, price_mode="list")
                if staple_mom is not None:
                    row["retail_price_velocity_promo_adjusted_7d_pct"] = staple_mom
                if food_cpi is not None and staple_mom is not None:
                    row["shelf_vs_official_food_cpi_gap_pp"] = round(staple_mom - food_cpi, 2)
            countries.append(row)

        retail_count = sum(1 for c in countries if c.get("data_status") == "retail_and_macro")
        return {
            "panel": "CAF_andean_food_affordability",
            "countries": countries,
            "retail_coverage_countries": retail_count,
            "macro_only_countries": [c["country"] for c in countries if c.get("data_status") == "macro_only"],
            "line": line,
            "days": days,
            "disclaimer_es": (
                "Panel comparativo CAF Andino: alimentos y salario mínimo. Perú incluye canasta "
                "online observada; Bolivia y Ecuador solo IPC alimentario oficial hasta indexar retail. "
                "No usar para ranking político sin revisar cobertura por país."
            ),
            "methodology": "andean_panel_v1",
        }


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
