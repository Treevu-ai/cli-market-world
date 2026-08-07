#!/usr/bin/env python3
"""Fase 4.1 — Mine BRAND_MAP candidates from real resolved data.

Every past BRAND_MAP entry that fixed a real production bug (danlac, cea,
hering, genrico/noinformado's exclusion) was found by a human manually
auditing canonical_product_id after the fact — reactive, one incident at a
time. This script automates the *finding* step: it extracts the brand slug
baked into every resolved canonical_product_id, counts how many snapshots
carry each slug, and reports the highest-volume slugs that are NOT already a
BRAND_MAP key — i.e. brand names canonicalize_brand() (cli-market-index,
engines/normalizer/brand_normalizer.py) fell through to either its raw-slug
fallback or its weak first-capitalized-token fallback for, at production
scale.

This is deliberately NOT automatic. It produces a report for a human to
review — promoting a slug to BRAND_MAP means deciding what the *correct*
canonical brand and its known variant spellings actually are, which requires
judgment this script has no way to make (see cli-market-index's own BRAND_MAP
comments: "not guessed, to avoid false canonicalization for brands never
verified").

Usage:
    python3 ops/mine_brand_candidates.py [--min-count 20] [--top 30] [--samples 3]

Needs the same DB access as the rest of this repo (DATABASE_URL / local
sqlite fallback via market_core.get_db()).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

GENERATED = Path(__file__).resolve().parent / "generated" / "reports"

# Non-brand id-prefix markers that would otherwise look like a brand slug
# when naively parsing canonical_product_id.split("_")[1] — "gov" from
# _build_gov_product_id (core/resolver.py), which has no brand at all.
_NON_BRAND_SLUGS = frozenset({"gov"})


def _extract_brand_slug(canonical_product_id: str) -> str | None:
    """canonical_product_id format: prod_{brand_slug}_{category}_{qty}{unit}[_{variety}]
    (core/resolver.py:_build_product_id). brand_slug itself is guaranteed
    underscore-free — _slugify() strips everything but [a-z0-9] — so the
    second '_'-separated token is always exactly the brand slug, never a
    fragment of category/qty."""
    if not canonical_product_id or not canonical_product_id.startswith("prod_"):
        return None
    parts = canonical_product_id.split("_")
    if len(parts) < 2:
        return None
    slug = parts[1]
    if slug in _NON_BRAND_SLUGS or not slug:
        return None
    return slug


def mine_candidates(db, *, min_count: int, top: int, samples: int) -> list[dict]:
    from engines.normalizer.brand_normalizer import BRAND_MAP

    known_brands = set(BRAND_MAP.keys())

    rows = db.execute(
        """
        SELECT canonical_product_id, name, brand, store
        FROM price_snapshots
        WHERE canonical_product_id IS NOT NULL AND canonical_product_id != ''
        """
    ).fetchall()

    counts: dict[str, int] = defaultdict(int)
    examples: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    for row in rows:
        slug = _extract_brand_slug(row["canonical_product_id"])
        if not slug or slug in known_brands:
            continue
        counts[slug] += 1
        if len(examples[slug]) < samples:
            examples[slug].append((
                str(row["name"] or "")[:80],
                str(row["brand"] or "")[:40],
                str(row["store"] or ""),
            ))

    candidates = [
        {
            "brand_slug": slug,
            "snapshot_count": n,
            "examples": [
                {"name": ex[0], "raw_brand": ex[1], "store": ex[2]}
                for ex in examples[slug]
            ],
        }
        for slug, n in counts.items()
        if n >= min_count
    ]
    candidates.sort(key=lambda c: c["snapshot_count"], reverse=True)
    return candidates[:top]


def _print_report(candidates: list[dict], *, total_unmapped_snapshots: int) -> None:
    print(f"\n=== BRAND_MAP candidates (Fase 4.1) ===")
    print(f"Total snapshots on an unmapped brand slug: {total_unmapped_snapshots:,}")
    print(f"Top {len(candidates)} candidates by volume (screening only — review before promoting):\n")
    for c in candidates:
        print(f"  {c['brand_slug']!r} — {c['snapshot_count']:,} snapshots")
        for ex in c["examples"]:
            print(f"      name={ex['name']!r} raw_brand={ex['raw_brand']!r} store={ex['store']}")
    print(
        "\nNota: un slug alto en volumen NO implica automáticamente que sea una "
        "marca real mal mapeada — puede ser un fallback legítimo (ej. token "
        "genérico del nombre) que no amerita entrada en BRAND_MAP. Cada "
        "candidato requiere revisión humana antes de promoverlo — este script "
        "no modifica BRAND_MAP."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine BRAND_MAP candidates (Fase 4.1)")
    parser.add_argument("--min-count", type=int, default=20)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    from market_core import get_db

    db = get_db()
    try:
        candidates = mine_candidates(db, min_count=args.min_count, top=args.top, samples=args.samples)
        total_unmapped = sum(c["snapshot_count"] for c in candidates)
    finally:
        db.close()

    if args.json:
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
    else:
        _print_report(candidates, total_unmapped_snapshots=total_unmapped)


if __name__ == "__main__":
    main()
