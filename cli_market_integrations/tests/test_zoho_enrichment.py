"""Tests for cli_market_integrations.adapters.zoho.enrichment"""
from __future__ import annotations
import pytest
from cli_market_integrations.adapters.zoho.enrichment import (
    build_lead_market_fields,
    build_deal_market_fields,
    build_product_market_fields,
    calculate_market_score,
    calculate_recommended_stock,
)

SCORES  = {"scores": {"retail_aggression": 85.6, "price_fairness": 89.1, "basket_stress": 0.0}}
BRIEF   = {"shelf_signal": "stable"}
SUMMARY = {"country": "PE", "brief": BRIEF, "scores": SCORES}
BUY     = {"signal": "buy_now"}
MOD     = {"risk_level": "moderate"}
TIER    = {"error": "tier_insufficient"}
PROD    = {"data": [{"Quantity_In_Stock": 50, "Lead_Time": 7, "Daily_Demand": 20}]}


class TestBuildLeadMarketFields:
    def test_all_keys(self):
        f = build_lead_market_fields(SUMMARY)
        for k in ("Market_Basket_Stress","Market_Inflation_Signal","Market_Price_Fairness","Market_Retail_Aggression","Market_Score","Market_Data_Updated"):
            assert k in f

    def test_camel_case(self):
        f = build_lead_market_fields(SUMMARY)
        assert all(k[0].isupper() for k in f)

    def test_score_in_range(self):
        f = build_lead_market_fields(SUMMARY)
        assert 0.0 <= f["Market_Score"] <= 100.0


class TestBuildDealMarketFields:
    def test_camel_case(self):
        f = build_deal_market_fields(BUY, MOD)
        assert all(k[0].isupper() for k in f)

    def test_buy_now(self):
        f = build_deal_market_fields(BUY, MOD)
        assert "ahora" in f["Market_Recommended_Action"].lower()

    def test_tier_graceful(self):
        f = build_deal_market_fields(TIER, TIER)
        assert f["Procurement_Signal"] == "unavailable"
        assert f["Price_Risk_Level"] == "unknown"


class TestBuildProductMarketFields:
    def test_buy_now_stock(self):
        f = build_product_market_fields(BUY, MOD, PROD)
        assert f["Recommended_Stock"] == 168  # 20*7*1.2

    def test_never_below_current(self):
        big = {"data": [{"Quantity_In_Stock": 500, "Lead_Time": 7, "Daily_Demand": 20}]}
        f = build_product_market_fields({"signal": "wait"}, MOD, big)
        assert f["Recommended_Stock"] == 500


class TestCalculateMarketScore:
    def test_neutral(self):
        s = calculate_market_score({}, {"retail_aggression": 50, "price_fairness": 50, "basket_stress": 0})
        assert s == pytest.approx(50.0, abs=1.0)

    def test_capped(self):
        assert calculate_market_score({}, {"retail_aggression": 200, "price_fairness": 200, "basket_stress": 0}) <= 100.0
        assert calculate_market_score({}, {"retail_aggression": -100, "price_fairness": -100, "basket_stress": 5}) >= 0.0


class TestCalculateRecommendedStock:
    def test_buy_now(self):
        assert calculate_recommended_stock({"Quantity_In_Stock": 0, "Lead_Time": 10, "Daily_Demand": 10}, "buy_now") == 120

    def test_wait(self):
        assert calculate_recommended_stock({"Quantity_In_Stock": 0, "Lead_Time": 10, "Daily_Demand": 10}, "wait") == 90

    def test_floor_current(self):
        assert calculate_recommended_stock({"Quantity_In_Stock": 500, "Lead_Time": 1, "Daily_Demand": 1}, "wait") == 500
