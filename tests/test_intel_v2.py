"""Unit tests for Intelligence v2 helpers (no full app import)."""

from __future__ import annotations

from market_intel_v2 import (
    PROMO_DISCOUNT_THRESHOLD,
    _affordability_headline_v2,
    build_coverage_table_rows,
    coverage_partial_label,
)


def test_affordability_headline_uses_average_not_ipc_gap():
    headline = _affordability_headline_v2(
        cc="PE",
        currency="PEN",
        canasta_avg=76.5,
        canastas_per_wage_avg=14.8,
        rpv_pct=2.1,
    )
    assert "promedio" in headline
    assert "RPV" in headline
    assert "IPC" not in headline
    assert "gap" not in headline.lower()


def test_promo_threshold_constant():
    assert PROMO_DISCOUNT_THRESHOLD == 0.03


def test_coverage_partial_label():
    assert coverage_partial_label(59.9) == "[COBERTURA PARCIAL]"
    assert coverage_partial_label(60.0) == ""
    assert coverage_partial_label(None) == ""


def test_build_coverage_table_rows_from_store_health():
    data = {
        "store_health": [
            {
                "store": "wong",
                "country": "PE",
                "line": "supermercados",
                "success_pct": 92.0,
                "coverage_7d_pct": 100.0,
                "last_snapshot": "2026-06-24T10:00:00",
            }
        ]
    }
    rows = build_coverage_table_rows(data)
    assert len(rows) == 1
    assert rows[0]["store"] == "wong"
    assert rows[0]["success_pct"] == 92.0
