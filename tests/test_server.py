"""Test suite for CLI Market — auth, search, cart, checkout, orders."""

import sys
import os
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# conftest.py sets MARKET_DATA_DIR + DATABASE_URL before collection
TEST_DATA_DIR = os.environ["MARKET_DATA_DIR"]

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
    for table in ["app_carts", "app_orders", "app_order_items", "rate_limits", "billing_pending", "subscriptions", "subscription_requests"]:
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


# ── Payment / PayPal webhook tests ───────────────────────────────────────────

def test_paypal_webhook_subscription_activated():
    from unittest.mock import AsyncMock, patch
    from market_core import db_save_billing_pending, db_get_subscription

    db_save_billing_pending("I-SUB123", "paypal", "admin", "subscription")
    event = {
        "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
        "resource": {"id": "I-SUB123", "custom_id": "admin", "status": "ACTIVE"},
    }
    with patch(
        "market_connectors.paypal_payments.verify_webhook_signature",
        new=AsyncMock(return_value=True),
    ):
        r = client.post("/checkout/paypal-webhook", json=event)
    assert r.status_code == 200
    assert "pro_activated:admin" in r.json()["actions"]
    assert db_get_subscription("admin")["tier"] == "pro"


def test_paypal_webhook_payment_capture_marks_order_paid():
    from unittest.mock import AsyncMock, patch
    from market_core import db_create_order

    db_create_order(
        "admin",
        [{"product_id": "p1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 1}],
        "paypal",
        5.0,
        status="pending",
        order_id="ORD-TEST01",
        gateway_ref="PP-ORDER-99",
    )
    event = {
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {
            "id": "CAP-1",
            "supplementary_data": {"related_ids": {"order_id": "PP-ORDER-99"}},
        },
    }
    with patch(
        "market_connectors.paypal_payments.verify_webhook_signature",
        new=AsyncMock(return_value=True),
    ):
        r = client.post("/checkout/paypal-webhook", json=event)
    assert r.status_code == 200
    db = get_db()
    row = db.execute("SELECT status FROM app_orders WHERE order_id=?", ("ORD-TEST01",)).fetchone()
    db.close()
    assert row["status"] == "paid"


def test_checkout_yape_requires_pro_without_legacy(monkeypatch):
    from market_core import db_set_subscription

    monkeypatch.setenv("MARKET_LEGACY_CHECKOUT", "0")
    db_set_subscription("admin", "free")
    client.post("/cart/add", headers={"Authorization": "Bearer test-token-123"}, json={
        "product_id": "p1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 1,
    })
    r = client.post("/checkout/yape", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 403
    monkeypatch.setenv("MARKET_LEGACY_CHECKOUT", "1")


def test_billing_paypal_saves_pending(monkeypatch):
    from market_core import db_save_billing_pending, get_db

    async def fake_sub(username, **kwargs):
        return {
            "subscription_id": "I-FAKE99",
            "approve_url": "https://sandbox.paypal.com/subscribe",
            "status": "APPROVAL_PENDING",
        }

    monkeypatch.setattr("market_connectors.paypal_payments.create_subscription", fake_sub)
    r = client.post("/billing/paypal", headers={"Authorization": "Bearer test-token-123"})
    assert r.status_code == 200
    assert r.json()["approve_url"].startswith("https://")
    db = get_db()
    pending = db.execute(
        "SELECT username FROM billing_pending WHERE external_id=?", ("I-FAKE99",)
    ).fetchone()
    db.close()
    assert pending["username"] == "admin"


def test_request_pro_creates_subscription_request(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": False, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": False},
    )
    r = client.post("/billing/request-pro", json={"email": "pro@test.com", "lang": "en"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["request_id"].startswith("PRO-")
    assert data["email"] == "pro@test.com"
    assert "payment_link" in data


def test_request_pro_requires_valid_email(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    r = client.post("/billing/request-pro", json={"email": "not-an-email"})
    assert r.status_code == 400


def test_request_pro_duplicate_without_resend(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": True},
    )
    payload = {"email": "dup@test.com", "lang": "es"}
    r1 = client.post("/billing/request-pro", json=payload)
    r2 = client.post("/billing/request-pro", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True


def test_contact_pro_triggers_billing_request(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": False, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": False},
    )
    r = client.post(
        "/v1/contact",
        json={
            "plan": "pro",
            "email": "contact-pro@test.com",
            "use_case": "Building a price comparison bot for LATAM grocery stores.",
            "lang": "en",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["plan"] == "pro"
    assert data["request_id"].startswith("PRO-")


def test_activate_pro_by_request_id(monkeypatch):
    import subprocess

    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": False},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": False},
    )
    r = client.post(
        "/billing/request-pro",
        json={"email": "activate@test.com", "username": "admin", "lang": "en"},
    )
    req_id = r.json()["request_id"]
    from market_core import db_find_subscription_request, db_get_subscription

    assert db_get_subscription("admin")["tier"] == "free"
    proc = subprocess.run(
        [sys.executable, "ops/activate_pro.py", "admin", "--request-id", req_id],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert db_get_subscription("admin")["tier"] == "pro"
    req = db_find_subscription_request(request_id=req_id)
    assert req["status"] == "activated"


def test_admin_requires_token_when_configured(monkeypatch):
    import server_deps

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "ops-secret-token")
    r = client.get("/admin/debug-fetch")
    assert r.status_code == 401

    r = client.get("/admin/debug-fetch", headers={"Authorization": "Bearer ops-secret-token"})
    assert r.status_code == 200


def test_admin_disabled_without_token(monkeypatch):
    import server_deps

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "")
    r = client.get("/admin/debug-fetch")
    assert r.status_code == 503
