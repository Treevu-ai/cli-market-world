"""Read-only analytics over price_snapshots.

Endpoints:
  GET /analytics/price-history   Snapshots filtered by product/store/line
  GET /analytics/stats           Totals + last snapshot timestamp
  GET /analytics/trending        Recent products (placeholder — sorted by queried_at)
  GET /analytics/brands          Top brands by snapshot count
  GET /analytics/indicators      Latest moat indicator values
"""

from __future__ import annotations

from fastapi import APIRouter, Header

from market_core import STORES, get_db
from backend_interface import get_indicator_catalog, get_latest_values
from server_deps import require_api_key

router = APIRouter(tags=["analytics"])


@router.get("/analytics/price-history", summary="Retrieve historical price snapshots for a product or store")
def price_history(
    product_id: str | None = None,
    store: str | None = None,
    line: str | None = None,
    country: str | None = None,
    limit: int = 50,
    authorization: str | None = Header(None),
):
    """Return time-series price snapshots filtered by product_id, store key, business line,
    and/or country. Ordered newest-first, up to limit records (default 50, max configurable).
    Use for price trend charts, volatility analysis, or verifying how long a price
    has held. product_id values come from search or compare results."""
    require_api_key(authorization)
    db = get_db()
    q = "SELECT * FROM price_snapshots WHERE 1=1"
    params: list = []
    if product_id:
        q += " AND product_id = ?"
        params.append(product_id)
    if store:
        q += " AND store = ?"
        params.append(store)
    if line:
        q += " AND line = ?"
        params.append(line)
    if country:
        country_stores = [
            s for s, sv in STORES.items()
            if sv.get("country", "").upper() == country.upper()
        ]
        if not country_stores:
            db.close()
            return {"count": 0, "snapshots": [], "country": country}
        placeholders = ",".join("?" * len(country_stores))
        q += f" AND store IN ({placeholders})"
        params.extend(country_stores)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(q, params).fetchall()
    db.close()
    return {"count": len(rows), "snapshots": [dict(r) for r in rows]}


@router.get("/analytics/stats", summary="Get data moat totals: snapshots, stores tracked, products, and freshness")
def analytics_stats(authorization: str | None = Header(None)):
    """Return aggregate counts for the data moat: total price snapshots, unique stores
    tracked, unique products, total search queries, and the timestamp of the latest
    snapshot. Use to verify moat health or show coverage stats to end users.
    Maps to the market_stats MCP tool."""
    require_api_key(authorization)
    db = get_db()
    total_snapshots = db.execute("SELECT COUNT(*) as n FROM price_snapshots").fetchone()["n"]
    total_queries = db.execute("SELECT COUNT(*) as n FROM search_queries").fetchone()["n"]
    stores_tracked = db.execute(
        "SELECT COUNT(DISTINCT store) as n FROM price_snapshots"
    ).fetchone()["n"]
    products_tracked = db.execute(
        "SELECT COUNT(DISTINCT product_id) as n FROM price_snapshots"
    ).fetchone()["n"]
    latest = db.execute("SELECT MAX(queried_at) as t FROM price_snapshots").fetchone()["t"]
    db.close()
    return {
        "total_price_snapshots": total_snapshots,
        "total_search_queries": total_queries,
        "unique_stores_tracked": stores_tracked,
        "unique_products_tracked": products_tracked,
        "latest_snapshot_at": latest,
    }


@router.get("/analytics/trending", summary="Get trending products ranked by price velocity (7-day change)")
def analytics_trending(country: str | None = None, line: str | None = None, limit: int = 10, authorization: str | None = Header(None)):
    """Return the most price-volatile products in the moat over the last 7 days,
    optionally filtered by country and business line. Each row includes change_pct
    (positive = price rose, negative = fell) and trend ('up' | 'down' | 'stable' | 'new').
    Products with no prior snapshot are ranked last. Maps to the market_trending MCP tool."""
    require_api_key(authorization)
    db = get_db()

    # Get the latest snapshot per (product_id, store) plus the most recent
    # snapshot from ≥7 days ago for the same pair, to compute price velocity.
    q = """
        SELECT
            p.name, p.store_name,
            p.price        AS current_price,
            p.currency, p.line_name, p.queried_at,
            (
                SELECT price FROM price_snapshots
                WHERE product_id = p.product_id
                  AND store = p.store
                  AND price > 0
                  AND queried_at <= datetime('now', '-7 days')
                ORDER BY queried_at DESC LIMIT 1
            ) AS prev_price
        FROM price_snapshots p
        JOIN (
            SELECT product_id, store, MAX(queried_at) AS latest_at
            FROM price_snapshots
            WHERE price > 0
            GROUP BY product_id, store
        ) cur
          ON p.product_id = cur.product_id
         AND p.store      = cur.store
         AND p.queried_at = cur.latest_at
        WHERE p.price > 0
    """
    params: list = []
    if line:
        q += " AND p.line = ?"
        params.append(line)
    if country:
        country_stores = [
            s for s, sv in STORES.items()
            if sv.get("country", "").upper() == country.upper()
        ]
        if country_stores:
            placeholders = ",".join("?" * len(country_stores))
            q += f" AND p.store IN ({placeholders})"
            params.extend(country_stores)
    q += " LIMIT ?"
    params.append(limit * 3)  # fetch extra before re-ranking by velocity
    rows = db.execute(q, params).fetchall()
    db.close()

    results = []
    for row in rows:
        r = dict(row)
        current = r.pop("current_price", 0) or 0
        prev = r.pop("prev_price", None)
        r["price"] = current
        if prev and prev > 0 and current > 0:
            change_pct = round((current - prev) / prev * 100, 1)
            r["change_pct"] = change_pct
            r["trend"] = "up" if change_pct > 1 else ("down" if change_pct < -1 else "stable")
        else:
            r["change_pct"] = None
            r["trend"] = "new"
        results.append(r)

    # Rank by absolute price velocity; products with no baseline go last
    results.sort(
        key=lambda x: abs(x["change_pct"]) if x["change_pct"] is not None else -1,
        reverse=True,
    )
    results = results[:limit]
    return {"trending": results, "total": len(results)}


@router.get("/analytics/brands", summary="Top brands in the data moat by snapshot count")
def analytics_brands(line: str | None = None, country: str | None = None, limit: int = 20, authorization: str | None = Header(None)):
    """Return the most-represented brands in the price snapshot database, ranked by
    number of snapshots. Filter by business line and country. Use for brand coverage
    analysis or to understand which brands dominate a category."""
    require_api_key(authorization)
    db = get_db()
    q = "SELECT brand, COUNT(*) as count FROM price_snapshots WHERE brand != '' AND price > 0"
    params: list = []
    if line:
        q += " AND line = ?"
        params.append(line)
    if country:
        # price_snapshots has no country column — derive it from store via STORES,
        # same pattern as brand_intel._pe_stores_for_country. Previously the
        # `country` param was accepted but silently ignored, so results were
        # global-scope regardless of the filter — dominated by data-quality
        # placeholder brand values ("Não Informado", "Genérico") and other
        # countries' brands crowding out the ones a caller actually asked for.
        store_keys = [s for s, sv in STORES.items() if sv.get("country", "").upper() == country.upper()]
        if not store_keys:
            db.close()
            return {"brands": [], "total": 0}
        q += f" AND store IN ({','.join('?' * len(store_keys))})"
        params.extend(store_keys)
    q += " GROUP BY brand ORDER BY count DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(q, params).fetchall()
    db.close()
    return {"brands": [dict(r) for r in rows], "total": len(rows)}


@router.get("/analytics/indicators", summary="Latest indicator values from the data moat (internal + external sources)")
def analytics_indicators(
    country: str | None = None,
    line: str | None = None,
    limit: int = 50,
    authorization: str | None = Header(None),
):
    """Return the most recent computed values for all available indicators, scoped by
    country and line. Combines internal moat indicators (promo_intensity, moat_freshness,
    price_dispersion) with public API sources (World Bank, IMF, Eurostat, BCB).
    Prefer GET /v1/intel/brief for a narrative summary; use this for raw indicator access."""
    require_api_key(authorization)
    db = get_db()
    values = get_latest_values(db, country=country, line=line, limit=limit)
    db.close()
    return {
        "count": len(values),
        "catalog_size": len(get_indicator_catalog()),
        "country": country,
        "line": line,
        "indicators": values,
    }
