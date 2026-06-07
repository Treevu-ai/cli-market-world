"""Go-live dashboard — KPIs and alerts."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_server import app

client = TestClient(app)

MOCK_ADOPTION = {
    "window_days": 30,
    "pypi": {"ok": True, "downloads_last_30d": 1000},
    "funnel": {
        "install": 20,
        "register": 10,
        "first_search": 2,
        "starter_subscribe": 0,
        "request_pro": 0,
        "activated": 0,
    },
    "comparison": {
        "search_per_register": 0.2,
        "register_per_install": 0.5,
    },
    "notes": [],
}

MOCK_FUNNEL = {
    "window_days": 30,
    "ttfv_median_minutes": 90.0,
    "events": {},
    "unique_users": {},
    "conversion": {},
    "funnel_steps": [],
}

MOCK_DASHBOARD = {
    "kpis": {
        "coverage_7d_pct": 55.0,
        "snapshots_24h": 100,
    },
    "moat_summary": {
        "coverage_7d_pct": 55.0,
        "collector_stale": True,
    },
    "collector": {"status": "stale"},
    "store_health": [
        {"store": "badstore", "success_pct": 10.0},
        {"store": "okstore", "success_pct": 95.0},
    ],
}


@patch("market_golive.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_golive.adoption_summary", return_value=MOCK_ADOPTION)
def test_go_live_summary_alerts(mock_adoption, mock_funnel):
    from market_golive import go_live_summary

    data = go_live_summary(days=30, dashboard_data=MOCK_DASHBOARD)
    assert data["overall_status"] in ("critical", "degraded")
    assert data["kpis"]["activation"]["status"] == "critical"
    assert data["kpis"]["data_moat"]["critical_store_count"] == 1
    codes = {a["code"] for a in data["alerts"]}
    assert "activation_low" in codes
    assert "moat_coverage_low" in codes
    assert "moat_stores_dead" in codes
    assert "collector_stale" in codes


@patch("market_golive.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_golive.adoption_summary", return_value=MOCK_ADOPTION)
def test_go_live_markdown(mock_adoption, mock_funnel):
    from market_golive import go_live_markdown

    md = go_live_markdown(days=30, dashboard_data=MOCK_DASHBOARD)
    assert "Go-live" in md
    assert "Activación" in md
    assert "Alertas" in md


@patch("market_golive.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_golive.adoption_summary", return_value=MOCK_ADOPTION)
def test_go_live_slack_lines(mock_adoption, mock_funnel):
    from market_golive import go_live_slack_lines

    lines = go_live_slack_lines(days=30, dashboard_data=MOCK_DASHBOARD)
    text = "\n".join(lines)
    assert "Go-live" in text
    assert "Activación" in text


@patch("routers.funnel.go_live_summary")
def test_dashboard_go_live_endpoint(mock_summary, monkeypatch):
    monkeypatch.setenv("MARKET_API_TOKEN", "test-admin-token")
    import server_deps

    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", "test-admin-token")
    mock_summary.return_value = {
        "window_days": 30,
        "overall_status": "healthy",
        "kpis": {},
        "alerts": [],
        "alert_count": {"critical": 0, "warn": 0, "info": 0},
    }
    r = client.get(
        "/dashboard/go-live?days=30",
        headers={"Authorization": "Bearer test-admin-token"},
    )
    assert r.status_code == 200
    assert r.json()["overall_status"] == "healthy"


@patch("market_golive.funnel_summary")
@patch("market_golive.adoption_summary")
def test_healthy_go_live(mock_adoption, mock_funnel):
    from market_golive import go_live_summary

    mock_adoption.return_value = {
        "window_days": 30,
        "pypi": {"ok": True, "downloads_last_30d": 500},
        "funnel": {
            "install": 10,
            "register": 5,
            "first_search": 4,
            "starter_subscribe": 1,
            "request_pro": 0,
            "activated": 1,
        },
        "comparison": {"search_per_register": 0.8},
        "notes": [],
    }
    mock_funnel.return_value = {
        "ttfv_median_minutes": 5.0,
        "window_days": 30,
        "events": {},
        "unique_users": {},
        "conversion": {},
        "funnel_steps": [],
    }
    dash = {
        "kpis": {"coverage_7d_pct": 85.0, "snapshots_24h": 500},
        "moat_summary": {"coverage_7d_pct": 85.0, "collector_stale": False},
        "collector": {"status": "ok"},
        "store_health": [{"store": "s1", "success_pct": 95.0}],
    }
    data = go_live_summary(days=30, dashboard_data=dash)
    assert data["overall_status"] == "healthy"
    assert data["alert_count"]["critical"] == 0