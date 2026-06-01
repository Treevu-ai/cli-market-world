"""Tests for GET /v1/sources/health and source_health module."""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from source_health import build_sources_health, store_health_state


def test_store_health_state_thresholds():
    assert store_health_state(85) == "ok"
    assert store_health_state(80) == "ok"
    assert store_health_state(79) == "partial"
    assert store_health_state(30) == "partial"
    assert store_health_state(29) == "dead"


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    import market_core

    data_dir = tmp_path / "market_data"
    data_dir.mkdir()
    db_file = data_dir / "market.db"
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setattr(market_core, "DATA_DIR", data_dir)
    monkeypatch.setattr(market_core, "DB_FILE", db_file)
    monkeypatch.setattr(market_core, "USE_PG", False)
    monkeypatch.setattr(market_core, "_db_initialized", False)

    # Reset the dashboard's in-memory 120s cache so /dashboard/data reflects
    # this test's fresh DB instead of stale data leaked from a prior test.
    import routers.dashboard as dashboard_mod
    monkeypatch.setattr(dashboard_mod, "_dashboard_data_cache", None)
    monkeypatch.setattr(dashboard_mod, "_dashboard_data_cache_at", 0.0)
    return market_core


def _seed_store_health(db, store: str, success_pct: float, failures: int = 0):
    total = 100
    successes = int(total * success_pct / 100)
    db.execute(
        """
        INSERT INTO store_health (store, total_requests, total_successes, consecutive_failures)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(store) DO UPDATE SET
            total_requests=excluded.total_requests,
            total_successes=excluded.total_successes,
            consecutive_failures=excluded.consecutive_failures
        """,
        (store, total, successes, failures),
    )


def test_build_sources_health_summary_counts(isolated_db):
    market_core = isolated_db
    market_core.ensure_db_initialized()
    db = market_core.get_db()

    for sid in list(market_core.get_default_stores())[:3]:
        _seed_store_health(db, sid, 90 if sid == market_core.get_default_stores()[0] else 50 if sid == market_core.get_default_stores()[1] else 10)

    recent = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO price_snapshots (product_id, store, store_name, name, price, currency, line, line_name, queried_at) "
        "VALUES ('p1', ?, 'Test', 'Item', 10, 'PEN', 'supermercados', 'Super', ?)",
        (market_core.get_default_stores()[0], recent),
    )
    db.commit()

    payload = build_sources_health(db, catalog_only=True)
    db.close()

    summary = payload["summary"]
    assert summary["total"] == len(payload["stores"])
    assert summary["ok"] + summary["partial"] + summary["dead"] == summary["total"]
    assert summary["ok"] >= 1
    assert summary["dead"] >= 1
    assert summary["partial"] >= 1

    ok_row = next(s for s in payload["stores"] if s["state"] == "ok")
    assert ok_row["fresh_24h"] is True


def test_sources_health_endpoint_matches_dashboard(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    market_core = isolated_db
    market_core.ensure_db_initialized()
    db = market_core.get_db()
    sid = market_core.get_default_stores()[0]
    _seed_store_health(db, sid, 95)
    db.commit()
    db.close()

    with TestClient(app) as client:
        health_r = client.get("/v1/sources/health")
        dash_r = client.get("/dashboard/data")

    assert health_r.status_code == 200
    body = health_r.json()
    assert "summary" in body
    assert body["summary"]["ok"] + body["summary"]["partial"] + body["summary"]["dead"] == body["summary"]["total"]

    dash = dash_r.json()
    dash_ok = sum(1 for h in dash.get("store_health", []) if float(h.get("success_pct") or 0) >= 80)
    dash_dead = sum(1 for h in dash.get("store_health", []) if float(h.get("success_pct") or 0) < 30)
    assert body["summary"]["ok"] == dash_ok
    assert body["summary"]["dead"] == dash_dead


def test_sources_health_filter_store(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    market_core = isolated_db
    market_core.ensure_db_initialized()
    db = market_core.get_db()
    sid = market_core.get_default_stores()[0]
    _seed_store_health(db, sid, 88)
    db.commit()
    db.close()

    with TestClient(app) as client:
        r = client.get(f"/v1/sources/health?store={sid}")

    assert r.status_code == 200
    stores = r.json()["stores"]
    assert len(stores) == 1
    assert stores[0]["store"] == sid
    assert stores[0]["state"] == "ok"


def test_health_collector_still_works(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    with TestClient(app) as client:
        r = client.get("/health/collector")
    assert r.status_code == 200
    assert "status" in r.json()
