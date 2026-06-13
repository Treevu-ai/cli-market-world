"""Tests for routers/analytics.py — price history, stats, trending, brands, indicators."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db
from market_server import app

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


# ── GET /analytics/price-history ─────────────────────────────────────────────

def test_price_history_requires_auth():
    r = client.get("/analytics/price-history")
    assert r.status_code == 401


def test_price_history_returns_structure():
    r = client.get("/analytics/price-history", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "snapshots" in data
    assert isinstance(data["snapshots"], list)


def test_price_history_with_store_filter():
    r = client.get("/analytics/price-history?store=wong", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "snapshots" in data


def test_price_history_with_product_filter():
    r = client.get("/analytics/price-history?product_id=prod-xyz", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_price_history_returns_inserted_row():
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, queried_at)
           VALUES ('hist-prod-1', 'metro', 'Metro', 'Arroz Costeño', 5.9, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/price-history?product_id=hist-prod-1", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert data["snapshots"][0]["product_id"] == "hist-prod-1"


def test_price_history_limit_param():
    r = client.get("/analytics/price-history?limit=1", headers=_AUTH)
    assert r.status_code == 200
    assert len(r.json()["snapshots"]) <= 1


# ── GET /analytics/stats ──────────────────────────────────────────────────────

def test_stats_requires_auth():
    r = client.get("/analytics/stats")
    assert r.status_code == 401


def test_stats_returns_expected_keys():
    r = client.get("/analytics/stats", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "total_price_snapshots" in data
    assert "total_search_queries" in data
    assert "unique_stores_tracked" in data
    assert "unique_products_tracked" in data
    assert "latest_snapshot_at" in data


def test_stats_counts_are_non_negative():
    r = client.get("/analytics/stats", headers=_AUTH)
    data = r.json()
    assert data["total_price_snapshots"] >= 0
    assert data["unique_stores_tracked"] >= 0


# ── GET /analytics/trending ───────────────────────────────────────────────────

def test_trending_requires_auth():
    r = client.get("/analytics/trending")
    assert r.status_code == 401


def test_trending_returns_structure():
    r = client.get("/analytics/trending", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "trending" in data
    assert "total" in data
    assert isinstance(data["trending"], list)


def test_trending_with_line_filter():
    r = client.get("/analytics/trending?line=supermercados&limit=5", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "trending" in data


# ── GET /analytics/brands ─────────────────────────────────────────────────────

def test_brands_requires_auth():
    r = client.get("/analytics/brands")
    assert r.status_code == 401


def test_brands_returns_structure():
    r = client.get("/analytics/brands", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "brands" in data
    assert "total" in data
    assert isinstance(data["brands"], list)


def test_brands_with_line_filter():
    r = client.get("/analytics/brands?line=supermercados&limit=5", headers=_AUTH)
    assert r.status_code == 200


# ── GET /analytics/indicators ─────────────────────────────────────────────────

def test_indicators_requires_auth():
    r = client.get("/analytics/indicators")
    assert r.status_code == 401


def test_indicators_returns_structure():
    r = client.get("/analytics/indicators", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "catalog_size" in data
    assert "indicators" in data
    assert isinstance(data["indicators"], list)


def test_indicators_with_country_filter():
    r = client.get("/analytics/indicators?country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["country"] == "PE"
