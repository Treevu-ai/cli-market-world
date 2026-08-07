#!/usr/bin/env python3
"""Re-resolve price_snapshots stuck on an over-fused canonical_product_id —
a Golden Record that groups genuinely different products (different cheese
varieties, milk vs. cooking cream, etc.) under one id.

Confirmed live 2026-08-06 (see cli-market-index#16): the current
_variety_fingerprint logic already computes a distinct, correct id for each
of these raw names — the over-fusion is stale data from before that logic
existed, not a bug in the current resolver. Uses --exact-only (default) so
each snapshot's own raw name resolves to its own distinct id via an exact
match or a fresh registration, instead of getting fuzzy/name-matched right
back onto the same over-fused id it's trying to split apart.

Confirmed over-fused ids (2026-08-06 audit, PE, major retailers):
  prod_laive_lacteos_0.18kg   -> cheddar/edam/andino/mozzarella/danbo queso, one id
  prod_gloria_lacteos_0.946l  -> entera/light/niños/chocolate milk AND cooking cream, one id

This is a one-off maintenance sweep, not part of the routine collector cycle.

Usage:
    python3 ops/reresolve_over_fused_variants.py --dry-run   # preview only
    python3 ops/reresolve_over_fused_variants.py              # apply
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OVER_FUSED_IDS = ["prod_laive_lacteos_0.18kg", "prod_gloria_lacteos_0.946l"]

DEFAULT_BATCH_LIMIT = 2000
DEFAULT_MAX_BATCHES = 20
DEFAULT_TIME_BUDGET_S = 600


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-resolve snapshots stuck on a known-over-fused canonical_product_id")
    parser.add_argument("--ids", nargs="*", default=OVER_FUSED_IDS)
    parser.add_argument("--limit", type=int, default=DEFAULT_BATCH_LIMIT)
    parser.add_argument("--max-batches", type=int, default=DEFAULT_MAX_BATCHES)
    parser.add_argument("--time-budget", type=int, default=DEFAULT_TIME_BUDGET_S)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-exact-only",
        action="store_true",
        help="Use normal fuzzy/name-match resolution instead of exact-only (not recommended — risks re-matching back onto the over-fused id).",
    )
    args = parser.parse_args()

    # A real canonical_product_id is prod_<brand>_<category>_<qty><unit>[_<variety>],
    # all lowercase alnum/underscore/dot — --ids is free-form CLI input. Unlike
    # reresolve_stale_brands.py's LIKE-pattern validation, this is pure
    # fail-fast sanity checking, not an injection guard: the fetch below uses
    # parameterized = / ANY / IN, which isn't wildcard-sensitive the way LIKE is.
    for cid in args.ids:
        if not re.fullmatch(r"prod_[a-z0-9_.]+", cid):
            parser.error(f"invalid --ids value {cid!r}: must match prod_[a-z0-9_.]+")

    from index_gate import index_stats, reresolve_snapshots_by_canonical_id

    before = index_stats()
    print(f"Canonical ids targeted: {args.ids}")
    print(f"Before: linkage_pct={before.get('linkage_pct')} match_type_distribution={before.get('match_type_distribution')}\n")

    t0 = time.monotonic()
    totals = {"resolved": 0, "linked": 0, "exact": 0, "fuzzy": 0, "auto": 0, "errors": 0}
    for batch_num in range(1, args.max_batches + 1):
        stats = reresolve_snapshots_by_canonical_id(
            args.ids, limit=args.limit, dry_run=args.dry_run, exact_only=not args.no_exact_only
        )
        for k in totals:
            totals[k] += int(stats.get(k, 0))
        print(f"  batch {batch_num}: fetched={stats.get('fetched', 0)} resolved={stats.get('resolved', 0)} "
              f"linked={stats.get('linked', 0)} exact={stats.get('exact', 0)} fuzzy={stats.get('fuzzy', 0)} "
              f"errors={stats.get('errors', 0)}")
        if not stats.get("fetched"):
            print("  (no more matching rows found — stopping)")
            break
        if not stats.get("resolved"):
            print(f"  (fetched {stats['fetched']} rows but resolved 0 — check errors/skipped above and re-run)")
            break
        if time.monotonic() - t0 > args.time_budget:
            print(f"  (time budget {args.time_budget}s reached — stopping, re-run to continue)")
            break

    print(f"\nTotals: {totals}")
    if not args.dry_run:
        after = index_stats()
        print(f"\nAfter: linkage_pct={after.get('linkage_pct')} match_type_distribution={after.get('match_type_distribution')}")


if __name__ == "__main__":
    main()
