"""
Enrichment logic — transforma datos de CLI Market en propiedades HubSpot.

Separa la lógica de negocio del middleware HTTP para que sea testeable sin
levantar un servidor FastAPI.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ── Helpers de normalización ──────────────────────────────────────────────────

def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Contact enrichment ────────────────────────────────────────────────────────

def build_contact_market_properties(
    market_summary: dict[str, Any],
    contact: dict[str, Any] | None = None,
) -> dict[str, str]:
    """
    Convierte el market_summary (brief + scores + inflation) en las
    propiedades custom que se escriben en HubSpot para el contacto.

    contact se usa para personalizar el basket_stress según income_level
    y family_size si están disponibles.
    """
    scores = market_summary.get("scores") or {}
    brief = market_summary.get("brief") or {}

    # Scores compuestos — los campos reales del endpoint /v1/intel/scores
    retail_aggression = _safe_float(
        scores.get("retail_aggression") or scores.get("scores", {}).get("retail_aggression")
    )
    price_fairness = _safe_float(
        scores.get("price_fairness") or scores.get("scores", {}).get("price_fairness")
    )
    basket_stress_raw = _safe_float(
        scores.get("basket_stress") or scores.get("scores", {}).get("basket_stress")
    )

    # Personalizar basket_stress según contexto del contacto
    basket_stress = _personalise_basket_stress(basket_stress_raw, contact)

    # shelf_signal del brief
    shelf_signal = (
        brief.get("shelf_signal")
        or brief.get("headline")
        or brief.get("summary")
        or "neutral"
    )
    # Truncar si es un string largo
    if isinstance(shelf_signal, str) and len(shelf_signal) > 200:
        shelf_signal = shelf_signal[:197] + "..."

    return {
        "market_basket_stress": f"{basket_stress:.4f}",
        "market_inflation_signal": str(shelf_signal),
        "market_price_fairness": f"{price_fairness:.2f}",
        "market_retail_aggression": f"{retail_aggression:.2f}",
        "market_data_updated": _now_iso(),
    }


def _personalise_basket_stress(
    base_stress: float,
    contact: dict[str, Any] | None,
) -> float:
    """
    Ajusta el basket_stress base según nivel de ingresos y tamaño de
    familia del contacto (si están disponibles en las props de HubSpot).
    """
    if not contact:
        return min(base_stress, 1.0)

    props = contact.get("properties") or {}

    income_level = (props.get("income_level") or "medium").lower()
    income_multiplier = {"low": 1.5, "medium": 1.0, "high": 0.7}.get(income_level, 1.0)

    try:
        family_size = int(props.get("family_size") or 1)
    except (TypeError, ValueError):
        family_size = 1
    family_multiplier = 1.0 + max(family_size - 1, 0) * 0.2

    return min(base_stress * income_multiplier * family_multiplier, 1.0)


# ── Deal enrichment ───────────────────────────────────────────────────────────

def build_deal_market_properties(
    procurement_signal: dict[str, Any],
    price_risk: dict[str, Any],
) -> dict[str, str]:
    """
    Convierte señales Pro de CLI Market en propiedades del deal de HubSpot.

    Si alguno de los endpoints devolvió error (tier insuficiente u otro),
    devuelve valores degradados en lugar de lanzar excepción.
    """
    # Procurement signal
    if procurement_signal.get("error"):
        signal = "unavailable"
        recommended_action = "Datos de procurement no disponibles (requiere tier Pro)"
    else:
        signal = (
            procurement_signal.get("signal")
            or procurement_signal.get("procurement_signal")
            or "monitor"
        ).lower()
        recommended_action = _action_for_signal(signal)

    # Price risk
    if price_risk.get("error"):
        risk_level = "unknown"
    else:
        risk_level = (
            price_risk.get("risk_level")
            or price_risk.get("level")
            or "moderate"
        ).lower()

    return {
        "price_risk_level": risk_level,
        "procurement_signal": signal,
        "market_recommended_action": recommended_action,
        "price_intelligence_updated": _now_iso(),
    }


def _action_for_signal(signal: str) -> str:
    return {
        "buy_now": "Contactar ahora — oportunidad de compra óptima",
        "monitor": "Monitorear — mercado estable, sin urgencia",
        "wait": "Esperar — se esperan mejores precios pronto",
    }.get(signal, f"Monitorear mercado ({signal})")


# ── Lead scoring helper ───────────────────────────────────────────────────────

def compute_lead_score_delta(contact_props: dict[str, str]) -> int:
    """
    Calcula el delta de lead score a aplicar en base a las propiedades
    de inteligencia de mercado recién escritas.

    Retorna un entero ≥ 0 (puntos a sumar). HubSpot aplica esto en Workflows.
    """
    delta = 0

    basket_stress = _safe_float(contact_props.get("market_basket_stress"))
    retail_aggression = _safe_float(contact_props.get("market_retail_aggression"))

    # Alto estrés de canasta → lead más urgente
    if basket_stress > 0.7:
        delta += 20
    elif basket_stress > 0.5:
        delta += 10

    # Alta agresión de retail → ventana de oportunidad
    if retail_aggression > 80:
        delta += 10

    return delta
