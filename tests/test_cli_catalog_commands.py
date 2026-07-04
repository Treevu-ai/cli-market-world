"""Tests for the catalog/discovery CLI commands mirroring previously
MCP-only tools: market brands, delivery, exchange, stock, ecosystem-radar,
price-alerts."""

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


def test_cmd_brands_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {"brands": [], "total": 0})
    args = argparse.Namespace(country="PE", line=None, limit=20, json=False)
    market_cli.cmd_brands(args)
    assert captured["path"] == "/analytics/brands?line=&country=PE&limit=20"


def test_cmd_delivery_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "store_name": "Metro", "delivery_available": True,
        "estimated_days": "2-5", "fee": 6.5, "message": "referential",
    })
    args = argparse.Namespace(product_id="543365", store="metro", zipcode=None, json=False)
    market_cli.cmd_delivery(args)
    assert captured["path"] == "/products/delivery/543365?store=metro&zipcode="


def test_cmd_exchange_calls_correct_endpoint(monkeypatch):
    captured = {}

    def _fake_cli_api(method, path, payload=None, *a, **k):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = payload
        return {"amount": 100, "from": "PEN", "to": "USD", "converted": 27.03, "rate": 0.27027}

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(amount=100.0, from_currency="pen", to_currency="usd", json=False)
    market_cli.cmd_exchange(args)

    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/utils/exchange"
    assert captured["payload"] == {"amount": 100.0, "from": "PEN", "to": "USD"}


def test_cmd_exchange_handles_missing_converted(monkeypatch):
    _patch_common(monkeypatch, {"error": "unsupported currency"})
    args = argparse.Namespace(amount=100.0, from_currency="PEN", to_currency="XYZ", json=False)
    market_cli.cmd_exchange(args)  # should not raise


def test_cmd_stock_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "product_id": "543365", "store": "metro", "stock": 99999,
        "name": "Leche Fresca Piamonte", "store_name": "Metro",
    })
    args = argparse.Namespace(product_id="543365", store="metro", json=False)
    market_cli.cmd_stock(args)
    assert captured["path"] == "/products/stock/543365?store=metro"


def test_cmd_stock_handles_missing_stock(monkeypatch):
    _patch_common(monkeypatch, {"product_id": "x", "store": "metro", "stock": None, "message": "No data"})
    args = argparse.Namespace(product_id="x", store="metro", json=False)
    market_cli.cmd_stock(args)  # should not raise


def test_cmd_ecosystem_radar_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {"launches": [], "disclaimer": "Ecosystem signal only; not price data."},
        "meta": {},
    })
    args = argparse.Namespace(topic="food", days=7, limit=20, json=False)
    market_cli.cmd_ecosystem_radar(args)
    assert captured["path"] == "/v1/ecosystem/launches?topic=food&days=7&limit=20"


def test_cmd_price_alerts_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {"alerts": [], "message": "0 alert(s) above 5.0% threshold."})
    args = argparse.Namespace(product="leche", store=None, threshold_pct=5.0, limit=10, json=False)
    market_cli.cmd_price_alerts(args)
    assert captured["path"] == "/v1/intel/alerts?product=leche&store=&threshold_pct=5.0&limit=10"


def test_cmd_price_alerts_escapes_special_characters(monkeypatch):
    captured = _patch_common(monkeypatch, {"alerts": [], "message": "none"})
    args = argparse.Namespace(product="leche & queso", store=None, threshold_pct=5.0, limit=10, json=False)
    market_cli.cmd_price_alerts(args)
    assert "product=leche%20%26%20queso" in captured["path"]


def test_cmd_price_alerts_renders_direction_and_prices(monkeypatch):
    _patch_common(monkeypatch, {
        "alerts": [
            {"product": "Leche Gloria", "store": "metro", "store_name": "Metro", "currency": "PEN",
             "first_price": 3.9, "last_price": 4.7, "delta_pct": 20.5, "direction": "up"},
        ],
        "message": "1 alert(s)",
    })
    args = argparse.Namespace(product="leche", store=None, threshold_pct=5.0, limit=10, json=False)
    market_cli.cmd_price_alerts(args)  # should not raise


def test_cmd_brands_json_mode_prints_raw_payload(monkeypatch):
    response = {"brands": [{"brand": "Gloria", "count": 10}]}
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: response)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())

    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(country=None, line=None, limit=20, json=True)
    market_cli.cmd_brands(args)

    assert len(printed) == 1
    assert json.loads(printed[0]) == response
