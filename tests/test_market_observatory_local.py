"""Tests for Observatory telemetry (core via world shim)."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from market_core.market_observatory import (
    _extract_geo_retailer,
    _weekly_agent_growth,
    classify_route,
    compute_daily_observatory_metrics,
    normalize_tool_name,
    observatory_snapshot_streak,
    record_agent_event,
)


def test_normalize_tool_name_maps_agent_ask():
    assert normalize_tool_name("market_agent_ask") == "market_ask"


def test_classify_route_skips_index_admin():
    assert classify_route("GET", "/index/stats") == (None, None)


def test_extract_geo_retailer_from_body():
    body = json.dumps({"query": "arroz", "store": "wong-pe", "country": "PE"}).encode()
    country, retailer = _extract_geo_retailer(headers={}, query_params={}, body=body)
    assert country == "PE"
    assert retailer == "wong-pe"


def test_internal_tool_not_recorded(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("OBSERVATORY_TELEMETRY", "1")
    import market_core.market_core as mc

    # monkeypatch.setattr (not a plain `mc.X = ...` assignment) so these
    # revert automatically after this test -- a raw assignment here has no
    # teardown, so it permanently flips market_core.market_core.USE_PG to
    # False for the rest of the pytest session the moment this test runs.
    # That's the actual root cause behind test-pg CI's persistent
    # test_vault.py-and-friends cluster (found 2026-08-05): downstream
    # modules read the *top-level* `market_core` package's USE_PG (a
    # `from .market_core import *` re-export, itself a one-time snapshot
    # frozen at first import -- see market_core/__init__.py), which stays
    # True even after this leaks the *submodule*'s live value to False, so
    # market_vault.py picks Postgres DDL while get_db() actually hands back
    # a SQLite connection underneath it.
    monkeypatch.setattr(mc, "_db_initialized", False)
    monkeypatch.setattr(mc, "USE_PG", False)
    monkeypatch.setattr(mc, "DATA_DIR", data_dir)
    monkeypatch.setattr(mc, "DB_FILE", data_dir / "market.db")
    mc.ensure_db_initialized()

    skipped = record_agent_event(
        agent_id="agent-local-1",
        tool_name="index_stats",
        success=True,
    )
    assert skipped.get("skipped") is True

    ok = record_agent_event(
        agent_id="agent-local-1",
        tool_name="market_search",
        success=True,
        retailer="wong-pe",
        country="PE",
    )
    assert ok.get("ok") is True


def test_weekly_agent_growth_calc():
    day_agents = {f"2026-06-{d:02d}": {f"a{d}"} for d in range(1, 15)}
    assert _weekly_agent_growth(day_agents) is not None


def test_compute_daily_observatory_metrics_sqlite_row(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("OBSERVATORY_TELEMETRY", "1")
    import market_core.market_core as mc

    # monkeypatch.setattr (not a plain `mc.X = ...` assignment) so these
    # revert automatically after this test -- a raw assignment here has no
    # teardown, so it permanently flips market_core.market_core.USE_PG to
    # False for the rest of the pytest session the moment this test runs.
    # That's the actual root cause behind test-pg CI's persistent
    # test_vault.py-and-friends cluster (found 2026-08-05): downstream
    # modules read the *top-level* `market_core` package's USE_PG (a
    # `from .market_core import *` re-export, itself a one-time snapshot
    # frozen at first import -- see market_core/__init__.py), which stays
    # True even after this leaks the *submodule*'s live value to False, so
    # market_vault.py picks Postgres DDL while get_db() actually hands back
    # a SQLite connection underneath it.
    monkeypatch.setattr(mc, "_db_initialized", False)
    monkeypatch.setattr(mc, "USE_PG", False)
    monkeypatch.setattr(mc, "DATA_DIR", data_dir)
    monkeypatch.setattr(mc, "DB_FILE", data_dir / "market.db")
    mc.ensure_db_initialized()

    record_agent_event(
        agent_id="agent-daily-1",
        tool_name="market_search",
        success=True,
        retailer="wong-pe",
        country="PE",
    )
    # record_agent_event() stamps occurred_at in UTC -- pass the same UTC date
    # here (not local date.today()) or this silently reads 0 activity near
    # the day boundary in any timezone offset from UTC (see
    # compute_daily_observatory_metrics' own docstring comment for the
    # production-code side of this fix, bf28f10).
    today_utc = datetime.now(timezone.utc).date()
    payload = compute_daily_observatory_metrics(day=today_utc)
    assert payload["daily_active_agents"] >= 1
    assert payload["date"] == today_utc.isoformat()


def test_observatory_snapshot_streak_sqlite(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("OBSERVATORY_TELEMETRY", "1")
    import market_core.market_core as mc

    # monkeypatch.setattr (not a plain `mc.X = ...` assignment) so these
    # revert automatically after this test -- a raw assignment here has no
    # teardown, so it permanently flips market_core.market_core.USE_PG to
    # False for the rest of the pytest session the moment this test runs.
    # That's the actual root cause behind test-pg CI's persistent
    # test_vault.py-and-friends cluster (found 2026-08-05): downstream
    # modules read the *top-level* `market_core` package's USE_PG (a
    # `from .market_core import *` re-export, itself a one-time snapshot
    # frozen at first import -- see market_core/__init__.py), which stays
    # True even after this leaks the *submodule*'s live value to False, so
    # market_vault.py picks Postgres DDL while get_db() actually hands back
    # a SQLite connection underneath it.
    monkeypatch.setattr(mc, "_db_initialized", False)
    monkeypatch.setattr(mc, "USE_PG", False)
    monkeypatch.setattr(mc, "DATA_DIR", data_dir)
    monkeypatch.setattr(mc, "DB_FILE", data_dir / "market.db")
    mc.ensure_db_initialized()

    compute_daily_observatory_metrics(day=datetime.now(timezone.utc).date())
    streak = observatory_snapshot_streak(days=7)
    assert streak["window_days"] == 7
    assert streak["snapshots_found"] >= 1
    assert streak["target"] == 7
    assert "ok" in streak
