"""Test suite for CLI Market — auth, search, cart, checkout, orders."""

import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Set temp dir BEFORE importing market_core (which calls init_db on import)
TEST_DATA_DIR = tempfile.mkdtemp(prefix="market_test_")
os.environ["MARKET_DATA_DIR"] = TEST_DATA_DIR

# Now safe to import
import pytest
from fastapi.testclient import TestClient
from market_core import (
    get_db, db_get_users, db_get_cart, db_get_orders,
    db_clear_cart, db_save_user,
)
from market_server import app, hash_password

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
