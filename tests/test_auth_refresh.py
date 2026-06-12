"""P1-D auth refresh integration — login, rotate, revoke, expiry header."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_ROOT = REPO_ROOT.parent / "cli-market-core"
if CORE_ROOT.is_dir():
    sys.path.insert(0, str(CORE_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from market_core import db_save_user, ensure_db_initialized, get_db
from market_core.auth_tokens import issue_session_tokens
from market_server import app, hash_password

ensure_db_initialized()
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_users():
    db = get_db()
    db.execute("DELETE FROM app_users")
    db.commit()
    db.close()
    yield


def test_login_returns_refresh_and_expires_at():
    db_save_user("alice", hash_password("secret"), None)
    r = client.post("/auth/login", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    data = r.json()
    assert data["token"]
    assert data["refresh_token"]
    assert data["expires_at"]


def test_refresh_rotates_access_token():
    db_save_user("bob", hash_password("secret"), None)
    login = client.post("/auth/login", json={"username": "bob", "password": "secret"}).json()
    r = client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["token"] != login["token"]
    assert data["refresh_token"]


def test_revoke_invalidates_session():
    db_save_user("carol", hash_password("secret"), None)
    login = client.post("/auth/login", json={"username": "carol", "password": "secret"}).json()
    token = login["token"]
    revoke = client.post("/auth/revoke", headers={"Authorization": f"Bearer {token}"})
    assert revoke.status_code == 200
    whoami = client.get("/auth/whoami", headers={"Authorization": f"Bearer {token}"})
    assert whoami.status_code == 401


def test_expired_token_returns_x_token_expired_header():
    db_save_user("dave", hash_password("secret"), None)
    issued = issue_session_tokens("dave")
    past = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    db = get_db()
    db.execute("UPDATE app_users SET token_expires_at=? WHERE username=?", (past, "dave"))
    db.commit()
    db.close()
    r = client.get("/auth/whoami", headers={"Authorization": f"Bearer {issued['token']}"})
    assert r.status_code == 401
    assert r.headers.get("x-token-expired", "").lower() == "true"
