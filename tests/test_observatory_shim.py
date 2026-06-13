"""Observatory shim re-exports from cli-market-core."""

from market_observatory import observatory_snapshot_streak  # noqa: F401


def test_observatory_snapshot_streak_empty(isolated_db):
    from market_observatory import ensure_observatory_schema

    ensure_observatory_schema()
    streak = observatory_snapshot_streak(days=7)
    assert streak["window_days"] == 7
    assert streak["target"] == 7
    assert streak["snapshots_found"] == 0
    assert streak["ok"] is False
