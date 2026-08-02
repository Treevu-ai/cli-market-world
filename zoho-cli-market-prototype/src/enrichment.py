"""
Enrichment logic — Zoho CRM + CLI Market.

Tres flujos:
  1. Lead enrichment   → campos market_* en Leads
  2. Deal enrichment   → señales Pro en Deals
  3. Inventory optimization → stock recomendado en Products

Lógica de negocio pura, sin dependencias de red ni FastAPI.
Testeable sin servidor ni keys reales.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── 1. Lead enrichment ────────────────────────────────────────────────────────

def build_lead_market_fields(
    market_summary: dict[str, Any],
    lead: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convierte market_summary (brief + scores + inflation) en los campos
    custom de Zoho Leads. Todos los valores son strings o numbers para
    compatibilidad con la API de Zoho.
    """
    scores_wrapper = market_summary.get("scores") or {}
    # /v1/intel/scores puede devolver los scores directamente o bajo "scores"
    scores = scores_wrapper.get("scores") or scores_wrapper

    brief = market_summary.get("brief") or {}

    retail_aggression = _safe_float(scores.get("retail_aggression"))
    price_fairness = _safe_float(scores.get("price_fairness"))
    basket_stress = _safe_float(scores.get("basket_stress"))

    market_score = calculate_market_score(lead or {}, scores)

    shelf_signal = (
        brief.get("shelf_signal") or brief.get("headline") or brief.get("summary") or "neutral"
    )
    if isinstance(shelf_signal, str) and len(shelf_signal) > 200:
        shelf_signal = shelf_signal[:197] + "..."

    return {
        "Market_Basket_Stress": round(basket_stress, 4),
        "Market_Inflation_Signal": str(shelf_signal),
        "Market_Price_Fairness": round(price_fairness, 2),
        "Market_Retail_Aggression": round(retail_aggression, 2),
        "Market_Score": round(market_score, 2),
        "Market_Data_Updated": _now_iso(),
    }


def calculate_market_score(lead: dict[str, Any], scores: dict[str, Any]) -> float:
    """
    Score de mercado 0–100 combinando señales de CLI Market con datos del lead.
    Mayor retail_aggression → oportunidad de venta promocional → sube score.
    Mayor basket_stress → cliente en aprietos → baja score.
    """
    base = 50.0

    retail_aggression = _safe_float(scores.get("retail_aggression"), 50.0)
    price_fairness = _safe_float(scores.get("price_fairness"), 50.0)
    basket_stress = _safe_float(scores.get("basket_stress"), 0.0)

    base += (retail_aggression - 50.0) * 0.3
    base += (price_fairness - 50.0) * 0.2
    base -= basket_stress * 20.0

    lead_score = _safe_float(
        (lead.get("data") or [{}])[0].get("Lead_Score")
        if isinstance(lead.get("data"), list)
        else lead.get("Lead_Score"),
        0.0,
    )
    base += lead_score * 0.1

    return max(0.0, min(100.0, base))


# ── 2. Deal enrichment ────────────────────────────────────────────────────────

def build_deal_market_fields(
    procurement_signal: dict[str, Any],
    price_risk: dict[str, Any],
) -> dict[str, Any]:
    """
    Campos de inteligencia de precios para un deal de Zoho.
    Maneja gracefully errores de tier (Pro insuficiente).
    """
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

    risk_level = (
        "unknown"
        if price_risk.get("error")
        else (price_risk.get("risk_level") or price_risk.get("level") or "moderate").lower()
    )

    return {
        "Price_Risk_Level": risk_level,
        "Procurement_Signal": signal,
        "Market_Recommended_Action": recommended_action,
        "Price_Intelligence_Updated": _now_iso(),
    }


def _action_for_signal(signal: str) -> str:
    return {
        "buy_now": "Contactar ahora — oportunidad de compra óptima",
        "monitor": "Monitorear — mercado estable, sin urgencia",
        "wait":    "Esperar — se esperan mejores precios pronto",
    }.get(signal, f"Monitorear mercado ({signal})")


# ── 3. Inventory optimization ─────────────────────────────────────────────────

def build_product_market_fields(
    procurement_signal: dict[str, Any],
    price_risk: dict[str, Any],
    product: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Campos de optimización de inventario para un producto de Zoho.
    Calcula el stock recomendado basado en la señal de procurement.
    """
    if procurement_signal.get("error"):
        signal = "unavailable"
    else:
        signal = (
            procurement_signal.get("signal")
            or procurement_signal.get("procurement_signal")
            or "monitor"
        ).lower()

    risk_level = (
        "unknown"
        if price_risk.get("error")
        else (price_risk.get("risk_level") or price_risk.get("level") or "moderate").lower()
    )

    recommended_stock = calculate_recommended_stock(product or {}, signal)

    return {
        "Market_Price_Risk": risk_level,
        "Procurement_Signal": signal,
        "Recommended_Stock": recommended_stock,
        "Market_Intelligence_Updated": _now_iso(),
    }


def calculate_recommended_stock(product: dict[str, Any], signal: str) -> int:
    """
    Stock recomendado según señal de procurement:
      buy_now → +20% (stockear antes de subida)
      wait    → -10% (no acumular, se esperan mejores precios)
      monitor → sin cambio

    Usa datos del producto de Zoho: Quantity_In_Stock, Lead_Time, Daily_Demand.
    Nunca devuelve menos que el stock actual.
    """
    # Extrae desde la forma raw de Zoho ("data":[{...}]) o plana
    prod = product
    if isinstance(product.get("data"), list) and product["data"]:
        prod = product["data"][0]

    current_stock = _safe_int(prod.get("Quantity_In_Stock"), 0)
    lead_time     = _safe_int(prod.get("Lead_Time"), 7)       # días
    daily_demand  = _safe_int(prod.get("Daily_Demand"), 10)   # unidades/día

    multiplier = {"buy_now": 1.2, "wait": 0.9}.get(signal, 1.0)
    base = daily_demand * lead_time
    recommended = int(base * multiplier)

    # Nunca bajar del stock actual
    return max(recommended, current_stock)
