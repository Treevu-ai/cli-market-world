"""Regression test for cli-market-backend#127 (S8/S22): procure resolved
"arroz" (rice) to a kitchen utensil ("Cuchara Para Arroz") because
/products/search results were ranked by price with no category filter, and
auto-added the wrong match to the cart with no confirmation step."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


def test_procure_prefers_food_match_over_cheaper_utensil(monkeypatch):
    def fake_api(method, path, params=None):
        if path == "/products/search":
            if params["query"] == "arroz":
                return {
                    "results": [
                        {"name": "Cuchara Para Arroz Brinox 2050/318", "price": 1599.0, "currency": "ARS", "store": "coppel_ar", "store_name": "Coppel AR", "id": "1", "line": "hogar"},
                        {"name": "Arroz Parboil Gallo Oro 1kg", "price": 3200.0, "currency": "ARS", "store": "vea_ar", "store_name": "Vea AR", "id": "2", "line": "supermercados"},
                    ]
                }
            return {"results": []}
        return {}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli, "input", lambda *_a: "n", raising=False)

    captured = {}

    def fake_print_json(*a, **k):
        pass

    args = argparse.Namespace(items_list="arroz", budget=10000, country="AR", json=True)
    monkeypatch.setattr(market_cli.console, "print", lambda payload: captured.__setitem__("out", payload))
    market_cli.cmd_procure(args)

    import json as _json
    result = _json.loads(captured["out"])
    assert result["items"][0]["product"] == "Arroz Parboil Gallo Oro 1kg"
    assert result["items"][0]["uncertain_match"] is False


def test_procure_flags_uncertain_match_when_no_food_candidate(monkeypatch):
    def fake_api(method, path, params=None):
        if path == "/products/search":
            return {
                "results": [
                    {"name": "Cuchara Para Arroz Brinox 2050/318", "price": 1599.0, "currency": "ARS", "store": "coppel_ar", "store_name": "Coppel AR", "id": "1", "line": "hogar"},
                ]
            }
        return {}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    captured = {}
    monkeypatch.setattr(market_cli.console, "print", lambda payload: captured.__setitem__("out", payload))

    args = argparse.Namespace(items_list="arroz", budget=10000, country="AR", json=True)
    market_cli.cmd_procure(args)

    import json as _json
    result = _json.loads(captured["out"])
    assert result["items"][0]["uncertain_match"] is True


def test_procure_requires_confirmation_before_cart_add(monkeypatch):
    """Regression for S22: procure used to add to cart with no review step."""
    cart_calls = []

    def fake_api(method, path, params=None):
        if path == "/products/search":
            return {"results": [{"name": "Leche Entera 1L", "price": 100.0, "currency": "PEN", "store": "wong", "store_name": "Wong", "id": "1", "line": "supermercados"}]}
        if path == "/cart/add":
            cart_calls.append(params)
            return {}
        return {}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli, "get_token", lambda: "fake-token")
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr("builtins.input", lambda *_a: "n")

    args = argparse.Namespace(items_list="leche", budget=1000, country="PE", json=False)
    market_cli.cmd_procure(args)

    assert cart_calls == [], "cart/add must not be called when the user declines confirmation"
