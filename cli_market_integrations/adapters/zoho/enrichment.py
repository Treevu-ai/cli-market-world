"""
Zoho enrichment — uses shared helpers, adds Zoho-specific logic.
Lead market score, inventory stock calculation are Zoho-specific.
"""
from __future__ import annotations
from typing import Any
from cli_market_integrations.shared.enrichment import safe_float, safe_int, now_iso, extract_scores, build_deal_pro_fields


def build_lead_market_fields(market_summary: dict[str, Any], lead: dict[str, Any] | None = None) -> dict[str, Any]:
    scores_raw = market_summary.get("scores") or {}
    scores = extract_scores(scores_raw)
    brief = market_summary.get("brief") or {}
    shelf_signal = brief.get("shelf_signal") or brief.get("headline") or brief.get("summary") or "neutral"
    if isinstance(shelf_signal, str) and len(shelf_signal) > 200:
        shelf_signal = shelf_signal[:197] + "..."
    return {
        "Market_Basket_Stress": round(scores["basket_stress"], 4),
        "Market_Inflation_Signal": str(shelf_signal),
        "Market_Price_Fairness": round(scores["price_fairness"], 2),
        "Market_Retail_Aggression": round(scores["retail_aggression"], 2),
        "Market_Score": round(calculate_market_score(lead or {}, scores), 2),
        "Market_Data_Updated": now_iso(),
    }


def calculate_market_score(lead: dict[str, Any], scores: dict[str, Any]) -> float:
    base = 50.0 + (scores.get("retail_aggression", 50.0) - 50.0) * 0.3 + (scores.get("price_fairness", 50.0) - 50.0) * 0.2 - scores.get("basket_stress", 0.0) * 20.0
    lead_score = safe_float(
        (lead.get("data") or [{}])[0].get("Lead_Score") if isinstance(lead.get("data"), list) else lead.get("Lead_Score"), 0.0
    )
    return max(0.0, min(100.0, base + lead_score * 0.1))


def build_deal_market_fields(procurement_signal: dict[str, Any], price_risk: dict[str, Any]) -> dict[str, Any]:
    """Maps shared deal pro fields to Zoho CamelCase field names."""
    shared = build_deal_pro_fields(procurement_signal, price_risk, "Price_Intelligence_Updated")
    return {
        "Price_Risk_Level": shared["risk_level"],
        "Procurement_Signal": shared["signal"],
        "Market_Recommended_Action": shared["recommended_action"],
        "Price_Intelligence_Updated": shared["timestamp"],
    }


def build_product_market_fields(procurement_signal: dict[str, Any], price_risk: dict[str, Any], product: dict[str, Any] | None = None) -> dict[str, Any]:
    signal = "unavailable" if procurement_signal.get("error") else (procurement_signal.get("signal") or procurement_signal.get("procurement_signal") or "monitor").lower()
    risk_level = "unknown" if price_risk.get("error") else (price_risk.get("risk_level") or price_risk.get("level") or "moderate").lower()
    return {
        "Market_Price_Risk": risk_level,
        "Procurement_Signal": signal,
        "Recommended_Stock": calculate_recommended_stock(product or {}, signal),
        "Market_Intelligence_Updated": now_iso(),
    }


def calculate_recommended_stock(product: dict[str, Any], signal: str) -> int:
    prod = product
    if isinstance(product.get("data"), list) and product["data"]: prod = product["data"][0]
    current = safe_int(prod.get("Quantity_In_Stock"), 0)
    base = safe_int(prod.get("Daily_Demand"), 10) * safe_int(prod.get("Lead_Time"), 7)
    recommended = int(base * {"buy_now": 1.2, "wait": 0.9}.get(signal, 1.0))
    return max(recommended, current)
