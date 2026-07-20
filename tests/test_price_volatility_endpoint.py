"""Tests for GET /v1/intel/price-volatility (routers/intel.py)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, db_save_user, db_set_subscription
from market_server import app, hash_password

import server_deps
import routers.intel as intel_router

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "pro")
    yield
    db_set_subscription("admin", "free")


def _fake_report(**kwargs):
    return {
        "generated_at": "2026-07-19T00:00:00+00:00",
        "country": kwargs.get("country", "PE"),
        "moat": {"total_prices": 1000, "store_count": 5},
        "analysis": {
            "products_with_multi_store_prices": 12,
            "products_high_spread_20pct_plus": 3,
            "products_with_outlier_retailers": 2,
            "avg_cv_pct": 8.4,
            "avg_spread_pct": 15.2,
        },
        "top_volatile": [{"name": "Arroz", "cv_pct": 22.1, "spread_pct": 30.0, "n_stores": 4}],
        "category_volatility": {"abarrotes": {"products": 5, "avg_cv_pct": 10.1, "avg_spread_pct": 18.0}},
        "retailer_stats": {"tottus": {"products_indexed": 10, "consistency_score": 90.0}},
        "data_available": True,
    }


def test_price_volatility_requires_auth():
    r = client.get("/v1/intel/price-volatility")
    assert r.status_code == 401


def test_price_volatility_requires_pro():
    db_set_subscription("admin", "starter")
    try:
        r = client.get("/v1/intel/price-volatility", headers=_AUTH)
        assert r.status_code == 403
        assert "Pro" in r.json()["detail"]
    finally:
        db_set_subscription("admin", "pro")


def test_price_volatility_returns_structure(monkeypatch):
    monkeypatch.setattr(intel_router, "build_price_volatility_report", _fake_report)
    r = client.get("/v1/intel/price-volatility", headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    for key in ("analysis", "top_volatile", "category_volatility", "retailer_stats", "data_available"):
        assert key in body
    assert body["data_available"] is True


def test_price_volatility_passes_query_params(monkeypatch):
    captured = {}

    def spy(**kwargs):
        captured.update(kwargs)
        return _fake_report(**kwargs)

    monkeypatch.setattr(intel_router, "build_price_volatility_report", spy)
    r = client.get("/v1/intel/price-volatility?country=CO&top=5", headers=_AUTH)
    assert r.status_code == 200
    assert captured == {"country": "CO", "top_n": 5}


def test_price_volatility_empty_country_returns_no_data(monkeypatch):
    def empty_report(**kwargs):
        return {
            "generated_at": "2026-07-19T00:00:00+00:00",
            "country": kwargs.get("country", "PE"),
            "moat": {"total_prices": 0, "store_count": 0},
            "analysis": {
                "products_with_multi_store_prices": 0,
                "products_high_spread_20pct_plus": 0,
                "products_with_outlier_retailers": 0,
                "avg_cv_pct": None,
                "avg_spread_pct": None,
            },
            "top_volatile": [],
            "category_volatility": {},
            "retailer_stats": {},
            "data_available": False,
        }

    monkeypatch.setattr(intel_router, "build_price_volatility_report", empty_report)
    r = client.get("/v1/intel/price-volatility?country=ZZ", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["data_available"] is False


def test_price_volatility_top_param_bounds():
    r = client.get("/v1/intel/price-volatility?top=0", headers=_AUTH)
    assert r.status_code == 422
    r = client.get("/v1/intel/price-volatility?top=101", headers=_AUTH)
    assert r.status_code == 422
