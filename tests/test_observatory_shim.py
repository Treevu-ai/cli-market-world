"""World shim re-exports core Observatory; streak lives in cli-market-core (T-173 / 1.9.35+)."""

import pytest


def test_shim_reexports_observatory_middleware():
    from market_core.market_observatory import ObservatoryMiddleware as CoreMiddleware
    from market_observatory import ObservatoryMiddleware

    assert ObservatoryMiddleware is CoreMiddleware


def test_observatory_snapshot_streak_empty(isolated_db):
    from datetime import date

    try:
        from market_core.market_observatory import (
            compute_daily_observatory_metrics,
            observatory_snapshot_streak,
        )
    except ImportError:
        pytest.skip("observatory_snapshot_streak requires cli-market-core>=1.9.35")

    compute_daily_observatory_metrics(day=date.today())
    streak = observatory_snapshot_streak(days=7)
    assert streak["window_days"] == 7
    assert streak["snapshots_found"] >= 1
