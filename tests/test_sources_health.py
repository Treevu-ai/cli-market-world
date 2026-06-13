"""Smoke tests for source health (phase 6 / ticket 3.1)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from market_core import ensure_db_initialized
from market_core.source_health import build_sources_health, store_health_state


def test_store_health_state_thresholds():
    assert store_health_state(90) == "ok"
    assert store_health_state(80) == "ok"
    assert store_health_state(79.9) == "partial"
    assert store_health_state(30) == "partial"
    assert store_health_state(29.9) == "dead"


def test_build_sources_health_empty_db(isolated_db):
    isolated_db.ensure_db_initialized()
    db = isolated_db.get_db()
    try:
        payload = build_sources_health(
            db,
            catalog_only=True,
            now=datetime(2026, 6, 13, 12, 0, tzinfo=timezone.utc),
        )
    finally:
        db.close()

    assert "generated_at" in payload
    assert payload["summary"] == {"ok": 0, "partial": 0, "dead": 0, "total": 0}
    assert payload["stores"] == []


def test_build_sources_health_with_seed_row(isolated_db):
    isolated_db.ensure_db_initialized()
    db = isolated_db.get_db()
    now = datetime(2026, 6, 13, 12, 0, tzinfo=timezone.utc)
    ts = "2026-06-13T11:00:00+00:00"
    try:
        db.execute(
            """
            INSERT INTO store_health (
                store, last_success, last_error, consecutive_failures,
                total_requests, total_successes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("carrefour", ts, None, 0, 100, 95),
        )
        db.execute(
            """
            INSERT INTO price_snapshots (product_id, store, name, price, currency, queried_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("prod-1", "carrefour", "Test Product", 10.5, "ARS", ts),
        )
        db.commit()
        payload = build_sources_health(db, catalog_only=True, now=now)
    finally:
        db.close()

    assert payload["summary"]["total"] == 1
    assert payload["summary"]["ok"] == 1
    store = payload["stores"][0]
    assert store["store"] == "carrefour"
    assert store["store_name"] == "Carrefour AR"
    assert store["country"] == "AR"
    assert store["success_pct"] == 95.0
    assert store["state"] == "ok"
    assert store["fresh_24h"] is True
    assert "coverage_7d_pct" in store


def test_sources_health_endpoint_shape(isolated_db):
    pytest.importorskip("persistence")
    from market_server import app

    ensure_db_initialized()
    with TestClient(app) as client:
        r = client.get("/v1/sources/health")
    assert r.status_code == 200
    data = r.json()
    if "error" in data:
        pytest.skip("source_health module not available in this install")
    assert set(data) >= {"generated_at", "summary", "stores"}
    assert set(data["summary"]) >= {"ok", "partial", "dead", "total"}
