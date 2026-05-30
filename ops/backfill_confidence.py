#!/usr/bin/env python3
"""Backfill price_snapshots.confidence (discount + median outliers).

Run once after deploy Fase 7, then optionally after major collector runs:

  python3 ops/backfill_confidence.py
  python3 ops/backfill_confidence.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from market_core import ensure_db_initialized, get_db  # noqa: E402
from market_db import price_snapshots_has_confidence  # noqa: E402
from market_spread import find_median_outliers  # noqa: E402
from price_confidence import compute_snapshot_confidence  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill price_snapshots.confidence")
    parser.add_argument("--dry-run", action="store_true", help="Report counts only")
    args = parser.parse_args()

    ensure_db_initialized()
    db = get_db()
    if not price_snapshots_has_confidence(db):
        print("confidence column missing — restart API/collector to run migration", file=sys.stderr)
        db.close()
        return 1

    rows = db.execute(
        "SELECT id, price, list_price FROM price_snapshots WHERE price > 0 AND price < 999999"
    ).fetchall()
    suspect_discount = 0
    for r in rows:
        list_price = float(r["list_price"]) if r.get("list_price") else None
        conf = compute_snapshot_confidence(float(r["price"]), list_price)
        if conf == "suspect":
            suspect_discount += 1
        if not args.dry_run:
            db.execute("UPDATE price_snapshots SET confidence = ? WHERE id = ?", (conf, r["id"]))

    products = db.execute(
        """
        SELECT line, line_name, currency, category, name, price, store, store_name
        FROM price_snapshots WHERE price > 0 AND price < 999999
        """
    ).fetchall()
    outlier_keys = {
        (o.get("store"), o.get("name"))
        for o in find_median_outliers([dict(p) for p in products], min_group=5, band=5.0, limit=50000)
    }
    outlier_groups = len(outlier_keys)
    if not args.dry_run:
        for store, name in outlier_keys:
            if store and name:
                db.execute(
                    "UPDATE price_snapshots SET confidence = 'suspect' WHERE store = ? AND name = ?",
                    (store, name),
                )
        db.commit()
    db.close()

    mode = "dry-run" if args.dry_run else "applied"
    print(
        f"Backfill ({mode}): {len(rows)} rows scanned, "
        f"{suspect_discount} discount-suspect, {outlier_groups} outlier groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
