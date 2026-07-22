"""Tests for GET /v1/retailers/{store_id}/dashboard (Growth-tier price-vs-competitors view)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db
from market_server import app

from backend_interface import invalidate_credential_cache

ensure_db_initialized()
client = TestClient(app)

_STORE = "test_gd_store"
_PEER = "test_gd_peer"
_TOKEN = "test-growth-dashboard-token-abc123"


@pytest.fixture
def growth_dashboard_fixture():
    db = get_db()
    for sid in (_STORE, _PEER):
        db.execute("DELETE FROM price_snapshots WHERE store = ?", (sid,))
        db.execute("DELETE FROM store_credentials WHERE store_id = ?", (sid,))
    db.execute(
        "INSERT INTO store_credentials "
        "(store_id, platform, store_name, country, line, active, is_growth, growth_dashboard_token) "
        "VALUES (?, 'woocommerce', 'Test GD Store', 'PE', 'electro', 1, 1, ?)",
        (_STORE, _TOKEN),
    )
    db.execute(
        "INSERT INTO store_credentials "
        "(store_id, platform, store_name, country, line, active, wc_consumer_key, wc_consumer_secret) "
        "VALUES (?, 'woocommerce', 'Test GD Peer', 'PE', 'electro', 1, 'ck_test', 'cs_test')",
        (_PEER,),
    )
    # Same product: our store more expensive than the peer.
    db.execute(
        "INSERT INTO price_snapshots (product_id, store, name, price, currency, queried_at) "
        "VALUES ('p1', ?, 'Testgd Widget', 100, 'PEN', datetime('now'))",
        (_STORE,),
    )
    db.execute(
        "INSERT INTO price_snapshots (product_id, store, name, price, currency, queried_at) "
        "VALUES ('p2', ?, 'Testgd Widget', 80, 'PEN', datetime('now'))",
        (_PEER,),
    )
    db.commit()
    db.close()
    invalidate_credential_cache()
    yield
    db = get_db()
    for sid in (_STORE, _PEER):
        db.execute("DELETE FROM price_snapshots WHERE store = ?", (sid,))
        db.execute("DELETE FROM store_credentials WHERE store_id = ?", (sid,))
    db.commit()
    db.close()
    invalidate_credential_cache()


def test_dashboard_requires_growth_flag():
    r = client.get("/v1/retailers/some_non_growth_store/dashboard?token=x")
    assert r.status_code == 404


def test_dashboard_wrong_token(growth_dashboard_fixture):
    r = client.get(f"/v1/retailers/{_STORE}/dashboard?token=wrong-token")
    assert r.status_code == 403


def test_dashboard_missing_token(growth_dashboard_fixture):
    r = client.get(f"/v1/retailers/{_STORE}/dashboard")
    assert r.status_code == 422  # token is a required query param


def test_dashboard_happy_path(growth_dashboard_fixture):
    r = client.get(f"/v1/retailers/{_STORE}/dashboard?token={_TOKEN}")
    assert r.status_code == 200
    data = r.json()
    assert data["store_id"] == _STORE
    assert data["products_compared"] == 1
    assert data["products_you_are_cheapest"] == 0
    product = data["products"][0]
    assert product["your_price"] == 100
    assert product["cheapest_competitor_price"] == 80
    assert product["you_are_cheapest"] is False
    assert product["delta_pct"] == 25.0
