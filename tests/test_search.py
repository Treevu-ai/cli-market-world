"""Tests for routers/search.py — product search, stock, delivery, barcode, enrich."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

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


# ── POST /products/search ─────────────────────────────────────────────────────

def test_search_requires_auth():
    r = client.post("/products/search", json={"query": "leche"})
    assert r.status_code == 401


def test_search_empty_query_returns_422():
    r = client.post("/products/search", json={"query": ""}, headers=_AUTH)
    assert r.status_code == 422


def test_search_returns_query_and_results_keys():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post("/products/search", json={"query": "leche"}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "query" in data
    assert "results" in data
    assert "total" in data
    assert data["query"] == "leche"
    assert data["total"] == 0


def test_search_with_store_filter():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post(
            "/products/search",
            json={"query": "arroz", "store": "wong", "country": "PE"},
            headers=_AUTH,
        )
    assert r.status_code == 200


def test_search_errors_in_partial_response():
    # live=true exercises the per-store scrape path (_parallel_fetch_stores);
    # the default path now reads price_snapshots and has no per-store errors.
    errors = [{"store": "somestore", "error": "timeout"}]
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, errors))):
        r = client.post("/products/search", json={"query": "aceite", "live": True}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data.get("partial") is True
    assert len(data["errors"]) >= 1


def test_search_query_sanitizes_special_chars():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post(
            "/products/search",
            json={"query": "<script>alert(1)</script>leche"},
            headers=_AUTH,
        )
    assert r.status_code == 200
    assert "<script>" not in r.json()["query"]


# ── POST /products/compare ────────────────────────────────────────────────────

def test_compare_no_auth_returns_401():
    r = client.post("/products/compare", json={"query": "leche"})
    assert r.status_code == 401


def test_compare_returns_comparison_structure():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post("/products/compare", json={"query": "arroz"}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "comparison" in data
    assert "stores_compared" in data


# ── GET /products/stock/{product_id} ─────────────────────────────────────────

def test_stock_requires_auth():
    r = client.get("/products/stock/prod-123?store=wong")
    assert r.status_code == 401


def test_stock_not_found_returns_no_data():
    r = client.get("/products/stock/no-such-product?store=wong", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["stock"] is None
    assert "message" in data


def test_stock_found_returns_stock_info():
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, stock, queried_at)
           VALUES ('test-prod-1', 'wong', 'Wong', 'Leche Gloria 1L', 3.5, 'PEN', 'supermercados', 'Supermercados', 12, datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/products/stock/test-prod-1?store=wong", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["product_id"] == "test-prod-1"
    assert data["store"] == "wong"
    assert data["stock"] == 12
    assert data["name"] == "Leche Gloria 1L"


# ── GET /products/delivery/{product_id} ──────────────────────────────────────

def test_delivery_no_auth_required():
    r = client.get("/products/delivery/prod-123?store=wong")
    assert r.status_code == 200


def test_delivery_returns_expected_fields():
    r = client.get("/products/delivery/prod-abc?store=plaza_vea")
    assert r.status_code == 200
    data = r.json()
    assert data["product_id"] == "prod-abc"
    assert data["store"] == "plaza_vea"
    assert "delivery_available" in data
    assert "estimated_days" in data


def test_delivery_unknown_store_still_returns_200():
    r = client.get("/products/delivery/prod-xyz?store=unknown_store_xyz")
    assert r.status_code == 200
    data = r.json()
    assert data["store"] == "unknown_store_xyz"


# ── GET /products/barcode/{code} ──────────────────────────────────────────────

def test_barcode_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "product": {
            "product_name": "Leche Entera",
            "brands": "Gloria",
            "nutriscore_grade": "b",
            "categories": "Dairy",
        }
    }
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/barcode/7501234567890")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Leche Entera"
    assert data["brand"] == "Gloria"
    assert data["nutriscore"] == "B"
    assert data["code"] == "7501234567890"


def test_barcode_not_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/barcode/0000000000000")
    assert r.status_code == 200
    assert "error" in r.json()


# ── GET /products/enrich ──────────────────────────────────────────────────────

def test_enrich_returns_results():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "products": [
            {"product_name": "Arroz", "brands": "Costeño", "nutriscore_grade": "a", "code": "123"},
        ],
        "count": 1,
    }
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/enrich?query=arroz&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["results"][0]["name"] == "Arroz"


def test_enrich_upstream_failure_returns_empty():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/enrich?query=xyz")
    assert r.status_code == 200
    assert r.json()["results"] == []
    assert r.json()["total"] == 0


# ── GET /categories/{store} ───────────────────────────────────────────────────

def test_categories_unknown_store_returns_404():
    r = client.get("/categories/no_such_store_xyz")
    assert r.status_code == 404
