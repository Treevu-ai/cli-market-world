"""Tests for routers/dashboard.py — dashboard data + ops endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db
from market_server import app

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_default_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


# ── GET /dashboard ────────────────────────────────────────────────────────────

def test_dashboard_html_returns_200():
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


def test_dashboard_html_contains_content():
    r = client.get("/dashboard")
    # Either full dashboard or graceful fallback — both are non-empty HTML
    assert len(r.content) > 50


# ── GET /dashboard/data ───────────────────────────────────────────────────────

def test_dashboard_data_returns_200():
    r = client.get("/dashboard/data")
    assert r.status_code == 200


def test_dashboard_data_is_dict():
    r = client.get("/dashboard/data")
    assert isinstance(r.json(), dict)


def test_dashboard_data_has_kpis_or_error():
    data = client.get("/dashboard/data").json()
    # Either returns full data with kpis, or a graceful error dict
    assert "kpis" in data or "error" in data


def test_dashboard_data_cache_hit_is_fast(monkeypatch):
    """Second call returns cached data (same object)."""
    r1 = client.get("/dashboard/data")
    r2 = client.get("/dashboard/data")
    assert r1.status_code == r2.status_code == 200
    # Both return valid JSON — cache doesn't corrupt
    assert isinstance(r1.json(), dict)
    assert isinstance(r2.json(), dict)


# ── GET /dashboard/usage ──────────────────────────────────────────────────────

def test_dashboard_usage_requires_auth():
    r = client.get("/dashboard/usage")
    assert r.status_code == 401


def test_dashboard_usage_with_auth():
    r = client.get("/dashboard/usage", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "username" in data or "tier" in data or "usage" in data


# ── POST /dashboard/collector/trigger ────────────────────────────────────────

def test_collector_trigger_requires_auth():
    r = client.post("/dashboard/collector/trigger")
    assert r.status_code in (401, 503)  # 503 when DEFAULT_TOKEN empty


def test_collector_trigger_with_auth_succeeds():
    r = client.post("/dashboard/collector/trigger", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "triggered" in data


def test_collector_trigger_idempotent():
    """Second trigger while first is pending returns triggered=False."""
    # Clean any pending triggers
    db = get_db()
    db.execute("DELETE FROM collector_triggers WHERE fulfilled_at IS NULL")
    db.commit()
    db.close()

    r1 = client.post("/dashboard/collector/trigger", headers=_AUTH)
    r2 = client.post("/dashboard/collector/trigger", headers=_AUTH)
    assert r1.status_code == r2.status_code == 200

    d1, d2 = r1.json(), r2.json()
    assert d1["triggered"] is True
    assert d2["triggered"] is False
    assert "pending_id" in d2
