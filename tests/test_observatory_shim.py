"""World shim re-exports core Observatory (cli-market-core>=1.9.35 streak, 1.9.36 missions)."""

from datetime import date

from market_core.market_observatory import (
    ObservatoryMiddleware,
    compute_daily_observatory_metrics,
    observatory_snapshot_streak,
)


def test_shim_reexports_observatory_middleware():
    from market_observatory import ObservatoryMiddleware as ShimMiddleware

    assert ShimMiddleware is ObservatoryMiddleware


def test_observatory_snapshot_streak_empty(isolated_db):
    compute_daily_observatory_metrics(day=date.today())
    streak = observatory_snapshot_streak(days=7)
    assert streak["window_days"] == 7
    assert streak["snapshots_found"] >= 1
