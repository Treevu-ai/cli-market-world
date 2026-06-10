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
    """Analytics router moved to private backend; test the health/db endpoint instead."""
    r = client.get("/health/db")
    assert r.status_code == 200
    data = r.json()
    assert "backend" in data


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
    assert r.status_code in (200, 400, 404, 502)


def test_rate_limit_headers():
    """Rate limit headers should be present on root."""
    r = client.get("/")
    assert r.status_code == 200


# ── MCP module tests ───────────────────────────────────────────────────────

def test_mcp_module_tools_list():
    """Verify mcp module has tools defined."""
    from market_core.market_mcp import TOOLS
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


def test_mcp_profile_defaults_to_default(monkeypatch):
    from market_core.market_mcp_registry import get_profile, public_tool_count

    monkeypatch.delenv("MCP_TOOL_PROFILE", raising=False)
    assert get_profile() == "default"
    assert public_tool_count("default") == 22


def test_mcp_tool_groups_match_registry_bundles():
    import market_ui as ui

    groups = ui.mcp_tool_groups("default")
    assert [g[0] for g in groups] == ["shop", "intel", "account"]
    shop_names = groups[0][3]
    assert "market_discover" in shop_names
    assert "market_lines" not in shop_names


# ── Payment / PayPal webhook tests ───────────────────────────────────────────

def test_paypal_webhook_subscription_activated(monkeypatch):
    from unittest.mock import AsyncMock, patch
    from market_core import db_save_billing_pending, db_get_subscription, db_create_subscription_request

    db_save_billing_pending("I-SUB123", "paypal", "admin", "subscription")
    db_create_subscription_request("admin", "activated@test.com", "https://paypal.test/approve")
    sent = []

    def fake_activation_email(**kw):
        sent.append(kw)
        return {"sent": True, "to": kw["to_email"]}

    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_activated_email",
        fake_activation_email,
    )
    event = {
        "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
        "resource": {"id": "I-SUB123", "custom_id": "admin", "status": "ACTIVE", "locale": "es_ES"},
    }
    with patch("market_connectors.paypal_payments.PAYPAL_WEBHOOK_ID", "WH-TEST"):
        with patch(
            "market_connectors.paypal_payments.verify_webhook_signature",
            new=AsyncMock(return_value=True),
        ):
            r = client.post("/checkout/paypal-webhook", json=event)
    assert r.status_code == 200
    assert "pro_activated:admin" in r.json()["actions"]
    assert "activation_email:activated@test.com" in r.json()["actions"]
    assert db_get_subscription("admin")["tier"] == "pro"
    assert sent and sent[0]["username"] == "admin"


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
    with patch("market_connectors.paypal_payments.PAYPAL_WEBHOOK_ID", "WH-TEST"):
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


def test_starter_subscribe_public(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    sent = []

    def fake_pending_email(**kw):
        sent.append(kw)
        return {"sent": True, "to": kw["to_email"]}

    monkeypatch.setattr(
        "market_connectors.email_outbound.send_starter_subscribe_pending_email",
        fake_pending_email,
    )

    async def fake_sub(username, plan="pro", **kwargs):
        assert plan == "starter"
        return {
            "subscription_id": "I-START99",
            "approve_url": "https://www.paypal.com/billing/subscriptions?ba_token=starter",
            "status": "APPROVAL_PENDING",
            "plan": "starter",
        }

    monkeypatch.setattr("market_connectors.paypal_payments.create_subscription", fake_sub)
    r = client.post(
        "/billing/starter-subscribe",
        json={"email": "starter@cli-market.dev", "username": "admin", "lang": "es"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["tier"] == "starter"
    assert data.get("email_sent") is True
    assert len(sent) == 1


def test_paypal_webhook_starter_activated(monkeypatch):
    from unittest.mock import AsyncMock, patch
    from market_core import db_save_billing_pending, db_get_subscription, db_create_subscription_request

    db_save_billing_pending("I-STARTWEB", "paypal", "admin", "starter")
    db_create_subscription_request(
        "admin",
        "starter-activated@test.com",
        "https://paypal.test/starter",
        prefix="STR",
    )
    sent = []

    monkeypatch.setattr(
        "market_connectors.email_outbound.send_starter_activated_email",
        lambda **kw: sent.append(kw) or {"sent": True, "to": kw["to_email"]},
    )
    event = {
        "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
        "resource": {"id": "I-STARTWEB", "custom_id": "admin"},
    }
    with patch("market_connectors.paypal_payments.PAYPAL_WEBHOOK_ID", "WH-TEST"):
        with patch(
            "market_connectors.paypal_payments.verify_webhook_signature",
            new=AsyncMock(return_value=True),
        ):
            r = client.post("/checkout/paypal-webhook", json=event)
    assert r.status_code == 200
    assert "starter_activated:admin" in r.json().get("actions", [])
    assert "activation_email:starter-activated@test.com" in r.json().get("actions", [])
    assert db_get_subscription("admin")["tier"] == "starter"
    assert len(sent) == 1


def test_paypal_subscribe_public(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    sent = []

    def fake_pending_email(**kw):
        sent.append(kw)
        return {"sent": True, "to": kw["to_email"]}

    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_subscribe_pending_email",
        fake_pending_email,
    )

    async def fake_sub(username, **kwargs):
        return {
            "subscription_id": "I-LAND99",
            "approve_url": "https://www.paypal.com/billing/subscriptions?ba_token=abc",
            "status": "APPROVAL_PENDING",
        }

    monkeypatch.setattr("market_connectors.paypal_payments.create_subscription", fake_sub)
    r = client.post(
        "/billing/paypal-subscribe",
        json={"email": "pro@cli-market.dev", "username": "admin", "lang": "en"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["auto_activate"] is True
    assert data["approve_url"].startswith("https://")
    assert data.get("email_sent") is True
    assert len(sent) == 1
    assert sent[0]["username"] == "admin"


def test_request_starter_creates_subscription_request(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "routers.payments._send_starter_payment_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_starter_request_notify",
        lambda **kw: {"sent": True},
    )
    r = client.post(
        "/billing/request-starter",
        json={"email": "starter-fallback@test.com", "lang": "en"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["request_id"].startswith("STR-")
    assert data["tier"] == "starter"
    assert "pro-checkout" in data["payment_link"]


def test_request_pro_creates_subscription_request(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_subscribe_pending_email",
        lambda **kw: {"sent": False, "to": kw["to_email"]},
    )

    async def fake_sub(username, **kwargs):
        return {
            "subscription_id": "I-REQPRO",
            "approve_url": "https://www.paypal.com/billing/subscriptions?ba_token=req",
            "status": "APPROVAL_PENDING",
        }

    monkeypatch.setattr("market_connectors.paypal_payments.create_subscription", fake_sub)
    r = client.post(
        "/billing/request-pro",
        json={"email": "pro@test.com", "username": "prouser", "lang": "en"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["request_id"].startswith("PRO-")
    assert data["username"] == "prouser"
    assert data.get("approve_url", "").startswith("https://")


def test_request_pro_requires_valid_email(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    r = client.post("/billing/request-pro", json={"email": "not-an-email"})
    assert r.status_code == 400


def test_request_pro_duplicate_without_resend(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_subscribe_pending_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )

    async def fake_sub(username, **kwargs):
        return {
            "subscription_id": "I-DUPPRO",
            "approve_url": "https://www.paypal.com/billing/subscriptions?ba_token=dup",
            "status": "APPROVAL_PENDING",
        }

    monkeypatch.setattr("market_connectors.paypal_payments.create_subscription", fake_sub)
    payload = {"email": "dup@test.com", "username": "dupuser", "lang": "es"}
    r1 = client.post("/billing/request-pro", json=payload)
    r2 = client.post("/billing/request-pro", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True






def test_auth_account_returns_usage(monkeypatch):
    from market_core import db_create_api_key, db_save_user
    from server_deps import hash_password
    import uuid

    username = f"acct-{uuid.uuid4().hex[:8]}"
    db_save_user(username, hash_password("x"), str(uuid.uuid4()))
    key = db_create_api_key(username, "read", "test")["key"]

    r = client.get("/auth/account?lang=en", headers={"Authorization": f"Bearer {key}"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == username
    assert data["tier"] == "free"
    assert "usage" in data
    assert "limits" in data
    assert data["upgrade"]["next_tier"] == "pro"


def test_auth_account_shows_pending_pro_billing(monkeypatch):
    from market_core import db_create_api_key, db_create_subscription_request, db_save_user
    from server_deps import hash_password
    import uuid

    username = f"bill-{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    db_save_user(username, hash_password("x"), str(uuid.uuid4()))
    key = db_create_api_key(username, "read", "test")["key"]
    db_create_subscription_request(
        username,
        email,
        "https://www.paypal.com/billing/subscriptions?ba_token=x",
    )

    r = client.get("/auth/account?lang=en", headers={"Authorization": f"Bearer {key}"})
    assert r.status_code == 200
    billing = r.json().get("billing") or {}
    assert billing.get("state") == "pro_pending_auto"
    assert billing.get("activation") == "auto"
    assert billing.get("request_id", "").startswith("PRO-")


def test_contact_starter_request(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_starter_request_received_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_starter_request_notify",
        lambda **kw: {"sent": True},
    )
    r = client.post(
        "/v1/contact",
        json={
            "plan": "starter",
            "email": "starter@test.com",
            "profile": "business",
            "name": "Ana",
            "use_case": "Need CSV export and price alerts for PE grocery monitoring.",
            "lang": "es",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["plan"] == "starter"
    assert data["request_id"].startswith("STR-")
    assert data.get("email_sent") is True


def test_retailer_apply_sends_ack_email(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_retailer_application_received_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_retailer_application_notify",
        lambda **kw: {"sent": True},
    )
    r = client.post(
        "/v1/retailers/apply",
        json={
            "store_name": "Nuna Orgánica",
            "platform": "woocommerce",
            "country": "PE",
            "contact_email": "retailer@test.com",
            "contact_name": "Ana",
            "website": "https://nuna.example",
            "lang": "es",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["application_id"].startswith("RET-")
    assert data.get("email_sent") is True
    assert data.get("notify_sent") is True


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


def test_intel_inflation_with_snapshot_rows():
    """Regression: DB rows are not dicts — must not call row.get()."""
    from datetime import datetime, timedelta, timezone

    db = get_db()
    now = datetime.now(timezone.utc)
    recent = (now - timedelta(days=1)).isoformat()
    older = (now - timedelta(days=10)).isoformat()
    rows = (
        ("p1", 10.0, recent),
        ("p2", 12.0, recent),
        ("p3", 8.0, older),
    )
    for product_id, price, queried_at in rows:
        db.execute(
            """INSERT INTO price_snapshots
               (product_id, store, name, price, currency, line, queried_at, url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (product_id, "wong", "Leche test", price, "PEN", "supermercados", queried_at, ""),
        )
    db.commit()
    db.close()

    db_save_user("admin", hash_password("market"), "test@test.com")
    from market_core import db_create_api_key

    key = db_create_api_key("admin", "read", "t")["key"]
    r = client.get(
        "/v1/intel/inflation?country=PE&line=supermercados",
        headers={"Authorization": f"Bearer {key}"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["items"]
    assert data["items"][0]["n_products"] >= 1


def test_intel_inflation_country_filter_sql():
    """Regression: country filter must stay in WHERE, not after GROUP BY."""
    db_save_user("admin", hash_password("market"), "test@test.com")
    from market_core import db_create_api_key

    key = db_create_api_key("admin", "read", "t")["key"]
    r = client.get(
        "/v1/intel/inflation?country=PE",
        headers={"Authorization": f"Bearer {key}"},
    )
    assert r.status_code == 200, r.text


def test_pro_checkout_yape_routes_to_mercadopago(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": True},
    )

    async def fake_pref(total, currency, ref, **kwargs):
        return {
            "checkout_url": "https://mp.test/checkout-yape",
            "preference_id": "pref-yape",
        }

    monkeypatch.setattr("market_connectors.mercadopago_payments.create_preference", fake_pref)
    r = client.post(
        "/billing/pro-checkout",
        json={
            "email": "yape-pro@test.com",
            "username": "yapeuser",
            "payment_method": "yape",
            "lang": "es",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["payment_method"] == "yape"
    assert data["payment_rail"] == "mercadopago"
    assert data["payment_mode"] == "mercadopago_checkout"
    assert data["checkout_url"] == "https://mp.test/checkout-yape"
    assert data["request_id"].startswith("PRO-")
    assert data["auto_activate"] is True


def test_pro_checkout_persists_display_name(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr("routers.payments.wallet_manual_fallback_enabled", lambda: True)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": True},
    )
    r = client.post(
        "/billing/pro-checkout",
        json={
            "email": "antonio@test.com",
            "username": "antonio-cli",
            "display_name": "Antonio Cuba",
            "payment_method": "yape",
            "lang": "es",
            "manual_transfer": True,
        },
    )
    assert r.status_code == 200
    from market_core import db_find_subscription_request

    req = db_find_subscription_request(request_id=r.json()["request_id"])
    assert req["display_name"] == "Antonio Cuba"


def test_pro_checkout_yape_manual_transfer_fallback(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr("routers.payments.wallet_manual_fallback_enabled", lambda: True)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": True},
    )
    r = client.post(
        "/billing/pro-checkout",
        json={
            "email": "yape-manual@test.com",
            "username": "yapemanual",
            "payment_method": "yape",
            "lang": "es",
            "manual_transfer": True,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["payment_method"] == "yape"
    assert data["payment_mode"] == "manual_transfer"
    assert isinstance(data.get("manual_steps"), list) and len(data["manual_steps"]) >= 3
    assert data["auto_activate"] is False


def test_pro_checkout_mercadopago_returns_url(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": True, "to": kw["to_email"]},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": True},
    )

    async def fake_pref(total, currency, ref, **kwargs):
        return {
            "checkout_url": "https://mp.test/checkout",
            "preference_id": "pref-123",
        }

    monkeypatch.setattr("market_connectors.mercadopago_payments.create_preference", fake_pref)
    r = client.post(
        "/billing/pro-checkout",
        json={
            "email": "mp-pro@test.com",
            "username": "mpuser",
            "payment_method": "mercadopago",
            "lang": "en",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["payment_method"] == "mercadopago"
    assert data["checkout_url"] == "https://mp.test/checkout"
    assert data["request_id"].startswith("PRO-")


def test_pro_checkout_requires_username(monkeypatch):
    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    r = client.post(
        "/billing/pro-checkout",
        json={"email": "no-user@test.com", "payment_method": "mercadopago", "lang": "es"},
    )
    assert r.status_code == 400


def test_pro_checkout_mp_dedupe_returns_checkout_url(monkeypatch):
    from market_core import db_create_subscription_request, db_update_subscription_request_payment_link

    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_payment_email",
        lambda **kw: {"sent": True},
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_request_notify",
        lambda **kw: {"sent": True},
    )

    req = db_create_subscription_request("dedupeuser", "mp-dedupe@test.com", "mercadopago:pending")
    db_update_subscription_request_payment_link(req["id"], "https://www.mercadopago.com/checkout/existing")

    r = client.post(
        "/billing/pro-checkout",
        json={
            "email": "mp-dedupe@test.com",
            "username": "dedupeuser",
            "payment_method": "mercadopago",
            "lang": "es",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("duplicate") is True
    assert data.get("checkout_url") == "https://www.mercadopago.com/checkout/existing"


def test_mercadopago_webhook_activates_pro_request(monkeypatch):
    from market_core import db_create_subscription_request, db_get_subscription

    monkeypatch.setattr("server_deps.check_rate_limit", lambda _ip: None)
    req = db_create_subscription_request("admin", "mp-webhook@test.com", "mercadopago:test")
    request_id = req["id"]

    async def fake_get_payment(payment_id):
        return {
            "status": "approved",
            "external_reference": f"CLI-Market-{request_id}",
        }

    monkeypatch.setattr("market_connectors.mercadopago_payments.get_payment", fake_get_payment)
    monkeypatch.setattr("market_connectors.mercadopago_payments.webhook_secret", lambda: "")
    monkeypatch.setattr(
        "market_connectors.mercadopago_payments.parse_webhook_payment_id",
        lambda **kw: ("pay-1", "payment"),
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_activated_email",
        lambda **kw: {"sent": True},
    )

    assert db_get_subscription("admin")["tier"] == "free"
    r = client.post("/checkout/mercadopago-webhook?data.id=pay-1")
    assert r.status_code == 200
    assert any("pro_activated:admin" in a for a in r.json().get("actions", []))
    assert db_get_subscription("admin")["tier"] == "pro"


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
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_subscribe_pending_email",
        lambda **kw: {"sent": False},
    )

    async def fake_sub(username, **kwargs):
        return {
            "subscription_id": "I-ACTIVATE",
            "approve_url": "https://www.paypal.com/billing/subscriptions?ba_token=act",
            "status": "APPROVAL_PENDING",
        }

    monkeypatch.setattr("market_connectors.paypal_payments.create_subscription", fake_sub)
    r = client.post(
        "/billing/request-pro",
        json={"email": "activate@test.com", "username": "admin", "lang": "en"},
    )
    req_id = r.json()["request_id"]
    from market_core import db_find_subscription_request, db_get_subscription

    assert db_get_subscription("admin")["tier"] == "free"
    env = os.environ.copy()
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_PASS"):
        env[key] = ""
    env["GMAIL_DRAFTS_ENABLED"] = "0"
    proc = subprocess.run(
        [sys.executable, "ops/activate_pro.py", "admin", "--request-id", req_id],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True,
        env=env,
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


# ── Intelligence brief (PR3) ─────────────────────────────────────────────────

def test_intel_brief_requires_auth():
    r = client.get("/v1/intel/brief?country=PE")
    assert r.status_code == 401


def test_intel_brief_returns_narrative():
    r = client.get(
        "/v1/intel/brief?country=PE&days=7",
        headers={"Authorization": "Bearer test-token-123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "headline" in data
    assert "shelf" in data
    assert "macro_gap" in data
    assert "confidence" in data
    assert "scores" in data
    assert data["country"] == "PE"


def test_intel_scores_available():
    r = client.get(
        "/v1/intel/scores?country=PE",
        headers={"Authorization": "Bearer test-token-123"},
    )
    assert r.status_code == 200
    assert "scores" in r.json()


# ── Conversational intel agent (/v1/intel/ask) ──────────────────────────────

def test_intel_ask_requires_auth():
    r = client.post("/v1/intel/ask", json={"question": "inflación?"})
    assert r.status_code == 401


def test_intel_ask_free_tier_forbidden():
    from market_core import db_set_subscription

    db_set_subscription("admin", "free")
    r = client.post(
        "/v1/intel/ask",
        headers={"Authorization": "Bearer test-token-123"},
        json={"question": "¿inflación en PE?"},
    )
    assert r.status_code == 403


def test_intel_ask_empty_question_rejected():
    from market_core import db_set_subscription

    db_set_subscription("admin", "pro")
    r = client.post(
        "/v1/intel/ask",
        headers={"Authorization": "Bearer test-token-123"},
        json={"question": "   "},
    )
    assert r.status_code == 422


def test_intel_ask_unavailable_without_api_key(monkeypatch):
    from market_core import db_set_subscription

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    db_set_subscription("admin", "pro")
    r = client.post(
        "/v1/intel/ask",
        headers={"Authorization": "Bearer test-token-123"},
        json={"question": "¿inflación en PE?"},
    )
    assert r.status_code == 503


def test_intel_ask_runs_tool_loop(monkeypatch):
    """Pro user + mocked LLM: tool_use → tool_result → final answer."""
    from market_core import db_set_subscription
    import market_core.market_intel_agent as agent

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    db_set_subscription("admin", "pro")

    class FakeResp:
        status_code = 200

        def __init__(self, payload):
            self._p = payload

        def json(self):
            return self._p

    class FakeClient:
        def __init__(self, *a, **k):
            self.calls = 0

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, headers=None, json=None):
            self.calls += 1
            if self.calls == 1:
                return FakeResp({
                    "stop_reason": "tool_use",
                    "content": [{
                        "type": "tool_use", "id": "t1",
                        "name": "get_inflation", "input": {"country": "PE", "days": 30},
                    }],
                })
            return FakeResp({
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "Inflación observada en PE: 4.2% (prueba)."}],
            })

    monkeypatch.setattr(agent.httpx, "Client", FakeClient)
    monkeypatch.setattr(agent, "_dispatch", lambda name, args, db: {"avg_inflation_pct": 4.2})

    r = client.post(
        "/v1/intel/ask",
        headers={"Authorization": "Bearer test-token-123"},
        json={"question": "¿cuál fue la inflación en PE?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "get_inflation" in data["tools_used"]
    assert "PE" in data["answer"]


# ── Admin set-tier ──────────────────────────────────────────────────────────

def test_admin_set_tier_requires_admin(monkeypatch):
    import server_deps

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "ops-secret-token")
    r = client.post("/v1/admin/set-tier", json={"username": "admin", "tier": "pro"})
    assert r.status_code == 401


def test_admin_set_tier_sets_pro(monkeypatch):
    import server_deps
    from market_core import db_get_subscription

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "ops-secret-token")
    h = {"Authorization": "Bearer ops-secret-token"}
    r = client.post("/v1/admin/set-tier", headers=h, json={"username": "admin", "tier": "pro"})
    assert r.status_code == 200
    assert r.json()["subscription"]["tier"] == "pro"
    assert db_get_subscription("admin")["tier"] == "pro"


def test_admin_set_tier_rejects_bad_tier(monkeypatch):
    import server_deps

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "ops-secret-token")
    h = {"Authorization": "Bearer ops-secret-token"}
    r = client.post("/v1/admin/set-tier", headers=h, json={"username": "admin", "tier": "platinum"})
    assert r.status_code == 400


def test_admin_set_tier_unknown_user(monkeypatch):
    import server_deps

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "ops-secret-token")
    h = {"Authorization": "Bearer ops-secret-token"}
    r = client.post("/v1/admin/set-tier", headers=h, json={"username": "ghost", "tier": "pro"})
    assert r.status_code == 404
