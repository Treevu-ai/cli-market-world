"""Regression tests for the aggregate MCP telemetry credential guard."""
from __future__ import annotations

from market_core import db_save_user, ensure_db_initialized, get_db
from market_funnel import ensure_funnel_schema, record_funnel_event
from ops.mcp_credential_guard import credential_counts, has_raw_credentials


def test_credential_guard_ignores_normal_and_redacted_mcp_identities():
    ensure_db_initialized()
    ensure_funnel_schema()
    db_save_user("guard-normal-user", "test-password-hash", "guard-normal-token")
    record_funnel_event("mcp_connect", username="guard-normal-user")
    record_funnel_event("mcp_tool_call", username="redacted-mcp-key-1")
    record_funnel_event("mcp_tool_call", username="demo:guard-session")

    counts = credential_counts()

    assert counts == {}
    assert has_raw_credentials(counts) is False


def test_credential_guard_detects_api_key_like_value_without_echoing_it():
    raw_like_value = "sk-" + ("x" * 24)
    try:
        record_funnel_event("mcp_connect", username=raw_like_value)

        counts = credential_counts()

        assert counts == {"api_key": 1}
        assert has_raw_credentials(counts) is True
    finally:
        db = get_db()
        try:
            db.execute("DELETE FROM funnel_events WHERE username = ?", (raw_like_value,))
            db.commit()
        finally:
            db.close()
