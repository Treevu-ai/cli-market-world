"""Shim — canonical implementation in cli-market-core (``market_core.market_observatory``).

World keeps this top-level module for backward-compatible imports
(``from market_observatory import ObservatoryMiddleware``).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from market_core import get_db
from market_core.market_observatory import *  # noqa: F403,F401

try:
    from market_core.market_observatory import observatory_snapshot_streak  # noqa: F401
except ImportError:
    from market_core.market_observatory import ensure_observatory_schema

    def observatory_snapshot_streak(*, days: int = 7) -> dict[str, Any]:
        """Fallback until cli-market-core >1.9.34 (see ops/patches + T-173)."""
        ensure_observatory_schema()
        days = max(1, min(days, 30))
        cutoff = (date.today() - timedelta(days=days - 1)).isoformat()
        db = get_db()
        try:
            row = db.execute(
                "SELECT COUNT(*) AS n FROM daily_observatory_metrics WHERE date >= ?",
                (cutoff,),
            ).fetchone()
            found = int(row["n"] or 0) if row else 0
        finally:
            db.close()
        return {
            "window_days": days,
            "snapshots_found": found,
            "target": days,
            "ok": found >= days,
            "cutoff_date": cutoff,
        }
