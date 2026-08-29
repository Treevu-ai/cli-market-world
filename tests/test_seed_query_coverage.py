"""Guard against a store/line silently receiving zero seed queries.

2026-07-24 incident: the "suplementos" line had zero SEED_QUERIES entries and
no STORE_QUERY_OVERRIDES, so collect_one_pg's `queries_for_line == 0` check
(collect_prices.py) made the daemon skip all 10 stores on that line every
cycle, discovered only by a manual coverage audit. That line was fixed, but
nothing guarded against it happening again for a new store/line. This test
is that guard (cli-market-core PRD 2026-08-28, backlog Epic B / B1).
"""

from __future__ import annotations

from market_core import STORES

import collect_prices as cp


def _queries_for_line(store: str, line: str) -> int:
    """Mirrors collect_one_pg's own queries_for_line computation exactly."""
    queries = cp.queries_for_store(store, cp.SEED_QUERIES)
    return sum(1 for _q, lf in queries if not lf or lf == line)


def test_every_store_line_has_at_least_one_reachable_query():
    orphans = []
    for store, cfg in STORES.items():
        line = cfg.get("line", "")
        if _queries_for_line(store, line) == 0:
            orphans.append((store, line))
    assert not orphans, (
        f"{len(orphans)} store(s) have zero reachable seed queries for their "
        f"line and will be silently skipped every collection cycle "
        f"(collect_one_pg's queries_for_line == 0 short-circuit): {orphans}"
    )


def test_every_line_present_in_stores_has_seed_or_override_coverage():
    """Same guard at the line level, independent of any one store's overrides
    — catches a brand-new line added to STORES before any store on it exists,
    which the per-store test above can't see yet."""
    lines_in_use = {cfg.get("line", "") for cfg in STORES.values()}
    seed_lines = {lf or "supermercados" for _q, lf in cp.SEED_QUERIES}
    override_lines = {
        lf or "supermercados"
        for entries in cp.STORE_QUERY_OVERRIDES.values()
        for _q, lf in entries
    }
    covered = seed_lines | override_lines
    uncovered = lines_in_use - covered
    assert not uncovered, (
        f"line(s) {uncovered} appear in STORES but have no SEED_QUERIES and "
        f"no STORE_QUERY_OVERRIDES entry — any store on these lines collects "
        f"zero prices every cycle"
    )


def test_regression_orphan_line_is_detected():
    """Confirms the guard actually fires, using a synthetic orphan line —
    this is what the 2026-07-24 incident would have looked like if this test
    had existed at the time."""
    orphan_store = "__test_orphan_store__"
    orphan_line = "__test_orphan_line__"
    assert _queries_for_line(orphan_store, orphan_line) == 0
