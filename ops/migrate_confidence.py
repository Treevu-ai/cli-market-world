#!/usr/bin/env python3
"""One-shot migration: add confidence column to price_snapshots on Railway PG."""
from market_core import get_db
from market_db import _migrate_price_snapshots_v7, price_snapshots_has_confidence

db = get_db()
print(f"has_confidence before: {price_snapshots_has_confidence(db)}")
_migrate_price_snapshots_v7(db)
db.commit()
print(f"has_confidence after: {price_snapshots_has_confidence(db)}")
db.close()
print("done")
