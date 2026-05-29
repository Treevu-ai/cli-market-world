"""Tests for dashboard quality funnel."""

from dashboard_quality import build_quality_funnel


def test_build_quality_funnel_tiers():
    funnel = build_quality_funnel(
        captured=43071,
        flagged_discounts=800,
        flagged_outliers=47,
        citable=3,
    )
    assert funnel["captured"] == 43071
    assert funnel["flagged"] == 847
    assert funnel["clean"] == 42224
    assert funnel["citable"] == 3
    assert "discount>=90%" in funnel["filters"]
