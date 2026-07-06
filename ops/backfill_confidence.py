#!/usr/bin/env python3
"""Backfill price_snapshots.confidence (discount + median outliers).

Run once after deploy Fase 7, then optionally after major collector runs:

  python3 ops/backfill_confidence.py
  python3 ops/backfill_confidence.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _row_val(row, key: str):
    """Works for dict rows (PG) and sqlite3.Row (SQLite)."""
    if hasattr(row, "get"):
        return row.get(key)
    try:
        return row[key]
    except (KeyError, IndexError):
        return None


def main() -> int:
    import market_core
    from market_core import ensure_db_initialized, get_db
    from market_db import price_snapshots_has_confidence
    from market_spread import find_median_outliers
    from price_confidence import compute_snapshot_confidence

    parser = argparse.ArgumentParser(description="Backfill price_snapshots.confidence")
    parser.add_argument("--dry-run", action="store_true", help="Report counts only")
    parser.add_argument(
        "--allow-sqlite",
        action="store_true",
        help="Allow running against local SQLite even when DATABASE_URL is set",
    )
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL", "").strip()
    ensure_db_initialized()
    if db_url and not market_core.USE_PG and not args.allow_sqlite:
        print(
            "DATABASE_URL is set but PostgreSQL is unavailable.\n"
            "  pip install psycopg2-binary\n"
            "  export DATABASE_URL='postgresql://...'  # fly postgres connect -a cli-market-db\n"
            "Or pass --allow-sqlite to backfill local market.db only.",
            file=sys.stderr,
        )
        return 1

    backend = "PostgreSQL" if market_core.USE_PG else f"SQLite ({market_core.DB_FILE})"
    print(f"Backfill target: {backend}")

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
        lp = _row_val(r, "list_price")
        list_price = float(lp) if lp else None
        conf = compute_snapshot_confidence(float(r["price"]), list_price)
        if conf == "suspect":
            suspect_discount += 1
        if not args.dry_run:
            db.execute(
                "UPDATE price_snapshots SET confidence = ? WHERE id = ?",
                (conf, r["id"]),
            )

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
