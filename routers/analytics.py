"""Read-only analytics over price_snapshots.

Endpoints:
  GET /analytics/price-history   Snapshots filtered by product/store/line
  GET /analytics/stats           Totals + last snapshot timestamp
  GET /analytics/trending        Recent products (Pro — live computed values)
  GET /analytics/brands          Top brands by snapshot count
  GET /analytics/indicators      Latest moat indicator values (Pro — live computed values)
"""

from __future__ import annotations

from fastapi import APIRouter, Header

from market_core import STORES, get_db
from backend_interface import get_indicator_catalog, get_latest_values
from routers.search import _is_relevant, _normalize_text, _query_tokens
from server_deps import require_api_key, require_pro

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
    require_pro(authorization)
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


# These are already accent/casing-normalized forms (checked against the same
# _normalize_text key used for merging, not the raw brand string) — e.g.
# "Genérico", "GENÉRICO", and "Generico" all fold to "generico" here.
_BRAND_JUNK = {"", "n a", "na", "generic", "generico", "generica"}


@router.get("/analytics/brands", summary="Top brands in the data moat by snapshot count")
def analytics_brands(
    line: str | None = None,
    country: str | None = None,
    query: str | None = None,
    limit: int = 20,
    authorization: str | None = Header(None),
):
    """Return the most-represented brands in the price snapshot database, ranked by
    number of snapshots. Filter by business line and country. Use for brand coverage
    analysis or to understand which brands dominate a category.

    `query` scopes brands to a specific product category (e.g. query='cafe')
    instead of every brand in the line — word-boundary matched against the
    product name (same relevance logic as /v1/search/products/search), so
    'cafe' doesn't spuriously match an unrelated product whose name merely
    contains the substring.

    Brand values matching a store's own name (e.g. brand="Wong" in a Wong
    snapshot) are kept as-is, not filtered — several retailers sell private-
    label ("marca blanca") products under their own store name as the brand,
    so that's real brand data, not a scraping artifact.

    Casing variants of the same brand ("Gloria"/"GLORIA") are merged into one
    row (counts summed, display name = the most frequent casing) — the raw
    column keeps whatever casing each retailer's page used, which otherwise
    fragments one brand into several rows.

    When `country` is given, each row also carries `is_new`: true the first
    time this brand has ever been seen for that country across all calls
    (tracked in known_brands) — a signal that a scrape found a new market
    entrant. Omitted (null) when no country filter is given, since "new for
    which scope" would be ambiguous without one."""
    require_api_key(authorization)
    db = get_db()
    q_tokens = _query_tokens(query) if query else []

    if q_tokens:
        from market_core.market_db import name_like_clause
        sql = "SELECT brand, name FROM price_snapshots WHERE brand != '' AND price > 0"
    else:
        sql = "SELECT brand, COUNT(*) as count FROM price_snapshots WHERE brand != '' AND price > 0"
    params: list = []
    if line:
        sql += " AND line = ?"
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
        sql += f" AND store IN ({','.join('?' * len(store_keys))})"
        params.extend(store_keys)
    if q_tokens:
        like = name_like_clause()
        sql += " AND (" + " OR ".join(like for _ in q_tokens) + ")"
        params.extend(f"%{t}%" for t in q_tokens)
    else:
        sql += " GROUP BY brand ORDER BY count DESC"
    rows = db.execute(sql, params).fetchall()

    # Merge casing, accent, AND spacing variants in Python — SQL GROUP BY
    # brand treats "Gloria"/"GLORIA" (casing), "Nescafe"/"NESCAFÉ" (accents),
    # and "Valle Norte"/"VALLENORTE" (spacing) as distinct groups, which is
    # exactly the fragmentation we're undoing here. First pass groups by the
    # same accent-folding normalize_text product search already uses
    # (preserves word spacing); second pass merges groups whose spacing-
    # collapsed form is identical, since two genuinely different brands
    # coincidentally sharing every letter in the same order once spaces are
    # removed is vanishingly unlikely in practice. When query is set, rows
    # are ungrouped (product) rows — apply word-boundary relevance filtering
    # and count brand occurrences here instead of in SQL. Track per-variant
    # sub-counts (not just first-seen) so the displayed spelling is the most
    # frequent one even when every row here contributes a count of 1 (the
    # query branch).
    variant_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        row = dict(row)
        if q_tokens and not _is_relevant(row.get("name", ""), q_tokens):
            continue
        brand = row["brand"]
        key = _normalize_text(brand).strip()
        if key in _BRAND_JUNK:
            continue
        row_count = 1 if q_tokens else row["count"]
        variants = variant_counts.setdefault(key, {})
        variants[brand] = variants.get(brand, 0) + row_count

    spaceless_groups: dict[str, list[dict[str, int]]] = {}
    for key, variants in variant_counts.items():
        spaceless_groups.setdefault(key.replace(" ", ""), []).append(variants)

    merged = []
    for group in spaceless_groups.values():
        combined: dict[str, int] = {}
        for variants in group:
            for brand, count in variants.items():
                combined[brand] = combined.get(brand, 0) + count
        display = max(combined, key=combined.get)
        merged.append({"display": display, "count": sum(combined.values())})

    results = sorted(merged, key=lambda b: b["count"], reverse=True)[:limit]
    brands_out = [{"brand": b["display"], "count": b["count"]} for b in results]

    if country:
        try:
            from market_brand_registry import diff_and_record_new_brands
            new_normalized = diff_and_record_new_brands(db, country, [b["brand"] for b in brands_out])
        except Exception:
            # known_brands missing/unreachable shouldn't break brand listing
            # itself — degrade to "unknown" rather than 500 the whole endpoint.
            new_normalized = set()
        for b in brands_out:
            b["is_new"] = b["brand"].strip().lower() in new_normalized
    else:
        for b in brands_out:
            b["is_new"] = None

    db.close()
    return {"brands": brands_out, "total": len(brands_out)}


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
    require_pro(authorization)
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
