"""Tests for _compute_dashboard_data_locked's lock-timeout fallback.

Regression coverage for the 2026-08-10 incident: a request that died
mid-compute left its session holding the Postgres advisory lock, hanging
every subsequent request to /dashboard/data indefinitely. The fix adds a
lock_timeout and a stale-cache fallback — these tests exercise that path
directly (PG-only code, so it's skipped locally unless USE_PG is patched).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

import routers.dashboard as dashboard


class _FakeDb:
    def __init__(self, *, fail_on_lock: bool):
        self.fail_on_lock = fail_on_lock
        self.executed: list[str] = []

    def execute(self, sql, params=None):
        self.executed.append(sql)
        if "pg_advisory_lock" in sql and self.fail_on_lock:
            raise Exception("canceling statement due to lock timeout")
        return MagicMock()

    def rollback(self):
        pass

    def close(self):
        pass


def test_lock_timeout_falls_back_to_stale_cache():
    fake_db = _FakeDb(fail_on_lock=True)
    with patch.object(dashboard, "get_db", return_value=fake_db), \
         patch("market_core.USE_PG", True), \
         patch.object(dashboard, "_load_shared_dashboard_cache", return_value={"stale": True}) as m_load:
        result = dashboard._compute_dashboard_data_locked()

    assert result == {"stale": True}
    # Must be asked for a stale payload (ignore_ttl), not just a fresh hit.
    assert any(call.kwargs.get("ignore_ttl") for call in m_load.call_args_list)
    assert any("lock_timeout" in sql for sql in fake_db.executed)


def test_lock_timeout_with_no_cache_raises_503():
    fake_db = _FakeDb(fail_on_lock=True)
    with patch.object(dashboard, "get_db", return_value=fake_db), \
         patch("market_core.USE_PG", True), \
         patch.object(dashboard, "_load_shared_dashboard_cache", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            dashboard._compute_dashboard_data_locked()

    assert exc_info.value.status_code == 503


def test_lock_acquired_propagates_real_errors():
    """A failure AFTER the lock is acquired is a real bug — must not be
    swallowed into a fake 503/stale-cache response."""
    fake_db = _FakeDb(fail_on_lock=False)
    with patch.object(dashboard, "get_db", return_value=fake_db), \
         patch("market_core.USE_PG", True), \
         patch.object(dashboard, "_load_shared_dashboard_cache", return_value=None), \
         patch.object(dashboard, "_dashboard_data", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            dashboard._compute_dashboard_data_locked()
