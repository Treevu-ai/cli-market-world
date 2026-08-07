#!/usr/bin/env python3
"""Discover more over-fused canonical_product_id values (screening only).

cli-market-index#16 found that some Golden Records group genuinely
different products under one canonical_product_id — confirmed for
prod_laive_lacteos_0.18kg (5 cheese varieties) and prod_gloria_lacteos_0.946l
(milk variants + cooking cream), both stale data from before the current
_variety_fingerprint logic existed, already fixed via
ops/reresolve_over_fused_variants.py.

This script finds MORE candidates: for every canonical_product_id with more
than one distinct raw product name attached, it recomputes what the CURRENT
cli-market-index resolver logic (canonicalize_brand + extract_measurement +
infer_category + _variety_fingerprint + _build_product_id) would produce for
each distinct name. If that recomputation disagrees — different names under
the same stored id would compute different ids today — the group is flagged
as an over-fusion candidate.

Deliberately NOT automatic. Some multi-name groups under one id are
legitimate (e.g. minor name variants of the literal same SKU across
retailers, or cases where the fingerprint intentionally treats two spellings
as the same product) — a human should look at the flagged names before
feeding a canonical_product_id into ops/reresolve_over_fused_variants.py.

Usage:
    python3 ops/mine_over_fused_variants.py [--min-rows 5] [--top 30]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _fresh_id(name: str, brand: str) -> str | None:
    from core.resolver import _build_product_id, _variety_fingerprint, infer_category
    from engines.normalizer.brand_normalizer import canonicalize_brand
    from engines.normalizer.unit_normalizer import extract_measurement

    brand_slug = canonicalize_brand(brand or "", name)
    measurement = extract_measurement(name)
    if not measurement:
        return None
    qty, unit = measurement
    category_hint = infer_category(name)
    variety = _variety_fingerprint(name, brand_slug, category_hint)
    return _build_product_id(brand_slug, category_hint, qty, unit, variety)


def mine_candidates(db, *, min_rows: int, top: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT canonical_product_id, name, brand
        FROM price_snapshots
        WHERE canonical_product_id IS NOT NULL AND canonical_product_id != ''
          AND name IS NOT NULL AND trim(name) != ''
        """
    ).fetchall()

    by_id: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in rows:
        by_id[row["canonical_product_id"]].append((str(row["name"]), str(row["brand"] or "")))

    candidates = []
    for cid, members in by_id.items():
        distinct_names = {n for n, _ in members}
        if len(distinct_names) < 2:
            continue

        fresh_ids: dict[str, set[str]] = defaultdict(set)
        for name, brand in members:
            fresh = _fresh_id(name, brand)
            if fresh:
                fresh_ids[fresh].add(name)

        if len(fresh_ids) < 2:
            continue  # current logic agrees these belong together

        candidates.append(
            {
                "canonical_product_id": cid,
                "row_count": len(members),
                "distinct_fresh_ids": len(fresh_ids),
                "examples": [
                    {"fresh_id": fid, "names": sorted(names)[:3]}
                    for fid, names in sorted(fresh_ids.items(), key=lambda kv: -len(kv[1]))[:6]
                ],
            }
        )

    candidates = [c for c in candidates if c["row_count"] >= min_rows]
    candidates.sort(key=lambda c: c["row_count"], reverse=True)
    return candidates[:top]


def _print_report(candidates: list[dict]) -> None:
    print("\n=== Over-fused canonical_product_id candidates ===")
    print(f"Found {len(candidates)} candidates (screening only — review before re-resolving):\n")
    for c in candidates:
        print(f"  {c['canonical_product_id']!r} — {c['row_count']} rows, {c['distinct_fresh_ids']} distinct ids under current logic")
        for ex in c["examples"]:
            print(f"      -> {ex['fresh_id']}: {ex['names']}")
    print(
        "\nNota: no todo grupo marcado es necesariamente un error — algunos "
        "nombres distintos legítimamente deberían compartir Golden Record. "
        "Revisar los ejemplos antes de correr "
        "ops/reresolve_over_fused_variants.py --ids <canonical_product_id ...> "
        "— este script no modifica nada."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine over-fused canonical_product_id candidates")
    parser.add_argument("--min-rows", type=int, default=5)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    from market_core import get_db

    db = get_db()
    try:
        candidates = mine_candidates(db, min_rows=args.min_rows, top=args.top)
    finally:
        db.close()

    if args.json:
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
    else:
        _print_report(candidates)


if __name__ == "__main__":
    main()
