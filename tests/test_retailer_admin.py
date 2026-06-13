"""Tests for routers/retailers.py and routers/retailer_admin.py."""

from __future__ import annotations

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from market_core import get_db, db_save_user, ensure_db_initialized
from market_server import app, hash_password

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    import server_deps
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db = get_db()
    for table in ["retailer_applications", "contacts", "app_users", "rate_limits"]:
        db.execute(f"DELETE FROM {table}")
    db.commit()
    db.close()
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)


_VALID_APPLY = {
    "store_name": "SuperWong",
    "platform": "vtex",
    "country": "PE",
    "contact_email": "tienda@example.com",
}


# ── /v1/retailers/apply — validation ─────────────────────────────────────────

def test_retailer_apply_missing_store_name():
    body = {**_VALID_APPLY, "store_name": ""}
    r = client.post("/v1/retailers/apply", json=body)
    assert r.status_code == 400


def test_retailer_apply_invalid_platform():
    body = {**_VALID_APPLY, "platform": "amazon"}
    r = client.post("/v1/retailers/apply", json=body)
    assert r.status_code == 400


def test_retailer_apply_invalid_country_too_long():
    body = {**_VALID_APPLY, "country": "PER"}
    r = client.post("/v1/retailers/apply", json=body)
    assert r.status_code == 400


def test_retailer_apply_invalid_email():
    body = {**_VALID_APPLY, "contact_email": "not-an-email"}
    r = client.post("/v1/retailers/apply", json=body)
    assert r.status_code == 400


def test_retailer_apply_happy_path(monkeypatch):
    monkeypatch.setattr(
        "routers.retailers.send_retailer_application_received_email",
        lambda **_: {"sent": True},
        raising=False,
    )
    monkeypatch.setattr(
        "routers.retailers.send_retailer_application_notify",
        lambda **_: {"sent": True},
        raising=False,
    )

    # Patch inside the function's local import scope
    import market_connectors.email_outbound as eo
    monkeypatch.setattr(eo, "send_retailer_application_received_email", lambda **_: {"sent": True})
    monkeypatch.setattr(eo, "send_retailer_application_notify", lambda **_: {"sent": True})

    r = client.post("/v1/retailers/apply", json=_VALID_APPLY)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["application_id"].startswith("RET-")
    assert data["status"] == "pending"


def test_retailer_apply_persists_to_db(monkeypatch):
    import market_connectors.email_outbound as eo
    monkeypatch.setattr(eo, "send_retailer_application_received_email", lambda **_: {"sent": False})
    monkeypatch.setattr(eo, "send_retailer_application_notify", lambda **_: {"sent": False})

    r = client.post("/v1/retailers/apply", json=_VALID_APPLY)
    assert r.status_code == 200
    app_id = r.json()["application_id"]

    db = get_db()
    row = db.execute("SELECT * FROM retailer_applications WHERE id=?", (app_id,)).fetchone()
    db.close()
    assert row is not None
    assert row["store_name"] == "SuperWong"
    assert row["status"] == "pending"


# ── /v1/contact ──────────────────────────────────────────────────────────────

def test_contact_invalid_email():
    r = client.post("/v1/contact", json={"email": "bad", "use_case": "I need pricing data", "plan": "free"})
    assert r.status_code == 400


def test_contact_use_case_too_short():
    r = client.post("/v1/contact", json={"email": "a@b.com", "use_case": "short", "plan": "free"})
    assert r.status_code == 400


def test_contact_free_plan_inserts_contact():
    r = client.post("/v1/contact", json={
        "email": "dev@example.com",
        "use_case": "I want to integrate price data into my app",
        "plan": "free",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is True

    db = get_db()
    row = db.execute("SELECT * FROM contacts WHERE username='dev@example.com'").fetchone()
    db.close()
    assert row is not None


def test_contact_starter_plan_routes_to_subscription(monkeypatch):
    import market_connectors.email_outbound as eo
    monkeypatch.setattr(eo, "send_starter_request_received_email", lambda **_: {"sent": False})
    monkeypatch.setattr(eo, "send_starter_request_notify", lambda **_: {"sent": False})

    r = client.post("/v1/contact", json={
        "email": "starter@example.com",
        "use_case": "Need starter tier for my procurement workflow",
        "plan": "starter",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["plan"] == "starter"
    assert data.get("request_id", "").startswith("STR-")


def test_contact_pro_plan_routes_to_pro_request(monkeypatch):
    import market_connectors.email_outbound as eo
    monkeypatch.setattr(eo, "send_pro_request_received_email", lambda **_: {"sent": False}, raising=False)
    monkeypatch.setattr(eo, "send_pro_request_notify", lambda **_: {"sent": False}, raising=False)
    # process_pro_subscription_request uses several email functions; patch the whole module path
    monkeypatch.setattr(
        "routers.billing.activation._send_starter_payment_email",
        lambda **_: {"sent": False},
        raising=False,
    )

    r = client.post("/v1/contact", json={
        "email": "pro@example.com",
        "use_case": "Need pro tier with full analytics access",
        "plan": "pro",
    })
    # Should succeed (200) and return plan=pro; payment_link may be None without PayPal configured
    assert r.status_code == 200
    data = r.json()
    assert data["plan"] == "pro"


# ── /admin/contacts ───────────────────────────────────────────────────────────

def test_admin_contacts_requires_auth():
    r = client.get("/admin/contacts")
    assert r.status_code == 401


def test_admin_contacts_returns_list():
    r = client.get("/admin/contacts", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "contacts" in data
    assert isinstance(data["contacts"], list)


# ── /admin/retailer-applications ─────────────────────────────────────────────

def test_admin_retailer_applications_requires_auth():
    r = client.get("/admin/retailer-applications")
    assert r.status_code == 401


def test_admin_retailer_applications_with_auth():
    """Returns 200 or 503 depending on whether retailer_onboarding is installed."""
    r = client.get("/admin/retailer-applications", headers=_AUTH)
    assert r.status_code in (200, 503)


def test_admin_retailer_application_detail_requires_auth():
    r = client.get("/admin/retailer-applications/RET-00000000")
    assert r.status_code == 401


def test_admin_retailer_application_detail_with_auth_not_found():
    """Returns 404 if installed and not found, or 503 if retailer_onboarding absent."""
    r = client.get("/admin/retailer-applications/RET-00000000", headers=_AUTH)
    assert r.status_code in (404, 503)


def test_admin_approve_requires_auth():
    r = client.post("/admin/retailer-applications/RET-00000000/approve")
    assert r.status_code == 401


def test_admin_reject_requires_auth():
    r = client.post("/admin/retailer-applications/RET-00000000/reject")
    assert r.status_code == 401


def test_admin_store_credentials_requires_auth():
    r = client.get("/admin/store-credentials")
    assert r.status_code == 401


def test_admin_store_credentials_returns_summary():
    r = client.get("/admin/store-credentials", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "credentials" in data
    assert "active_catalog_size" in data
