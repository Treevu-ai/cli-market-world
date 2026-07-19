#!/usr/bin/env python3
"""
market-server — Agentic Market backend.

Thin FastAPI app factory. ALL endpoint code lives in routers/*.py and
business logic in market_core.py / server_deps.py.

To run:
    python market_server.py
    → http://localhost:8765
    → http://localhost:8765/docs

Adding a new endpoint:
    1. Pick the router that fits the domain (or create routers/<domain>.py).
    2. Define the endpoint there with `@router.<method>(path)`.
    3. If you're creating a new router, register it below with
       `app.include_router(<new>_router)`.

There are NO inline @app.<method> endpoints here. If you find yourself
about to add one — instead, find or create the right router.
"""

from __future__ import annotations

import os
import tomllib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from market_core import (
    COUNTRIES,
    LINES,
    STORES,
    db_migrate_from_json,
    ensure_db_initialized,
    logger as log,
)
from market_security import production_payment_config_warnings

# Server-only helpers (auth, rate limit, hashing) live in server_deps.py.
# Re-exported below — tests and external code import these from market_server.
from server_deps import (  # noqa: F401
    auth_user,
    hash_password,
    verify_password,
    check_auth_brute_force,
    record_auth_failure,
    require_api_key,
    require_user,
    check_rate_limit,
    DEFAULT_TOKEN,
    RATE_LIMIT_MIN,
    RATE_LIMIT_DAY,
    RATE_LIMIT_WINDOW,
    AUTH_MAX_ATTEMPTS,
    AUTH_WINDOW,
    _auth_attempts,
)

logger = log.getChild("server")


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize DB schema and migrate legacy JSON data on startup.

    Replaces the previous side-effect-at-import pattern. Idempotent.
    """
    ensure_db_initialized()
    from market_core import USE_PG
    try:
        db = get_db()
        if USE_PG:
            db.execute("""
                CREATE TABLE IF NOT EXISTS messenger_sessions (
                    platform_id TEXT PRIMARY KEY,
                    username TEXT,
                    last_context TEXT,
                    user_tier TEXT DEFAULT 'starter',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        else:
            db.execute("""
                CREATE TABLE IF NOT EXISTS messenger_sessions (
                    platform_id TEXT PRIMARY KEY,
                    username TEXT,
                    last_context TEXT,
                    user_tier TEXT DEFAULT 'starter',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
        db.commit()
        db.close()
    except Exception as e:
        logger.warning("messenger_sessions schema skipped: %s", e)
    from market_security import is_production_deploy
    if is_production_deploy() and not USE_PG:
        raise RuntimeError(
            "Production deploy detected but running on SQLite (USE_PG=False). "
            "This means DATABASE_URL is missing or PostgreSQL is unreachable. "
            "Refusing to start — an empty SQLite would serve 0 data."
        )
    try:
        from market_audit import ensure_audit_schema
        ensure_audit_schema()
    except Exception as e:
        logger.warning("Audit schema skipped: %s", e)
    try:
        from market_vault import backfill_vault_bindings_from_audit, ensure_vault_schema
        ensure_vault_schema()
        backfill_vault_bindings_from_audit()
    except Exception as e:
        logger.warning("Vault bindings backfill skipped: %s", e)
    try:
        from market_funnel import ensure_funnel_schema
        ensure_funnel_schema()
    except Exception as e:
        logger.warning("Funnel schema skipped: %s", e)
    try:
        from market_observatory import ensure_observatory_schema
        ensure_observatory_schema()
    except Exception as e:
        logger.warning("Observatory schema skipped: %s", e)
    try:
        db_migrate_from_json()
    except Exception as e:
        logger.warning("JSON migration skipped: %s", e)
    for warning in production_payment_config_warnings():
        logger.warning("Payment security: %s", warning)
    try:
        from market_security import patch_alert_webhook_dispatch

        patch_alert_webhook_dispatch()
    except Exception as e:
        logger.warning("Alert webhook SSRF patch skipped: %s", e)
    # Watchdog: alert ops if we started on a SQLite fallback or with a stale/
    # empty moat (non-fatal, cooldown-gated).
    try:
        from market_health_alert import alert_if_unhealthy
        alert_if_unhealthy(source="api-startup")
    except Exception as e:
        logger.warning("Moat health check failed (non-fatal): %s", e)
    try:
        from routers.integrations.telegram import register_telegram_commands
        await register_telegram_commands()
    except Exception as e:
        logger.warning("Telegram command menu registration skipped: %s", e)
    yield


# ── App ──────────────────────────────────────────────────────────────────────

from market_core.market_mcp_registry import public_tool_count
from market_stats import PACKAGE_VERSION, RETAILERS_VERIFIED, COUNTRIES as MS_COUNTRIES


def _world_api_version() -> str:
    """OpenAPI version = world release (pyproject), not core PACKAGE_VERSION."""
    try:
        data = tomllib.loads(
            (Path(__file__).resolve().parent / "pyproject.toml").read_text(encoding="utf-8")
        )
        return str(data["project"]["version"])
    except Exception:
        return PACKAGE_VERSION


_MCP_DEFAULT = public_tool_count("default")
_MCP_LEGACY = public_tool_count("legacy")

app = FastAPI(
    title="CLI Market API",
    description=(
        f"Commerce infrastructure for AI agents — {RETAILERS_VERIFIED} verified retailers, "
        f"{_MCP_DEFAULT} curated MCP tools ({_MCP_LEGACY} legacy), "
        f"{MS_COUNTRIES} countries. Agent-ready."
    ),
    version=_world_api_version(),
    lifespan=lifespan,
)

from market_core import db_validate_api_key
from market_observatory import ObservatoryMiddleware

app.add_middleware(
    ObservatoryMiddleware,
    auth_user_fn=auth_user,
    api_key_fn=db_validate_api_key,
)
_DEFAULT_CORS_ORIGINS = ",".join([
    "https://cli-market.dev",
    "https://www.cli-market.dev",
    "https://procurecopilot.com",
    "https://procure-copilot.contacto-8e4.workers.dev",
    "http://localhost:3000",
    "http://localhost:8765",
])
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS).split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Agent-ID", "X-Session-ID", "X-Country"],
)

# Core intel routes (cli-market-core <1.11.4) omit Depends(_v1_auth). Gate here until pin bumps.
_CORE_INTEL_AUTH_PATHS = frozenset({
    "/v1/intel/price-risk",
    "/v1/intel/inflation-report",
    "/v1/intel/procurement-signal",
    "/v1/intel/regulatory",
    "/v1/moat/confidence",
})


@app.middleware("http")
async def core_intel_api_key_gate(request: Request, call_next):
    path = request.url.path.rstrip("/") or "/"
    if path in _CORE_INTEL_AUTH_PATHS:
        try:
            require_api_key(request.headers.get("authorization"))
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)


# ── Routers ──────────────────────────────────────────────────────────────────

from routers.admin import router as admin_router
from routers.alerts import router as alerts_router
from routers.agent import router as agent_router
from routers.analytics import router as analytics_router
from routers.auth import router as auth_router
from routers.cart import router as cart_router
from routers.data_v1 import router as data_v1_router
from routers.dashboard import router as dashboard_router
from routers.data_export import router as data_export_router
from routers.funnel import router as funnel_router
from routers.observatory import router as observatory_router
from routers.health import router as health_router
from routers.index_api import router as index_router
from routers.intel import router as intel_router
from routers.media import router as media_router
from routers.misc import router as misc_router
from routers.orders import router as orders_router
from routers.payments import router as payments_router
from routers.public_demo import router as public_demo_router
from routers.slack_ops import router as slack_ops_router
from routers.retailers import router as retailers_router
from routers.retailer_admin import router as retailer_admin_router
from routers.search import router as search_router
from routers.integrations.whatsapp import router as whatsapp_router
from routers.integrations.telegram import router as telegram_router

# Ported from cli-market-backend (consolidation — single source of truth)
from routers.discovery import router as discovery_router
from routers.intelligence_web import router as intelligence_web_router
from routers.mcp_http import router as mcp_http_router
from routers.vault import router as vault_router
from routers.brand_intel import router as brand_intel_router

# Order doesn't matter functionally — each router declares its own paths.
# Listed alphabetically by router file for easy navigation.
for r in (
    admin_router,
    agent_router,
    alerts_router,
    analytics_router,
    auth_router,
    brand_intel_router,
    cart_router,
    dashboard_router,
    data_v1_router,
    data_export_router,
    discovery_router,
    funnel_router,
    observatory_router,
    health_router,
    index_router,
    intel_router,
    intelligence_web_router,
    mcp_http_router,
    media_router,
    misc_router,
    orders_router,
    payments_router,
    public_demo_router,
    retailers_router,
    retailer_admin_router,
    search_router,
    slack_ops_router,
    telegram_router,
    vault_router,
    whatsapp_router,
):
    app.include_router(r)

# Cost-of-Living OS v1 routes from cli-market-core (Waves 1–4).
# Mounted after world routers so existing handlers win on duplicate paths;
# adds missions (optimize-purchase), intel affordability, affiliate-click, etc.
from market_core import api_routes as core_api_routes
from market_core.api_routes import router as core_v1_router

core_api_routes._auth_fn = require_api_key
app.include_router(core_v1_router, prefix="/v1")


# ── Entrypoint ───────────────────────────────────────────────────────────────

def main():
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8765"))

    logger.info(f"CLI Market API starting on http://{host}:{port}")
    logger.info(f"  {len(STORES)} stores, {len(LINES)} lines, {len(COUNTRIES)} countries")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
