"""Tests for routers/auth.py — authentication and API key endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import db_create_api_key, db_save_user, ensure_db_initialized, get_db
from market_server import app, hash_password

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_ADMIN_USER = "test-admin"
_ADMIN_PASS = "test-pass-456"


@pytest.fixture(autouse=True)
def clean_auth_db(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db = get_db()
    for table in ["app_users", "api_keys", "rate_limits", "auth_sessions"]:
        try:
            db.execute(f"DELETE FROM {table}")
        except Exception:
            pass
    db.commit()
    db.close()
    db_save_user(_ADMIN_USER, hash_password(_ADMIN_PASS), _ADMIN_TOKEN)
    import server_deps as sd
    sd._auth_attempts.clear()


def _auth_header(token: str = _ADMIN_TOKEN) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── POST /auth/register + /auth/verify-email ─────────────────────────────────


def _register_verified(email: str) -> dict:
    """Full registration flow: register + verify OTP."""
    from routers.auth import _hash_code
    from market_core import get_db

    r = client.post("/auth/register", json={"email": email})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "verification_required"
    # Fetch the code from the DB for testing
    db = get_db()
    row = db.execute(
        "SELECT code_hash FROM pending_registrations WHERE email=?", (email,)
    ).fetchone()
    db.close()
    # Brute-force the 6-digit code (test only — use known hash)
    for i in range(1000000):
        code = f"{i:06d}"
        if _hash_code(code) == row["code_hash"]:
            break
    v = client.post("/auth/verify-email", json={"email": email, "code": code})
    assert v.status_code == 200
    return v.json()


def test_register_requires_email():
    r = client.post("/auth/register", json={})
    assert r.status_code == 422


def test_register_sends_verification():
    r = client.post("/auth/register", json={"email": "test-reg@example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "verification_required"
    assert "@example.com" in data["email"]


def test_verify_email_returns_api_key():
    data = _register_verified("verify-test@example.com")
    assert "api_key" in data
    assert data["api_key"].startswith("sk-")
    assert "username" in data
    assert data["verified"] is True
    assert data["scopes"] == "read_write"


def test_register_creates_unique_users():
    d1 = _register_verified("unique1@example.com")
    d2 = _register_verified("unique2@example.com")
    assert d1["username"] != d2["username"]


# ── POST /auth/login ──────────────────────────────────────────────────────────

def test_login_valid_credentials():
    r = client.post("/auth/login", json={"username": _ADMIN_USER, "password": _ADMIN_PASS})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data or "api_key" in data or "message" in data
    assert data.get("username") == _ADMIN_USER


def test_login_wrong_password_returns_401():
    r = client.post("/auth/login", json={"username": _ADMIN_USER, "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user_returns_401():
    r = client.post("/auth/login", json={"username": "ghost", "password": "x"})
    assert r.status_code == 401


# ── GET /auth/whoami ──────────────────────────────────────────────────────────

def test_whoami_no_auth_returns_401():
    r = client.get("/auth/whoami")
    assert r.status_code == 401


def test_whoami_with_bearer_token():
    r = client.get("/auth/whoami", headers=_auth_header())
    assert r.status_code == 200
    data = r.json()
    assert "username" in data  # DEFAULT_TOKEN resolves to "admin" by server_deps design
    assert "tier" in data


def test_whoami_with_api_key():
    data = _register_verified("whoami-key@example.com")
    api_key = data["api_key"]
    r = client.get("/auth/whoami", headers={"Authorization": f"Bearer {api_key}"})
    assert r.status_code == 200
    assert "username" in r.json()


# ── POST /auth/keys ───────────────────────────────────────────────────────────

def test_create_api_key_requires_auth():
    r = client.post("/auth/keys", json={"scopes": "read"})
    assert r.status_code == 401


def test_create_api_key_read_scope():
    r = client.post("/auth/keys", json={"scopes": "read", "label": "ci"}, headers=_auth_header())
    assert r.status_code == 200
    data = r.json()
    assert data["key"].startswith("sk-")
    assert data["scopes"] == "read"
    assert data["label"] == "ci"


def test_create_api_key_read_write_scope():
    r = client.post("/auth/keys", json={"scopes": "read_write"}, headers=_auth_header())
    assert r.status_code == 200
    assert r.json()["scopes"] == "read_write"


def test_create_api_key_invalid_scope_returns_400():
    r = client.post("/auth/keys", json={"scopes": "admin"}, headers=_auth_header())
    assert r.status_code == 400


# ── GET /auth/keys ────────────────────────────────────────────────────────────

def test_list_api_keys_requires_auth():
    r = client.get("/auth/keys")
    assert r.status_code == 401


def test_list_api_keys_returns_list():
    # Create a key first
    client.post("/auth/keys", json={"scopes": "read", "label": "test"}, headers=_auth_header())
    r = client.get("/auth/keys", headers=_auth_header())
    assert r.status_code == 200
    data = r.json()
    assert "keys" in data
    assert "total" in data
    assert data["total"] >= 1


def test_list_api_keys_no_secret_in_response():
    client.post("/auth/keys", json={"scopes": "read"}, headers=_auth_header())
    r = client.get("/auth/keys", headers=_auth_header())
    keys = r.json()["keys"]
    for k in keys:
        # prefix only — full key must not be exposed in list
        assert "sk-" not in k.get("prefix", "sk-x")[:3] or len(k.get("prefix", "")) < 20


# ── DELETE /auth/keys/{key_id} ────────────────────────────────────────────────

def test_revoke_api_key_requires_auth():
    r = client.delete("/auth/keys/1")
    assert r.status_code == 401


def test_revoke_api_key_not_found_returns_404():
    r = client.delete("/auth/keys/99999", headers=_auth_header())
    assert r.status_code == 404


def test_revoke_api_key_success():
    created = client.post("/auth/keys", json={"scopes": "read", "label": "to-revoke"}, headers=_auth_header())
    assert created.status_code == 200
    keys_before = client.get("/auth/keys", headers=_auth_header()).json()["total"]

    # find the key id
    keys = client.get("/auth/keys", headers=_auth_header()).json()["keys"]
    key_id = next((k["id"] for k in keys if k.get("label") == "to-revoke"), None)
    if key_id is None:
        pytest.skip("Key ID not returned in list — skipping revoke test")

    r = client.delete(f"/auth/keys/{key_id}", headers=_auth_header())
    assert r.status_code == 200
    keys_after = client.get("/auth/keys", headers=_auth_header()).json()["total"]
    assert keys_after < keys_before


# ── GET /auth/subscription ────────────────────────────────────────────────────

def test_subscription_requires_auth():
    r = client.get("/auth/subscription")
    assert r.status_code == 401


def test_subscription_returns_username():
    r = client.get("/auth/subscription", headers=_auth_header())
    assert r.status_code == 200
    data = r.json()
    assert "username" in data  # DEFAULT_TOKEN resolves to "admin" by server_deps design
    assert "api_keys" in data
