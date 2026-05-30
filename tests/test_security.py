"""Security regression tests — webhooks and SSRF guards."""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from market_server import app

client = TestClient(app)


def test_paypal_webhook_rejects_without_verification_in_production(monkeypatch):
    monkeypatch.setenv("PAYPAL_SANDBOX", "false")
    monkeypatch.delenv("PAYPAL_WEBHOOK_ID", raising=False)
    monkeypatch.delenv("PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS", raising=False)
    event = {
        "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
        "resource": {"id": "I-EVIL", "custom_id": "attacker", "status": "ACTIVE"},
    }
    r = client.post("/checkout/paypal-webhook", json=event)
    assert r.status_code == 503


def test_paypal_webhook_rejects_unsigned_in_sandbox_by_default(monkeypatch):
    monkeypatch.setenv("PAYPAL_SANDBOX", "true")
    monkeypatch.delenv("PAYPAL_WEBHOOK_ID", raising=False)
    monkeypatch.delenv("PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS", raising=False)
    r = client.post(
        "/checkout/paypal-webhook",
        json={"event_type": "CHECKOUT.ORDER.COMPLETED", "resource": {}},
    )
    assert r.status_code == 401


def test_paypal_webhook_allows_explicit_sandbox_bypass(monkeypatch):
    monkeypatch.setenv("PAYPAL_SANDBOX", "true")
    monkeypatch.delenv("PAYPAL_WEBHOOK_ID", raising=False)
    monkeypatch.setenv("PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS", "1")
    r = client.post(
        "/checkout/paypal-webhook",
        json={"event_type": "CHECKOUT.ORDER.COMPLETED", "resource": {}},
    )
    assert r.status_code == 200


def test_checkout_webhook_requires_secret_in_production(monkeypatch):
    monkeypatch.setenv("PAYPAL_SANDBOX", "false")
    monkeypatch.delenv("CHECKOUT_WEBHOOK_SECRET", raising=False)
    r = client.post("/checkout/webhook?order_id=ORD-TEST&status=paid")
    assert r.status_code == 503


def test_checkout_webhook_rejects_bad_secret_when_configured(monkeypatch):
    monkeypatch.setenv("CHECKOUT_WEBHOOK_SECRET", "good-secret")
    r = client.post("/checkout/webhook?order_id=ORD-TEST&status=paid&secret=wrong")
    assert r.status_code == 401


def test_ticket_scan_url_blocks_loopback():
    r = client.post("/v1/ticket/scan-url", json={"url": "http://127.0.0.1/image.jpg"})
    assert r.status_code == 400
    assert "non-public" in r.json()["detail"].lower() or "not allowed" in r.json()["detail"].lower()


def test_ticket_scan_url_blocks_metadata_host():
    r = client.post(
        "/v1/ticket/scan-url",
        json={"url": "http://169.254.169.254/latest/meta-data/"},
    )
    assert r.status_code == 400


def test_validate_public_http_url_accepts_https():
    from market_security import validate_public_http_url

    assert validate_public_http_url("https://example.com/image.png").startswith("https://")
