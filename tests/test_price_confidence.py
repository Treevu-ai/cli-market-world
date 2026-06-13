"""Tests for market_core.price_confidence — all public functions."""

from __future__ import annotations

import pytest
from market_core.price_confidence import (
    DISCOUNT_PUBLIC_MAX,
    DISCOUNT_PUBLIC_MIN,
    MARKETING_MAX_SPREAD,
    MEDIAN_OUTLIER_BAND,
    compute_snapshot_confidence,
    discount_is_scrape_error,
    discount_pct,
    discount_public_ok,
    median_outlier_bounds,
    price_vs_median_confidence,
    spread_confidence,
    spread_public_ok,
)


# ── discount_public_ok ────────────────────────────────────────────────────────

def test_discount_public_ok_none_is_false():
    assert discount_public_ok(None) is False


def test_discount_public_ok_below_min_is_false():
    assert discount_public_ok(DISCOUNT_PUBLIC_MIN - 0.1) is False


def test_discount_public_ok_at_min_is_true():
    assert discount_public_ok(DISCOUNT_PUBLIC_MIN) is True


def test_discount_public_ok_midrange_is_true():
    assert discount_public_ok(30.0) is True


def test_discount_public_ok_at_max_is_true():
    assert discount_public_ok(DISCOUNT_PUBLIC_MAX) is True


def test_discount_public_ok_above_max_is_false():
    assert discount_public_ok(DISCOUNT_PUBLIC_MAX + 0.1) is False


def test_discount_public_ok_zero_is_false():
    assert discount_public_ok(0) is False


# ── discount_is_scrape_error ──────────────────────────────────────────────────

def test_discount_is_scrape_error_none_is_false():
    assert discount_is_scrape_error(None) is False


def test_discount_is_scrape_error_below_threshold_is_false():
    assert discount_is_scrape_error(89.9) is False


def test_discount_is_scrape_error_at_threshold_is_true():
    assert discount_is_scrape_error(90) is True


def test_discount_is_scrape_error_above_threshold_is_true():
    assert discount_is_scrape_error(99) is True


def test_discount_is_scrape_error_100_is_true():
    assert discount_is_scrape_error(100) is True


# ── discount_pct ──────────────────────────────────────────────────────────────

def test_discount_pct_no_list_price_is_none():
    assert discount_pct(10.0, None) is None


def test_discount_pct_list_price_equals_price_is_none():
    assert discount_pct(10.0, 10.0) is None


def test_discount_pct_price_above_list_price_is_none():
    assert discount_pct(15.0, 10.0) is None


def test_discount_pct_zero_price_is_none():
    assert discount_pct(0, 10.0) is None


def test_discount_pct_normal_case():
    result = discount_pct(80.0, 100.0)
    assert result == 20.0


def test_discount_pct_rounds_to_one_decimal():
    result = discount_pct(66.0, 100.0)
    assert result == 34.0


# ── compute_snapshot_confidence ───────────────────────────────────────────────

def test_compute_snapshot_confidence_no_list_price_is_ok():
    assert compute_snapshot_confidence(10.0, None) == "ok"


def test_compute_snapshot_confidence_normal_discount_is_ok():
    # 20% discount — well within range, no scrape error
    assert compute_snapshot_confidence(80.0, 100.0) == "ok"


def test_compute_snapshot_confidence_extreme_discount_is_suspect():
    # 95% discount — triggers scrape error detection
    assert compute_snapshot_confidence(5.0, 100.0) == "suspect"


def test_compute_snapshot_confidence_no_discount_is_ok():
    # price == list_price → discount_pct returns None → not a scrape error
    assert compute_snapshot_confidence(100.0, 100.0) == "ok"


# ── spread_confidence ─────────────────────────────────────────────────────────

def test_spread_confidence_low_is_ok():
    assert spread_confidence(1.5) == "ok"


def test_spread_confidence_at_threshold_is_ok():
    assert spread_confidence(2.0) == "ok"


def test_spread_confidence_above_two_is_warn():
    assert spread_confidence(2.1) == "warn"


def test_spread_confidence_at_marketing_max_is_warn():
    assert spread_confidence(MARKETING_MAX_SPREAD) == "warn"


def test_spread_confidence_above_marketing_max_is_crit():
    assert spread_confidence(MARKETING_MAX_SPREAD + 0.1) == "crit"


# ── spread_public_ok ──────────────────────────────────────────────────────────

def test_spread_public_ok_low_spread():
    assert spread_public_ok(1.0) is True


def test_spread_public_ok_warn_spread_is_ok():
    assert spread_public_ok(5.0) is True


def test_spread_public_ok_crit_spread_is_false():
    assert spread_public_ok(MARKETING_MAX_SPREAD + 1) is False


# ── median_outlier_bounds ─────────────────────────────────────────────────────

def test_median_outlier_bounds_zero_median():
    lo, hi = median_outlier_bounds(0)
    assert lo == 0.0 and hi == 0.0


def test_median_outlier_bounds_negative_median():
    lo, hi = median_outlier_bounds(-5)
    assert lo == 0.0 and hi == 0.0


def test_median_outlier_bounds_normal():
    lo, hi = median_outlier_bounds(10.0)
    assert lo == pytest.approx(10.0 / MEDIAN_OUTLIER_BAND)
    assert hi == pytest.approx(10.0 * MEDIAN_OUTLIER_BAND)


def test_median_outlier_bounds_custom_band():
    lo, hi = median_outlier_bounds(20.0, band=2.0)
    assert lo == pytest.approx(10.0)
    assert hi == pytest.approx(40.0)


# ── price_vs_median_confidence ────────────────────────────────────────────────

def test_price_vs_median_confidence_zero_price_is_ok():
    assert price_vs_median_confidence(0, 100.0) == "ok"


def test_price_vs_median_confidence_zero_median_is_ok():
    assert price_vs_median_confidence(50.0, 0) == "ok"


def test_price_vs_median_confidence_within_band_is_ok():
    assert price_vs_median_confidence(10.0, 10.0) == "ok"


def test_price_vs_median_confidence_too_low_is_suspect():
    # price << median/band → outlier
    median = 100.0
    lo = median / MEDIAN_OUTLIER_BAND
    assert price_vs_median_confidence(lo - 1, median) == "suspect"


def test_price_vs_median_confidence_too_high_is_suspect():
    median = 100.0
    hi = median * MEDIAN_OUTLIER_BAND
    assert price_vs_median_confidence(hi + 1, median) == "suspect"


def test_price_vs_median_confidence_custom_band():
    # band=2 → range [50, 200] for median=100
    assert price_vs_median_confidence(60.0, 100.0, band=2.0) == "ok"
    assert price_vs_median_confidence(201.0, 100.0, band=2.0) == "suspect"
