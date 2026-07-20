"""Regression tests for ops/price_volatility_report.py's HTTP contract with the real
backend endpoints. build_report() silently degraded to data_available: False in
production because it was written against a stale/imagined API shape — these tests
pin the real request/response contracts of GET /analytics/trending and
POST /v1/basket/compare (routers/analytics.py, market_core/market_basket.py)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ops.price_volatility_report import (
    _extract_prices_from_basket,
    _fetch_basket,
    _fetch_trending,
)


def _json_response(payload):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = payload
    return resp


def test_fetch_trending_calls_analytics_trending_endpoint():
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        return _json_response({"trending": [], "total": 0})

    with patch("ops.price_volatility_report.httpx.get", side_effect=fake_get):
        _fetch_trending(country="PE", limit=50)

    assert "/analytics/trending" in captured["url"]
    assert "/products/trending" not in captured["url"]
    assert captured["params"] == {"country": "PE", "limit": 50}


def test_fetch_trending_parses_real_response_shape():
    """GET /analytics/trending returns {"trending": [...], "total": N} — not
    "products" or "items". Rows carry "name", not "product_id"/"id"."""
    payload = {
        "trending": [
            {"name": "Arroz Costeño 750g", "store_name": "Wong", "price": 5.5, "change_pct": 3.2, "trend": "up"},
        ],
        "total": 1,
    }
    with patch("ops.price_volatility_report.httpx.get", return_value=_json_response(payload)):
        result = _fetch_trending(country="PE", limit=50)

    assert result == payload["trending"]


def test_fetch_basket_sends_items_with_name_not_product_ids():
    """POST /v1/basket/compare expects {"items": [{"name": ...}]} — the endpoint
    resolves items by name against price_snapshots; it has no concept of a
    pre-existing "product id" supplied by the caller."""
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["body"] = json
        return _json_response({"items_searched": 1, "items_found": 1, "stores": []})

    with patch("ops.price_volatility_report.httpx.post", side_effect=fake_post):
        _fetch_basket(["Arroz Costeño 750g"], country="PE")

    assert captured["body"]["items"] == [{"name": "Arroz Costeño 750g"}]
    assert "products" not in captured["body"]


def test_extract_prices_from_basket_inverts_store_grouped_response():
    """build_basket_compare() groups its response by STORE
    (stores: [{store_name, breakdown: [{item, unit_price}]}]), not by item —
    this must invert that into a per-item prices_by_store dict."""
    basket = {
        "items_searched": 1,
        "items_found": 1,
        "stores": [
            {
                "store": "wong",
                "store_name": "Wong",
                "total": 5.5,
                "breakdown": [
                    {"item": "arroz", "qty": 1, "unit_price": 5.5, "product_id": "p1"},
                ],
            },
            {
                "store": "metro",
                "store_name": "Metro",
                "total": 6.9,
                "breakdown": [
                    {"item": "arroz", "qty": 1, "unit_price": 6.9, "product_id": "p2"},
                ],
            },
        ],
    }

    result = _extract_prices_from_basket(basket)

    assert len(result) == 1
    row = result[0]
    assert row["name"] == "arroz"
    assert row["prices_by_store"] == {"Wong": 5.5, "Metro": 6.9}
    assert row["n_stores"] == 2
    assert row["min_price"] == 5.5
    assert row["max_price"] == 6.9


def test_extract_prices_from_basket_drops_items_found_at_only_one_store():
    basket = {
        "stores": [
            {"store_name": "Wong", "breakdown": [{"item": "arroz", "unit_price": 5.5}]},
        ],
    }
    assert _extract_prices_from_basket(basket) == []
