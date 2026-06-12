"""Intelligence API — indicator catalog, scores, inflation, enrichment, alerts.

Endpoints:
  GET  /v1/intel/indicators                 Catalog of all 34 indicators
  GET  /v1/intel/indicators/{key}           Single indicator detail + latest value
  GET  /v1/intel/scores                     Composite scores from indicators
  GET  /v1/intel/inflation                  Price change 7d by line/currency
  GET  /v1/intel/alerts                     Price alerts (threshold-based)
  GET  /v1/intel/enrichment                 Enrichment indicators (OFF, Wiki, etc.)
  GET  /v1/intel/enrichment/subcategories   Subcategory-level enrichment
  GET  /v1/intel/brief                      One-call intelligence narrative (PR3)
  POST /v1/intel/refresh                    Trigger indicator recomputation
  POST /v1/intel/enrichment/refresh         Trigger enrichment-only refresh
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, field_validator

from market_core import STORES, get_db, price_to_usd
from market_billing import db_get_subscription
from server_deps import require_api_key, require_pro, require_starter
from backend_interface import (
    ENRICHMENT_INDICATOR_KEYS,
    build_intel_brief,
    get_indicator_catalog,
    get_latest_values,
    get_scores,
)

logger = logging.getLogger("market.server").getChild("intel")
router = APIRouter(prefix="/v1/intel", tags=["intelligence"])


def _catalog(db) -> list[dict]:
    """Tolerate both catalog signatures: the public repo exposes
    get_indicator_catalog() (no args); the private backend exposes
    get_indicator_catalog(db). Call whichever the installed version provides."""
    try:
        return get_indicator_catalog(db)
    except TypeError:
        return get_indicator_catalog()


# ── Conversational agent ─────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def _clean(cls, v: str) -> str:
        v = (v or "").strip()[:500]
        if not v:
            raise ValueError("La pregunta no puede estar vacía")
        return v


def _check_agent_quota(username: str, db) -> None:
    """Enforce monthly agent query quota for Starter tier (50/month).

    Pro and Enterprise have agent_queries_month == -1 (unlimited).
    Free has 0 — blocked upstream by require_starter.
    """
    sub = db_get_subscription(username)
    monthly_limit = sub.get("agent_queries_month", 0)
    if monthly_limit == -1:
        return  # unlimited
    if monthly_limit == 0:
        raise HTTPException(status_code=403, detail="Agent access not included in your plan.")
    from datetime import timezone as tz
    now = datetime.now(tz.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    row = db.execute(
        "SELECT COUNT(*) as n FROM agent_queries WHERE username=? AND queried_at>=?",
        (username, month_start),
    ).fetchone()
    used = row["n"] if row else 0
    remaining = monthly_limit - used
    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Monthly agent quota exhausted ({monthly_limit} queries/month on Starter). "
                "Upgrade to Pro for unlimited access: /billing/paypal"
            ),
        )


def _record_agent_query(username: str, db) -> int:
    """Log an agent query and return remaining quota (-1 if unlimited)."""
    from datetime import timezone as tz
    sub = db_get_subscription(username)
    monthly_limit = sub.get("agent_queries_month", 0)
    db.execute(
        "INSERT INTO agent_queries (username, queried_at) VALUES (?, ?)",
        (username, datetime.now(tz.utc).isoformat()),
    )
    db.commit()
    if monthly_limit == -1:
        return -1
    now = datetime.now(tz.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    row = db.execute(
        "SELECT COUNT(*) as n FROM agent_queries WHERE username=? AND queried_at>=?",
        (username, month_start),
    ).fetchone()
    used = row["n"] if row else 1
    return max(0, monthly_limit - used)


@router.post("/ask")
def intel_ask(body: AskRequest, authorization: str | None = Header(None)):
    """Natural-language Q&A over the data moat. Starter+ (50 queries/month) or Pro/Enterprise (unlimited).

    Runs a Claude tool-use loop against the live intelligence functions
    (inflation, indicators, prices, dispersion, staple momentum) and returns a
    grounded answer. Returns 503 if the agent isn't configured on the server.
    """
    username = require_starter(authorization)
    from market_intel_agent import AgentUnavailable, ask_intel

    db = get_db()
    try:
        _check_agent_quota(username, db)
        result = ask_intel(body.question, db)
        remaining = _record_agent_query(username, db)
        if remaining != -1:
            result["agent_queries_remaining"] = remaining
        return result
    except AgentUnavailable as e:
        raise HTTPException(
            status_code=503,
            detail=f"Intel agent unavailable: {e}",
        )
    finally:
        db.close()


# ── Catalog ────────────────────────────────────────────────────────────────────

@router.get("/indicators")
def list_indicators(authorization: str | None = Header(None)):
    """Return the full indicator catalog (34 definitions)."""
    require_api_key(authorization)
    db = get_db()
    try:
        catalog = _catalog(db)
        return {"indicators": catalog, "total": len(catalog)}
    finally:
        db.close()


@router.get("/indicators/{key}")
def get_indicator(
    key: str,
    country: str | None = Query(None),
    line: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Single indicator definition + latest values (optionally scoped)."""
    require_api_key(authorization)
    db = get_db()
    try:
        catalog = _catalog(db)
        match = next((i for i in catalog if i["key"] == key), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Indicator '{key}' not found")
        values = get_latest_values(db, country=country, line=line)
        latest = next((v for v in values if v.get("key") == key), None)
        return {"indicator": match, "latest_value": latest}
    finally:
        db.close()


# ── Brief (PR3) ───────────────────────────────────────────────────────────────

@router.get("/brief")
def intel_brief(
    country: str | None = Query(None),
    line: str | None = Query(None),
    days: int = Query(7, ge=1, le=90),
    include_catalog: bool = Query(False),
    authorization: str | None = Header(None),
):
    """One-call intelligence narrative: shelf signals, macro gap, scores, confidence."""
    require_api_key(authorization)
    db = get_db()
    try:
        return build_intel_brief(
            db,
            country=country.upper() if country else None,
            line=line,
            days=days,
            include_catalog=include_catalog,
        )
    finally:
        db.close()


# ── Scores ──────────────────────────────────────────────────────────────────────

@router.get("/scores")
def list_scores(
    country: str | None = Query(None),
    line: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Composite scores derived from indicators (14 scores)."""
    require_api_key(authorization)
    db = get_db()
    try:
        return get_scores(db, country=country, line=line)
    finally:
        db.close()


# ── Inflation ───────────────────────────────────────────────────────────────────

@router.get("/inflation")
def get_inflation(
    country: str | None = Query(None),
    line: str | None = Query(None),
    days: int = Query(7, ge=1, le=90),
    authorization: str | None = Header(None),
):
    """Price change over `days` by line + currency, from price_snapshots."""
    require_api_key(authorization)
    db = get_db()
    try:
        now = datetime.now(timezone.utc)
        recent_cutoff = (now - timedelta(days=days)).isoformat()
        older_cutoff = (now - timedelta(days=days * 2)).isoformat()

        # Per (line, currency) pairs with recent data
        pair_sql = """SELECT line, currency, COUNT(*) as n
                      FROM price_snapshots
                      WHERE price > 0 AND price < 999999 AND queried_at >= ?"""
        params: list = [recent_cutoff]
        if country:
            store_keys = [k for k, s in STORES.items() if s.get("country") == country.upper()]
            if not store_keys:
                return {"items": [], "avg_inflation_pct": 0, "country": country}
            placeholders = ",".join("?" * len(store_keys))
            pair_sql += f" AND store IN ({placeholders})"
            params.extend(store_keys)
        if line:
            pair_sql += " AND line = ?"
            params.append(line)
        pair_sql += " GROUP BY line, currency"

        pairs = db.execute(pair_sql, params).fetchall()

        from market_core import LINES

        items: list[dict] = []
        deltas: list[float] = []
        for pair in pairs:
            ln = pair["line"]
            cur = pair["currency"] or ""
            recent_avg = db.execute(
                """SELECT ROUND(AVG(price)::numeric, 2) as avg_price
                   FROM price_snapshots
                   WHERE line=? AND currency=? AND price>0 AND price<999999 AND queried_at>=?""",
                (ln, cur, recent_cutoff),
            ).fetchone()
            older_avg = db.execute(
                """SELECT ROUND(AVG(price)::numeric, 2) as avg_price
                   FROM price_snapshots
                   WHERE line=? AND currency=? AND price>0 AND price<999999
                     AND queried_at>=? AND queried_at<?""",
                (ln, cur, older_cutoff, recent_cutoff),
            ).fetchone()
            r_avg = float(recent_avg["avg_price"] or 0) if recent_avg else 0.0
            o_avg = float(older_avg["avg_price"] or 0) if older_avg else 0.0
            delta = round((r_avg - o_avg) / o_avg * 100, 1) if o_avg > 0 else 0
            deltas.append(delta)
            items.append({
                "line": (LINES.get(ln, {}).get("name") or ln),
                "line_key": ln,
                "currency": cur,
                "avg_now": r_avg,
                "avg_before": o_avg,
                "delta_pct": delta,
                "avg_now_usd": price_to_usd(r_avg, cur),
                "avg_before_usd": price_to_usd(o_avg, cur),
                "n_products": int(pair["n"] or 0),
            })

        avg_inflation = round(sum(deltas) / len(deltas), 1) if deltas else 0.0

        return {
            "items": items,
            "avg_inflation_pct": avg_inflation,
            "days": days,
            "country": country,
            "line": line,
            "disclaimer": "Inflación observada desde góndola online. No reemplaza IPC oficial (INEI, INDEC, etc.).",
        }
    finally:
        db.close()


# ── Alerts ──────────────────────────────────────────────────────────────────────

@router.get("/alerts")
def get_alerts(
    product: str = Query(..., min_length=1),
    store: str | None = Query(None),
    threshold_pct: float = Query(5.0, ge=0.1, le=100.0),
    limit: int = Query(10, ge=1, le=50),
    authorization: str | None = Header(None),
):
    """Alert when a product's price changed beyond threshold_pct."""
    require_api_key(authorization)
    db = get_db()
    try:
        params: list = [f"%{product}%"]
        store_clause = ""
        if store:
            store_clause = "AND store = ?"
            params.append(store)
        rows = db.execute(
            f"""SELECT product_id, store, store_name, name, price, list_price, currency,
                       queried_at
                FROM price_snapshots
                WHERE name LIKE ? AND price > 0 {store_clause}
                ORDER BY queried_at DESC LIMIT ?""",
            params + [limit * 2],
        ).fetchall()
        return {"product": product, "store": store, "threshold_pct": threshold_pct, "results": [dict(r) for r in rows]}
    finally:
        db.close()


# ── Refresh ─────────────────────────────────────────────────────────────────────

@router.post("/refresh")
def refresh_indicators(
    country: str | None = Query(None),
    line: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Trigger indicator recomputation from price_snapshots data.

    Computes internal indicators (promo_intensity, moat_freshness, etc.) directly
    from price_snapshots. External indicators (World Bank, IMF, etc.) require the
    collector backend and are returned as 0 when not available.
    """
    require_pro(authorization)
    db = get_db()
    try:
        internal_written = _refresh_internal_indicators(db, country=country, line=line)
        db.commit()
        return {
            "ok": True,
            "internal_written": internal_written,
            "external_written": 0,
            "enrichment_written": 0,
            "country": country,
            "line": line,
            "hint": "External indicators require the collector backend. Use POST /v1/intel/refresh on the deployed API for full refresh.",
        }
    finally:
        db.close()


@router.post("/enrichment/refresh")
def refresh_enrichment(
    country: str = Query("PE"),
    authorization: str | None = Header(None),
):
    """Refresh enrichment indicators only (OFF, Wiki, Open-Meteo, etc.)."""
    require_pro(authorization)
    db = get_db()
    try:
        # Enrichment indicators currently come from the collector backend.
        # From the public repo, we return the current state.
        values = get_latest_values(db, country=country)
        enrichment = [v for v in values if v.get("key") in ENRICHMENT_INDICATOR_KEYS]
        return {
            "ok": True,
            "enrichment_written": len(enrichment),
            "country": country,
            "hint": "Full enrichment refresh requires the collector backend with external API access.",
        }
    finally:
        db.close()


# ── Enrichment ──────────────────────────────────────────────────────────────────

@router.get("/enrichment")
def get_enrichment(
    country: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Enrichment indicators: OFF, Wiki, Open-Meteo, World Bank food CPI."""
    require_api_key(authorization)
    db = get_db()
    try:
        values = get_latest_values(db, country=country, limit=100)
        enrichment = [v for v in values if v.get("key") in ENRICHMENT_INDICATOR_KEYS]
        return {
            "indicators": enrichment,
            "total": len(enrichment),
            "country": country,
            "sources": "Open Food Facts · Wikimedia Pageviews · Open-Meteo · World Bank",
        }
    finally:
        db.close()


@router.get("/enrichment/subcategories")
def get_enrichment_subcategories(
    country: str = Query("PE"),
    authorization: str | None = Header(None),
):
    """Subcategory-level enrichment (10 canasta items × Wiki momentum)."""
    require_api_key(authorization)
    db = get_db()
    try:
        values = get_latest_values(db, country=country, limit=200)
        subcat = [
            v for v in values
            if v.get("key", "").startswith("subcat_")
        ]
        return {
            "subcategories": subcat,
            "total": len(subcat),
            "country": country,
        }
    finally:
        db.close()


# ── Internal refresh helpers ────────────────────────────────────────────────────

def _refresh_internal_indicators(db, *, country: str | None = None, line: str | None = None) -> int:
    """Compute internal indicators from price_snapshots and write to indicator_values.

    Returns count of values written.
    """
    from datetime import timezone as tz
    now = datetime.now(tz.utc).isoformat()

    # Scope: set country from store filter or use all
    store_filter = ""
    store_params: list = []
    if country:
        store_keys = [k for k, s in STORES.items() if s.get("country") == country.upper()]
        if store_keys:
            placeholders = ",".join("?" * len(store_keys))
            store_filter = f"AND store IN ({placeholders})"
            store_params = list(store_keys)
        else:
            return 0

    scope = f"{country or 'global'}:{line or 'all'}"

    # Total snapshots (inventory)
    total = db.execute(
        f"SELECT COUNT(*) as n FROM price_snapshots WHERE price > 0 AND price < 999999 {store_filter}",
        store_params,
    ).fetchone()["n"]

    # Snapshots < 24h (freshness)
    cutoff_24h = (datetime.now(tz.utc) - timedelta(hours=24)).isoformat()
    snapshots_24h = db.execute(
        f"""SELECT COUNT(*) as n FROM price_snapshots
            WHERE price > 0 AND price < 999999 AND queried_at >= ? {store_filter}""",
        [cutoff_24h] + store_params,
    ).fetchone()["n"]

    # Stores with data
    stores_indexed = db.execute(
        f"SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE price > 0 {store_filter}",
        store_params,
    ).fetchone()["n"]

    # Promo intensity
    promo_count = db.execute(
        f"""SELECT COUNT(*) as n FROM price_snapshots
            WHERE price > 0 AND list_price > price AND price < 999999 {store_filter}""",
        store_params,
    ).fetchone()["n"]

    values_to_write: list[tuple] = []

    # moat_freshness
    freshness_pct = round(snapshots_24h / total * 100, 1) if total > 0 else 0.0
    values_to_write.append(("moat_freshness", scope, country, line, freshness_pct, now))

    # store_coverage
    values_to_write.append(("store_coverage", scope, country, line, stores_indexed, now))

    # promo_intensity
    promo_pct = round(promo_count / total * 100, 1) if total > 0 else 0.0
    values_to_write.append(("promo_intensity", scope, country, line, promo_pct, now))

    # Write values
    written = 0
    for key, sc, cc, ln, val, ts in values_to_write:
        try:
            db.execute(
                """INSERT INTO indicator_values (indicator_key, scope, country, line, value, recorded_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (key, sc, cc, ln, val, ts),
            )
            written += 1
        except Exception as e:
            logger.warning("_refresh_internal: %s skipped: %s", key, e)

    return written


# ── Price Pulse async jobs (Intelligence tier) ────────────────────────────────


class PricePulseSubmit(BaseModel):
    country: str = "PE"
    callback_url: str = ""

    @field_validator("country")
    @classmethod
    def _country_code(cls, v: str) -> str:
        c = (v or "PE").strip().upper()[:2]
        if len(c) != 2:
            raise ValueError("country must be 2-letter ISO code")
        return c


@router.post("/price-pulse")
def submit_price_pulse(
    body: PricePulseSubmit,
    authorization: str | None = Header(None),
):
    """Enqueue Price Pulse report generation (async worker)."""
    username = require_pro(authorization)
    from market_core.intel_jobs import db_create_intel_job

    job = db_create_intel_job(
        username,
        job_type="price_pulse",
        country=body.country,
        callback_url=(body.callback_url or "").strip(),
    )
    return {"ok": True, **job}


@router.get("/price-pulse/{job_id}")
def get_price_pulse_status(job_id: str, authorization: str | None = Header(None)):
    username = require_pro(authorization)
    from market_core.intel_jobs import db_get_intel_job

    job = db_get_intel_job(job_id)
    if not job or job.get("username") != username:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/price-pulse/{job_id}/download")
def download_price_pulse_report(job_id: str, authorization: str | None = Header(None)):
    from pathlib import Path

    from fastapi.responses import FileResponse

    username = require_pro(authorization)
    from market_core.intel_jobs import db_get_intel_job

    job = db_get_intel_job(job_id)
    if not job or job.get("username") != username:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") != "completed":
        raise HTTPException(status_code=409, detail=f"Job status is {job.get('status')}")
    path = (job.get("output_path") or "").strip()
    if not path or not Path(path).is_file():
        raise HTTPException(status_code=404, detail="Report file missing")
    return FileResponse(path, media_type="text/markdown", filename=Path(path).name)
