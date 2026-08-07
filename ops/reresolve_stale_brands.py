#!/usr/bin/env python3
"""Fase 4.1-bis — Re-resolve snapshots stuck on an already-fixed brand bug.

ops/mine_brand_candidates.py found that ~8,300 price_snapshots rows carry a
canonical_product_id built from a brand slug that BRAND_MAP or
GENERIC_BRAND_TOKENS (cli-market-index) already handles correctly — the fix
shipped, but nothing ever re-resolved the snapshots that were linked *before*
it shipped. Routine backfill (index_gate.backfill_canonical_product_ids) only
touches snapshots with no canonical_product_id at all, so these stay wrong
forever without an explicit sweep.

Confirmed stale slugs (2026-08-06 mining run against production):
  ca           -> BRAND_MAP["cea"] already covers "c&a"/"cea"      (3,612 snapshots)
  heringadulto -> BRAND_MAP["hering"] already covers "hering adulto" (1,720 snapshots)
  noinformado  -> GENERIC_BRAND_TOKENS already covers "não informado" (1,636 snapshots)
  genrico      -> GENERIC_BRAND_TOKENS already covers "genérico"     (885 snapshots)
  heringkids   -> BRAND_MAP["hering"] already covers "hering kids"   (459 snapshots)

This is a one-off maintenance sweep, not part of the routine collector cycle
— run it once after confirming the fix is live, not on a schedule.

Usage:
    python3 ops/reresolve_stale_brands.py --dry-run   # preview only
    python3 ops/reresolve_stale_brands.py              # apply
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

STALE_SLUGS = ["ca", "heringadulto", "noinformado", "genrico", "heringkids"]

DEFAULT_BATCH_LIMIT = 2000
DEFAULT_MAX_BATCHES = 20
DEFAULT_TIME_BUDGET_S = 600


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-resolve snapshots stuck on a known-fixed brand bug")
    parser.add_argument("--slugs", nargs="*", default=STALE_SLUGS)
    parser.add_argument("--limit", type=int, default=DEFAULT_BATCH_LIMIT)
    parser.add_argument("--max-batches", type=int, default=DEFAULT_MAX_BATCHES)
    parser.add_argument("--time-budget", type=int, default=DEFAULT_TIME_BUDGET_S)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--exact-only",
        action="store_true",
        help=(
            "Bypass fuzzy/name-match resolution and only accept an exact "
            "canonical_product_id match (or create a fresh one). Required "
            "for slugs whose stale products are discoverable via "
            "cli-market-index's alias-indexing bug — see "
            "index_gate._resolve_exact_only's docstring."
        ),
    )
    args = parser.parse_args()

    # A real brand_slug is always [a-z0-9]+ (core/resolver.py's _slugify
    # strips everything else) — --slugs is free-form CLI input, and
    # _fetch_stale_snapshot_rows only escapes the two underscores it inserts
    # around the slug, not characters inside it. An unvalidated "%" or "_"
    # here isn't a SQL-injection risk (still parameterized) but would be
    # interpreted as a LIKE wildcard, matching far more than intended.
    for slug in args.slugs:
        if not re.fullmatch(r"[a-z0-9]+", slug):
            parser.error(f"invalid --slugs value {slug!r}: must match [a-z0-9]+")

    from index_gate import index_stats, reresolve_stale_snapshots

    before = index_stats()
    print(f"Slugs targeted: {args.slugs}")
    print(f"Before: linkage_pct={before.get('linkage_pct')} match_type_distribution={before.get('match_type_distribution')}\n")

    t0 = time.monotonic()
    totals = {"resolved": 0, "linked": 0, "exact": 0, "fuzzy": 0, "auto": 0, "errors": 0}
    for batch_num in range(1, args.max_batches + 1):
        stats = reresolve_stale_snapshots(
            args.slugs, limit=args.limit, dry_run=args.dry_run, exact_only=args.exact_only
        )
        for k in totals:
            totals[k] += int(stats.get(k, 0))
        print(f"  batch {batch_num}: fetched={stats.get('fetched', 0)} resolved={stats.get('resolved', 0)} "
              f"linked={stats.get('linked', 0)} exact={stats.get('exact', 0)} fuzzy={stats.get('fuzzy', 0)} "
              f"errors={stats.get('errors', 0)}")
        if not stats.get("fetched"):
            print("  (no more stale rows found — stopping)")
            break
        if not stats.get("resolved"):
            print(f"  (fetched {stats['fetched']} rows but resolved 0 — stale rows likely remain; "
                  f"check errors/skipped above and re-run)")
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
