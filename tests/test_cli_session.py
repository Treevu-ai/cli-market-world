"""CLI session persistence after login."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_core


@pytest.fixture(autouse=True)
def clear_session():
    if market_core.SESSION_FILE.exists():
        market_core.SESSION_FILE.unlink()
    yield
    if market_core.SESSION_FILE.exists():
        market_core.SESSION_FILE.unlink()


def test_save_session_writes_file():
    market_core.save_session("admin", "sess-abc")
    assert market_core.SESSION_FILE.exists()
    saved = json.loads(market_core.SESSION_FILE.read_text(encoding="utf-8"))
    assert saved == {"username": "admin", "token": "sess-abc"}
    assert market_core.get_token() == "sess-abc"


def test_api_persists_session_on_login(monkeypatch):
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {
        "message": "Autenticado",
        "username": "admin",
        "token": "sess-login-1",
    }
    monkeypatch.setattr(market_core.httpx, "post", lambda *a, **k: fake_resp)

    data = market_core.api("POST", "/auth/login", {"username": "admin", "password": "market"})
    assert data["token"] == "sess-login-1"
    assert market_core.get_token() == "sess-login-1"


def test_api_sends_bearer_for_protected_routes(monkeypatch):
    market_core.save_session("admin", "sess-xyz")
    captured = {}

    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"username": "admin"}

    def fake_get(url, headers=None, timeout=30):
        captured["headers"] = headers
        return fake_resp

    monkeypatch.setattr(market_core.httpx, "get", fake_get)
    market_core.api("GET", "/auth/whoami")
    assert captured["headers"]["Authorization"] == "Bearer sess-xyz"
