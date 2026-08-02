"""
HubSpot enrichment — uses shared helpers, adds HubSpot-specific logic.
Contact personalisation (income_level, family_size) and lead score delta
are HubSpot-specific and stay here.
"""
from __future__ import annotations
from typing import Any
from cli_market_integrations.shared.enrichment import safe_float, now_iso, extract_scores, build_deal_pro_fields


def build_contact_market_properties(
    market_summary: dict[str, Any],
    contact: dict[str, Any] | None = None,
) -> dict[str, str]:
    scores_raw = market_summary.get("scores") or {}
    scores = extract_scores(scores_raw)
    brief = market_summary.get("brief") or {}

    basket_stress = _personalise_basket_stress(scores["basket_stress"], contact)
    shelf_signal = brief.get("shelf_signal") or brief.get("headline") or brief.get("summary") or "neutral"
    if isinstance(shelf_signal, str) and len(shelf_signal) > 200:
        shelf_signal = shelf_signal[:197] + "..."

    return {
        "market_basket_stress": f"{basket_stress:.4f}",
        "market_inflation_signal": str(shelf_signal),
        "market_price_fairness": f"{scores['price_fairness']:.2f}",
        "market_retail_aggression": f"{scores['retail_aggression']:.2f}",
        "market_data_updated": now_iso(),
    }


def _personalise_basket_stress(base: float, contact: dict[str, Any] | None) -> float:
    if not contact:
        return min(base, 1.0)
    props = contact.get("properties") or {}
    income_multiplier = {"low": 1.5, "medium": 1.0, "high": 0.7}.get((props.get("income_level") or "medium").lower(), 1.0)
    try: family_size = int(props.get("family_size") or 1)
    except: family_size = 1
    return min(base * income_multiplier * (1.0 + max(family_size - 1, 0) * 0.2), 1.0)


def build_deal_market_properties(
    procurement_signal: dict[str, Any],
    price_risk: dict[str, Any],
) -> dict[str, str]:
    """Maps shared deal pro fields to HubSpot snake_case property names."""
    shared = build_deal_pro_fields(procurement_signal, price_risk, "price_intelligence_updated")
    return {
        "price_risk_level": shared["risk_level"],
        "procurement_signal": shared["signal"],
        "market_recommended_action": shared["recommended_action"],
        "price_intelligence_updated": shared["timestamp"],
    }


def compute_lead_score_delta(contact_props: dict[str, str]) -> int:
    delta = 0
    stress = safe_float(contact_props.get("market_basket_stress"))
    aggression = safe_float(contact_props.get("market_retail_aggression"))
    if stress > 0.7: delta += 20
    elif stress > 0.5: delta += 10
    if aggression > 80: delta += 10
    return delta
