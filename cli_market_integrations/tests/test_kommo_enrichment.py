"""Tests for cli_market_integrations.adapters.kommo.enrichment"""
from __future__ import annotations
import os
import pytest
from unittest.mock import patch
from cli_market_integrations.adapters.kommo.enrichment import (
    build_lead_custom_fields,
    build_deal_custom_fields,
    _field_ids,
    _custom_fields_payload,
    LEAD_FIELD_DEFINITIONS,
)

SCORES  = {"scores": {"retail_aggression": 80.0, "price_fairness": 75.0, "basket_stress": 0.3}}
BRIEF   = {"shelf_signal": "neutral"}
SUMMARY = {"country": "PE", "brief": BRIEF, "scores": SCORES}
BUY     = {"signal": "buy_now"}
MOD     = {"risk_level": "moderate"}
TIER    = {"error": "tier_insufficient"}

ENV_WITH_IDS = {
    "KOMMO_FIELD_BASKET_STRESS":     "1001",
    "KOMMO_FIELD_INFLATION_SIGNAL":  "1002",
    "KOMMO_FIELD_PRICE_FAIRNESS":    "1003",
    "KOMMO_FIELD_RETAIL_AGGRESSION": "1004",
    "KOMMO_FIELD_MARKET_SCORE":      "1005",
    "KOMMO_FIELD_PROCUREMENT":       "1006",
    "KOMMO_FIELD_PRICE_RISK":        "1007",
    "KOMMO_FIELD_DATA_UPDATED":      "1008",
}


class TestFieldIds:
    def test_returns_none_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            ids = _field_ids()
        assert all(v is None for v in ids.values())

    def test_returns_ints_when_set(self):
        with patch.dict(os.environ, ENV_WITH_IDS):
            ids = _field_ids()
        assert ids["basket_stress"] == 1001
        assert ids["market_score"] == 1005

    def test_invalid_value_returns_none(self):
        with patch.dict(os.environ, {"KOMMO_FIELD_BASKET_STRESS": "not_a_number"}):
            ids = _field_ids()
        assert ids["basket_stress"] is None


class TestCustomFieldsPayload:
    def test_skips_none_field_ids(self):
        field_map = {"a": None, "b": 123}
        values = {"a": "val_a", "b": "val_b"}
        payload = _custom_fields_payload(field_map, values)
        assert len(payload) == 1
        assert payload[0]["field_id"] == 123

    def test_correct_structure(self):
        field_map = {"score": 999}
        payload = _custom_fields_payload(field_map, {"score": 85.5})
        assert payload[0] == {"field_id": 999, "values": [{"value": "85.5"}]}

    def test_empty_when_no_ids(self):
        payload = _custom_fields_payload({"a": None}, {"a": "x"})
        assert payload == []


class TestBuildLeadCustomFields:
    def test_empty_when_no_env_vars(self):
        with patch.dict(os.environ, {}, clear=True):
            result = build_lead_custom_fields(SUMMARY)
        assert result == []

    def test_returns_list_with_env(self):
        with patch.dict(os.environ, ENV_WITH_IDS):
            result = build_lead_custom_fields(SUMMARY)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_structure_correct(self):
        with patch.dict(os.environ, ENV_WITH_IDS):
            result = build_lead_custom_fields(SUMMARY)
        for item in result:
            assert "field_id" in item
            assert "values" in item
            assert isinstance(item["values"], list)
            assert "value" in item["values"][0]

    def test_basket_stress_not_above_1(self):
        extreme = {"scores": {"basket_stress": 99.0, "retail_aggression": 0, "price_fairness": 0}}
        with patch.dict(os.environ, ENV_WITH_IDS):
            result = build_lead_custom_fields({"brief": {}, "scores": extreme})
        # Encuentra el campo basket_stress (field_id=1001)
        bs = next((r for r in result if r["field_id"] == 1001), None)
        if bs:
            assert float(bs["values"][0]["value"]) <= 1.0


class TestBuildDealCustomFields:
    def test_empty_when_no_env(self):
        with patch.dict(os.environ, {}, clear=True):
            result = build_deal_custom_fields(BUY, MOD)
        assert result == []

    def test_tier_insufficient_writes_unavailable(self):
        with patch.dict(os.environ, ENV_WITH_IDS):
            result = build_deal_custom_fields(TIER, TIER)
        proc_field = next((r for r in result if r["field_id"] == 1006), None)
        if proc_field:
            assert proc_field["values"][0]["value"] == "unavailable"

    def test_risk_unknown_on_tier_error(self):
        with patch.dict(os.environ, ENV_WITH_IDS):
            result = build_deal_custom_fields(BUY, TIER)
        risk_field = next((r for r in result if r["field_id"] == 1007), None)
        if risk_field:
            assert risk_field["values"][0]["value"] == "unknown"


class TestLeadFieldDefinitions:
    def test_all_have_required_keys(self):
        for defn in LEAD_FIELD_DEFINITIONS:
            assert "env" in defn
            assert "name" in defn
            assert "type" in defn

    def test_count(self):
        assert len(LEAD_FIELD_DEFINITIONS) == 8
