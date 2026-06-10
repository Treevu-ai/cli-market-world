"""Observatory API + telemetry."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_ROOT = REPO_ROOT.parent / "cli-market-core"
if CORE_ROOT.is_dir():
    sys.path.insert(0, str(CORE_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from market_observatory import ensure_observatory_schema, record_agent_event
from market_server import app

ensure_db_initialized()
ensure_observatory_schema()
client = TestClient(app)


def test_analytics_observatory_public():
    record_agent_event(
        agent_id="obs-test-agent",
        tool_name="market_search",
        success=True,
        identity_source="x_agent_id",
    )
    r = client.get("/analytics/observatory?days=30")
    assert r.status_code == 200
    data = r.json()
    assert "maa" in data
    assert data["calls_success"] >= 1
    assert data["telemetry_enabled"] is True


def test_classify_route_skips_health():
    from market_observatory import classify_route

    assert classify_route("GET", "/health") == (None, None)
