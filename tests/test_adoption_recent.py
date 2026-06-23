"""Adoption admin + noise filtering."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_funnel import ensure_funnel_schema, funnel_recent_users, is_noise_username, record_funnel_event
from market_server import app

client = TestClient(app)


def test_is_noise_username():
    assert is_noise_username("smoke1780946263")
    assert is_noise_username("deploy-test-user")
    # Known test accounts are noise
    assert is_noise_username("user-87db316c7763")
    assert is_noise_username("user-a8d64197d3a4")
    # Real public registrations (user-<hex>) are NOT noise
    assert not is_noise_username("user-e1a725b9acac")
    assert not is_noise_username("user-f8e0ed09eb3b")
    assert not is_noise_username("user-4477834e4371")
    assert not is_noise_username("acubatruweb")


def test_funnel_recent_users_filters_noise():
    ensure_funnel_schema()
    record_funnel_event("register", username="acubatruweb", dedupe=True)
    record_funnel_event("first_search", username="acubatruweb", dedupe=True)
    record_funnel_event("register", username="smoke-test-1", dedupe=True)

    users = funnel_recent_users(hours=24 * 90, limit=20, exclude_noise=True)
    names = {u["username"] for u in users}
    assert "acubatruweb" in names
    assert "smoke-test-1" not in names
    if users:
        real = next(u for u in users if u["username"] == "acubatruweb")
        assert real["has_search"] is True


def test_dashboard_adoption_recent_requires_admin(monkeypatch):
    import server_deps

    monkeypatch.setenv("MARKET_API_TOKEN", "admin-test-token")
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "admin-test-token")
    r = client.get("/dashboard/adoption/recent?days=30")
    assert r.status_code == 401
    r2 = client.get(
        "/dashboard/adoption/recent?days=30",
        headers={"Authorization": "Bearer admin-test-token"},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert "users" in body
    assert body.get("noise_filter") is True