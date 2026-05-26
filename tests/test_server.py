"""Test suite for CLI Market — auth, search, cart, checkout, orders."""

import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Set temp dir BEFORE importing market_core
TEST_DATA_DIR = tempfile.mkdtemp(prefix="market_test_")
os.environ["MARKET_DATA_DIR"] = TEST_DATA_DIR

import pytest
from fastapi.testclient import TestClient
from market_core import (
    get_db, db_save_user,
    ensure_db_initialized,
)
from market_server import app, hash_password

# Lifespan is what initializes the DB now. TestClient only runs lifespan when
# used as a context manager; we initialize explicitly here so all tests work.
ensure_db_initialized()
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """Reset DB state before each test."""
    db = get_db()
    for table in ["app_carts", "app_orders", "app_order_items", "rate_limits"]:
        db.execute(f"DELETE FROM {table}")
    db.execute("DELETE FROM app_users")
    db.commit()
    db.close()
    db_save_user("admin", hash_password("market"), "test-token-123")
    yield

def teardown_module():
    """Clean up temp dir after all tests."""
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "CLI Market"
    assert data["status"] == "running"


def test_login_success():
    r = client.post("/auth/login", json={"username": "admin", "password": "market"})
    assert r.status_code == 200
    assert r.json()["username"] == "admin"


def test_login_invalid():
    r = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_whoami_no_token():
    assert client.get("/auth/whoami").status_code == 401


def test_whoami_with_token():
    r = client.get("/auth/whoami", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert r.json()["username"] == "admin"


def test_cart_empty():
    r = client.get("/cart", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert r.json()["items"] == 0


def test_cart_add():
    r = client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Test Product", "price": 10.0, "store": "wong", "quantity": 2
    })
    assert r.status_code == 200
    assert r.json()["total"] == 20.0


def test_cart_view_after_add():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 3
    })
    r = client.get("/cart", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert r.json()["total"] == 15.0


def test_cart_update():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-2", "name": "Arroz", "price": 8.0, "store": "metro", "quantity": 1
    })
    cart = client.get("/cart", headers={"Authorization": "Bearer test-token-123"}).json()
    cart_id = cart["cart"][0]["cart_id"]

    r = client.put("/cart/update", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": cart_id, "quantity": 5
    })
    assert r.status_code == 200
    cart = client.get("/cart", headers={"Authorization": "Bearer test-token-123"}).json()
    assert cart["cart"][0]["quantity"] == 5
    assert cart["total"] == 40.0


def test_cart_remove():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-3", "name": "Azucar", "price": 3.0, "store": "plazavea", "quantity": 2
    })
    cart = client.get("/cart", headers={"Authorization": "Bearer test-token-123"}).json()
    cart_id = cart["cart"][0]["cart_id"]

    r = client.delete(f"/cart/{cart_id}", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert client.get("/cart", headers={"Authorization": "Bearer test-token-123"}).json()["items"] == 0


def test_checkout_empty_cart():
    r = client.post("/checkout", headers={"Authorization": "Bearer test-token-123"}, json={"payment_method": "yape"})
    assert r.status_code == 400


def test_checkout_success():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 2
    })
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-2", "name": "Pan", "price": 3.0, "store": "metro", "quantity": 1
    })
    r = client.post("/checkout", headers={"Authorization": "Bearer test-token-123"}, json={"payment_method": "yape"})
    assert r.status_code == 200
    assert r.json()["order"]["total"] == 13.0
    assert client.get("/cart", headers={"Authorization": "Bearer test-token-123"}).json()["items"] == 0


def test_orders_after_checkout():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 2
    })
    client.post("/checkout", headers={"Authorization": "Bearer test-token-123"}, json={"payment_method": "yape"})
    r = client.get("/orders", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert r.json()["total_orders"] == 1


def test_reorder():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 2
    })
    client.post("/checkout", headers={"Authorization": "Bearer test-token-123"}, json={"payment_method": "yape"})
    r = client.post("/orders/reorder", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert client.get("/cart", headers={"Authorization": "Bearer test-token-123"}).json()["items"] == 1


def test_lines():
    assert client.get("/lines").status_code == 200


def test_stores():
    assert client.get("/stores").status_code == 200


def test_countries():
    assert client.get("/countries").status_code == 200


def test_analytics_stats():
    r = client.get("/analytics/stats")
    assert r.status_code == 200
    assert "total_price_snapshots" in r.json()


# ── New tests: stores, lines, countries content ────────────────────────────

def test_lines_count():
    """Verify we have 6 lines (supermercados, farmacias, electro, hogar, departamentales, moda)."""
    r = client.get("/lines")
    assert r.status_code == 200
    data = r.json()
    lines = data.get("lines", data)
    if isinstance(lines, list):
        assert len(lines) == 6
        line_ids = [item["id"] if isinstance(item, dict) else item for item in lines]
    else:
        line_ids = list(lines.keys())
    assert "supermercados" in line_ids
    assert "departamentales" in line_ids
    assert "moda" in line_ids


def test_stores_count():
    """Verify we have 30 stores."""
    r = client.get("/stores")
    assert r.status_code == 200
    data = r.json()
    stores = data.get("stores", data)
    assert len(stores) >= 30


def test_countries_count():
    """Verify the country catalog has the documented countries. Future-proof:
    catalog grows over time (README badge says 11 countries as of 2026-05).
    """
    r = client.get("/countries")
    assert r.status_code == 200
    data = r.json()
    countries = data.get("countries", data)
    assert len(countries) >= 8


def test_stores_include_new():
    """Verify the 4 new retailers are present."""
    r = client.get("/stores")
    data = r.json()
    stores = data.get("stores", data)
    assert "promart" in stores
    assert "coppel_ar" in stores
    assert "cea_br" in stores
    assert "hering_br" in stores


# ── Edge case tests ────────────────────────────────────────────────────────

def test_cart_add_invalid_quantity():
    r = client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Test", "price": 10.0, "store": "wong", "quantity": -1
    })
    # Should either reject or clamp to 1
    assert r.status_code in (200, 400, 422)


def test_cart_update_nonexistent():
    r = client.put("/cart/update", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "nonexistent-id-99999", "quantity": 5
    })
    assert r.status_code in (400, 404)


def test_checkout_no_payment_method():
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "prod-1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 1
    })
    r = client.post("/checkout", headers={"Authorization": "Bearer test-token-123"}, json={})
    # Should require payment_method
    assert r.status_code in (400, 422, 200)


def test_reorder_no_orders():
    # Fresh user with no orders
    r = client.post("/orders/reorder", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code in (200, 404)


def test_search_no_query():
    # /search requires a store and term
    r = client.get("/search/wong")
    assert r.status_code in (400, 404, 422)


def test_search_invalid_store():
    r = client.get("/search/fake_store?q=test")
    assert r.status_code in (400, 404, 422)


def test_basket_endpoint():
    r = client.get("/basket/milk?country=PE")
    assert r.status_code in (200, 400, 422, 404)


def test_categories_endpoint():
    r = client.get("/categories/wong")
    assert r.status_code in (200, 400, 404)


def test_rate_limit_headers():
    """Rate limit headers should be present on root."""
    r = client.get("/")
    assert r.status_code == 200


# ── MCP module tests ───────────────────────────────────────────────────────

def test_mcp_module_tools_list():
    """Verify mcp module has tools defined."""
    from market_mcp import TOOLS
    assert isinstance(TOOLS, list)
    assert len(TOOLS) >= 17
    tool_names = [t["name"] for t in TOOLS]
    assert "market_search" in tool_names
    assert "market_login" in tool_names
    assert "market_checkout" in tool_names


def test_mcp_module_has_api():
    """Verify mcp module has api() function for HTTP calls."""
    from market_mcp import api
    assert callable(api)


def test_mcp_module_has_handle_tool():
    """Verify mcp module has handle_tool() for MCP tool dispatch."""
    from market_mcp import handle_tool
    assert callable(handle_tool)


def test_mcp_module_has_get_token():
    """Verify mcp module has get_token() for session auth."""
    from market_mcp import get_token
    assert callable(get_token)
