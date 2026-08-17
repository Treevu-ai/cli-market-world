"""P3 funnel instrumentation + PAM tier 1.5 synthetic journey."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_core import db_save_user, ensure_db_initialized, get_db
from market_funnel import ensure_funnel_schema, funnel_summary, is_noise_meta, record_funnel_event
from market_server import app
from server_deps import hash_password

ensure_db_initialized()
ensure_funnel_schema()
client = TestClient(app)


def test_record_and_summary():
    record_funnel_event("register", username="u-funnel-1", dedupe=True)
    record_funnel_event("first_search", username="u-funnel-1", dedupe=True)
    record_funnel_event("request_pro", username="u-funnel-1")
    record_funnel_event("activated", username="u-funnel-1", dedupe=True)
    data = funnel_summary(days=30)
    assert data["events"]["register"] >= 1
    assert len(data["funnel_steps"]) >= 3


def test_v1_events_endpoint():
    r = client.post("/v1/events", json={"event": "install", "session_id": "test-sess"})
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_install_dedupe_by_session_id():
    sid = "install-dedupe-sess-1"
    first = client.post(
        "/v1/events",
        json={"event": "install", "session_id": sid, "dedupe": True, "meta": {"source": "test"}},
    )
    second = client.post(
        "/v1/events",
        json={"event": "install", "session_id": sid, "dedupe": True, "meta": {"source": "test"}},
    )
    assert first.status_code == 200
    assert first.json().get("ok") is True
    assert second.json().get("deduped") is True


def test_tutorial_and_mcp_setup_events():
    r1 = client.post(
        "/v1/events",
        json={"event": "tutorial_completed", "session_id": "tutorial-sess", "meta": {"demo": True}},
    )
    r2 = client.post(
        "/v1/events",
        json={"event": "mcp_setup_completed", "session_id": "mcp-sess", "meta": {"ide": "cursor"}},
    )
    assert r1.status_code == 200 and r1.json().get("ok") is True
    assert r2.status_code == 200 and r2.json().get("ok") is True
    data = funnel_summary(days=30)
    assert data["events"].get("tutorial_completed", 0) >= 1
    assert data["events"].get("mcp_setup_completed", 0) >= 1


def test_mcp_tool_call_event():
    r = client.post(
        "/v1/events",
        json={
            "event": "mcp_tool_call",
            "dedupe": False,
            "meta": {"tool": "market_search", "success": True, "source": "mcp_client"},
        },
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True
    data = funnel_summary(days=30)
    assert data["events"].get("mcp_tool_call", 0) >= 1


def test_v1_events_ignores_untrusted_body_username_that_looks_like_local_credentials_path():
    suspicious = r"c:\Users\acuba\Downloads\CREDENCIALES MARKET RICARDO CUBA.txt aqui mis credenciaes"

    r = client.post(
        "/v1/events",
        json={
            "event": "mcp_tool_call",
            "username": suspicious,
            "meta": {"tool": "market_search", "source": "mcp_client"},
        },
    )

    assert r.status_code == 200
    db = get_db()
    try:
        row = db.execute(
            "SELECT username FROM funnel_events WHERE event='mcp_tool_call' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        db.close()
    assert row is not None
    assert row["username"] is None


def test_v1_events_keeps_known_body_username_when_no_auth_header_is_present():
    db_save_user("funnel-known-user", hash_password("market"), "funnel-known-token")

    r = client.post(
        "/v1/events",
        json={
            "event": "mcp_tool_call",
            "username": "funnel-known-user",
            "meta": {"tool": "market_search", "source": "mcp_client"},
        },
    )

    assert r.status_code == 200
    db = get_db()
    try:
        row = db.execute(
            "SELECT username FROM funnel_events WHERE event='mcp_tool_call' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        db.close()
    assert row is not None
    assert row["username"] == "funnel-known-user"


def test_starter_subscribe_event():
    r = client.post(
        "/v1/events",
        json={"event": "starter_subscribe", "session_id": "landing-sess", "meta": {"source": "test"}},
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True
    data = funnel_summary(days=30)
    assert data["events"].get("starter_subscribe", 0) >= 1
    steps = [s["step"] for s in data["funnel_steps"]]
    assert "starter_subscribe" in steps


def test_is_noise_meta():
    assert is_noise_meta({"source": "test"}) is True
    assert is_noise_meta({"source": "ci"}) is True
    assert is_noise_meta({"source": "smoke"}) is True
    assert is_noise_meta({"source": "mcp_client"}) is False
    assert is_noise_meta({"source": "landing"}) is False
    assert is_noise_meta(None) is False
    assert is_noise_meta({}) is False
    assert is_noise_meta('{"source": "test"}') is True
    assert is_noise_meta('{"source": "real"}') is False


def test_funnel_summary_exclude_noise_filters_test_meta():
    record_funnel_event("register", username="noise-meta-user", meta={"source": "test"})
    with_noise = funnel_summary(days=30, exclude_noise=False)
    without_noise = funnel_summary(days=30, exclude_noise=True)
    assert with_noise["events"]["register"] >= without_noise["events"]["register"]


def test_analytics_funnel_public():
    r = client.get("/analytics/funnel")
    assert r.status_code == 200
    body = r.json()
    assert "funnel_steps" in body
    assert "ttfv_median_minutes" in body


def _register_with_email(email: str) -> dict:
    """Complete the 2-step registration flow for tests."""
    from routers.auth import _hash_code
    from market_core import get_db

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


def test_pam_journey_synthetic():
    """PAM tier 1.5 — market init path: register → whoami → search → account."""
    reg_data = _register_with_email("pam-journey@example.com")
    key = reg_data["api_key"]
    headers = {"Authorization": f"Bearer {key}"}

    who = client.get("/auth/whoami", headers=headers)
    assert who.status_code == 200
    assert who.json().get("tier") == "free"

    search = client.post(
        "/products/search",
        json={"query": "leche", "limit": 3, "country": "PE"},
        headers=headers,
    )
    assert search.status_code == 200

    acct = client.get("/auth/account?lang=en", headers=headers)
    assert acct.status_code == 200
    body = acct.json()
    assert body["tier"] == "free"
    assert "usage" in body
    assert body["upgrade"]["next_tier"] == "pro"