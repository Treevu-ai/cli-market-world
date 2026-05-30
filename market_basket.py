"""Snapshot-based basic basket (canasta) — aligned with dashboard canasta_basica."""

from __future__ import annotations

from market_core import STORES
from market_spread import CANASTA_ITEMS, matches_canasta_item
from market_units import is_standard_canasta_pack

CANASTA_TOTAL_ITEMS = 10
CANASTA_PARTIAL_THRESHOLD = 6  # 60% — below this, totals are not comparable
DEFAULT_MIN_ITEMS = 3


def build_canasta_basica(
    db,
    *,
    store_keys: list[str] | None = None,
    min_items: int = DEFAULT_MIN_ITEMS,
    limit: int = 10,
) -> list[dict]:
    """Aggregate 10-item canasta totals per store from price_snapshots."""
    allowed = set(store_keys) if store_keys else None
    canasta: dict[str, dict] = {}

    for prod in CANASTA_ITEMS:
        rows = db.execute(
            """SELECT store_name, store, name, price, currency
               FROM price_snapshots
               WHERE line='supermercados' AND price>0 AND price<999999 AND name LIKE ?""",
            (f"%{prod}%",),
        ).fetchall()
        store_best: dict[tuple[str, str], float] = {}
        store_fallback: dict[tuple[str, str], float] = {}
        for r in rows:
            if allowed is not None and r["store"] not in allowed:
                continue
            row = {"line": "supermercados", "name": r["name"]}
            if not matches_canasta_item(row, prod):
                continue
            key = (r["store"], r["currency"])
            price = float(r["price"])
            if is_standard_canasta_pack(r["name"], prod):
                if key not in store_best or price < store_best[key]:
                    store_best[key] = price
            elif key not in store_best:
                if key not in store_fallback or price < store_fallback[key]:
                    store_fallback[key] = price
        for key, price in store_fallback.items():
            if key not in store_best:
                store_best[key] = price
        for (store_slug, cur), best_price in store_best.items():
            meta = STORES.get(store_slug, {})
            display = meta.get("name") or store_slug
            canasta.setdefault(
                store_slug,
                {
                    "store": store_slug,
                    "store_name": display,
                    "items": 0,
                    "total": 0.0,
                    "currency": cur,
                },
            )
            canasta[store_slug]["items"] += 1
            canasta[store_slug]["total"] = round(canasta[store_slug]["total"] + best_price, 2)

    return sorted(
        [v for v in canasta.values() if v["items"] >= min_items],
        key=lambda x: x["total"],
    )[:limit]


def build_snapshot_basket(
    db,
    *,
    store_keys: list[str] | None = None,
    min_items: int = DEFAULT_MIN_ITEMS,
) -> dict:
    """API payload for GET /v1/basket (DB snapshots, not live scrape)."""
    rows = build_canasta_basica(db, store_keys=store_keys, min_items=min_items, limit=100)
    last_row = db.execute(
        "SELECT MAX(queried_at) as ts FROM price_snapshots WHERE price > 0"
    ).fetchone()
    snapshot_at = last_row["ts"] if last_row else None

    stores = []
    for row in rows:
        items_found = int(row["items"])
        stores.append({
            "store": row["store"],
            "store_name": row["store_name"],
            "items_found": items_found,
            "completeness_pct": items_found * 10,
            "comparable": items_found >= CANASTA_PARTIAL_THRESHOLD,
            "total": row["total"],
            "currency": row["currency"],
        })

    return {
        "source": "snapshot",
        "snapshot_at": str(snapshot_at) if snapshot_at else None,
        "items_total": CANASTA_TOTAL_ITEMS,
        "partial_threshold": CANASTA_PARTIAL_THRESHOLD,
        "min_items": min_items,
        "stores": stores,
    }
