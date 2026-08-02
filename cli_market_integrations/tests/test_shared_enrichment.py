"""Tests for cli_market_integrations.shared.enrichment"""
from __future__ import annotations
import pytest
from cli_market_integrations.shared.enrichment import (
    safe_float, safe_int, now_iso, action_for_signal,
    extract_scores, build_deal_pro_fields,
)


class TestSafeFloat:
    def test_int(self):           assert safe_float(5) == 5.0
    def test_str(self):           assert safe_float("3.14") == pytest.approx(3.14)
    def test_none(self):          assert safe_float(None) == 0.0
    def test_default(self):       assert safe_float(None, 99.0) == 99.0
    def test_invalid(self):       assert safe_float("abc") == 0.0
    def test_zero(self):          assert safe_float(0) == 0.0


class TestSafeInt:
    def test_float(self):         assert safe_int(3.9) == 3
    def test_str(self):           assert safe_int("7") == 7
    def test_none(self):          assert safe_int(None) == 0
    def test_default(self):       assert safe_int(None, 10) == 10
    def test_invalid(self):       assert safe_int("x") == 0


class TestNowIso:
    def test_returns_string(self):
        s = now_iso()
        assert isinstance(s, str) and "T" in s

    def test_has_utc_indicator(self):
        s = now_iso()
        assert "+" in s or s.endswith("Z")


class TestActionForSignal:
    def test_buy_now(self):   assert "ahora"     in action_for_signal("buy_now").lower()
    def test_wait(self):      assert "esperar"   in action_for_signal("wait").lower()
    def test_monitor(self):   assert "monitorear" in action_for_signal("monitor").lower()
    def test_unknown(self):   assert "monitorear" in action_for_signal("xyz").lower()


class TestExtractScores:
    def test_flat(self):
        s = extract_scores({"retail_aggression": 85.0, "price_fairness": 90.0, "basket_stress": 0.2})
        assert s["retail_aggression"] == pytest.approx(85.0)
        assert s["price_fairness"] == pytest.approx(90.0)
        assert s["basket_stress"] == pytest.approx(0.2)

    def test_nested(self):
        s = extract_scores({"scores": {"retail_aggression": 70.0, "price_fairness": 60.0, "basket_stress": 0.5}})
        assert s["retail_aggression"] == pytest.approx(70.0)

    def test_empty_defaults_zero(self):
        s = extract_scores({})
        assert s["retail_aggression"] == 0.0

    def test_string_values_coerced(self):
        s = extract_scores({"retail_aggression": "85.6", "price_fairness": "0", "basket_stress": "0"})
        assert s["retail_aggression"] == pytest.approx(85.6)


class TestBuildDealProFields:
    BUY  = {"signal": "buy_now"}
    MOD  = {"risk_level": "moderate"}
    ERR  = {"error": "tier_insufficient"}

    def test_keys(self):
        r = build_deal_pro_fields(self.BUY, self.MOD, "ts")
        for k in ("risk_level", "signal", "recommended_action", "timestamp"):
            assert k in r

    def test_buy_now(self):
        r = build_deal_pro_fields(self.BUY, self.MOD, "ts")
        assert r["signal"] == "buy_now"
        assert "ahora" in r["recommended_action"].lower()

    def test_tier_procurement(self):
        r = build_deal_pro_fields(self.ERR, self.MOD, "ts")
        assert r["signal"] == "unavailable"
        assert "Pro" in r["recommended_action"]

    def test_tier_risk(self):
        r = build_deal_pro_fields(self.BUY, self.ERR, "ts")
        assert r["risk_level"] == "unknown"

    def test_timestamp_iso(self):
        r = build_deal_pro_fields(self.BUY, self.MOD, "ts")
        assert "T" in r["timestamp"]
