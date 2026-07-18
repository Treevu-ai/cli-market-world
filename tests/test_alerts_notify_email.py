"""notify_email must be locked to the caller's own verified account email.

Mirrors the same fix applied in the sibling cli-market-backend repo: without
this check, any Starter+ user could set notify_email to an arbitrary
third-party address and use price alerts as an SMTP relay against it
(harassment/phishing risk, reputational damage to CLI Market's sender).
"""

from __future__ import annotations

import pytest


def _setup_starter_user(market_core, username="alerts-user", email="owner@example.com"):
    """Mirror the real registration path: app_users.email set once, OTP-verified."""
    from market_core import db_create_api_key, db_save_user, db_set_subscription

    market_core.ensure_db_initialized()
    db_save_user(username, "salt:deadbeef", None, email)
    db_set_subscription(username, "starter")
    key_rec = db_create_api_key(username, scopes="read", label="e2e")
    return key_rec["key"]


@pytest.fixture
def alerts_client(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    market_core = isolated_db
    market_core.ensure_db_initialized()
    return TestClient(app), market_core


def _create_alert_body(notify_email: str = "") -> dict:
    return {
        "condition": "price_drop",
        "product_query": "leche gloria",
        "threshold_pct": 5.0,
        "notify_email": notify_email,
    }


class TestNotifyEmailRestriction:
    def test_notify_email_matching_account_is_accepted(self, alerts_client):
        client, mc = alerts_client
        api_key = _setup_starter_user(mc, email="owner@example.com")

        r = client.post(
            "/v1/alerts",
            json=_create_alert_body("owner@example.com"),
            headers={"Authorization": f"Bearer {api_key}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["alert"]["notify_email"] == "owner@example.com"

    def test_notify_email_for_third_party_is_rejected(self, alerts_client):
        client, mc = alerts_client
        api_key = _setup_starter_user(mc, email="owner@example.com")

        r = client.post(
            "/v1/alerts",
            json=_create_alert_body("victim@example.com"),
            headers={"Authorization": f"Bearer {api_key}"},
        )
        assert r.status_code == 403
        assert "verified email" in r.json()["detail"]

    def test_blank_notify_email_requires_webhook_or_email(self, alerts_client):
        client, mc = alerts_client
        api_key = _setup_starter_user(mc, email="owner@example.com")

        r = client.post(
            "/v1/alerts",
            json=_create_alert_body(""),
            headers={"Authorization": f"Bearer {api_key}"},
        )
        # No email and no webhook — same 400 as before this fix, unrelated to it.
        assert r.status_code == 400
