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


# ── Open redirect fix: checkout return/cancel/success/failure URLs ─────────────


def test_validate_cli_market_redirect_url_allows_own_domain():
    from market_security import validate_cli_market_redirect_url

    url = "https://cli-market.dev/account?order=success"
    assert validate_cli_market_redirect_url(url, "https://cli-market.dev?fallback") == url


def test_validate_cli_market_redirect_url_allows_subdomain():
    from market_security import validate_cli_market_redirect_url

    url = "https://app.procurecopilot.com/dashboard"
    assert validate_cli_market_redirect_url(url, "https://cli-market.dev?fallback") == url


def test_validate_cli_market_redirect_url_blocks_foreign_domain():
    from market_security import validate_cli_market_redirect_url

    default = "https://cli-market.dev?order=success"
    assert validate_cli_market_redirect_url("https://evil.example/phish", default) == default


def test_validate_cli_market_redirect_url_blocks_lookalike_domain():
    from market_security import validate_cli_market_redirect_url

    default = "https://cli-market.dev?order=success"
    # "cli-market.dev.evil.example" is NOT a subdomain of cli-market.dev
    assert validate_cli_market_redirect_url("https://cli-market.dev.evil.example", default) == default


def test_validate_cli_market_redirect_url_blocks_non_https():
    from market_security import validate_cli_market_redirect_url

    default = "https://cli-market.dev?order=success"
    assert validate_cli_market_redirect_url("http://cli-market.dev", default) == default


def test_checkout_paypal_ignores_foreign_return_url():
    _add_cart()
    mock_result = {"order_id": "PP-1", "approve_url": "https://paypal.com/approve/1"}
    captured = {}

    async def _capture_create_order(*args, **kwargs):
        captured.update(kwargs)
        return mock_result

    with patch("market_connectors.paypal_payments.create_order", new=_capture_create_order, create=True):
        r = client.post(
            "/checkout/paypal",
            headers=_auth(),
            json={"return_url": "https://evil.example/phish", "cancel_url": "https://evil.example/cancel"},
        )
    assert r.status_code == 200
    assert captured["return_url"] == "https://cli-market.dev?order=success"
    assert captured["cancel_url"] == "https://cli-market.dev?order=cancelled"


def test_checkout_mercadopago_ignores_foreign_success_url():
    _add_cart()
    mock_result = {"checkout_url": "https://mercadopago.com/checkout/1", "preference_id": "pref1"}
    captured = {}

    async def _capture_create_preference(*args, **kwargs):
        captured.update(kwargs)
        return mock_result

    with patch(
        "market_connectors.mercadopago_payments.create_preference",
        new=_capture_create_preference,
        create=True,
    ):
        r = client.post(
            "/checkout/mercadopago",
            headers=_auth(),
            json={"success_url": "https://evil.example/phish"},
        )
    assert r.status_code == 200
    assert captured["success_url"] == "https://cli-market.dev?mp=success"


# ── Mercado Pago webhook: production secret enforcement + dedup ────────────────


def test_mercadopago_webhook_requires_secret_in_production():
    with (
        patch("routers.checkout.webhooks.is_production_deploy", return_value=True),
        patch("market_connectors.mercadopago_payments.webhook_secret", return_value=""),
    ):
        r = client.post("/checkout/mercadopago-webhook?id=pay_123")
    assert r.status_code == 503


def test_mercadopago_webhook_allows_missing_secret_outside_production():
    with (
        patch("routers.checkout.webhooks.is_production_deploy", return_value=False),
        patch("market_connectors.mercadopago_payments.webhook_secret", return_value=""),
        patch(
            "market_connectors.mercadopago_payments.get_payment",
            new=AsyncMock(return_value={"error": "not_found"}),
        ),
    ):
        r = client.post("/checkout/mercadopago-webhook?id=pay_123")
    assert r.status_code == 200


def test_mercadopago_webhook_dedups_same_payment_id():
    pay_result = {"status": "approved", "external_reference": "CLI-Market-ORD-MPDUP"}
    with (
        patch("routers.checkout.webhooks.is_production_deploy", return_value=False),
        patch("market_connectors.mercadopago_payments.webhook_secret", return_value=""),
        patch(
            "market_connectors.mercadopago_payments.get_payment",
            new=AsyncMock(return_value=pay_result),
        ),
    ):
        r1 = client.post("/checkout/mercadopago-webhook?id=pay_dup_1")
        r2 = client.post("/checkout/mercadopago-webhook?id=pay_dup_1")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True
