"""Pepy.tech PyPI stats integration."""

import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_server import app

client = TestClient(app)

MOCK_PEPY = {
    "id": "cli-market-world",
    "total_downloads": 11155,
    "versions": ["1.9.4", "1.6.0"],
    "downloads": {
        "2026-06-01": {"1.9.4": 100, "1.6.0": 50},
        "2026-06-06": {"1.9.4": 200},
        "2026-06-07": {"1.9.4": 40},
        "2026-06-08": {"1.9.4": 60},
    },
    "metadata": {"latest_version": "1.9.4"},
}

MOCK_PRO = {
    "downloads": {
        "2026-06-01": {"1.9.4": 90, "1.6.0": 45},
        "2026-06-06": {"1.9.4": 180},
        "2026-06-07": {"1.9.4": 35},
        "2026-06-08": {"1.9.4": 55},
    }
}


@patch.dict("os.environ", {"PEPY_API_KEY": "test-key"}, clear=False)
@patch("market_pepy._fetch_json")
def test_pepy_summary(mock_fetch):
    from market_pepy import pepy_summary

    def side_effect(path: str):
        if "service-api" in path and "includeCIDownloads=false" in path:
            return MOCK_PRO
        if path.startswith("/api/v2/projects/"):
            return MOCK_PEPY
        return None

    mock_fetch.side_effect = side_effect
    import market_pepy as mp

    mp._CACHE.clear()
    mp._CACHE_AT = {}
    data = pepy_summary(force=True)
    assert data["ok"] is True
    assert data["total_downloads"] == 11155
    assert data["latest_version"] == "1.9.4"
    assert data["windows_source"] == "pro_no_ci"
    assert data["downloads_last_30d"] == data["downloads_last_30d_no_ci"]
    assert data["downloads_last_30d_raw"] >= data["downloads_last_30d"]
    assert data["ci_share_pct_30d"] is not None
    assert isinstance(data["daily_series_14d"], list)
    assert len(data["daily_series_14d"]) == 14
    assert isinstance(data["top_versions_30d"], list)


@patch.dict("os.environ", {"PEPY_API_KEY": "test-key"}, clear=False)
@patch("market_pepy._fetch_json")
def test_pepy_multi_summary_merges_series(mock_fetch):
    from market_pepy import pepy_multi_summary

    def side_effect(path: str):
        if "service-api" in path:
            return MOCK_PRO
        if "cli-market-core" in path:
            return {**MOCK_PEPY, "id": "cli-market-core", "total_downloads": 5000}
        if "cli-market-world" in path:
            return MOCK_PEPY
        return None

    mock_fetch.side_effect = side_effect
    import market_pepy as mp

    mp._CACHE.clear()
    mp._CACHE_AT = {}
    data = pepy_multi_summary(force=True)
    assert data["ok"] is True
    combined = data["combined"]
    assert combined["windows_source"] == "pro_no_ci"
    assert combined["downloads_last_30d_no_ci"] is not None
    assert isinstance(combined["daily_series_14d"], list)
    assert isinstance(combined["top_versions_30d"], list)


def test_daily_series_zero_fills():
    from market_pepy import _daily_series

    today = date.today()
    day1 = (today - timedelta(days=1)).isoformat()
    series = _daily_series({day1: {"1.0.0": 10}}, days=3, end=today)
    assert len(series) == 3
    assert series[-1]["downloads"] == 0
    assert series[-2]["downloads"] == 10


def test_ci_share_pct():
    from market_pepy import _ci_share_pct

    assert _ci_share_pct(100, 90) == 10.0
    assert _ci_share_pct(0, 0) is None


@patch.dict("os.environ", {}, clear=True)
def test_analytics_pypi_public_consolidated():
    import market_pepy as mp

    mp._CACHE.clear()
    mp._CACHE_AT = {}
    r = client.get("/analytics/pypi")
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert int(body.get("total_downloads") or 0) >= 20196
    assert "consolidated" in (body.get("project") or "").lower()
