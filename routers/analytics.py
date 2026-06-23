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

from market_core import get_db
from backend_interface import get_indicator_catalog, get_latest_values
from server_deps import require_api_key

router = APIRouter(tags=["analytics"])


@router.get("/analytics/price-history", summary="Retrieve historical price snapshots for a product or store")
def price_history(
    product_id: str | None = None,
    store: str | None = None,
    line: str | None = None,
    limit: int = 50,
    authorization: str | None = Header(None),
):
    """Return time-series price snapshots filtered by product_id, store key, and/or
    business line. Ordered newest-first, up to limit records (default 50, max configurable).
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


@router.get("/analytics/trending", summary="Get recently updated products from the data moat")
def analytics_trending(country: str | None = None, line: str | None = None, limit: int = 10, authorization: str | None = Header(None)):
    """Return the most recently updated products in the moat, optionally filtered by
    business line. Note: 'trending' currently reflects recency of collector refresh,
    not price-movement velocity — a future update will add real trend scoring.
    Use as a discovery feed or to surface newly collected items. Maps to the
    market_trending MCP tool."""
    require_api_key(authorization)
    db = get_db()
    q = (
        "SELECT name, store_name, price, currency, line_name, queried_at "
        "FROM price_snapshots WHERE price > 0"
    )
    params: list = []
    # NOTE: country filter is currently a no-op (the original code had a bug).
    # When we wire it up properly, follow the same pattern as
    # /v1/data/export — translate country → store list via STORES.
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit * 2)
    rows = db.execute(q, params).fetchall()
    db.close()
    return {"trending": [dict(r) for r in rows], "total": len(rows)}


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
