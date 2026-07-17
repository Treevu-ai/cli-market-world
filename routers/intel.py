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
  GET  /v1/intel/andean-panel               CAF Andean panel PE/BO/EC (P2)
  POST /v1/intel/refresh                    Trigger indicator recomputation
  POST /v1/intel/enrichment/refresh         Trigger enrichment-only refresh
  GET  /v1/intel/macro                      Tipo de cambio + IPC Lima (BCRP, oficial)
  POST /v1/intel/macro/refresh              Fetch latest BCRP tipo de cambio + IPC
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, field_validator

from market_core import STORES, get_db, price_to_usd
from market_billing import db_get_subscription
from market_security import validate_public_http_url
from server_deps import require_pro, require_starter
from index_gate import gov_collect_bcrp, gov_macro_snapshot
from backend_interface import (
    ENRICHMENT_INDICATOR_KEYS,
    build_intel_brief,
    get_indicator_catalog,
    get_latest_values,
    get_scores,
)
from market_intel_v2 import (
    PROMO_DISCOUNT_THRESHOLD,
    _RPV_DISCLAIMER_ES,
    build_andean_panel,
    compute_affordability_v2,
)
from market_core.market_intel_products import compute_price_deal_alerts
from market_core.response_envelope import build_provenance, envelope, timing

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


@router.post("/ask", summary="Ask a natural-language question over the intelligence data moat")
def intel_ask(body: AskRequest, authorization: str | None = Header(None)):
    """Ask a free-form question about prices, inflation, or market conditions and get a
    grounded, sourced answer. Runs a tool-use agent loop against live intelligence data
    (inflation, indicators, dispersion, staple momentum). Starter tier: 50 queries/month.
    Pro/Enterprise: unlimited. Returns 503 if the agent backend is not configured."""
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

@router.get("/indicators", summary="List all 44 intelligence indicator definitions")
def list_indicators(authorization: str | None = Header(None)):
    """Return the full indicator catalog with key, name, source, and description for each
    indicator. Sources include internal moat data plus OpenFoodFacts, Wikimedia,
    IMF, Eurostat, World Bank, and BCB. Use to discover available indicator keys
    before calling GET /v1/intel/indicators/{key} for a specific value."""
    require_pro(authorization)
    db = get_db()
    try:
        catalog = _catalog(db)
        return {"indicators": catalog, "total": len(catalog)}
    finally:
        db.close()


@router.get("/indicators/{key}", summary="Get a single indicator's definition and latest value")
def get_indicator(
    key: str,
    country: str | None = Query(None),
    line: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Return the definition and most recent computed value for one indicator key.
    Optionally filter by country (e.g. PE, AR) and business line. Get valid keys
    from GET /v1/intel/indicators first."""
    require_pro(authorization)
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

@router.get(
    "/brief",
    summary="One-call intelligence brief: shelf signals, macro gap, scores, and confidence",
)
def intel_brief(
    country: str | None = Query(None),
    line: str | None = Query(None),
    days: int = Query(7, ge=1, le=90),
    include_catalog: bool = Query(False),
    authorization: str | None = Header(None),
):
    """The canonical entry point for market intelligence. Returns a structured brief
    combining shelf price signals, inflation delta, composite scores, moat confidence,
    and macro context in a single call. Filter by country (PE, AR, BR, etc.) and
    business line (supermercados, farmacias, etc.). Use this before market_inflation
    or market_scores when you want a full picture rather than a single metric.
    Maps to the market_intel_brief MCP tool."""
    require_pro(authorization)
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


@router.get(
    "/andean-panel",
    summary="CAF Andean food-affordability panel (PE retail+macro, BO/EC macro-only)",
)
def intel_andean_panel(
    line: str = Query("supermercados"),
    days: int = Query(30, ge=1, le=365),
    enveloped: bool = Query(True),
    authorization: str | None = Header(None),
):
    """Cross-country Andean panel for CAF-style food affordability comparisons."""
    require_pro(authorization)
    db = get_db()
    try:
        with timing() as t:
            result = build_andean_panel(db, line=line, days=days)
        retail_count = int(result.get("retail_coverage_countries") or 0)
        confidence = "ok" if retail_count >= 1 else "low"
        prov = build_provenance(
            primary_source="price_snapshots",
            methodology=result.get("methodology", "andean_panel_v1"),
        )
        if enveloped:
            return envelope(
                result,
                confidence=confidence,
                latency_ms=t.elapsed_ms,
                extra_meta={"provenance": prov},
            )
        return result
    finally:
        db.close()


# ── Scores ──────────────────────────────────────────────────────────────────────

@router.get("/scores", summary="Get composite market scores derived from indicators")
def list_scores(
    country: str | None = Query(None),
    line: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Return composite scores (e.g. shelf_health, price_volatility, promo_intensity)
    computed from the raw indicator set. Scores are 0–100 normalized and scoped by
    country and business line. Use for at-a-glance market health signals without
    reading raw indicator values. Maps to the market_scores MCP tool."""
    require_pro(authorization)
    db = get_db()
    try:
        return get_scores(db, country=country, line=line)
    finally:
        db.close()


# ── Inflation ───────────────────────────────────────────────────────────────────

@router.get("/inflation", summary="Shelf price inflation over a rolling window by category and country")
def get_inflation(
    country: str | None = Query(None),
    line: str | None = Query(None),
    days: int = Query(7, ge=1, le=90),
    authorization: str | None = Header(None),
):
    """Return observed shelf price change (delta_pct) for each business line over a
    rolling window of `days` (default 7, max 90). Filter by country and line.
    Data comes from the price_snapshots moat — not official CPI. Use for procurement
    cost-trend analysis, price alerts, and inflation monitoring. Maps to the
    market_inflation MCP tool."""
    require_pro(authorization)
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
                """SELECT AVG(price) as avg_price
                   FROM price_snapshots
                   WHERE line=? AND currency=? AND price>0 AND price<999999 AND queried_at>=?""",
                (ln, cur, recent_cutoff),
            ).fetchone()
            older_avg = db.execute(
                """SELECT AVG(price) as avg_price
                   FROM price_snapshots
                   WHERE line=? AND currency=? AND price>0 AND price<999999
                     AND queried_at>=? AND queried_at<?""",
                (ln, cur, older_cutoff, recent_cutoff),
            ).fetchone()
            r_avg = round(float(recent_avg["avg_price"] or 0), 2) if recent_avg else 0.0
            o_avg = round(float(older_avg["avg_price"] or 0), 2) if older_avg else 0.0
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

        weighted_sum = sum(
            it["delta_pct"] * it["n_products"] for it in items if it["n_products"] > 0
        )
        total_n = sum(it["n_products"] for it in items if it["n_products"] > 0)
        avg_inflation = round(weighted_sum / total_n, 1) if total_n > 0 else 0.0

        currencies_in_result = list({it["currency"] for it in items if it["currency"]})
        mixed_currency = len(currencies_in_result) > 1

        return {
            "items": items,
            "metric_name": "Retail Price Velocity (RPV)",
            "retail_price_velocity_pct": avg_inflation,
            "avg_inflation_pct": avg_inflation,
            "avg_rpv_7d_pct": avg_inflation,
            "avg_inflation_note": (
                "Promedio ponderado por n_products. Mezcla monedas: interprete por currency."
                if mixed_currency
                else "Promedio ponderado por n_products."
            ),
            "period_note": (
                f"Ventana: {days} días rolling de precios de góndola online. "
                "No equivale a IPC oficial (encuesta de hogares, canasta mensual/anual). "
                "CLI Market RPV ≠ CPI — distinto canal, canasta y período."
            ),
            "days": days,
            "country": country,
            "line": line,
            "metric": "shelf_price_momentum_7d",
            "metric_label": "Retail Price Velocity (RPV)",
            "methodology": "docs/methodology.md#1-retail-price-velocity-rpv",
            "disclaimer": _RPV_DISCLAIMER_ES,
        }
    finally:
        db.close()


# ── Alerts ──────────────────────────────────────────────────────────────────────

@router.get("/alerts", summary="Find products with active discounts at or above a threshold")
def get_alerts(
    product: str = Query(..., min_length=1),
    store: str | None = Query(None),
    threshold_pct: float = Query(5.0, ge=0.1, le=100.0),
    limit: int = Query(10, ge=1, le=50),
    authorization: str | None = Header(None),
):
    """Return products matching a name query where the current price is at least
    threshold_pct% below the list price, ordered by deepest discount first.
    Optionally scope to a specific store key. Use for deal hunting and price-drop
    notifications. Maps to the market_price_alerts MCP tool."""
    require_pro(authorization)
    db = get_db()
    try:
        return compute_price_deal_alerts(
            db,
            product=product,
            store=store,
            threshold_pct=threshold_pct,
            limit=limit,
        )
    finally:
        db.close()


# ── Refresh ─────────────────────────────────────────────────────────────────────

@router.post("/refresh", summary="Trigger indicator recomputation from price snapshot data (Pro)")
def refresh_indicators(
    country: str | None = Query(None),
    line: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Recompute internal indicators (promo_intensity, moat_freshness, price_dispersion,
    etc.) directly from the price_snapshots database. Requires Pro tier. External
    indicators (World Bank, IMF, Eurostat) require the collector backend and are
    not updated by this endpoint. Filter by country and line to scope the refresh."""
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


# ── Macro (Gov Connectors — BCRP) ────────────────────────────────────────────
# specs/gov-connectors-prd.md — Golden Records sourced from Banco Central de
# Reserva del Perú instead of retail scraping. Separate concept from RPV
# above: BCRP's IPC is an official household consumption basket; RPV is
# online shelf-price momentum. They deliberately measure different things.

@router.get("/macro", summary="Tipo de cambio USD/PEN e IPC Lima Metropolitana (BCRP, oficial)")
def get_macro(authorization: str | None = Header(None)):
    """Latest official tipo de cambio (venta/compra) and IPC Lima Metropolitana
    from BCRP — Peru's central bank. Use to contextualize PEN-denominated
    prices, or as an official CPI reference point alongside the shelf-price
    RPV signal from /v1/intel/inflation (CLI Market RPV ≠ CPI — see that
    endpoint's disclaimer). Raw gov data — Free tier, per
    specs/gov-connectors-prd.md DD-3 (derived indicators like RCLI are Pro)."""
    require_pro(authorization)
    return gov_macro_snapshot()


@router.post("/macro/refresh", summary="Fetch latest tipo de cambio + IPC from BCRP's series API")
async def refresh_macro(authorization: str | None = Header(None)):
    """Fetch tipo de cambio and IPC Lima from BCRP's documented series API and
    persist as gov-sourced Golden Records. Unlike the retail collector cycle,
    BCRP has no anti-bot protection and returns a handful of values — safe to
    call on-demand rather than only on a schedule."""
    require_pro(authorization)
    return await gov_collect_bcrp()


# ── Enrichment ──────────────────────────────────────────────────────────────────

@router.get("/enrichment", summary="Get external enrichment indicators (OpenFoodFacts, World Bank, Wikimedia)")
def get_enrichment(
    country: str | None = Query(None),
    authorization: str | None = Header(None),
):
    """Return enrichment indicators sourced from external public APIs: OpenFoodFacts
    (nutritional data), Wikimedia Pageviews (category momentum), Open-Meteo (weather
    impact on demand), and World Bank food CPI. Filter by country. Use to enrich
    procurement decisions with demand signals and macro context."""
    require_pro(authorization)
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


@router.get("/enrichment/subcategories", summary="Get subcategory-level enrichment (canasta items × Wikimedia momentum)")
def get_enrichment_subcategories(
    country: str = Query("PE"),
    authorization: str | None = Header(None),
):
    """Return enrichment indicators broken down by canasta subcategory (e.g. leche,
    arroz, aceite) crossed with Wikimedia search momentum. Useful for identifying
    which food categories have rising consumer interest. Defaults to Peru (PE)."""
    require_pro(authorization)
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

    # Promo intensity — umbral 3% (methodology.md §6)
    promo_count = db.execute(
        f"""SELECT COUNT(*) as n FROM price_snapshots
            WHERE price > 0 AND list_price > price AND price < 999999
              AND (list_price - price) * 1.0 / list_price >= ? {store_filter}""",
        [PROMO_DISCOUNT_THRESHOLD, *store_params],
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


# ── Affordability v2 (overrides core route — registered before core_v1_router) ─

@router.get("/affordability", summary="Affordability OS v2 — canasta promedio + best/worst")
def intel_affordability_v2(
    country: str = Query("PE", description="PE, AR, MX, BR, CO, CL"),
    line: str = Query("supermercados"),
    days: int = Query(30, ge=1, le=365),
    enveloped: bool = Query(True),
    authorization: str | None = Header(None),
):
    """Cost-of-living composite. Titular usa canasta promedio; ver docs/methodology.md §4."""
    require_pro(authorization)
    db = get_db()
    try:
        with timing() as t:
            result = compute_affordability_v2(db, country=country, line=line, days=days)
        components = result.get("components") or {}
        confidence = components.get("canasta_band_confidence") or (
            "ok" if components.get("canasta_average") else "low"
        )
        prov = build_provenance(
            primary_source="price_snapshots",
            methodology=result.get("methodology", "affordability_os_v2"),
        )
        if enveloped:
            return envelope(
                result,
                confidence=confidence,
                latency_ms=t.elapsed_ms,
                extra_meta={"provenance": prov},
            )
        return result
    finally:
        db.close()


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

    callback_url = (body.callback_url or "").strip()
    if callback_url:
        try:
            callback_url = validate_public_http_url(callback_url)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = db_create_intel_job(
        username,
        job_type="price_pulse",
        country=body.country,
        callback_url=callback_url,
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
