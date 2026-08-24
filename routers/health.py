"""Health checks, root, and catalog endpoints (lines / stores / countries).

Endpoints:
  GET /                  Service banner + counts
  GET /health            Liveness check
  GET /health/collector  Collector freshness (last run, age, store coverage)
  GET /v1/sources/health Per-store scraping health (success rate + freshness)
  GET /health/stats      Live moat KPIs + golden linkage % + sources summary
  GET /v1/capabilities   Public commerce capability matrix (checkout scope, payments)
  GET /lines             Catalog of business lines with their stores
  GET /stores            Catalog of retailers (filterable by country/line)
  GET /countries         Catalog of countries with store lists
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from market_core import STORES, LINES, COUNTRIES, get_db
from server_deps import check_rate_limit
from backend_interface import build_sources_health, get_store_profile
from store_credentials import get_custom_store_ids

logger = logging.getLogger("market.server").getChild("health")

from collector_health import (
    WAF_GHA_ONLY_STORES,
    _age_hours,
    build_collector_catalog_identity,
    circuit_skip_threshold,
    derive_collector_status,
)

router = APIRouter(tags=["health"])

_circuit_skip_threshold = circuit_skip_threshold
@router.get("/health")
def health():
    return {"status": "healthy"}


@router.get("/health/db")
def health_db():
    """Database backend diagnostic — confirms PG vs SQLite."""
    import market_core
    # Hitting this endpoint also nudges a Postgres recovery attempt when we
    # are in SQLite fallback mode (throttled internally).
    try:
        market_core.recover_pg_if_needed()
    except Exception:
        pass
    from market_core import USE_PG, DATABASE_URL, DB_FILE
    pg_error = None
    if DATABASE_URL and not USE_PG:
        # PG was attempted but fell back — try to get the connection error
        try:
            import psycopg2
            psycopg2.connect(DATABASE_URL, connect_timeout=5)
        except Exception as e:
            pg_error = str(e)[:200]
    db = get_db()
    try:
        db_type = "postgresql" if USE_PG else "sqlite"
        snapshots = db.execute("SELECT COUNT(*) as n FROM price_snapshots").fetchone()["n"]
        if not USE_PG:
            tables = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        else:
            tables = db.execute(
                "SELECT tablename as name FROM pg_catalog.pg_tables WHERE schemaname='public' ORDER BY tablename"
            ).fetchall()
        db.close()
        upsert_ready = None
        if USE_PG:
            try:
                chk = get_db()
                upsert_ready = bool(chk.execute(
                    """
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = 'price_snapshots'
                      AND indexdef ILIKE '%UNIQUE%'
                      AND indexdef ILIKE '%product_id%'
                      AND indexdef ILIKE '%store%'
                    LIMIT 1
                    """
                ).fetchone())
                chk.close()
            except Exception:
                upsert_ready = False
        return {
            "backend": db_type,
            "database_url_set": bool(DATABASE_URL),
            "db_file": str(DB_FILE) if not USE_PG else None,
            "snapshots": snapshots,
            "price_snapshots_upsert_ready": upsert_ready,
            "tables": [t["name"] for t in tables],
            "pg_error": pg_error,
        }
    except Exception as e:
        return {"backend": "error", "detail": str(e)}


@router.get("/health/collector")
def health_collector():
    """Collector health: last run, staleness, store coverage."""
    circuit_open: list[str] = []
    inactive: list[str] = []
    try:
        db = get_db()
        last = db.execute(
            "SELECT started_at, finished_at, stores_attempted, stores_succeeded, prices_collected "
            "FROM collector_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]
        active_stores = db.execute(
            "SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE price > 0"
        ).fetchone()["n"]
        skip = _circuit_skip_threshold()
        catalog = list(STORES)
        try:
            health_rows = db.execute(
                "SELECT store, consecutive_failures, total_requests FROM store_health"
            ).fetchall()
            by_store = {r["store"]: r for r in health_rows}
            circuit_open = sorted(
                s for s in catalog
                if int((by_store.get(s) or {}).get("consecutive_failures") or 0) >= skip
            )
            inactive = sorted(
                s for s in catalog
                if s not in by_store or int((by_store.get(s) or {}).get("total_requests") or 0) == 0
            )
            inactive = [s for s in inactive if s not in set(circuit_open)]
        except Exception:
            circuit_open, inactive = [], []
        db.close()
    except Exception:
        return {"status": "unknown", "error": "Database not initialized"}

    if not last:
        return {"status": "unknown", "message": "No collector runs yet", "runs_total": 0}

    finished = last["finished_at"]
    if finished:
        status, age_h = derive_collector_status(
            finished_at=finished,
            prices_collected=last["prices_collected"],
        )
    else:
        status = "running"
        age_h = None

    catalog_identity = build_collector_catalog_identity(
        catalog_ids=list(STORES),
        attempted=last["stores_attempted"] or 0,
        succeeded=last["stores_succeeded"] or 0,
        circuit_open=circuit_open,
        inactive=inactive,
    )
    return {
        "status": status,
        "last_run": last["started_at"],
        "last_finished": finished,
        "age_hours": round(age_h, 1) if age_h is not None else None,
        "stores_attempted": last["stores_attempted"],
        "stores_succeeded": last["stores_succeeded"],
        "prices_collected": last["prices_collected"],
        "stores_active": active_stores or 0,
        "stores_total": len(STORES),
        "runs_total": total_runs,
        "catalog": catalog_identity,
        "data_gate_closes_on": ["stale", "dead"],
    }


@router.get("/v1/capabilities")
def commerce_capabilities():
    """Public matrix: what checkout does (CLI Market internal payment) vs retailer fulfillment."""
    from market_core.commerce_capabilities import get_commerce_capabilities

    return get_commerce_capabilities()


@router.get("/v1/sources/health")
def sources_health(
    store: str | None = None,
    catalog_only: bool = True,
):
    """Per-store scraping health: success rate, failures, and snapshot freshness."""
    db = get_db()
    try:
        return build_sources_health(db, catalog_only=catalog_only, store=store)
    finally:
        db.close()


@router.get("/")
def root(request: Request):
    try:
        check_rate_limit(request.client.host if request.client else "unknown")
    except Exception as e:
        logger.warning("Rate limit check failed: %s", e)
    return {
        "name": "CLI Market",
        "status": "running",
        "stores": len(STORES),
        "lines": len(LINES),
        "countries": len(COUNTRIES),
        "docs": "/docs",
    }


@router.get("/lines")
def list_lines():
    # STORES alone is the static built-in catalog — see /stores' identical
    # fix above for why dynamically-approved retailers must be included too.
    growth_flags = _growth_flags_by_store()
    all_keys = list(STORES.keys()) + get_custom_store_ids()
    result: dict[str, dict] = {}
    for line_id, line_meta in LINES.items():
        line_stores: dict[str, dict] = {}
        for sk in all_keys:
            sv = STORES.get(sk) or get_store_profile(sk)
            if sv and sv.get("line") == line_id:
                line_stores[sk] = {
                    "name": sv["name"],
                    "country": sv["country"],
                    "currency": sv["currency"],
                    "base": sv.get("base", ""),
                    "emoji": sv.get("emoji", ""),
                    "is_growth": growth_flags.get(sk, False),
                }
        result[line_id] = {
            "name": line_meta["name"],
            "emoji": line_meta["emoji"],
            "description": line_meta["description"],
            "stores": line_stores,
            "total_stores": len(line_stores),
        }
    return {"lines": result, "total": len(result)}


def _growth_flags_by_store() -> dict[str, bool]:
    """store_id -> is_growth, for badging the public store catalog."""
    db = get_db()
    try:
        rows = db.execute("SELECT store_id, is_growth FROM store_credentials").fetchall()
    except Exception:
        return {}  # is_growth column not yet migrated
    finally:
        db.close()
    return {dict(r)["store_id"]: bool(dict(r)["is_growth"]) for r in rows}


@router.get("/stores", summary="List all verified retailers, filterable by country and business line")
def list_stores(country: str | None = None, line: str | None = None):
    """Return the catalog of verified active retailers with their store key, name,
    country, currency, business line, and base URL. Filter by country (PE, AR, BR, MX,
    CO, CL, IT, FR) and/or line (supermercados, farmacias, electro, moda, hogar,
    departamentales). Use store keys from this response as the stores list when calling
    POST /v1/basket/compare to scope a basket to a specific country."""
    growth_flags = _growth_flags_by_store()
    result = {}
    # STORES alone is the static built-in catalog — retailers approved via
    # /admin/retailer-applications/{id}/approve (e.g. grintek_pe) only exist
    # in store_credentials/get_custom_store_ids(), so limiting to STORES here
    # silently hid every approved retailer from the public catalog that
    # market_stores/market_discover (MCP tools) and /v1/basket/compare both
    # read from.
    all_keys = list(STORES.keys()) + get_custom_store_ids()
    for key in all_keys:
        s = STORES.get(key) or get_store_profile(key)
        if not s:
            continue
        if country and s["country"] != country.upper():
            continue
        if line and s["line"] != line:
            continue
        result[key] = {
            "name": s["name"],
            "country": s["country"],
            "currency": s["currency"],
            "line": s["line"],
            "line_name": LINES.get(s["line"], {}).get("name", s["line"]),
            "base": s["base"],
            "is_growth": growth_flags.get(key, False),
        }
    return {"stores": result, "total": len(result)}


@router.get("/countries", summary="List supported countries with their active retailer counts")
def list_countries():
    """Return the 8 supported countries (PE, AR, BR, MX, CO, CL, IT, FR) with their
    names and the list of active retailer store keys for each. Use to discover which
    countries are supported before filtering a search or basket by country."""
    return {
        "countries": {
            code: {"name": c["name"], "stores": c["stores"], "count": len(c["stores"])}
            for code, c in COUNTRIES.items()
        }
    }

@router.get("/health/deep")
def health_deep():
    """Unified deep health check — probes Postgres, Index, Observatory, Collector in one call.

    Designed for Fly.io healthcheck integration and ops dashboards.
    Returns overall status (healthy/degraded/unhealthy) plus per-subsystem detail.
    """
    from market_core import USE_PG

    checks: dict = {}
    failures = 0

    # 1. Database
    try:
        db = get_db()
        row = db.execute("SELECT COUNT(*) as n FROM price_snapshots").fetchone()
        db.close()
        snap_count = row["n"] if row else 0
        checks["database"] = {
            "status": "ok",
            "backend": "postgresql" if USE_PG else "sqlite",
            "price_snapshots": snap_count,
        }
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)[:200]}
        failures += 1

    # 2. Collector freshness
    try:
        db = get_db()
        last = db.execute(
            "SELECT finished_at, prices_collected "
            "FROM collector_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        db.close()
        if last and last["finished_at"]:
            coll_status, age_h = derive_collector_status(
                finished_at=last["finished_at"],
                prices_collected=last["prices_collected"],
            )
            checks["collector"] = {
                "status": coll_status,
                "age_hours": round(age_h, 1) if age_h is not None else None,
                "prices_last_run": last["prices_collected"],
            }
            if coll_status in ("stale", "dead"):
                failures += 1
        else:
            checks["collector"] = {"status": "unknown", "message": "no runs yet"}
    except Exception as e:
        checks["collector"] = {"status": "error", "error": str(e)[:200]}
        failures += 1

    # 3. Index (Golden Records)
    try:
        from index_gate import registry_size as _registry_size
        rsize = _registry_size()
        checks["index"] = {"status": "ok", "registry_size": rsize}
    except Exception as e:
        checks["index"] = {"status": "unavailable", "error": str(e)[:200]}

    # 4. Observatory (telemetry)
    # db.close() moved to finally: the old success-path-only close() leaked
    # a connection on every exception here (e.g. table not yet migrated in
    # a fresh env) -- found 2026-08-05.
    db = None
    try:
        db = get_db()
        obs = db.execute(
            "SELECT COUNT(*) as n FROM observatory_events"
        ).fetchone()
        checks["observatory"] = {"status": "ok", "events": obs["n"] if obs else 0}
    except Exception:
        checks["observatory"] = {"status": "unavailable"}
    finally:
        if db is not None:
            db.close()

    # 5. Funnel
    db = None
    try:
        db = get_db()
        funnel = db.execute(
            "SELECT COUNT(*) as n FROM funnel_events"
        ).fetchone()
        checks["funnel"] = {"status": "ok", "events": funnel["n"] if funnel else 0}
    except Exception:
        checks["funnel"] = {"status": "unavailable"}
    finally:
        if db is not None:
            db.close()

    overall = "healthy" if failures == 0 else ("degraded" if failures == 1 else "unhealthy")
    return {"status": overall, "checks": checks}


@router.get("/health/stats")
def health_stats():
    """Live KPIs for the landing page — lightweight, no dashboard deps."""
    from market_core.health_stats import build_health_stats

    registry_size = None
    try:
        from index_gate import registry_size as _registry_size

        registry_size = _registry_size()
    except Exception:
        pass

    db = get_db()
    try:
        return build_health_stats(db, registry_size=registry_size)
    finally:
        db.close()
