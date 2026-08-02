"""
Shared enrichment helpers — used by HubSpot and Zoho adapters.

Provides:
  - Type-safe coercion helpers (_safe_float, _safe_int, _now_iso)
  - Shared signal→action mapping (_action_for_signal)
  - Common deal field builder (build_deal_market_fields)
  - Common pro-signal field builder (build_pro_signal_fields)

CRM-specific enrichment logic (lead scoring, contact personalisation,
inventory stock calculation) lives in each adapter's enrichment.py.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ── Type-safe coercion ────────────────────────────────────────────────────────

def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Signal → action ───────────────────────────────────────────────────────────

def action_for_signal(signal: str) -> str:
    return {
        "buy_now": "Contactar ahora — oportunidad de compra óptima",
        "monitor": "Monitorear — mercado estable, sin urgencia",
        "wait":    "Esperar — se esperan mejores precios pronto",
    }.get(signal, f"Monitorear mercado ({signal})")


# ── Score extraction (normalises nested vs flat API responses) ─────────────────

def extract_scores(scores_payload: dict[str, Any]) -> dict[str, float]:
    """
    /v1/intel/scores may return scores directly or nested under "scores".
    Returns a flat dict with float values.
    """
    inner = scores_payload.get("scores") or scores_payload
    return {
        "retail_aggression": safe_float(inner.get("retail_aggression")),
        "price_fairness":    safe_float(inner.get("price_fairness")),
        "basket_stress":     safe_float(inner.get("basket_stress")),
    }


# ── Shared deal enrichment ────────────────────────────────────────────────────

def build_deal_pro_fields(
    procurement_signal: dict[str, Any],
    price_risk: dict[str, Any],
    ts_field: str,
) -> dict[str, str]:
    """
    Build deal/opportunity fields from Pro CLI Market signals.
    Used by both HubSpot (Price_Risk_Level → snake_case props) and
    Zoho (Price_Risk_Level → CamelCase fields).

    ts_field: name of the timestamp field for this CRM
              HubSpot → "price_intelligence_updated"
              Zoho    → "Price_Intelligence_Updated"
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
        recommended_action = action_for_signal(signal)

    risk_level = (
        "unknown"
        if price_risk.get("error")
        else (price_risk.get("risk_level") or price_risk.get("level") or "moderate").lower()
    )

    return {
        "risk_level": risk_level,
        "signal": signal,
        "recommended_action": recommended_action,
        "timestamp": now_iso(),
    }
