"""Tests for market_audit — audit log recording and querying."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_core import ensure_db_initialized, get_db

ensure_db_initialized()

import market_audit


@pytest.fixture(autouse=True)
def clean_audit():
    market_audit._schema_ready = False
    market_audit.ensure_audit_schema()
    db = get_db()
    db.execute("DELETE FROM audit_log")
    db.commit()
    db.close()
    yield


def test_ensure_schema_creates_table():
    db = get_db()
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
    ).fetchone()
    db.close()
    assert row is not None


def test_ensure_schema_idempotent():
    market_audit.ensure_audit_schema()
    market_audit.ensure_audit_schema()


def test_record_audit_basic():
    market_audit.record_audit("test_action", username="alice")
    rows = market_audit.get_audit_log(limit=10)
    assert len(rows) == 1
    assert rows[0]["username"] == "alice"
    assert rows[0]["action"] == "test_action"


def test_record_audit_with_detail():
    market_audit.record_audit(
        "vault_setup",
        username="bob",
        resource="st_abc",
        detail={"setup_token": "st_abc", "customer": "c1"},
    )
    rows = market_audit.get_audit_log(limit=10)
    assert len(rows) == 1
    assert rows[0]["resource"] == "st_abc"
    assert "st_abc" in (rows[0]["detail"] or "")


def test_record_audit_with_ip_and_ua():
    market_audit.record_audit(
        "login",
        username="eve",
        ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )
    rows = market_audit.get_audit_log(limit=10)
    assert rows[0]["ip"] == "192.168.1.1"
    assert rows[0]["user_agent"] == "Mozilla/5.0"


def test_get_audit_log_filter_by_username():
    market_audit.record_audit("a", username="alice")
    market_audit.record_audit("b", username="bob")
    market_audit.record_audit("c", username="alice")
    rows = market_audit.get_audit_log(username="alice")
    assert len(rows) == 2
    assert all(r["username"] == "alice" for r in rows)


def test_get_audit_log_filter_by_action():
    market_audit.record_audit("vault_setup", username="u1")
    market_audit.record_audit("vault_charge", username="u1")
    market_audit.record_audit("vault_setup", username="u2")
    rows = market_audit.get_audit_log(action="vault_setup")
    assert len(rows) == 2


def test_get_audit_log_limit():
    for i in range(5):
        market_audit.record_audit(f"action_{i}", username="user")
    rows = market_audit.get_audit_log(limit=3)
    assert len(rows) == 3


def test_get_audit_log_order_desc():
    market_audit.record_audit("first", username="u")
    market_audit.record_audit("second", username="u")
    rows = market_audit.get_audit_log(limit=10)
    assert rows[0]["action"] == "second"
    assert rows[1]["action"] == "first"


def test_record_audit_no_exception_on_failure():
    """record_audit should never raise — it swallows exceptions."""
    import unittest.mock as mock

    with mock.patch("market_audit.get_db", side_effect=RuntimeError("db gone")):
        market_audit.record_audit("oops", username="ghost")
