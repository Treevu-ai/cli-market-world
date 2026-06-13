"""Tests for routers/admin.py — admin-only ops endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from market_core import db_save_user, db_set_subscription, ensure_db_initialized, get_db
from market_server import app, hash_password

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)


# ── GET /admin/debug-fetch ────────────────────────────────────────────────────

def test_debug_fetch_requires_auth():
    r = client.get("/admin/debug-fetch")
    assert r.status_code == 401


def test_debug_fetch_no_token_returns_503_or_401():
    # When DEFAULT_TOKEN is empty, require_admin returns 503
    import server_deps as sd
    old = sd.DEFAULT_TOKEN
    sd.DEFAULT_TOKEN = ""
    try:
        r = client.get("/admin/debug-fetch")
        assert r.status_code in (401, 503)
    finally:
        sd.DEFAULT_TOKEN = old


def test_debug_fetch_with_auth_returns_results():
    mock_fetch = AsyncMock(return_value=[])
    with patch("routers.admin.fetch_store", mock_fetch):
        r = client.get("/admin/debug-fetch?store=wong&query=leche", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["store"] == "wong"
    assert data["query"] == "leche"
    assert "results" in data
    assert "products" in data


# ── POST /v1/admin/set-tier ───────────────────────────────────────────────────

def test_set_tier_requires_auth():
    r = client.post("/v1/admin/set-tier", json={"username": "admin", "tier": "pro"})
    assert r.status_code == 401


def test_set_tier_invalid_tier_returns_400():
    r = client.post(
        "/v1/admin/set-tier",
        json={"username": "admin", "tier": "superadmin"},
        headers=_AUTH,
    )
    assert r.status_code == 400


def test_set_tier_unknown_user_returns_404():
    r = client.post(
        "/v1/admin/set-tier",
        json={"username": "ghost_user_xyz", "tier": "pro"},
        headers=_AUTH,
    )
    assert r.status_code == 404


def test_set_tier_missing_username_returns_400():
    r = client.post("/v1/admin/set-tier", json={"tier": "pro"}, headers=_AUTH)
    assert r.status_code == 400


def test_set_tier_success():
    r = client.post(
        "/v1/admin/set-tier",
        json={"username": "admin", "tier": "free"},
        headers=_AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "admin"
    assert "subscription" in data


# ── POST /v1/admin/revoke-api-key ─────────────────────────────────────────────

def test_revoke_api_key_requires_auth():
    r = client.post("/v1/admin/revoke-api-key", json={"api_key": "sk-test"})
    assert r.status_code == 401


def test_revoke_api_key_missing_key_returns_400():
    r = client.post("/v1/admin/revoke-api-key", json={}, headers=_AUTH)
    assert r.status_code == 400


def test_revoke_api_key_unknown_returns_404():
    r = client.post(
        "/v1/admin/revoke-api-key",
        json={"api_key": "sk-nonexistentkey99999"},
        headers=_AUTH,
    )
    assert r.status_code == 404


# ── POST /admin/activate-pro-request ─────────────────────────────────────────

def test_activate_pro_request_requires_auth():
    r = client.post("/admin/activate-pro-request", json={"request_id": "PRO-12345678"})
    assert r.status_code == 401


def test_activate_pro_request_invalid_prefix_returns_400():
    r = client.post(
        "/admin/activate-pro-request",
        json={"request_id": "NOTPRO-12345678"},
        headers=_AUTH,
    )
    assert r.status_code == 400


def test_activate_pro_request_not_found_returns_404():
    r = client.post(
        "/admin/activate-pro-request",
        json={"request_id": "PRO-XXXXXXXX"},
        headers=_AUTH,
    )
    assert r.status_code == 404


# ── POST /admin/resend-pro-activation-email ───────────────────────────────────

def test_resend_pro_email_requires_auth():
    r = client.post("/admin/resend-pro-activation-email", json={"request_id": "PRO-12345678"})
    assert r.status_code == 401


def test_resend_pro_email_invalid_prefix_returns_400():
    r = client.post(
        "/admin/resend-pro-activation-email",
        json={"request_id": "BAD-12345678"},
        headers=_AUTH,
    )
    assert r.status_code == 400


def test_resend_pro_email_not_found_returns_404():
    r = client.post(
        "/admin/resend-pro-activation-email",
        json={"request_id": "PRO-NOTFOUND0"},
        headers=_AUTH,
    )
    assert r.status_code == 404


# ── POST /admin/collect ───────────────────────────────────────────────────────

def test_collect_requires_auth():
    r = client.post("/admin/collect")
    assert r.status_code == 401


def test_collect_handles_missing_module():
    """collect_prices module may not be installed — returns graceful fallback."""
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "collect_prices":
            raise ImportError("collect_prices not available")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        r = client.post("/admin/collect?stores=0&queries=0", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is False
    assert "error" in data


# ── POST /v1/admin/scan-stores ────────────────────────────────────────────────

def test_scan_stores_requires_auth():
    r = client.post("/v1/admin/scan-stores", json={})
    assert r.status_code == 401


def test_scan_stores_returns_structure():
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_resp)

    with patch("routers.admin.httpx.AsyncClient", return_value=mock_client):
        r = client.post("/v1/admin/scan-stores", json={}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "scanned" in data
    assert "working" in data
    assert "candidates" in data


# ── POST /admin/cron/funnel-digest ────────────────────────────────────────────

def test_funnel_digest_requires_auth():
    r = client.post("/admin/cron/funnel-digest")
    assert r.status_code == 401


def test_funnel_digest_slack_not_configured_returns_503():
    import sys
    import types

    fake_billing_slack = types.ModuleType("billing_slack")
    fake_billing_slack.format_funnel_digest_message = lambda **kw: "preview text"
    fake_billing_slack.notify_funnel_digest = lambda **kw: False  # Slack not configured

    original = sys.modules.get("billing_slack")
    sys.modules["billing_slack"] = fake_billing_slack
    try:
        r = client.post("/admin/cron/funnel-digest", headers=_AUTH)
        assert r.status_code == 503
    finally:
        if original is None:
            sys.modules.pop("billing_slack", None)
        else:
            sys.modules["billing_slack"] = original


# ── POST /admin/cron/adoption-index ──────────────────────────────────────────

def test_adoption_index_requires_auth():
    r = client.post("/admin/cron/adoption-index")
    assert r.status_code == 401


def test_adoption_index_with_auth():
    mock_payload = {"score": 42, "grade": "B"}
    mock_saved = {"id": 1}
    with (
        patch("market_adoption_index.compute_adoption_index", return_value=mock_payload),
        patch("market_adoption_index.persist_snapshot", return_value=mock_saved),
    ):
        r = client.post("/admin/cron/adoption-index", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["score"] == 42


# ── POST /admin/cron/indicators-refresh ──────────────────────────────────────

def test_indicators_refresh_requires_auth():
    r = client.post("/admin/cron/indicators-refresh")
    assert r.status_code == 401


def test_indicators_refresh_with_auth():
    mock_result = {"updated": 3}
    with (
        patch("market_indicators.refresh_after_collection", return_value=mock_result),
        patch("market_indicators.refresh_indicators", return_value=mock_result),
    ):
        r = client.post("/admin/cron/indicators-refresh", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_indicators_refresh_with_country():
    mock_result = {"updated": 1}
    with patch("market_indicators.refresh_indicators", return_value=mock_result):
        r = client.post("/admin/cron/indicators-refresh?country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["country"] == "PE"
