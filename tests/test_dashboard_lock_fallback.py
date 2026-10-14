"""Tests for _compute_dashboard_data_locked's lock-timeout fallback, and for
_run_dashboard_compute_bounded's compute-timeout fallback.

Regression coverage for the 2026-08-10 incident: a request that died
mid-compute left its session holding the Postgres advisory lock, hanging
every subsequent request to /dashboard/data indefinitely. The fix adds a
lock_timeout and a stale-cache fallback — these tests exercise that path
directly (PG-only code, so it's skipped locally unless USE_PG is patched).

Also covers the 2026-09-08 follow-up (cli-market-world#563): the lock_timeout
only bounded the *wait to acquire* the lock — _dashboard_data() itself, once
the lock was held, could still run unbounded and block the worker (observed
live: one machine's own /health failed ~30s during a slow compute). Same
stale-cache-fallback pattern, now covering the compute itself too.
"""

from __future__ import annotations

import time
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


def test_lock_holder_bounds_idle_in_transaction_time():
    """Regression for the 2026-09-11 orphaned-advisory-lock incident:
    lock_db's own connection sits idle-in-transaction for the whole compute
    window (the real work runs on a different connection, in
    _run_dashboard_compute_bounded's background thread). Confirmed live
    that idle_in_transaction_session_timeout was 0 (disabled) at the DB
    level, so an abandoned lock_db session (process killed, unhandled
    exception) held the advisory lock forever until a deploy restarted the
    process. Must bound this session's own idle time so Postgres reclaims
    it (and releases the lock) on its own."""
    fake_db = _FakeDb(fail_on_lock=False)
    with patch.object(dashboard, "get_db", return_value=fake_db), \
         patch("market_core.USE_PG", True), \
         patch.object(dashboard, "_load_shared_dashboard_cache", return_value={"cached": True}):
        dashboard._compute_dashboard_data_locked()

    assert any("idle_in_transaction_session_timeout" in sql for sql in fake_db.executed)


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


def test_compute_timeout_falls_back_to_stale_cache(monkeypatch):
    monkeypatch.setattr(dashboard, "_DASHBOARD_COMPUTE_TIMEOUT_S", 0.05)
    monkeypatch.setattr(dashboard, "_dashboard_data", lambda: time.sleep(0.15))
    with patch.object(dashboard, "_load_shared_dashboard_cache", return_value={"stale": True}) as m_load, \
         patch.object(dashboard, "_save_shared_dashboard_cache") as m_save:
        result = dashboard._run_dashboard_compute_bounded()

        assert result == {"stale": True}
        assert any(call.kwargs.get("ignore_ttl") for call in m_load.call_args_list)
        # The slow compute keeps running in the background -- it must not be
        # saved to cache synchronously as if it had completed in time.
        m_save.assert_not_called()
        time.sleep(0.2)  # let the background thread + its callback finish
        # inside this test's own patch scope, so it can't leak into another
        # test's mocks once this `with` block exits.


def test_compute_timeout_with_no_cache_raises_503(monkeypatch):
    monkeypatch.setattr(dashboard, "_DASHBOARD_COMPUTE_TIMEOUT_S", 0.05)
    monkeypatch.setattr(dashboard, "_dashboard_data", lambda: time.sleep(0.15))
    with patch.object(dashboard, "_load_shared_dashboard_cache", return_value=None), \
         patch.object(dashboard, "_save_shared_dashboard_cache"):
        with pytest.raises(HTTPException) as exc_info:
            dashboard._run_dashboard_compute_bounded()
        assert exc_info.value.status_code == 503
        time.sleep(0.2)  # see comment above


def test_compute_real_error_still_propagates(monkeypatch):
    """Same principle as test_lock_acquired_propagates_real_errors: a real
    bug in _dashboard_data() (not a timeout) must not be swallowed into a
    stale-cache/503 response."""
    monkeypatch.setattr(dashboard, "_dashboard_data", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with patch.object(dashboard, "_load_shared_dashboard_cache", return_value={"stale": True}):
        with pytest.raises(RuntimeError, match="boom"):
            dashboard._run_dashboard_compute_bounded()


def test_slow_compute_still_populates_cache_for_next_request(monkeypatch):
    """The timed-out compute isn't cancelled -- once it finishes in the
    background, it should still save to the shared cache so the *next*
    request benefits, even though this one already fell back to stale."""
    monkeypatch.setattr(dashboard, "_DASHBOARD_COMPUTE_TIMEOUT_S", 0.05)
    monkeypatch.setattr(dashboard, "_dashboard_data", lambda: (time.sleep(0.2), {"fresh": True})[1])
    with patch.object(dashboard, "_load_shared_dashboard_cache", return_value={"stale": True}), \
         patch.object(dashboard, "_save_shared_dashboard_cache") as m_save:
        result = dashboard._run_dashboard_compute_bounded()
        assert result == {"stale": True}
        m_save.assert_not_called()
        time.sleep(0.3)  # let the background thread finish

    m_save.assert_called_once_with({"fresh": True})
