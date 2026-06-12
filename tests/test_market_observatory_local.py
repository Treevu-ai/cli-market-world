"""Tests for world-local market_observatory (P0 telemetry fixes)."""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from market_observatory import (
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

    mc._db_initialized = False
    mc.USE_PG = False
    mc.DATA_DIR = data_dir
    mc.DB_FILE = data_dir / "market.db"
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

    mc._db_initialized = False
    mc.USE_PG = False
    mc.DATA_DIR = data_dir
    mc.DB_FILE = data_dir / "market.db"
    mc.ensure_db_initialized()

    record_agent_event(
        agent_id="agent-daily-1",
        tool_name="market_search",
        success=True,
        retailer="wong-pe",
        country="PE",
    )
    payload = compute_daily_observatory_metrics(day=date.today())
    assert payload["daily_active_agents"] >= 1
    assert payload["date"] == date.today().isoformat()


def test_observatory_snapshot_streak_sqlite(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("OBSERVATORY_TELEMETRY", "1")
    import market_core.market_core as mc

    mc._db_initialized = False
    mc.USE_PG = False
    mc.DATA_DIR = data_dir
    mc.DB_FILE = data_dir / "market.db"
    mc.ensure_db_initialized()

    compute_daily_observatory_metrics(day=date.today())
    streak = observatory_snapshot_streak(days=7)
    assert streak["window_days"] == 7
    assert streak["snapshots_found"] >= 1
    assert streak["target"] == 7
    assert "ok" in streak
