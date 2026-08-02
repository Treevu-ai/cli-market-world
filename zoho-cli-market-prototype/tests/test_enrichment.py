"""
Tests unitarios para la lógica de enrichment de Zoho CRM.
Sin red, sin Zoho real, sin CLI Market real.
"""
from __future__ import annotations

import pytest
from src.enrichment import (
    build_lead_market_fields,
    build_deal_market_fields,
    build_product_market_fields,
    calculate_market_score,
    calculate_recommended_stock,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

SCORES_SAMPLE = {
    "scores": {
        "retail_aggression": 85.6,
        "price_fairness": 89.1,
        "basket_stress": 0.0,
    }
}

BRIEF_SAMPLE = {
    "shelf_signal": "4.3 pp below official CPI",
}

MARKET_SUMMARY = {
    "country": "PE",
    "brief": BRIEF_SAMPLE,
    "scores": SCORES_SAMPLE,
    "inflation": {"rpv": -1.2},
}

PROCUREMENT_BUY_NOW   = {"signal": "buy_now"}
PROCUREMENT_WAIT      = {"signal": "wait"}
PROCUREMENT_MONITOR   = {"signal": "monitor"}
PROCUREMENT_TIER_ERR  = {"error": "tier_insufficient", "status_code": 403}

PRICE_RISK_MODERATE   = {"risk_level": "moderate"}
PRICE_RISK_TIER_ERR   = {"error": "tier_insufficient", "status_code": 403}

PRODUCT_SAMPLE = {
    "data": [{
        "Product_Name": "Arroz Costeño 1kg",
        "Quantity_In_Stock": 50,
        "Lead_Time": 7,
        "Daily_Demand": 20,
    }]
}


# ── build_lead_market_fields ─────────────────────────────────────────────────

class TestBuildLeadMarketFields:
    def test_returns_all_required_keys(self):
        fields = build_lead_market_fields(MARKET_SUMMARY)
        for key in (
            "Market_Basket_Stress", "Market_Inflation_Signal",
            "Market_Price_Fairness", "Market_Retail_Aggression",
            "Market_Score", "Market_Data_Updated",
        ):
            assert key in fields, f"Missing key: {key}"

    def test_market_score_in_range(self):
        fields = build_lead_market_fields(MARKET_SUMMARY)
        assert 0.0 <= fields["Market_Score"] <= 100.0

    def test_basket_stress_never_negative(self):
        fields = build_lead_market_fields(MARKET_SUMMARY)
        assert fields["Market_Basket_Stress"] >= 0.0

    def test_shelf_signal_string(self):
        fields = build_lead_market_fields(MARKET_SUMMARY)
        assert isinstance(fields["Market_Inflation_Signal"], str)

    def test_shelf_signal_truncated_long(self):
        long_brief = {"shelf_signal": "x" * 300}
        fields = build_lead_market_fields({"brief": long_brief, "scores": {}})
        assert len(fields["Market_Inflation_Signal"]) <= 203

    def test_empty_market_summary_does_not_raise(self):
        fields = build_lead_market_fields({})
        assert fields["Market_Basket_Stress"] == 0.0
        assert fields["Market_Score"] >= 0.0

    def test_with_lead_data_zoho_wrapper(self):
        lead = {"data": [{"Lead_Score": 80}]}
        fields = build_lead_market_fields(MARKET_SUMMARY, lead)
        # Lead_Score 80 suma 8 puntos al score
        fields_no_lead = build_lead_market_fields(MARKET_SUMMARY)
        assert fields["Market_Score"] > fields_no_lead["Market_Score"]

    def test_scores_under_scores_key(self):
        """El endpoint /v1/intel/scores puede anidar bajo 'scores'."""
        nested = {"scores": {"retail_aggression": 90.0, "price_fairness": 70.0, "basket_stress": 0.1}}
        fields = build_lead_market_fields({"brief": {}, "scores": nested})
        assert fields["Market_Retail_Aggression"] == pytest.approx(90.0, abs=0.01)


# ── calculate_market_score ────────────────────────────────────────────────────

class TestCalculateMarketScore:
    def test_neutral_inputs_give_near_50(self):
        score = calculate_market_score({}, {"retail_aggression": 50, "price_fairness": 50, "basket_stress": 0})
        assert score == pytest.approx(50.0, abs=1.0)

    def test_high_retail_aggression_raises_score(self):
        score_high = calculate_market_score({}, {"retail_aggression": 100, "price_fairness": 50, "basket_stress": 0})
        score_low  = calculate_market_score({}, {"retail_aggression": 0,   "price_fairness": 50, "basket_stress": 0})
        assert score_high > score_low

    def test_high_basket_stress_lowers_score(self):
        score_stress = calculate_market_score({}, {"retail_aggression": 50, "price_fairness": 50, "basket_stress": 1.0})
        score_none   = calculate_market_score({}, {"retail_aggression": 50, "price_fairness": 50, "basket_stress": 0.0})
        assert score_stress < score_none

    def test_score_capped_0_100(self):
        extreme = {"retail_aggression": 200, "price_fairness": 200, "basket_stress": 0}
        assert calculate_market_score({}, extreme) <= 100.0
        extreme_low = {"retail_aggression": -100, "price_fairness": -100, "basket_stress": 5}
        assert calculate_market_score({}, extreme_low) >= 0.0


# ── build_deal_market_fields ──────────────────────────────────────────────────

class TestBuildDealMarketFields:
    def test_returns_all_required_keys(self):
        fields = build_deal_market_fields(PROCUREMENT_BUY_NOW, PRICE_RISK_MODERATE)
        for key in ("Price_Risk_Level", "Procurement_Signal", "Market_Recommended_Action", "Price_Intelligence_Updated"):
            assert key in fields

    def test_buy_now_action(self):
        fields = build_deal_market_fields(PROCUREMENT_BUY_NOW, PRICE_RISK_MODERATE)
        assert "ahora" in fields["Market_Recommended_Action"].lower()
        assert fields["Procurement_Signal"] == "buy_now"

    def test_wait_action(self):
        fields = build_deal_market_fields(PROCUREMENT_WAIT, PRICE_RISK_MODERATE)
        assert "esperar" in fields["Market_Recommended_Action"].lower()

    def test_monitor_action(self):
        fields = build_deal_market_fields(PROCUREMENT_MONITOR, PRICE_RISK_MODERATE)
        assert "monitorear" in fields["Market_Recommended_Action"].lower()

    def test_tier_insufficient_procurement(self):
        fields = build_deal_market_fields(PROCUREMENT_TIER_ERR, PRICE_RISK_MODERATE)
        assert fields["Procurement_Signal"] == "unavailable"
        assert "Pro" in fields["Market_Recommended_Action"]

    def test_tier_insufficient_price_risk(self):
        fields = build_deal_market_fields(PROCUREMENT_BUY_NOW, PRICE_RISK_TIER_ERR)
        assert fields["Price_Risk_Level"] == "unknown"

    def test_both_tier_insufficient(self):
        fields = build_deal_market_fields(PROCUREMENT_TIER_ERR, PRICE_RISK_TIER_ERR)
        assert fields["Procurement_Signal"] == "unavailable"
        assert fields["Price_Risk_Level"] == "unknown"


# ── build_product_market_fields ───────────────────────────────────────────────

class TestBuildProductMarketFields:
    def test_returns_all_required_keys(self):
        fields = build_product_market_fields(PROCUREMENT_BUY_NOW, PRICE_RISK_MODERATE, PRODUCT_SAMPLE)
        for key in ("Market_Price_Risk", "Procurement_Signal", "Recommended_Stock", "Market_Intelligence_Updated"):
            assert key in fields

    def test_buy_now_increases_stock(self):
        fields = build_product_market_fields(PROCUREMENT_BUY_NOW, PRICE_RISK_MODERATE, PRODUCT_SAMPLE)
        # daily_demand=20, lead_time=7 → base=140 * 1.2 = 168
        assert fields["Recommended_Stock"] == 168

    def test_wait_decreases_stock(self):
        fields = build_product_market_fields(PROCUREMENT_WAIT, PRICE_RISK_MODERATE, PRODUCT_SAMPLE)
        # 140 * 0.9 = 126, pero stock actual es 50, 126 > 50 → 126
        assert fields["Recommended_Stock"] == 126

    def test_monitor_keeps_base(self):
        fields = build_product_market_fields(PROCUREMENT_MONITOR, PRICE_RISK_MODERATE, PRODUCT_SAMPLE)
        assert fields["Recommended_Stock"] == 140

    def test_never_below_current_stock(self):
        # Stock actual = 200, base = 20*7=140*0.9=126 < 200 → mantiene 200
        big_stock = {"data": [{"Quantity_In_Stock": 200, "Lead_Time": 7, "Daily_Demand": 20}]}
        fields = build_product_market_fields(PROCUREMENT_WAIT, PRICE_RISK_MODERATE, big_stock)
        assert fields["Recommended_Stock"] == 200

    def test_tier_insufficient_graceful(self):
        fields = build_product_market_fields(PROCUREMENT_TIER_ERR, PRICE_RISK_TIER_ERR, PRODUCT_SAMPLE)
        assert fields["Procurement_Signal"] == "unavailable"
        assert fields["Market_Price_Risk"] == "unknown"
        # Aun con señal unavailable calcula stock con multiplier 1.0 (monitor)
        assert fields["Recommended_Stock"] >= 0


# ── calculate_recommended_stock ───────────────────────────────────────────────

class TestCalculateRecommendedStock:
    def test_buy_now_multiplier(self):
        prod = {"Quantity_In_Stock": 0, "Lead_Time": 10, "Daily_Demand": 10}
        assert calculate_recommended_stock(prod, "buy_now") == 120  # 100 * 1.2

    def test_wait_multiplier(self):
        prod = {"Quantity_In_Stock": 0, "Lead_Time": 10, "Daily_Demand": 10}
        assert calculate_recommended_stock(prod, "wait") == 90  # 100 * 0.9

    def test_monitor_no_change(self):
        prod = {"Quantity_In_Stock": 0, "Lead_Time": 10, "Daily_Demand": 10}
        assert calculate_recommended_stock(prod, "monitor") == 100

    def test_never_below_current_stock(self):
        prod = {"Quantity_In_Stock": 500, "Lead_Time": 1, "Daily_Demand": 1}
        # base = 1*1*0.9 = 0 → mantiene 500
        assert calculate_recommended_stock(prod, "wait") == 500

    def test_missing_fields_use_defaults(self):
        # Sin campos → daily_demand=10, lead_time=7, stock=0
        result = calculate_recommended_stock({}, "buy_now")
        assert result == 84  # 10 * 7 * 1.2

    def test_zoho_wrapper_format(self):
        prod = {"data": [{"Quantity_In_Stock": 0, "Lead_Time": 5, "Daily_Demand": 4}]}
        assert calculate_recommended_stock(prod, "buy_now") == 24  # 4*5*1.2
