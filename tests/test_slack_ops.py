"""Tests for routers/slack_ops.py — Slack interactivity endpoint."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from market_server import app

ensure_db_initialized()
client = TestClient(app)

_SECRET = "test-slack-signing-secret"
_SLACK_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def _make_signature(body: bytes, ts: str, secret: str = _SECRET) -> str:
    base = f"v0:{ts}:{body.decode()}"
    return "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()


def _slack_body(action_id: str = "activate_pro_request", value: str = "PRO-ABCD1234") -> bytes:
    payload = json.dumps({
        "type": "block_actions",
        "user": {"id": "U123456"},
        "actions": [{"action_id": action_id, "value": value}],
    })
    return urlencode({"payload": payload}).encode()


# ── No secret configured ─────────────────────────────────────────────────────

def test_slack_no_secret_returns_503(monkeypatch):
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    r = client.post("/slack/interactions", content=b"payload=x", headers=_SLACK_HEADERS)
    assert r.status_code == 503


# ── Signature verification ────────────────────────────────────────────────────

def test_slack_invalid_signature_returns_401(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", _SECRET)
    ts = str(int(time.time()))
    r = client.post(
        "/slack/interactions",
        content=b"payload=x",
        headers={**_SLACK_HEADERS, "X-Slack-Request-Timestamp": ts, "X-Slack-Signature": "v0=bad"},
    )
    assert r.status_code == 401


def test_slack_expired_timestamp_returns_401(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", _SECRET)
    stale = str(int(time.time()) - 400)  # 6+ minutes ago
    body = b"payload=x"
    sig = _make_signature(body, stale)
    r = client.post(
        "/slack/interactions",
        content=body,
        headers={**_SLACK_HEADERS, "X-Slack-Request-Timestamp": stale, "X-Slack-Signature": sig},
    )
    assert r.status_code == 401


def test_slack_missing_timestamp_returns_401(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", _SECRET)
    r = client.post(
        "/slack/interactions",
        content=b"payload=x",
        headers={**_SLACK_HEADERS, "X-Slack-Signature": "v0=anything"},
    )
    assert r.status_code == 401


# ── Payload routing (all with valid signatures) ───────────────────────────────

def _post_slack(body: bytes, monkeypatch) -> dict:
    monkeypatch.setenv("SLACK_SIGNING_SECRET", _SECRET)
    ts = str(int(time.time()))
    sig = _make_signature(body, ts)
    r = client.post(
        "/slack/interactions",
        content=body,
        headers={**_SLACK_HEADERS, "X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig},
    )
    assert r.status_code == 200
    return r.json()


def test_slack_non_block_actions_type_is_ok(monkeypatch):
    payload = json.dumps({"type": "shortcut"})
    body = urlencode({"payload": payload}).encode()
    data = _post_slack(body, monkeypatch)
    assert data.get("ok") is True


def test_slack_unknown_action_id_is_ok(monkeypatch):
    body = _slack_body(action_id="some_other_action")
    data = _post_slack(body, monkeypatch)
    assert data.get("ok") is True


def test_slack_invalid_pro_ref_returns_ephemeral(monkeypatch):
    body = _slack_body(value="NOTPRO-123")
    data = _post_slack(body, monkeypatch)
    assert data.get("response_type") == "ephemeral"
    assert "inválida" in data.get("text", "").lower() or "inv" in data.get("text", "").lower()


def test_slack_unauthorized_user_blocked(monkeypatch):
    # Ensure user-restriction check is active (DEFAULT_TOKEN must be truthy)
    monkeypatch.setattr("routers.slack_ops.DEFAULT_TOKEN", "test-token-123")
    monkeypatch.setenv("SLACK_ACTIVATE_PRO_USERS", "U_ALLOWED")
    import routers.slack_ops as _slack_mod
    monkeypatch.setattr(_slack_mod, "DEFAULT_TOKEN", "test-token-123")
    body = _slack_body(value="PRO-ABCD1234")
    data = _post_slack(body, monkeypatch)
    assert data.get("response_type") == "ephemeral"
    assert "autorizado" in data.get("text", "").lower()


def test_slack_valid_pro_ref_not_found_returns_ephemeral(monkeypatch):
    monkeypatch.delenv("SLACK_ACTIVATE_PRO_USERS", raising=False)
    body = _slack_body(value="PRO-NOTFOUND")
    data = _post_slack(body, monkeypatch)
    # PRO-NOTFOUND does not exist in DB → activation fails → ephemeral response
    assert data.get("response_type") == "ephemeral"
