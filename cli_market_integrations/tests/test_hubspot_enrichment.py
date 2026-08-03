"""Tests for cli_market_integrations.adapters.hubspot.enrichment"""
from __future__ import annotations
from cli_market_integrations.adapters.hubspot.enrichment import (
    build_contact_market_properties,
    build_deal_market_properties,
    compute_lead_score_delta,
)

SCORES  = {"scores": {"retail_aggression": 85.6, "price_fairness": 89.1, "basket_stress": 0.45}}
BRIEF   = {"shelf_signal": "4.3 pp below official CPI"}
SUMMARY = {"country": "PE", "brief": BRIEF, "scores": SCORES}
BUY     = {"signal": "buy_now"}
MOD     = {"risk_level": "moderate"}
TIER    = {"error": "tier_insufficient"}


class TestBuildContactMarketProperties:
    def test_all_keys(self):
        p = build_contact_market_properties(SUMMARY)
        for k in ("market_basket_stress","market_inflation_signal","market_price_fairness","market_retail_aggression","market_data_updated"):
            assert k in p

    def test_snake_case(self):
        p = build_contact_market_properties(SUMMARY)
        assert all(k == k.lower() for k in p), "HubSpot props must be snake_case"

    def test_all_strings(self):
        p = build_contact_market_properties(SUMMARY)
        for k, v in p.items():
            assert isinstance(v, str), f"{k} should be str"

    def test_stress_capped(self):
        extreme = {"scores": {"basket_stress": 99.0, "retail_aggression": 0, "price_fairness": 0}}
        c = {"properties": {"income_level": "low", "family_size": "5"}}
        p = build_contact_market_properties({"brief": {}, "scores": extreme}, c)
        assert float(p["market_basket_stress"]) <= 1.0

    def test_low_income_raises_stress(self):
        cl = {"properties": {"income_level": "low",  "family_size": "1"}}
        ch = {"properties": {"income_level": "high", "family_size": "1"}}
        sl = float(build_contact_market_properties(SUMMARY, cl)["market_basket_stress"])
        sh = float(build_contact_market_properties(SUMMARY, ch)["market_basket_stress"])
        assert sl > sh

    def test_empty_no_raise(self):
        p = build_contact_market_properties({})
        assert "market_basket_stress" in p


class TestBuildDealMarketProperties:
    def test_all_keys(self):
        p = build_deal_market_properties(BUY, MOD)
        for k in ("price_risk_level","procurement_signal","market_recommended_action","price_intelligence_updated"):
            assert k in p

    def test_snake_case(self):
        p = build_deal_market_properties(BUY, MOD)
        assert all(k == k.lower() for k in p)

    def test_buy_now(self):
        p = build_deal_market_properties(BUY, MOD)
        assert "ahora" in p["market_recommended_action"].lower()

    def test_tier_procurement(self):
        p = build_deal_market_properties(TIER, MOD)
        assert p["procurement_signal"] == "unavailable"

    def test_tier_risk(self):
        p = build_deal_market_properties(BUY, TIER)
        assert p["price_risk_level"] == "unknown"


class TestComputeLeadScoreDelta:
    def test_high_stress_high_aggression(self):
        assert compute_lead_score_delta({"market_basket_stress": "0.85", "market_retail_aggression": "90.0"}) == 30

    def test_zero_all(self):
        assert compute_lead_score_delta({"market_basket_stress": "0.1", "market_retail_aggression": "30.0"}) == 0

    def test_empty_no_raise(self):
        assert compute_lead_score_delta({}) == 0
