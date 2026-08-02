"""
Tests unitarios para la lógica de enrichment (sin red, sin HubSpot real).
"""
from __future__ import annotations

import pytest
from src.enrichment import (
    build_contact_market_properties,
    build_deal_market_properties,
    compute_lead_score_delta,
    _personalise_basket_stress,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

SCORES_SAMPLE = {
    "scores": {
        "retail_aggression": 85.6,
        "price_fairness": 89.1,
        "basket_stress": 0.45,
    }
}

BRIEF_SAMPLE = {
    "shelf_signal": "4.3 pp below official CPI",
    "headline": "Retail activo con deflación moderada",
}

MARKET_SUMMARY_SAMPLE = {
    "country": "PE",
    "brief": BRIEF_SAMPLE,
    "scores": SCORES_SAMPLE,
    "inflation": {"rpv": -1.2, "days": 7},
}

PROCUREMENT_SAMPLE = {"signal": "buy_now"}
PRICE_RISK_SAMPLE = {"risk_level": "moderate"}


# ── Contact enrichment ────────────────────────────────────────────────────────

class TestBuildContactMarketProperties:
    def test_returns_all_required_keys(self):
        props = build_contact_market_properties(MARKET_SUMMARY_SAMPLE)
        assert "market_basket_stress" in props
        assert "market_inflation_signal" in props
        assert "market_price_fairness" in props
        assert "market_retail_aggression" in props
        assert "market_data_updated" in props

    def test_all_values_are_strings(self):
        props = build_contact_market_properties(MARKET_SUMMARY_SAMPLE)
        for k, v in props.items():
            assert isinstance(v, str), f"{k} should be str, got {type(v)}"

    def test_basket_stress_capped_at_1(self):
        extreme_scores = {"scores": {"basket_stress": 99.0, "retail_aggression": 0, "price_fairness": 0}}
        contact = {"properties": {"income_level": "low", "family_size": "5"}}
        props = build_contact_market_properties({"brief": {}, "scores": extreme_scores}, contact)
        stress = float(props["market_basket_stress"])
        assert stress <= 1.0

    def test_shelf_signal_truncated_if_long(self):
        long_brief = {"shelf_signal": "x" * 300}
        props = build_contact_market_properties({"brief": long_brief, "scores": {}})
        assert len(props["market_inflation_signal"]) <= 203  # 200 + "..."

    def test_empty_market_summary_does_not_raise(self):
        props = build_contact_market_properties({})
        assert "market_basket_stress" in props
        assert float(props["market_basket_stress"]) == 0.0

    def test_personalisation_low_income_increases_stress(self):
        contact_low = {"properties": {"income_level": "low", "family_size": "1"}}
        contact_high = {"properties": {"income_level": "high", "family_size": "1"}}
        props_low = build_contact_market_properties(MARKET_SUMMARY_SAMPLE, contact_low)
        props_high = build_contact_market_properties(MARKET_SUMMARY_SAMPLE, contact_high)
        assert float(props_low["market_basket_stress"]) > float(props_high["market_basket_stress"])

    def test_personalisation_family_size_increases_stress(self):
        contact_small = {"properties": {"income_level": "medium", "family_size": "1"}}
        contact_large = {"properties": {"income_level": "medium", "family_size": "6"}}
        props_small = build_contact_market_properties(MARKET_SUMMARY_SAMPLE, contact_small)
        props_large = build_contact_market_properties(MARKET_SUMMARY_SAMPLE, contact_large)
        assert float(props_large["market_basket_stress"]) > float(props_small["market_basket_stress"])


# ── Deal enrichment ───────────────────────────────────────────────────────────

class TestBuildDealMarketProperties:
    def test_returns_all_required_keys(self):
        props = build_deal_market_properties(PROCUREMENT_SAMPLE, PRICE_RISK_SAMPLE)
        assert "price_risk_level" in props
        assert "procurement_signal" in props
        assert "market_recommended_action" in props
        assert "price_intelligence_updated" in props

    def test_buy_now_signal_produces_action(self):
        props = build_deal_market_properties({"signal": "buy_now"}, PRICE_RISK_SAMPLE)
        assert "ahora" in props["market_recommended_action"].lower()

    def test_wait_signal(self):
        props = build_deal_market_properties({"signal": "wait"}, PRICE_RISK_SAMPLE)
        assert "esperar" in props["market_recommended_action"].lower()

    def test_monitor_signal(self):
        props = build_deal_market_properties({"signal": "monitor"}, PRICE_RISK_SAMPLE)
        assert "monitorear" in props["market_recommended_action"].lower()

    def test_tier_insufficient_procurement(self):
        props = build_deal_market_properties(
            {"error": "tier_insufficient"}, PRICE_RISK_SAMPLE
        )
        assert props["procurement_signal"] == "unavailable"
        assert "Pro" in props["market_recommended_action"]

    def test_tier_insufficient_price_risk(self):
        props = build_deal_market_properties(PROCUREMENT_SAMPLE, {"error": "tier_insufficient"})
        assert props["price_risk_level"] == "unknown"

    def test_all_values_are_strings(self):
        props = build_deal_market_properties(PROCUREMENT_SAMPLE, PRICE_RISK_SAMPLE)
        for k, v in props.items():
            assert isinstance(v, str), f"{k} should be str, got {type(v)}"


# ── Lead score ────────────────────────────────────────────────────────────────

class TestComputeLeadScoreDelta:
    def test_high_stress_gives_max_delta(self):
        props = {
            "market_basket_stress": "0.85",
            "market_retail_aggression": "90.0",
        }
        delta = compute_lead_score_delta(props)
        assert delta == 30  # 20 (stress>0.7) + 10 (aggression>80)

    def test_low_stress_and_low_aggression_gives_zero(self):
        props = {
            "market_basket_stress": "0.1",
            "market_retail_aggression": "30.0",
        }
        assert compute_lead_score_delta(props) == 0

    def test_medium_stress_no_aggression(self):
        props = {
            "market_basket_stress": "0.6",
            "market_retail_aggression": "50.0",
        }
        assert compute_lead_score_delta(props) == 10

    def test_missing_props_does_not_raise(self):
        assert compute_lead_score_delta({}) == 0
