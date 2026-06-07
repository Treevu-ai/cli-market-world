"""PyPI vs funnel adoption comparison."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_server import app

client = TestClient(app)

MOCK_PEPY = {
    "ok": True,
    "project": "cli-market",
    "total_downloads": 11155,
    "downloads_last_7d": 900,
    "downloads_last_30d": 3486,
    "downloads_last_30d_no_ci": None,
    "top_version_30d": "1.9.4",
    "latest_version": "1.9.4",
    "fetched_at": "2026-06-07T12:00:00+00:00",
}

MOCK_FUNNEL = {
    "window_days": 30,
    "events": {
        "install": 40,
        "register": 12,
        "first_search": 8,
        "starter_subscribe": 2,
        "request_pro": 1,
        "activated": 0,
    },
    "unique_users": {
        "with_search": 8,
        "with_starter_subscribe": 2,
        "with_pro_request": 1,
        "activated": 0,
    },
    "conversion": {
        "register_to_search": 0.667,
        "search_to_starter": 0.25,
        "search_to_pro": 0.125,
        "pro_to_activated": None,
    },
    "funnel_steps": [
        {"step": "install", "count": 40, "drop_off_pct": None},
        {"step": "register", "count": 12, "drop_off_pct": 70.0},
        {"step": "first_search", "count": 8, "drop_off_pct": 33.3},
        {"step": "starter_subscribe", "count": 2, "drop_off_pct": 75.0},
        {"step": "request_pro", "count": 1, "drop_off_pct": 50.0},
        {"step": "activated", "count": 0, "drop_off_pct": None},
    ],
}


@patch("market_adoption.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_adoption.pepy_summary", return_value=MOCK_PEPY)
def test_adoption_summary(mock_pepy, mock_funnel):
    from market_adoption import adoption_summary

    data = adoption_summary(days=30)
    assert data["pypi"]["downloads_last_30d"] == 3486
    assert data["funnel"]["register"] == 12
    assert data["funnel"]["first_search"] == 8
    assert data["comparison"]["register_per_pypi_30d"] == round(12 / 3486, 4)
    assert data["comparison"]["register_per_install"] == round(12 / 40, 4)
    assert any("install" in n.lower() or "pepy" in n.lower() for n in data["notes"])


@patch("market_adoption.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_adoption.pepy_summary", return_value=MOCK_PEPY)
def test_adoption_markdown(mock_pepy, mock_funnel):
    from market_adoption import adoption_markdown_section

    md = adoption_markdown_section(days=30)
    assert "## Adopción" in md
    assert "3,486" in md
    assert "register" in md.lower() or "Register" in md


@patch("market_adoption.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_adoption.pepy_summary", return_value=MOCK_PEPY)
def test_adoption_slack_lines(mock_pepy, mock_funnel):
    from market_adoption import adoption_slack_lines

    lines = adoption_slack_lines(days=30)
    text = "\n".join(lines)
    assert "Adopción" in text
    assert "PyPI" in text
    assert "Embudo" in text


@patch("routers.funnel.adoption_summary")
def test_analytics_adoption_endpoint(mock_summary):
    mock_summary.return_value = {
        "window_days": 30,
        "pypi": {"ok": True, "downloads_last_30d": 100},
        "funnel": {"install": 5, "register": 2},
        "comparison": {},
        "notes": [],
    }
    r = client.get("/analytics/adoption?days=30")
    assert r.status_code == 200
    body = r.json()
    assert body["window_days"] == 30
    assert body["pypi"]["downloads_last_30d"] == 100


@patch("market_adoption.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_adoption.pepy_summary", return_value=MOCK_PEPY)
def test_daily_briefing_slack_includes_adoption(mock_pepy, mock_funnel):
    import importlib.util
    from pathlib import Path

    path = Path(__file__).parent.parent / "ops" / "daily_briefing.py"
    spec = importlib.util.spec_from_file_location("daily_briefing_ops", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    msg = mod.build_slack_product_message("2026-06-07", {"kpis": {}}, {}, "ops/daily/x.md")
    assert "Adopción" in msg
    assert "PyPI" in msg