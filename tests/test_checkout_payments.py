"""P0-A checkout reliability — idempotency, webhook dedup, confirmation_mode."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
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
    # app_order_items.order_id references app_orders(order_id) -- deleting
    # app_orders first violates that FK on Postgres, which (unlike SQLite,
    # which doesn't enforce FKs by default) always enforces it. That failure
    # was silently swallowed by the bare except below, but the DB session
    # stays in an aborted-transaction state afterward, so the very next
    # statement (DELETE FROM app_users, unguarded) failed too -- every test
    # in this file, every run, once test-pg started actually hitting
    # Postgres (found 2026-08-05). Child tables must come before the parents
    # they reference.
    for table in (
        "app_order_items",
        "app_carts",
        "app_orders",
        "webhook_events_processed",
        "rate_limits",
        "subscriptions",
    ):
        try:
            db.execute(f"DELETE FROM {table}")
        except Exception:
            # Defense in depth: roll back so a future constraint issue on
            # one table can't poison every statement after it on Postgres.
            try:
                db._conn.rollback()
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


_TEST_PRODUCT_ID = "p1-checkout-test"


def _add_cart():
    # _prepare_pending_order now runs pre_checkout_validate against the live
    # price_snapshots table before charging (2026-08-11 checkout price-bypass
    # fix) — a bare cart/add with no matching snapshot gets rejected as
    # missing_snapshot (409), so seed one matching this cart's price exactly.
    # product_id is namespaced (not the generic "p1") because price_snapshots
    # is never cleared between test files -- a plain "p1"/"wong" row here
    # collided with test_server.py::test_intel_inflation_with_snapshot_rows's
    # own unguarded INSERT for the same key, breaking test-pg CI (2026-08-11).
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, stock, queried_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Supermercados', ?, ?)""",
        (
            _TEST_PRODUCT_ID, "wong", "Wong", "Leche", 5.0, "PEN", "supermercados", 100,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.commit()
    db.close()
    client.post(
        "/cart/add",
        headers=_auth(),
        json={"product_id": _TEST_PRODUCT_ID, "name": "Leche", "price": 5.0, "store": "wong", "quantity": 1},
    )


def test_checkout_rejects_tampered_cart_price():
    """Regression for the 2026-08-07 Cursor finding: AddToCartRequest.price
    is caller-controlled, so a client that POSTs a real product_id with a
    manipulated low price must not be able to check out at that price."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, stock, queried_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Supermercados', ?, ?)""",
        (
            "p-real-checkout-test", "wong", "Wong", "Aceite Primor 900ml", 50.0, "PEN", "supermercados", 100,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.commit()
    db.close()
    client.post(
        "/cart/add",
        headers=_auth(),
        json={
            "product_id": "p-real-checkout-test",
            "name": "Aceite Primor 900ml",
            "price": 0.01,
            "store": "wong",
            "quantity": 1,
        },
    )
    r = client.post("/checkout/yape", headers=_auth())
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert detail["ok"] is False
    # The order must never be created at the tampered price -- confirmed by
    # rejection alone, but assert the validated (real) total is what the
    # response reports back, not the 0.01 the client sent.
    assert detail["validated_total"] == 50.0


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
    params = "order_id=ORD-DUP01&status=paid"
    headers = {"X-Checkout-Webhook-Secret": secret} if secret else {}
    r1 = client.post(f"/checkout/webhook?{params}", headers=headers)
    r2 = client.post(f"/checkout/webhook?{params}", headers=headers)
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


def test_checkout_paypal_capture_rejects_other_users_order():
    """Regression: checkout_paypal_capture looked up an order purely by
    paypal_order_id (not secret -- it's returned in the /checkout/paypal
    response and appears in redirect URLs) and marked it paid without
    checking the order belonged to the caller. PayPal itself won't move
    money to an order the buyer never approved, but an attacker who obtains
    another user's paypal_order_id could still flip status to "paid" and
    fire the Procure payment notification for someone else's order.
    Found by security-reviewer scan 2026-08-19."""
    db_save_user("victim-paypal", hash_password("market"), "victim-paypal@test.com")
    db_create_order(
        "victim-paypal",
        [{"product_id": _TEST_PRODUCT_ID, "name": "test", "price": 10.0, "qty": 1}],
        "paypal",
        10.0,
        status="pending",
        gateway_ref="PP-VICTIM-1",
    )

    async def _capture_order(*args, **kwargs):
        raise AssertionError("capture_order must not be called for a non-owned order")

    with patch("market_connectors.paypal_payments.capture_order", new=_capture_order, create=True):
        r = client.post(
            "/checkout/paypal/capture",
            headers=_auth(),  # authenticated as "admin", not "victim-paypal"
            params={"paypal_order_id": "PP-VICTIM-1"},
        )
    assert r.status_code == 404


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
