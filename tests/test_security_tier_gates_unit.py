"""Unit tests for tier-gate regressions that do not require full app import."""

from __future__ import annotations


def test_core_v1_tier_routes_includes_products_substitutes():
    from server_deps import _CORE_V1_TIER_ROUTES

    assert _CORE_V1_TIER_ROUTES.get(("GET", "/v1/products/substitutes")) == "pro"


def test_mcp_pre_check_tier_includes_market_substitutes():
    from routers.mcp_http import _PRE_CHECK_TIER

    assert _PRE_CHECK_TIER.get("market_substitutes") == "pro"


def test_public_pulse_view_model_strips_pro_kpis():
    from intelligence_web import public_pulse_view_model

    pulse = {
        "country": "PE",
        "week": "2026-W34",
        "headline": "Test headline",
        "title": "Pulse",
        "kpis": {"pvi": 8.39, "bai": 100, "inflation_pct": 1.2},
        "executive_highlights": ["Pro-only highlight"],
        "moat": {"total_indexed": 1000, "snapshots_24h": 50, "coverage_7d_pct": 42.0},
        "largest_anomaly": {"subcategory": "leche", "delta_pct": 3.1},
        "publishable": True,
    }
    data = public_pulse_view_model(pulse)
    assert data["country"] == "PE"
    assert "kpis" not in data
    assert "executive_highlights" not in data
    assert "largest_anomaly" not in data
    assert data["moat"]["total_indexed"] == 1000
