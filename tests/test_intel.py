"""Tests for routers/intel.py — indicators, scores, inflation, alerts, enrichment, refresh."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, db_save_user, db_set_subscription
from market_server import app, hash_password

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


@pytest.fixture()
def pro_user(monkeypatch):
    """Elevate the admin user to Pro tier for pro-gated endpoints."""
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "pro")
    yield
    db_set_subscription("admin", "free")


# ── GET /v1/intel/indicators ──────────────────────────────────────────────────

def test_indicators_requires_auth():
    r = client.get("/v1/intel/indicators")
    assert r.status_code == 401


def test_indicators_returns_catalog():
    r = client.get("/v1/intel/indicators", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "indicators" in data
    assert "total" in data
    assert isinstance(data["indicators"], list)
    assert data["total"] >= 0


# ── GET /v1/intel/indicators/{key} ───────────────────────────────────────────

def test_indicator_detail_requires_auth():
    r = client.get("/v1/intel/indicators/moat_freshness")
    assert r.status_code == 401


def test_indicator_detail_unknown_key_returns_404():
    r = client.get("/v1/intel/indicators/no_such_indicator_xyz", headers=_AUTH)
    assert r.status_code == 404


def test_indicator_detail_returns_structure():
    # Get a valid key from the catalog first
    catalog_r = client.get("/v1/intel/indicators", headers=_AUTH)
    catalog = catalog_r.json()["indicators"]
    if not catalog:
        pytest.skip("Empty catalog — no keys to test")
    key = catalog[0]["key"]
    r = client.get(f"/v1/intel/indicators/{key}", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "indicator" in data
    assert "latest_value" in data


# ── GET /v1/intel/scores ──────────────────────────────────────────────────────

def test_scores_requires_auth():
    r = client.get("/v1/intel/scores")
    assert r.status_code == 401


def test_scores_returns_200():
    r = client.get("/v1/intel/scores", headers=_AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), (dict, list))


# ── GET /v1/intel/inflation ────────────────────────────────────────────────────

def test_inflation_requires_auth():
    r = client.get("/v1/intel/inflation")
    assert r.status_code == 401


def test_inflation_returns_structure():
    r = client.get("/v1/intel/inflation", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "avg_inflation_pct" in data
    assert "avg_rpv_7d_pct" in data
    assert "days" in data
    assert data.get("metric") == "shelf_price_momentum_7d"


def test_inflation_unknown_country_returns_empty():
    r = client.get("/v1/intel/inflation?country=ZZ", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["avg_inflation_pct"] == 0


# ── GET /v1/intel/alerts ──────────────────────────────────────────────────────

def test_alerts_requires_auth():
    r = client.get("/v1/intel/alerts?product=leche")
    assert r.status_code == 401


def test_alerts_missing_product_returns_422():
    r = client.get("/v1/intel/alerts", headers=_AUTH)
    assert r.status_code == 422


def test_alerts_returns_structure():
    r = client.get("/v1/intel/alerts?product=leche", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "product" in data
    assert "results" in data
    assert data["product"] == "leche"


def test_alerts_with_store_filter():
    r = client.get("/v1/intel/alerts?product=arroz&store=wong", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["store"] == "wong"


# ── GET /v1/intel/brief ────────────────────────────────────────────────────────

def test_brief_requires_auth():
    r = client.get("/v1/intel/brief")
    assert r.status_code == 401


def test_brief_returns_200():
    r = client.get("/v1/intel/brief", headers=_AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


def test_brief_with_params():
    r = client.get("/v1/intel/brief?country=PE&line=supermercados&days=7", headers=_AUTH)
    assert r.status_code == 200


# ── GET /v1/intel/enrichment ──────────────────────────────────────────────────

def test_enrichment_requires_auth():
    r = client.get("/v1/intel/enrichment")
    assert r.status_code == 401


def test_enrichment_returns_structure():
    r = client.get("/v1/intel/enrichment", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "indicators" in data
    assert "total" in data
    assert "sources" in data


# ── GET /v1/intel/enrichment/subcategories ────────────────────────────────────

def test_enrichment_subcategories_requires_auth():
    r = client.get("/v1/intel/enrichment/subcategories")
    assert r.status_code == 401


def test_enrichment_subcategories_returns_structure():
    r = client.get("/v1/intel/enrichment/subcategories", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "subcategories" in data
    assert "total" in data
    assert "country" in data


# ── POST /v1/intel/refresh ────────────────────────────────────────────────────

def test_refresh_requires_pro(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "free")
    r = client.post("/v1/intel/refresh", headers=_AUTH)
    assert r.status_code == 403


def test_refresh_with_pro_returns_ok(pro_user):
    r = client.post("/v1/intel/refresh", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "internal_written" in data


def test_refresh_with_country_scope(pro_user):
    r = client.post("/v1/intel/refresh?country=PE", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["country"] == "PE"


# ── POST /v1/intel/enrichment/refresh ────────────────────────────────────────

def test_enrichment_refresh_requires_pro(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "free")
    r = client.post("/v1/intel/enrichment/refresh", headers=_AUTH)
    assert r.status_code == 403


def test_enrichment_refresh_with_pro_returns_ok(pro_user):
    r = client.post("/v1/intel/enrichment/refresh?country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "enrichment_written" in data
