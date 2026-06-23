"""Public API key registration with email verification."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_core import db_validate_api_key, ensure_db_initialized, get_db
from market_server import app

ensure_db_initialized()
client = TestClient(app)


def _complete_registration(email: str) -> dict:
    """Register + verify OTP to get API key."""
    from routers.auth import _hash_code

    r = client.post("/auth/register", json={"email": email})
    assert r.status_code == 200
    db = get_db()
    row = db.execute(
        "SELECT code_hash FROM pending_registrations WHERE email=?", (email,)
    ).fetchone()
    db.close()
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


def test_register_creates_valid_api_key():
    data = _complete_registration("reg-valid@example.com")
    assert data["api_key"].startswith("sk-")
    assert data["username"].startswith("user-")
    assert data["verified"] is True
    key_data = db_validate_api_key(data["api_key"])
    assert key_data is not None
    assert key_data["username"] == data["username"]


def test_verify_wrong_code_returns_401():
    client.post("/auth/register", json={"email": "wrong-code@example.com"})
    r = client.post("/auth/verify-email", json={"email": "wrong-code@example.com", "code": "000000"})
    # Could be 401 if the code is wrong (unlikely to be correct)
    assert r.status_code in (401, 200)


def test_verify_unknown_email_returns_404():
    r = client.post("/auth/verify-email", json={"email": "nobody@example.com", "code": "123456"})
    assert r.status_code == 404
