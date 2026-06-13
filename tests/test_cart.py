"""Tests for routers/cart.py — add, view, update, remove cart items."""

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

_ITEM = {
    "product_id": "cart-prod-1",
    "name": "Leche Gloria 1L",
    "price": 3.5,
    "store": "wong",
    "quantity": 2,
    "url": "https://example.com/leche",
}


@pytest.fixture(autouse=True)
def clean_cart(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db = get_db()
    try:
        db.execute("DELETE FROM carts")
        db.commit()
    except Exception:
        pass
    db.close()


# ── POST /cart/add ────────────────────────────────────────────────────────────

def test_cart_add_requires_auth():
    r = client.post("/cart/add", json=_ITEM)
    assert r.status_code == 401


def test_cart_add_returns_structure():
    r = client.post("/cart/add", json=_ITEM, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "cart" in data
    assert "total" in data
    assert "items" in data
    assert "cart_id" in data


def test_cart_add_increments_count():
    r = client.post("/cart/add", json=_ITEM, headers=_AUTH)
    assert r.json()["items"] >= 1


def test_cart_add_total_is_correct():
    r = client.post("/cart/add", json=_ITEM, headers=_AUTH)
    data = r.json()
    # total = price * quantity
    assert data["total"] >= _ITEM["price"] * _ITEM["quantity"]


def test_cart_add_unknown_store_still_works():
    item = {**_ITEM, "store": "unknown_store_xyz", "product_id": "cart-prod-unk"}
    r = client.post("/cart/add", json=item, headers=_AUTH)
    assert r.status_code == 200


# ── GET /cart ─────────────────────────────────────────────────────────────────

def test_cart_view_requires_auth():
    r = client.get("/cart")
    assert r.status_code == 401


def test_cart_view_empty():
    r = client.get("/cart", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "username" in data
    assert "cart" in data
    assert "total" in data
    assert "items" in data


def test_cart_view_after_add():
    client.post("/cart/add", json=_ITEM, headers=_AUTH)
    r = client.get("/cart", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["items"] >= 1
    assert data["total"] > 0


# ── PUT /cart/update ──────────────────────────────────────────────────────────

def test_cart_update_requires_auth():
    r = client.put("/cart/update", json={"product_id": "x", "quantity": 1})
    assert r.status_code == 401


def test_cart_update_not_found_returns_404():
    r = client.put("/cart/update", json={"product_id": "no-such-id", "quantity": 1}, headers=_AUTH)
    assert r.status_code == 404


def test_cart_update_quantity():
    add_r = client.post("/cart/add", json=_ITEM, headers=_AUTH)
    assert add_r.status_code == 200
    # Use the product_id to update
    r = client.put(
        "/cart/update",
        json={"product_id": _ITEM["product_id"], "quantity": 5},
        headers=_AUTH,
    )
    assert r.status_code == 200
    cart = r.json()["cart"]
    updated = next((i for i in cart if i["product_id"] == _ITEM["product_id"]), None)
    assert updated is not None
    assert int(updated["quantity"]) == 5


# ── DELETE /cart/{product_id} ─────────────────────────────────────────────────

def test_cart_remove_requires_auth():
    r = client.delete("/cart/some-product")
    assert r.status_code == 401


def test_cart_remove_not_found_returns_404():
    r = client.delete("/cart/no-such-product", headers=_AUTH)
    assert r.status_code == 404


def test_cart_remove_success():
    client.post("/cart/add", json=_ITEM, headers=_AUTH)
    before_count = client.get("/cart", headers=_AUTH).json()["items"]
    r = client.delete(f"/cart/{_ITEM['product_id']}", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "cart" in data
    # One item was removed
    assert data["items"] < before_count


def test_cart_remove_reduces_total():
    client.post("/cart/add", json=_ITEM, headers=_AUTH)
    before = client.get("/cart", headers=_AUTH).json()["total"]
    client.delete(f"/cart/{_ITEM['product_id']}", headers=_AUTH)
    after = client.get("/cart", headers=_AUTH).json()["total"]
    assert after < before
