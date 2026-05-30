"""Dispersion analytics for GET /v1/dispersion."""

from __future__ import annotations

from market_spread import compute_dispersion
from price_confidence import spread_confidence
from quality_flagged import _load_products

MAX_LIMIT = 200
DEFAULT_LIMIT = 50


def build_dispersion(
    db,
    *,
    clean: bool = True,
    line: str | None = None,
    currency: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict:
    limit = min(max(int(limit), 1), MAX_LIMIT)
    offset = max(int(offset), 0)

    products = _load_products(db)
    if line:
        products = [p for p in products if p.get("line") == line]
    if currency:
        products = [p for p in products if (p.get("currency") or "") == currency]

    dispersion = compute_dispersion(products)
    items: list[dict] = []
    for row in dispersion:
        ratio = float(row.get("spread_ratio") or 0)
        status = row.get("status") or spread_confidence(ratio)
        if clean and status == "crit":
            continue
        item = {
            "line": row.get("line"),
            "line_key": row.get("line_key"),
            "subcategory": row.get("subcategory"),
            "currency": row.get("currency"),
            "spread_ratio": ratio,
            "status": status,
            "stores": row.get("count"),
            "avg_price": row.get("avg_price"),
            "min_price": row.get("min_price"),
            "max_price": row.get("max_price"),
            "price_basis": row.get("price_basis"),
        }
        if not clean and status == "crit":
            item["suspect"] = True
        items.append(item)

    page = items[offset : offset + limit]
    return {
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "clean": clean,
        "grouping": "line+currency+subcategory",
        "items": page,
    }
