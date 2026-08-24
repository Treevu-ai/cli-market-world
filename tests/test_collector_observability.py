"""COL-1..13 observability helpers — no live DB required."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops"))

from collector_health import (
    GATE_DELIST_STORES,
    build_collector_catalog_identity,
    derive_collector_status,
    filter_gate_denominator,
)
from source_health_overlay import apply_sources_health_overlay
from command_control_daily import _sparkline
from db_lock_monitor import check_run_clock


def test_derive_collector_status_sla_windows():
    now = datetime.now(timezone.utc)
    ok_at = (now - timedelta(hours=2)).isoformat()
    deg_at = (now - timedelta(hours=6)).isoformat()
    stale_at = (now - timedelta(hours=9)).isoformat()
    dead_at = (now - timedelta(hours=25)).isoformat()

    assert derive_collector_status(finished_at=ok_at, prices_collected=100)[0] == "ok"
    assert derive_collector_status(finished_at=deg_at, prices_collected=100)[0] == "degraded"
    assert derive_collector_status(finished_at=stale_at, prices_collected=100)[0] == "stale"
    assert derive_collector_status(finished_at=dead_at, prices_collected=100)[0] == "dead"
    assert derive_collector_status(finished_at=ok_at, prices_collected=0)[0] == "empty"


def test_catalog_identity_adds_up():
    ident = build_collector_catalog_identity(
        catalog_ids=["a", "b", "c", "d", "e"],
        attempted=3,
        succeeded=3,
        circuit_open=["d"],
        inactive=["e"],
    )
    assert ident["identity_ok"] is True
    assert ident["total"] == 5
    assert (
        ident["attempted"]
        + ident["skipped_circuit"]
        + ident["inactive"]
        + ident["unclassified"]
        == 5
    )


def test_overlay_fresh_24h_from_last_success():
    now = datetime(2026, 8, 24, 17, 0, tzinfo=timezone.utc)
    payload = {
        "stores": [
            {
                "store": "falabella_cl",
                "success_pct": 93.0,
                "consecutive_failures": 0,
                "state": "ok",
                "last_seen": None,
                "last_success": "2026-08-24T15:00:00+00:00",
                "coverage_7d_pct": 40.0,
                "fresh_24h": False,
            }
        ]
    }
    out = apply_sources_health_overlay(payload, now=now)
    assert out["stores"][0]["fresh_24h"] is True
    assert out["stores"][0]["store_day_hit_rate_7d_pct"] == 40.0


def test_overlay_circuit_open_not_ok():
    now = datetime(2026, 8, 24, 17, 0, tzinfo=timezone.utc)
    payload = {
        "stores": [
            {
                "store": "santiagonativo_cl",
                "success_pct": 93.0,
                "consecutive_failures": 10,
                "state": "ok",
                "last_seen": None,
                "last_success": "2026-08-01T00:00:00+00:00",
                "coverage_7d_pct": 0,
                "fresh_24h": False,
            }
        ]
    }
    out = apply_sources_health_overlay(payload, now=now)
    assert out["stores"][0]["state"] == "circuit_open"
    assert out["summary"]["circuit_open"] == 1
    assert out["summary"]["ok"] == 0


def test_sparkline_requires_baseline():
    assert _sparkline([]) == "n/a"
    assert _sparkline([193102]) == "n/a"
    assert _sparkline([193102, 0, 0, 0]) == "n/a"
    chart = _sparkline([10, 12, 11, 15])
    assert chart != "n/a"
    assert len(chart) == 4


def test_dual_clock_names_which_clock_failed(monkeypatch):
    class _Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"last_finished": "2000-01-01T00:00:00+00:00", "status": "dead"}

    import db_lock_monitor as mon

    monkeypatch.setattr(mon.httpx, "get", lambda *a, **k: _Resp())
    problem = check_run_clock(max_run_hours=5)
    assert problem is not None
    assert problem["clock"] == "collector_runs"
    assert problem["age_hours"] > 5


def test_gate_denominator_excludes_us_dtc_delist():
    catalog = ["wong_pe", "casper", "parachute", "brooklinen", "alo_yoga"]
    gated = filter_gate_denominator(catalog)
    assert "wong_pe" in gated
    assert "alo_yoga" in gated  # watch, still in denominator
    assert GATE_DELIST_STORES.isdisjoint(gated)
    assert len(gated) == 2
