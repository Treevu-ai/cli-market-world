"""
Kommo enrichment logic.

DIFERENCIA CRÍTICA vs HubSpot/Zoho:
  Kommo no tiene propiedades nombradas. Los custom fields se identifican por
  un field_id entero. Para escribir datos de CLI Market hay que:
    1. Crear los campos custom en Kommo (GET /api/v4/account → confirmar que existen).
    2. Configurar los IDs en env vars o en KOMMO_FIELD_IDS (ver abajo).
    3. El payload de update usa:
       {"custom_fields_values": [{"field_id": 123, "values": [{"value": "texto"}]}]}

Campos que creamos en Kommo (leads y contacts):
  CLI_Market_Basket_Stress     — numeric
  CLI_Market_Inflation_Signal  — text
  CLI_Market_Price_Fairness    — numeric
  CLI_Market_Retail_Aggression — numeric
  CLI_Market_Market_Score      — numeric  (solo leads)
  CLI_Market_Procurement       — text     (leads — señal Pro)
  CLI_Market_Price_Risk        — text     (leads — señal Pro)
  CLI_Market_Data_Updated      — text

Los IDs se configuran vía env vars. Si no están seteados, el middleware
solo puede hacer setup automático (crear campos) la primera vez.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from cli_market_integrations.shared.enrichment import (
    safe_float, now_iso, extract_scores, action_for_signal,
)

logger = logging.getLogger(__name__)


# ── Field ID resolution ───────────────────────────────────────────────────────

def _field_ids() -> dict[str, int | None]:
    """
    Lee los IDs de campos custom de Kommo desde env vars.
    Retorna None para los campos no configurados (se skippean silenciosamente).
    """
    def _id(key: str) -> int | None:
        v = os.getenv(key)
        try: return int(v) if v else None
        except ValueError: return None

    return {
        "basket_stress":     _id("KOMMO_FIELD_BASKET_STRESS"),
        "inflation_signal":  _id("KOMMO_FIELD_INFLATION_SIGNAL"),
        "price_fairness":    _id("KOMMO_FIELD_PRICE_FAIRNESS"),
        "retail_aggression": _id("KOMMO_FIELD_RETAIL_AGGRESSION"),
        "market_score":      _id("KOMMO_FIELD_MARKET_SCORE"),
        "procurement":       _id("KOMMO_FIELD_PROCUREMENT"),
        "price_risk":        _id("KOMMO_FIELD_PRICE_RISK"),
        "data_updated":      _id("KOMMO_FIELD_DATA_UPDATED"),
    }


def _custom_fields_payload(field_map: dict[str, int | None], values: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Construye el array custom_fields_values para el payload de Kommo.
    Solo incluye campos con field_id configurado.
    """
    result = []
    for key, fid in field_map.items():
        if fid is None or key not in values:
            continue
        val = values[key]
        if val is None:
            continue
        result.append({"field_id": fid, "values": [{"value": str(val)}]})
    return result


# ── Lead enrichment ───────────────────────────────────────────────────────────

def build_lead_custom_fields(
    market_summary: dict[str, Any],
    lead: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Retorna el array custom_fields_values para actualizar un lead de Kommo.
    Los valores que no tengan field_id configurado se omiten.
    """
    scores_raw = market_summary.get("scores") or {}
    scores = extract_scores(scores_raw)
    brief = market_summary.get("brief") or {}

    shelf_signal = (
        brief.get("shelf_signal") or brief.get("headline") or brief.get("summary") or "neutral"
    )
    if isinstance(shelf_signal, str) and len(shelf_signal) > 200:
        shelf_signal = shelf_signal[:197] + "..."

    market_score = _calculate_market_score(lead, scores)

    field_ids = _field_ids()
    values = {
        "basket_stress":     min(round(scores["basket_stress"], 4), 1.0),
        "inflation_signal":  str(shelf_signal),
        "price_fairness":    round(scores["price_fairness"], 2),
        "retail_aggression": round(scores["retail_aggression"], 2),
        "market_score":      round(market_score, 2),
        "data_updated":      now_iso(),
    }
    return _custom_fields_payload(field_ids, values)


def _calculate_market_score(lead: dict[str, Any] | None, scores: dict[str, Any]) -> float:
    """Market score 0-100 — mismo algoritmo que Zoho adapter."""
    base = (
        50.0
        + (scores.get("retail_aggression", 50.0) - 50.0) * 0.3
        + (scores.get("price_fairness", 50.0) - 50.0) * 0.2
        - scores.get("basket_stress", 0.0) * 20.0
    )
    return max(0.0, min(100.0, base))


# ── Deal/Lead Pro signals enrichment ──────────────────────────────────────────

def build_deal_custom_fields(
    procurement_signal: dict[str, Any],
    price_risk: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Retorna custom_fields_values con señales Pro para un lead/deal de Kommo.
    Graceful: si tier insuficiente, escribe "unavailable"/"unknown".
    """
    if procurement_signal.get("error"):
        signal = "unavailable"
    else:
        signal = (
            procurement_signal.get("signal")
            or procurement_signal.get("procurement_signal")
            or "monitor"
        ).lower()

    risk = (
        "unknown"
        if price_risk.get("error")
        else (price_risk.get("risk_level") or price_risk.get("level") or "moderate").lower()
    )

    field_ids = _field_ids()
    values = {
        "procurement": signal,
        "price_risk":  risk,
        "data_updated": now_iso(),
    }
    return _custom_fields_payload(field_ids, values)


# ── Field definitions (para setup automático) ─────────────────────────────────

LEAD_FIELD_DEFINITIONS = [
    {"env": "KOMMO_FIELD_BASKET_STRESS",     "name": "CLI_Market_Basket_Stress",     "type": "numeric"},
    {"env": "KOMMO_FIELD_INFLATION_SIGNAL",  "name": "CLI_Market_Inflation_Signal",  "type": "text"},
    {"env": "KOMMO_FIELD_PRICE_FAIRNESS",    "name": "CLI_Market_Price_Fairness",    "type": "numeric"},
    {"env": "KOMMO_FIELD_RETAIL_AGGRESSION", "name": "CLI_Market_Retail_Aggression", "type": "numeric"},
    {"env": "KOMMO_FIELD_MARKET_SCORE",      "name": "CLI_Market_Market_Score",      "type": "numeric"},
    {"env": "KOMMO_FIELD_PROCUREMENT",       "name": "CLI_Market_Procurement",       "type": "text"},
    {"env": "KOMMO_FIELD_PRICE_RISK",        "name": "CLI_Market_Price_Risk",        "type": "text"},
    {"env": "KOMMO_FIELD_DATA_UPDATED",      "name": "CLI_Market_Data_Updated",      "type": "text"},
]
