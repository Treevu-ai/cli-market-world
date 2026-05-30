"""Paginated price listings for GET /v1/prices."""

from __future__ import annotations

from market_core import STORES
from market_spread import find_median_outliers
from quality_flagged import _load_products

MAX_LIMIT = 500
DEFAULT_LIMIT = 100

_DISCOUNT_FLAGGED = """
    list_price > price AND price > 0 AND list_price < 999999
    AND ROUND(((1 - price / NULLIF(list_price, 0)) * 100)::numeric) >= 90
"""


def _stores_for_country(country: str | None) -> list[str] | None:
    if not country:
        return None
    code = country.upper()
    stores = [k for k, v in STORES.items() if v.get("country") == code]
    return stores or None


def _outlier_keys(db) -> set[tuple[str, str]]:
    products = _load_products(db)
    keys: set[tuple[str, str]] = set()
    for row in find_median_outliers(products, min_group=5, band=5.0, limit=None):
        pid = row.get("product_id")
        store = row.get("store")
        if pid and store:
            keys.add((str(pid), str(store)))
    return keys


def _build_where(
    *,
    clean: bool,
    country: str | None,
    line: str | None,
    currency: str | None,
    store: str | None,
    outlier_keys: set[tuple[str, str]],
) -> tuple[str, list]:
    clauses = ["price > 0", "price < 999999"]
    params: list = []

    if clean:
        clauses.append(f"NOT ({_DISCOUNT_FLAGGED})")

    if line:
        clauses.append("line = ?")
        params.append(line)
    if currency:
        clauses.append("currency = ?")
        params.append(currency)
    if store:
        clauses.append("store = ?")
        params.append(store)

    country_stores = _stores_for_country(country)
    if country_stores is not None:
        placeholders = ",".join("?" for _ in country_stores)
        clauses.append(f"store IN ({placeholders})")
        params.extend(country_stores)

    if clean and outlier_keys:
        for pid, st in outlier_keys:
            clauses.append("NOT (product_id = ? AND store = ?)")
            params.extend([pid, st])

    return " AND ".join(clauses), params


def _row_to_item(row: dict, *, clean: bool) -> dict:
    list_price = row.get("list_price")
    price = float(row.get("price") or 0)
    discount_pct = None
    if list_price and float(list_price) > price > 0:
        discount_pct = round((1 - price / float(list_price)) * 100, 1)

    return {
        "product_id": row.get("product_id"),
        "name": row.get("name"),
        "store": row.get("store"),
        "store_name": row.get("store_name"),
        "price": price,
        "currency": row.get("currency"),
        "line": row.get("line"),
        "line_name": row.get("line_name"),
        "queried_at": row.get("queried_at"),
        "discount_pct": discount_pct,
        "confidence": "ok" if clean else "raw",
    }


def build_prices(
    db,
    *,
    clean: bool = True,
    country: str | None = None,
    line: str | None = None,
    currency: str | None = None,
    store: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict:
    limit = min(max(int(limit), 1), MAX_LIMIT)
    offset = max(int(offset), 0)
    outlier_keys = _outlier_keys(db) if clean else set()
    where_sql, params = _build_where(
        clean=clean,
        country=country,
        line=line,
        currency=currency,
        store=store,
        outlier_keys=outlier_keys,
    )

    total_row = db.execute(
        f"SELECT COUNT(*) as n FROM price_snapshots WHERE {where_sql}",
        params,
    ).fetchone()
    total = int(total_row["n"] if total_row else 0)

    rows = db.execute(
        f"""
        SELECT product_id, name, store, store_name, price, list_price,
               currency, line, line_name, queried_at
        FROM price_snapshots
        WHERE {where_sql}
        ORDER BY queried_at DESC, store ASC, product_id ASC
        LIMIT ? OFFSET ?
        """,
        [*params, limit, offset],
    ).fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "clean": clean,
        "items": [_row_to_item(dict(r), clean=clean) for r in rows],
    }
