"""Brand Intelligence endpoints.

Provides per-brand price monitoring across retailers, including
competitor comparison and promo event detection.

Endpoints:
  GET  /v1/brand-monitor          SKUs + competitors cross-store snapshot
  GET  /v1/brand-monitor/promos   Promo activations for a brand (and competitors)
  POST /v1/brand-monitor/config   Register or update brand config (PVPs, competitors)
  GET  /v1/brand-monitor/alerts   Active deviations from suggested retail prices
"""

from __future__ import annotations

import json
import math


from fastapi import APIRouter, Header, Query

from market_core import STORES, get_db
from server_deps import require_api_key

router = APIRouter(tags=["brand-intelligence"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _pe_stores_for_country(country: str) -> list[str]:
    """Return store keys that belong to *country* (ISO-2, case-insensitive)."""
    return [
        s for s, sv in STORES.items()
        if sv.get("country", "").upper() == country.upper()
    ]


def _cv(prices: list[float]) -> float | None:
    """Coefficient of variation (std / mean).  Returns None when < 2 prices."""
    if len(prices) < 2:
        return None
    n = len(prices)
    mean = sum(prices) / n
    if mean == 0:
        return None
    variance = sum((p - mean) ** 2 for p in prices) / n
    return round(math.sqrt(variance) / mean, 4)


def _load_brand_config(db, api_key: str, brand_slug: str) -> dict | None:
    """Fetch stored brand config for this api_key + brand_slug."""
    row = db.execute(
        "SELECT * FROM brand_intel_config WHERE api_key = ? AND brand_slug = ?",
        [api_key, brand_slug],
    ).fetchone()
    return dict(row) if row else None


def _normalize_brand(raw: str) -> str:
    """Case-insensitive normalisation for brand matching."""
    return raw.strip().lower()


# ── GET /v1/brand-monitor ─────────────────────────────────────────────────────

@router.get("/v1/brand-monitor", summary="Cross-store SKU snapshot for a brand + declared competitors")
def brand_monitor(
    brand: str = Query(..., description="Brand name to monitor (e.g. 'Gloria')"),
    country: str = Query("PE", description="ISO-2 country code"),
    competitors: str | None = Query(None, description="Comma-separated competitor brand names"),
    line: str | None = Query(None, description="Business line filter (e.g. 'supermercados')"),
    days: int = Query(30, ge=1, le=90, description="History window in days"),
    authorization: str | None = Header(None),
):
    """Return the latest price snapshot for every SKU of *brand* across all
    stores in *country*, plus SKUs of each declared *competitor* brand.

    Each SKU row includes:
    - name, brand, store, store_name, price, list_price, discount, currency
    - queried_at (freshness)
    - dispersion_score (CV of price across stores for that canonical product_id)
    - deviations vs PVP if brand config has been registered via POST /v1/brand-monitor/config

    Promo events (discount > 0) are flagged inline with ``promo_active: true``.
    """
    require_api_key(authorization)
    db = get_db()

    all_brands = [brand]
    if competitors:
        all_brands += [b.strip() for b in competitors.split(",") if b.strip()]

    store_keys = _pe_stores_for_country(country)
    if not store_keys:
        return {"error": f"No stores found for country '{country}'", "my_skus": [], "competitor_skus": [], "summary": {}}

    placeholders_stores = ",".join("?" * len(store_keys))
    placeholders_brands = ",".join("?" * len(all_brands))

    # Latest snapshot per (product_id, store) within the window
    q = f"""
        SELECT
            p.product_id,
            p.name,
            p.brand,
            p.store,
            p.store_name,
            p.price,
            p.list_price,
            p.discount,
            p.currency,
            p.line,
            p.line_name,
            p.url,
            p.queried_at
        FROM price_snapshots p
        JOIN (
            SELECT product_id, store, MAX(queried_at) AS latest_at
            FROM price_snapshots
            WHERE price > 0
              AND store IN ({placeholders_stores})
              AND LOWER(brand) IN ({placeholders_brands})
              AND queried_at >= datetime('now', '-{days} days')
            GROUP BY product_id, store
        ) cur
          ON p.product_id = cur.product_id
         AND p.store      = cur.store
         AND p.queried_at = cur.latest_at
        WHERE p.price > 0
    """
    params: list = store_keys + [_normalize_brand(b) for b in all_brands]

    if line:
        q += " AND p.line = ?"
        params.append(line)

    q += " ORDER BY p.brand, p.name, p.store"

    rows = db.execute(q, params).fetchall()
    skus = [dict(r) for r in rows]

    # ── compute per-product_id dispersion score ───────────────────────────────
    from collections import defaultdict
    prices_by_pid: dict[str, list[float]] = defaultdict(list)
    for sku in skus:
        prices_by_pid[sku["product_id"]].append(sku["price"])

    dispersion: dict[str, float | None] = {
        pid: _cv(prices) for pid, prices in prices_by_pid.items()
    }

    # ── load PVP config if available ──────────────────────────────────────────
    pvp_map: dict[str, float] = {}
    try:
        config_row = db.execute(
            "SELECT sku_pvps FROM brand_intel_config WHERE LOWER(brand_slug) = ? LIMIT 1",
            [_normalize_brand(brand)],
        ).fetchone()
        if config_row and config_row["sku_pvps"]:
            pvp_map = json.loads(config_row["sku_pvps"])
    except Exception:
        pass  # config table may not exist yet on fresh DB

    # ── annotate each sku row ─────────────────────────────────────────────────
    my_brand_norm = _normalize_brand(brand)
    my_skus: list[dict] = []
    competitor_skus: list[dict] = []

    for sku in skus:
        sku["promo_active"] = bool(sku.get("discount") and sku["discount"] > 0)
        sku["dispersion_score"] = dispersion.get(sku["product_id"])

        pvp = pvp_map.get(sku["product_id"])
        if pvp and pvp > 0 and sku["price"] > 0:
            deviation_pct = round((sku["price"] - pvp) / pvp * 100, 1)
            sku["pvp_suggested"] = pvp
            sku["pvp_deviation_pct"] = deviation_pct
            if deviation_pct > 5:
                sku["pvp_alert"] = "above_pvp"
            elif deviation_pct < -15:
                sku["pvp_alert"] = "far_below_pvp"
            else:
                sku["pvp_alert"] = None
        else:
            sku["pvp_suggested"] = None
            sku["pvp_deviation_pct"] = None
            sku["pvp_alert"] = None

        if _normalize_brand(sku["brand"]) == my_brand_norm:
            my_skus.append(sku)
        else:
            competitor_skus.append(sku)

    # ── summary stats ─────────────────────────────────────────────────────────
    my_promo_count = sum(1 for s in my_skus if s["promo_active"])
    comp_promo_count = sum(1 for s in competitor_skus if s["promo_active"])
    alerts = [s for s in my_skus if s.get("pvp_alert")]

    summary = {
        "brand": brand,
        "country": country,
        "days_window": days,
        "my_skus_count": len(my_skus),
        "my_skus_with_promo": my_promo_count,
        "competitor_skus_count": len(competitor_skus),
        "competitor_skus_with_promo": comp_promo_count,
        "pvp_alerts_count": len(alerts),
        "stores_covered": len({s["store"] for s in my_skus}),
        "competitors_found": list({s["brand"] for s in competitor_skus}),
    }

    return {
        "summary": summary,
        "my_skus": my_skus,
        "competitor_skus": competitor_skus,
    }


# ── GET /v1/brand-monitor/promos ──────────────────────────────────────────────

@router.get("/v1/brand-monitor/promos", summary="Promo activation history for a brand and its competitors")
def brand_promo_history(
    brand: str = Query(..., description="Brand name"),
    country: str = Query("PE"),
    competitors: str | None = Query(None, description="Comma-separated competitor brands"),
    line: str | None = Query(None),
    days: int = Query(30, ge=1, le=90),
    authorization: str | None = Header(None),
):
    """Return all price_history rows where discount > 0 for the given brands
    within the window, ordered by most recent first.

    Use to reconstruct when and where a promo was active, its depth (%), and
    estimated duration (first → last observation with discount in the window).
    """
    require_api_key(authorization)
    db = get_db()

    all_brands = [brand]
    if competitors:
        all_brands += [b.strip() for b in competitors.split(",") if b.strip()]

    store_keys = _pe_stores_for_country(country)
    if not store_keys:
        return {"promo_events": [], "count": 0}

    # Try price_history first (append-only log); fall back to price_snapshots
    # In early deployments price_history may not be populated yet.
    placeholders_stores = ",".join("?" * len(store_keys))
    placeholders_brands = ",".join("?" * len(all_brands))

    def _query_table(table: str) -> list[dict]:
        q = f"""
            SELECT product_id, name, brand, store, store_name,
                   price, list_price, discount, currency, queried_at
            FROM {table}
            WHERE discount > 0
              AND price > 0
              AND store IN ({placeholders_stores})
              AND LOWER(brand) IN ({placeholders_brands})
              AND queried_at >= datetime('now', '-{days} days')
        """
        p: list = store_keys + [_normalize_brand(b) for b in all_brands]
        if line:
            q += " AND line = ?"
            p.append(line)
        q += " ORDER BY queried_at DESC LIMIT 500"
        try:
            rows = db.execute(q, p).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []

    events = _query_table("price_history")
    if not events:
        events = _query_table("price_snapshots")

    # Annotate discount depth
    for e in events:
        if e.get("list_price") and e["list_price"] > 0 and e.get("price"):
            e["discount_depth_pct"] = round(
                (e["list_price"] - e["price"]) / e["list_price"] * 100, 1
            )
        else:
            e["discount_depth_pct"] = e.get("discount")

    return {"promo_events": events, "count": len(events), "brands": all_brands}


# ── POST /v1/brand-monitor/config ─────────────────────────────────────────────

from pydantic import BaseModel

class BrandConfigPayload(BaseModel):
    brand_slug: str
    competitors: list[str] = []
    sku_pvps: dict[str, float] = {}  # product_id -> PVP sugerido


@router.post("/v1/brand-monitor/config", summary="Register or update brand config: PVPs and declared competitors")
def brand_config_upsert(
    payload: BrandConfigPayload,
    authorization: str | None = Header(None),
):
    """Create or update the brand configuration for the authenticated API key.

    ``sku_pvps`` is a mapping of product_id → suggested retail price.
    ``competitors`` is a list of brand names that will be included
    automatically in /v1/brand-monitor calls without explicit ``?competitors=``.

    Calling this endpoint again with the same brand_slug overwrites the config.
    """
    api_key = require_api_key(authorization)
    db = get_db()
    slug = _normalize_brand(payload.brand_slug)

    # Ensure table exists (idempotent DDL)
    db.execute("""
        CREATE TABLE IF NOT EXISTS brand_intel_config (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_slug TEXT NOT NULL,
            api_key    TEXT NOT NULL,
            sku_pvps   TEXT,
            competitors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(api_key, brand_slug)
        )
    """)

    sku_pvps_json = json.dumps(payload.sku_pvps) if payload.sku_pvps else None
    competitors_json = json.dumps(payload.competitors) if payload.competitors else None

    db.execute("""
        INSERT INTO brand_intel_config (brand_slug, api_key, sku_pvps, competitors, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(api_key, brand_slug) DO UPDATE SET
            sku_pvps    = excluded.sku_pvps,
            competitors = excluded.competitors,
            updated_at  = CURRENT_TIMESTAMP
    """, [slug, api_key, sku_pvps_json, competitors_json])
    db.commit()

    return {
        "status": "ok",
        "brand_slug": slug,
        "sku_pvps_registered": len(payload.sku_pvps),
        "competitors_registered": len(payload.competitors),
    }


# ── GET /v1/brand-monitor/alerts ──────────────────────────────────────────────

@router.get("/v1/brand-monitor/alerts", summary="Active PVP deviations for registered brand SKUs")
def brand_alerts(
    brand: str = Query(..., description="Brand slug (must match registered config)"),
    country: str = Query("PE"),
    authorization: str | None = Header(None),
):
    """Return only SKUs with active PVP deviations (above or far below the
    suggested retail price registered via POST /v1/brand-monitor/config).

    Requires a prior call to POST /v1/brand-monitor/config with sku_pvps.
    Returns an empty list if no config has been registered.
    """
    api_key = require_api_key(authorization)
    db = get_db()

    # Load config
    try:
        config_row = db.execute(
            "SELECT sku_pvps FROM brand_intel_config WHERE api_key = ? AND LOWER(brand_slug) = ?",
            [api_key, _normalize_brand(brand)],
        ).fetchone()
    except Exception:
        return {"alerts": [], "count": 0, "message": "No brand config found. Call POST /v1/brand-monitor/config first."}

    if not config_row or not config_row["sku_pvps"]:
        return {"alerts": [], "count": 0, "message": "No PVP config found for this brand."}

    pvp_map: dict[str, float] = json.loads(config_row["sku_pvps"])
    if not pvp_map:
        return {"alerts": [], "count": 0}

    store_keys = _pe_stores_for_country(country)
    placeholders_pids = ",".join("?" * len(pvp_map))
    placeholders_stores = ",".join("?" * len(store_keys))

    q = f"""
        SELECT p.product_id, p.name, p.brand, p.store, p.store_name,
               p.price, p.list_price, p.discount, p.currency, p.queried_at
        FROM price_snapshots p
        JOIN (
            SELECT product_id, store, MAX(queried_at) AS latest_at
            FROM price_snapshots
            WHERE price > 0
              AND product_id IN ({placeholders_pids})
              AND store IN ({placeholders_stores})
            GROUP BY product_id, store
        ) cur
          ON p.product_id = cur.product_id
         AND p.store      = cur.store
         AND p.queried_at = cur.latest_at
        WHERE p.price > 0
    """
    params: list = list(pvp_map.keys()) + store_keys
    rows = db.execute(q, params).fetchall()

    alerts = []
    for row in rows:
        r = dict(row)
        pvp = pvp_map.get(r["product_id"])
        if not pvp or pvp <= 0:
            continue
        deviation_pct = round((r["price"] - pvp) / pvp * 100, 1)
        r["pvp_suggested"] = pvp
        r["pvp_deviation_pct"] = deviation_pct
        if deviation_pct > 5:
            r["pvp_alert"] = "above_pvp"
            alerts.append(r)
        elif deviation_pct < -15:
            r["pvp_alert"] = "far_below_pvp"
            alerts.append(r)

    alerts.sort(key=lambda x: abs(x["pvp_deviation_pct"]), reverse=True)
    return {"alerts": alerts, "count": len(alerts)}
