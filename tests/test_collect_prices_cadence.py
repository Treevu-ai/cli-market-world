"""Tests for collect_prices.cycles_per_day -- the enrichment-refresh spacing
used by the daemon loop, extracted so the 4h->8h collection cadence change
(2026-08-29) has a regression test instead of only inline arithmetic."""

from __future__ import annotations

import pytest
from market_core import ensure_db_initialized

ensure_db_initialized()

import collect_prices as cp


@pytest.mark.parametrize(
    "interval_hours,expected",
    [
        (1, 24),
        (3, 8),
        (4, 6),  # the old default -- refresh every 6 cycles == 24h, unchanged
        (6, 4),
        (8, 3),  # the new default -- refresh every 3 cycles == 24h
        (12, 2),
        (13, 2),
        (20, 1),
        (24, 1),
        (25, 1),
        (48, 1),  # round(24/48) == round(0.5) == 0 without the max(1, ...) guard
        (0, 1),  # "run continuously" -- must not raise ZeroDivisionError
    ],
)
def test_cycles_per_day(interval_hours, expected):
    assert cp.cycles_per_day(interval_hours) == expected


def test_cycles_per_day_negative_interval_does_not_raise():
    assert cp.cycles_per_day(-1) == 1
