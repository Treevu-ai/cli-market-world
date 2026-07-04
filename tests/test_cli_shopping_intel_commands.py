"""Tests for the 6 new CLI commands mirroring previously MCP-only tools:
market stats, trending, price-risk, substitutes, price-history, favorites."""

from __future__ import annotations

import argparse
import json
from unittest.mock import MagicMock

import market_cli


def _status_mock():
    return MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False)


def _patch_common(monkeypatch, response):
    captured = {}

    def _fake_cli_api(method, path, *a, **k):
        captured["method"] = method
        captured["path"] = path
        return response

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)
    return captured


def test_cmd_stats_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "total_price_snapshots": 68108, "total_search_queries": 379,
        "unique_stores_tracked": 40, "unique_products_tracked": 63049,
        "latest_snapshot_at": "2026-07-04T01:50:01Z",
    })
    args = argparse.Namespace(json=False)
    market_cli.cmd_stats(args)
    assert captured["method"] == "GET"
    assert captured["path"] == "/analytics/stats"


def test_cmd_trending_calls_correct_endpoint_and_renders_empty(monkeypatch):
    captured = _patch_common(monkeypatch, {"trending": [], "total": 0})
    args = argparse.Namespace(country="PE", line=None, limit=10, json=False)
    market_cli.cmd_trending(args)
    assert captured["path"] == "/analytics/trending?country=PE&line=&limit=10"


def test_cmd_price_risk_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {
            "risk_level": "high",
            "risk_reason": "high promo intensity",
            "signals": {"price_dispersion_pct": 24.27, "promo_intensity_pct": 39.1,
                        "basket_stress_index": 0.07, "staple_momentum_7d_pct": 5.98},
        },
        "meta": {},
    })
    args = argparse.Namespace(country="PE", line=None, days=7, json=False)
    market_cli.cmd_price_risk(args)
    assert captured["path"] == "/v1/intel/price-risk?country=PE&line=&days=7"


def test_cmd_substitutes_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {
            "original": {"name": "Leche Fresca Piamonte", "store": "metro", "price": 4.8},
            "substitutes": [],
        },
        "meta": {},
    })
    args = argparse.Namespace(query="leche", country="PE", store=None, limit=3, json=False)
    market_cli.cmd_substitutes(args)
    assert captured["path"] == "/v1/products/substitutes?query=leche&country=PE&store=&limit=3"


def test_cmd_substitutes_escapes_special_characters_in_query(monkeypatch):
    """Regression: an unescaped '&' or '#' in a free-text query would corrupt
    the query string (e.g. query="leche & queso" would inject a bogus param)."""
    captured = _patch_common(monkeypatch, {"data": {"original": {}, "substitutes": []}, "meta": {}})
    args = argparse.Namespace(query="leche & queso #2", country="PE", store=None, limit=3, json=False)
    market_cli.cmd_substitutes(args)
    assert "&country=PE" in captured["path"]
    assert captured["path"].count("&") == 3  # only the 3 real param separators, none injected
    assert "query=leche%20%26%20queso%20%232" in captured["path"]


def test_cmd_substitutes_handles_missing_original(monkeypatch):
    _patch_common(monkeypatch, {"data": {"original": {}, "substitutes": []}, "meta": {}})
    args = argparse.Namespace(query="xyzzy", country="PE", store=None, limit=3, json=False)
    market_cli.cmd_substitutes(args)  # should not raise


def test_cmd_price_history_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "snapshots": [{"queried_at": "2026-07-04T01:25:00Z", "price": 4.8, "list_price": 7.9,
                       "discount": 39, "currency": "PEN", "name": "Leche Fresca Piamonte"}],
    })
    args = argparse.Namespace(product_id="543365", store="metro", line=None, limit=50, json=False)
    market_cli.cmd_price_history(args)
    assert captured["path"] == "/analytics/price-history?product_id=543365&store=metro&line=&limit=50"


def test_cmd_price_history_handles_empty_snapshots(monkeypatch):
    _patch_common(monkeypatch, {"snapshots": []})
    args = argparse.Namespace(product_id="unknown", store=None, line=None, limit=50, json=False)
    market_cli.cmd_price_history(args)  # should not raise


def test_cmd_favorites_list_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {"favorites": [], "total": 0})
    args = argparse.Namespace(action="list", product_id=None, name=None, store=None, json=False)
    market_cli.cmd_favorites(args)
    assert captured["method"] == "POST"
    assert captured["path"] == "/favorites"


def test_cmd_favorites_add_passes_payload(monkeypatch):
    posted = {}

    def _fake_cli_api(method, path, payload=None, *a, **k):
        posted["method"] = method
        posted["path"] = path
        posted["payload"] = payload
        return {"favorites": [{"name": "Leche", "store": "metro", "product_id": "543365"}]}

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(action="add", product_id="543365", name="Leche", store="metro", json=False)
    market_cli.cmd_favorites(args)

    assert posted["payload"]["action"] == "add"
    assert posted["payload"]["product_id"] == "543365"


def test_cmd_stats_json_mode_prints_raw_payload(monkeypatch):
    response = {"total_price_snapshots": 1}
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: response)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())

    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(json=True)
    market_cli.cmd_stats(args)

    assert len(printed) == 1
    assert json.loads(printed[0]) == response
