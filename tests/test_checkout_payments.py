"""P0-A checkout reliability — idempotency, webhook dedup, confirmation_mode."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_core import db_create_order, db_save_user, db_set_subscription, ensure_db_initialized, get_db
from market_server import app, hash_password

ensure_db_initialized()
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_payment_tables():
    db = get_db()
    for table in (
        "app_carts",
        "app_orders",
        "app_order_items",
        "webhook_events_processed",
        "rate_limits",
        "subscriptions",
    ):
        try:
            db.execute(f"DELETE FROM {table}")
        except Exception:
            pass
    db.execute("DELETE FROM app_users")
    db.commit()
    db.close()
    db_save_user("admin", hash_password("market"), "test-token-123")
    db_set_subscription("admin", "pro")
    yield


def _auth():
    return {"Authorization": "Bearer test-token-123"}


def _add_cart():
    client.post(
        "/cart/add",
        headers=_auth(),
        json={"product_id": "p1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 1},
    )


def test_checkout_yape_idempotency_key_same_order():
    _add_cart()
    headers = {**_auth(), "Idempotency-Key": "idem-e2e-001"}
    r1 = client.post("/checkout/yape", headers=headers)
    assert r1.status_code == 200
    oid1 = r1.json()["order_id"]

    _add_cart()
    r2 = client.post("/checkout/yape", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["order_id"] == oid1


def test_checkout_yape_confirmation_mode_manual():
    _add_cart()
    r = client.post("/checkout/yape", headers=_auth())
    assert r.status_code == 200
    data = r.json()
    assert data.get("confirmation_mode") == "manual" or data.get("auto_activate") is False


def test_checkout_webhook_duplicate_is_noop():
    db_create_order(
        "admin",
        [{"product_id": "p1", "name": "Leche", "price": 5.0, "store": "wong", "quantity": 1}],
        "yape",
        5.0,
        status="pending",
        order_id="ORD-DUP01",
    )
    secret = os.getenv("CHECKOUT_WEBHOOK_SECRET", "")
    params = f"order_id=ORD-DUP01&status=paid&secret={secret}"
    r1 = client.post(f"/checkout/webhook?{params}")
    r2 = client.post(f"/checkout/webhook?{params}")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True


def test_v1_capabilities_endpoint():
    r = client.get("/v1/capabilities")
    assert r.status_code == 200
    data = r.json()
    assert data["checkout"]["scope"] == "cli_market_internal"
    assert data["checkout"]["retailer_fulfillment"] is False


def test_paypal_webhook_duplicate_ignored():
    event = {
        "id": "WH-EVENT-DUP-1",
        "event_type": "BILLING.SUBSCRIPTION.CANCELLED",
        "resource": {"id": "I-NONE", "custom_id": "nobody"},
    }
    with patch("market_connectors.paypal_payments.PAYPAL_WEBHOOK_ID", "WH-TEST"):
        with patch(
            "market_connectors.paypal_payments.verify_webhook_signature",
            new=AsyncMock(return_value=True),
        ):
            r1 = client.post("/checkout/paypal-webhook", json=event)
            r2 = client.post("/checkout/paypal-webhook", json=event)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True
