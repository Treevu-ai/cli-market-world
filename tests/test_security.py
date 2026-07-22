"""Security regression tests — webhooks and SSRF guards."""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from market_core import db_create_api_key, db_save_user
from market_server import app, hash_password

import server_deps

client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


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


def test_ticket_scan_url_blocks_loopback(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    r = client.post("/v1/ticket/scan-url", json={"url": "http://127.0.0.1/image.jpg"}, headers=_AUTH)
    assert r.status_code == 400
    assert "non-public" in r.json()["detail"].lower() or "not allowed" in r.json()["detail"].lower()


def test_ticket_scan_url_blocks_metadata_host(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    r = client.post(
        "/v1/ticket/scan-url",
        json={"url": "http://169.254.169.254/latest/meta-data/"},
        headers=_AUTH,
    )
    assert r.status_code == 400


def test_validate_public_http_url_accepts_https():
    from market_security import validate_public_http_url

    assert validate_public_http_url("https://example.com/image.png").startswith("https://")


def test_validate_public_http_url_rejects_credentials():
    from market_security import validate_public_http_url

    with pytest.raises(ValueError, match="credentials"):
        validate_public_http_url("https://user:pass@example.com/hook")


def test_alert_webhook_blocks_loopback():
    db_save_user("ent-ssrf", hash_password("market"), "ent@test.com")
    from market_billing import db_set_subscription

    db_set_subscription("ent-ssrf", "enterprise")
    key = db_create_api_key("ent-ssrf", "read", "alert-ssrf")["key"]
    r = client.post(
        "/v1/alerts",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "condition": "price_jump",
            "product_query": "arroz",
            "notify_webhook": "https://127.0.0.1/hook",
        },
    )
    assert r.status_code == 400
    assert "non-public" in r.json()["detail"].lower() or "not allowed" in r.json()["detail"].lower()


def test_alert_webhook_blocks_metadata_host():
    db_save_user("ent-ssrf2", hash_password("market"), "ent2@test.com")
    from market_billing import db_set_subscription

    db_set_subscription("ent-ssrf2", "enterprise")
    key = db_create_api_key("ent-ssrf2", "read", "alert-ssrf2")["key"]
    r = client.post(
        "/v1/alerts",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "condition": "price_jump",
            "product_query": "arroz",
            "notify_webhook": "https://169.254.169.254/latest/meta-data/",
        },
    )
    assert r.status_code == 400


def test_price_pulse_callback_blocks_loopback():
    db_save_user("pp-ssrf", hash_password("market"), "pp@test.com")
    from market_billing import db_set_subscription

    db_set_subscription("pp-ssrf", "pro")
    key = db_create_api_key("pp-ssrf", "read", "pp-ssrf")["key"]
    r = client.post(
        "/v1/intel/price-pulse",
        headers={"Authorization": f"Bearer {key}"},
        json={"country": "PE", "callback_url": "https://127.0.0.1/callback"},
    )
    assert r.status_code == 400


def test_patch_alert_webhook_dispatch_blocks_private_url(monkeypatch):
    from market_security import patch_alert_webhook_dispatch

    patch_alert_webhook_dispatch()
    import market_core.market_alerts as ma

    ok = ma._send_webhook(
        {"id": "ALT-TEST", "name": "t", "condition": "price_jump", "product_query": "x", "notify_webhook": "https://127.0.0.1/hook"},
        {
            "product_id": "p1",
            "product_name": "Arroz",
            "store": "wong",
            "price_now": 5.0,
            "price_before": 4.0,
            "delta_pct": 25.0,
        },
    )
    assert ok is False


@pytest.mark.parametrize(
    "path",
    [
        "/v1/intel/affordability",
        "/v1/intel/procurement-signal",
        "/v1/intel/inflation-report",
        "/v1/intel/regulatory",
        "/v1/moat/confidence",
    ],
)
def test_intel_routes_require_api_key(path):
    r = client.get(path, params={"country": "PE"} if "regulatory" in path or "affordability" in path else None)
    assert r.status_code == 401


def test_procure_magic_token_does_not_embed_api_key(monkeypatch):
    import base64
    import json

    from market_core import db_save_user, ensure_db_initialized
    from procure_magic import create_procure_magic_token, provision_procure_api_key

    monkeypatch.setenv("PROCURE_MAGIC_SECRET", "test-secret-security-regression")
    ensure_db_initialized()
    db_save_user("sec-magic", "hash", "sess")
    api_key = provision_procure_api_key("sec-magic")
    token = create_procure_magic_token(username="sec-magic", api_key=api_key, tier="procure_pro")
    body = token.rsplit(".", 1)[0]
    pad = "=" * (-len(body) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(body + pad))
    assert "key" not in decoded
    assert api_key not in token
