"""Paginated flagged quality items for GET /v1/quality/flagged."""

from __future__ import annotations

from typing import Literal

from dashboard_quality import QUALITY_FILTERS, count_flagged_discounts
from market_spread import compute_dispersion, find_median_outliers
from price_confidence import spread_confidence

ReasonFilter = Literal["discount", "outlier", "spread"] | None

MAX_LIMIT = 200
DEFAULT_LIMIT = 50

REASON_DISCOUNT = "discount>=90%"
REASON_OUTLIER = "median_outlier_5x"
REASON_SPREAD = "spread>10x"

_DISCOUNT_INNER = """
    SELECT name, store, store_name, price, list_price,
           ROUND(((1 - price / NULLIF(list_price, 0)) * 100)::numeric) AS discount_pct,
           currency, line_name
    FROM price_snapshots
    WHERE list_price > price AND price > 0 AND list_price < 999999
"""


def _clamp_limit(limit: int) -> int:
    return min(max(int(limit), 1), MAX_LIMIT)


def _load_products(db) -> list[dict]:
    rows = db.execute(
        """
        SELECT line, line_name, currency, category, name, brand, price, store, store_name
        FROM price_snapshots
        WHERE price > 0 AND price < 999999
        """
    ).fetchall()
    return [dict(r) for r in rows]


def _format_discount(row: dict) -> dict:
    return {
        "name": row.get("name"),
        "store": row.get("store"),
        "store_name": row.get("store_name"),
        "reason": REASON_DISCOUNT,
        "discount_pct": float(row.get("discount_pct") or 0),
        "price": float(row.get("price") or 0),
        "list_price": float(row.get("list_price") or 0),
        "currency": row.get("currency"),
        "line_name": row.get("line_name"),
        "confidence": "suspect",
    }


def fetch_flagged_discounts(db, *, offset: int, limit: int) -> list[dict]:
    rows = db.execute(
        f"""
        SELECT name, store, store_name, price, list_price, discount_pct, currency, line_name
        FROM ({_DISCOUNT_INNER}) discounted
        WHERE discount_pct >= 90
        ORDER BY discount_pct DESC, store ASC, name ASC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()
    return [_format_discount(dict(r)) for r in rows]


def outliers_from_products(products: list[dict]) -> list[dict]:
    raw = find_median_outliers(products, min_group=5, band=5.0, limit=None)
    items: list[dict] = []
    for row in raw:
        items.append({
            "name": row.get("name"),
            "store": row.get("store"),
            "store_name": row.get("store_name"),
            "reason": REASON_OUTLIER,
            "discount_pct": None,
            "price": float(row.get("price") or 0),
            "list_price": None,
            "currency": row.get("currency"),
            "line_name": row.get("line_name"),
            "confidence": row.get("confidence", "suspect"),
            "group_median": row.get("group_median"),
            "deviation": row.get("deviation"),
        })
    return items


def spread_crit_from_products(products: list[dict]) -> list[dict]:
    dispersion = compute_dispersion(products)
    items: list[dict] = []
    for row in dispersion:
        ratio = float(row.get("spread_ratio") or 0)
        if spread_confidence(ratio) != "crit":
            continue
        label = row.get("subcategory") or row.get("line") or "?"
        items.append({
            "name": label,
            "store": None,
            "store_name": None,
            "reason": REASON_SPREAD,
            "discount_pct": None,
            "spread_ratio": ratio,
            "price": float(row.get("avg_price") or 0),
            "list_price": None,
            "currency": row.get("currency"),
            "line_name": row.get("line"),
            "confidence": "suspect",
            "subcategory": row.get("subcategory"),
            "stores_in_group": row.get("count"),
        })
    items.sort(key=lambda x: (-float(x.get("spread_ratio") or 0), x.get("line_name") or ""))
    return items


def _paginate_combined(
    db,
    *,
    discount_total: int,
    outliers: list[dict],
    spreads: list[dict],
    offset: int,
    limit: int,
) -> list[dict]:
    items: list[dict] = []
    remaining = limit
    pos = offset

    if pos < discount_total and remaining > 0:
        take = min(remaining, discount_total - pos)
        items.extend(fetch_flagged_discounts(db, offset=pos, limit=take))
        remaining -= take
    pos = max(0, pos - discount_total)

    if remaining > 0 and pos < len(outliers):
        take = min(remaining, len(outliers) - pos)
        items.extend(outliers[pos : pos + take])
        remaining -= take
    pos = max(0, pos - len(outliers))

    if remaining > 0 and pos < len(spreads):
        take = min(remaining, len(spreads) - pos)
        items.extend(spreads[pos : pos + take])

    return items


def build_flagged_quality(
    db,
    *,
    reason: ReasonFilter = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict:
    """Build paginated flagged-quality payload."""
    limit = _clamp_limit(limit)
    offset = max(int(offset), 0)

    discount_total = count_flagged_discounts(db)

    if reason == "discount":
        return {
            "total": discount_total,
            "limit": limit,
            "offset": offset,
            "filters_applied": list(QUALITY_FILTERS),
            "items": fetch_flagged_discounts(db, offset=offset, limit=limit),
        }

    products: list[dict] | None = None

    def _products() -> list[dict]:
        nonlocal products
        if products is None:
            products = _load_products(db)
        return products

    if reason == "outlier":
        outlier_items = outliers_from_products(_products())
        return {
            "total": len(outlier_items),
            "limit": limit,
            "offset": offset,
            "filters_applied": list(QUALITY_FILTERS),
            "items": outlier_items[offset : offset + limit],
        }

    if reason == "spread":
        spread_items = spread_crit_from_products(_products())
        return {
            "total": len(spread_items),
            "limit": limit,
            "offset": offset,
            "filters_applied": list(QUALITY_FILTERS),
            "items": spread_items[offset : offset + limit],
        }

    outlier_items = outliers_from_products(_products())
    spread_items = spread_crit_from_products(_products())
    total = discount_total + len(outlier_items) + len(spread_items)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "filters_applied": list(QUALITY_FILTERS),
        "items": _paginate_combined(
            db,
            discount_total=discount_total,
            outliers=outlier_items,
            spreads=spread_items,
            offset=offset,
            limit=limit,
        ),
    }
