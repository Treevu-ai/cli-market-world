"""Server-only dependencies shared across FastAPI routers.

These belong neither in market_core (which is data-layer-only, no HTTP concerns)
nor in any single router file. Anything that's both HTTP-related and used by
more than one router lives here.

Contents:
    - Auth: auth_user(), hash_password(), verify_password(), check_auth_brute_force()
    - Rate limit: check_rate_limit() (delegates to market_core.check_rate_limit_sqlite)
    - Constants: DEFAULT_TOKEN, RATE_LIMIT_*, AUTH_*
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
import os
from contextvars import ContextVar

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from market_core import (
    check_rate_limit_sqlite,
    db_get_users,
    db_validate_api_key,
    get_db,
)
from market_billing import db_get_subscription

logger = logging.getLogger("market.server_deps")


# ── Auth tokens ───────────────────────────────────────────────────────────────

DEFAULT_TOKEN = os.getenv("MARKET_API_TOKEN", "")


def auth_user(token: str) -> str:
    """Resolve a bearer token (or legacy session token, or sk- API key) to a username.

    Raises 401 on invalid credentials.
    """
    if token.startswith("demo-"):
        from market_core.demo_tokens import validate_demo_token

        sess = validate_demo_token(token)
        if not sess:
            raise HTTPException(status_code=401, detail="Demo token expired or invalid. Run: market demo")
        return f"demo:{sess['session_id']}"
    if DEFAULT_TOKEN and token == DEFAULT_TOKEN:
        return "admin"
    if token.startswith("sk-"):
        from market_core.platform_admin import is_platform_admin_api_key

        if is_platform_admin_api_key(token):
            return "admin"
        key_data = db_validate_api_key(token)
        if key_data:
            return key_data["username"]
    from market_core.auth_tokens import lookup_session_token

    session = lookup_session_token(token)
    if session:
        if session.get("expired"):
            raise HTTPException(
                status_code=401,
                detail="Session token expired. Run: market login or refresh.",
                headers={"X-Token-Expired": "true"},
            )
        return session["username"]
    users = db_get_users()
    for username, data in users.items():
        if data.get("token") == token:
            return username
    if token.startswith("sk-"):
        raise HTTPException(
            status_code=401,
            detail="API key inválida o revocada. Generá una nueva con 'market register' o revisá tu dashboard.",
        )
    raise HTTPException(status_code=401, detail="Token inválido. Usá 'market login'.")


# ── Password hashing ──────────────────────────────────────────────────────────

_PASSWORD_SCHEME = "pbkdf2_sha256"
_LEGACY_PASSWORD_ITERATIONS = 100_000
try:
    _PASSWORD_ITERATIONS = max(
        _LEGACY_PASSWORD_ITERATIONS,
        int(os.getenv("MARKET_PASSWORD_HASH_ITERATIONS", "600000")),
    )
except ValueError:
    _PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), _PASSWORD_ITERATIONS
    )
    return f"{_PASSWORD_SCHEME}${_PASSWORD_ITERATIONS}${salt}${h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith(f"{_PASSWORD_SCHEME}$"):
        try:
            scheme, iteration_text, salt, expected = stored.split("$", 3)
            iterations = int(iteration_text)
        except (TypeError, ValueError):
            raise HTTPException(status_code=500, detail="Invalid password hash format.")
        if scheme != _PASSWORD_SCHEME or iterations < _LEGACY_PASSWORD_ITERATIONS:
            raise HTTPException(status_code=500, detail="Invalid password hash parameters.")
    elif ":" in stored:
        # Pre-hardening records remain verifiable so existing users are not locked out.
        salt, expected = stored.split(":", 1)
        iterations = _LEGACY_PASSWORD_ITERATIONS
    else:
        raise HTTPException(
            status_code=500,
            detail="Legacy plaintext password detected. Contact admin.",
        )
    calculated = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), iterations
    ).hex()
    return hmac.compare_digest(expected, calculated)


# ── Brute-force protection ────────────────────────────────────────────────────

_auth_attempts: dict[str, list[float]] = {}
AUTH_MAX_ATTEMPTS = 5
AUTH_WINDOW = 300  # 5 minutes


def check_auth_brute_force(username: str) -> None:
    now = time.time()
    window_start = now - AUTH_WINDOW
    _auth_attempts.setdefault(username, [])
    _auth_attempts[username] = [t for t in _auth_attempts[username] if t > window_start]
    if len(_auth_attempts[username]) >= AUTH_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429, detail="Demasiados intentos. Esperá 5 minutos."
        )


def record_auth_failure(username: str) -> None:
    """Record a failed auth attempt — called from /auth/login after wrong password."""
    _auth_attempts.setdefault(username, []).append(time.time())


# ── Rate limiting ─────────────────────────────────────────────────────────────

RATE_LIMIT_MIN = int(os.getenv("RATE_LIMIT_MIN", "60"))
RATE_LIMIT_DAY = int(os.getenv("RATE_LIMIT_DAY", "1000"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


def check_rate_limit(ip: str) -> None:
    check_rate_limit_sqlite(
        ip,
        window_secs=RATE_LIMIT_WINDOW,
        max_req=RATE_LIMIT_MIN,
        daily_max=RATE_LIMIT_DAY,
    )


# ── Auth header helper ───────────────────────────────────────────────────────

def require_user(authorization: str | None) -> str:
    """Common pattern: Authorization header → username. Raises 401 if absent.

    Also applies per-user rate limiting so account-management endpoints
    (e.g. /auth/keys, /auth/revoke) can't be hammered by an authenticated
    user rotating IPs to bypass the IP-only limit.
    """
    if not authorization:
        logger.warning("auth.require_user: missing token")
        raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    check_user_rate_limit(username)
    return username


def require_admin(authorization: str | None) -> str:
    """Protect ops/admin routes with MARKET_API_TOKEN."""
    if not DEFAULT_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Admin API disabled — set MARKET_API_TOKEN on the server.",
        )
    if not authorization:
        raise HTTPException(status_code=401, detail="Admin token required")
    token = authorization.replace("Bearer ", "").strip()
    if token != DEFAULT_TOKEN:
        raise HTTPException(status_code=401, detail="Admin token invalid")
    return "admin"


# ── Messenger Sessions ────────────────────────────────────────────────────────────

def get_messenger_session(platform_id: str) -> dict:
    """Retrieve session context and tier for a conversational user.
    Returns a dict with platform_id, username, last_context, last_query,
    last_country, and user_tier.
    """
    db = None
    try:
        db = get_db()
        row = db.execute(
            "SELECT platform_id, username, last_context, last_query, last_country, user_tier "
            "FROM messenger_sessions WHERE platform_id = ?",
            (platform_id,)
        ).fetchone()
        if row:
            row = dict(row)
            return {
                "platform_id": row["platform_id"],
                "username": row["username"],
                "last_context": row["last_context"],
                "last_query": row.get("last_query"),
                "last_country": row.get("last_country"),
                "user_tier": row["user_tier"],
            }
    except Exception as e:
        logger.error("get_messenger_session error: %s", e)
    finally:
        # Never closed before (found 2026-08-05) -- called on every
        # conversational turn across telegram/whatsapp, so this was the
        # single biggest connection leak in the app, starving SQLite WAL
        # checkpointing over a long-running process/test session.
        if db is not None:
            db.close()
    return {
        "platform_id": platform_id,
        "username": None,
        "last_context": None,
        "last_query": None,
        "last_country": None,
        "user_tier": "starter",
    }


def update_messenger_session(
    platform_id: str,
    context: str,
    username: str = None,
    last_query: str = None,
    last_country: str = None,
):
    """Upsert session context. Updates last_context and updated_at timestamp.

    last_query/last_country are the free-text product search and resolved
    country from the most recent turn — read back by inline-keyboard button
    presses (which arrive as a bare action code, e.g. "cmp", with no room to
    carry the product text themselves) so a follow-up action can re-run the
    right search without asking the user to retype it.
    """
    db = None
    try:
        db = get_db()
        # Use UPSERT (SQLite 3.24+ / Postgres)
        db.execute("""
            INSERT INTO messenger_sessions (platform_id, username, last_context, last_query, last_country, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(platform_id) DO UPDATE SET
                last_context = excluded.last_context,
                last_query = COALESCE(excluded.last_query, messenger_sessions.last_query),
                last_country = COALESCE(excluded.last_country, messenger_sessions.last_country),
                username = COALESCE(excluded.username, messenger_sessions.username),
                updated_at = CURRENT_TIMESTAMP
        """, (platform_id, username, context, last_query, last_country))
        db.commit()
    except Exception as e:
        logger.error("update_messenger_session error: %s", e)
    finally:
        # Never closed before (found 2026-08-05) -- same leak class as
        # get_messenger_session() above.
        if db is not None:
            db.close()


def claim_messenger_update(platform: str, update_id: str | int, ttl_seconds: int = 604800) -> bool:
    """Atomically claim a provider update so retries don't repeat paid work.

    Returns True only for the first delivery seen within the retention window.
    ``received_at_epoch`` keeps the cleanup query portable between SQLite and
    PostgreSQL.
    """
    now = int(time.time())
    try:
        db = get_db()
        try:
            db.execute(
                "DELETE FROM messenger_updates WHERE platform = ? AND received_at_epoch < ?",
                (platform, now - ttl_seconds),
            )
            cursor = db.execute(
                "INSERT INTO messenger_updates (platform, update_id, received_at_epoch) VALUES (?, ?, ?) "
                "ON CONFLICT(platform, update_id) DO NOTHING",
                (platform, str(update_id), now),
            )
            db.commit()
            return cursor.rowcount == 1
        finally:
            db.close()
    except Exception as e:
        # Availability must win over dedupe if an older deployment has not run
        # the migration yet; the error is still visible to operations.
        logger.error("claim_messenger_update error: %s", e)
        return True

TIER_LIMITS: dict[str, tuple[int, int]] = {
    # Keep in sync with market_billing.TIERS["free"] (cli-market-core) — this
    # is only the fallback when a subscription row lacks a stored
    # req_limit_day/min. Registration (routers/auth.py) creates no
    # subscription row, so every account starts here until it upgrades.
    "free":       (15,      10),
    "starter":    (5_000,  120),
    "pro":       (10_000,  300),
    "data":      (100_000, 600),   # Tier 1 data/intel API — see market_billing.TIERS["data"]
    "enterprise": (-1,      -1),   # -1 = unlimited
}


def _get_user_tier_limits(username: str) -> tuple[int, int]:
    """Return (daily_max, per_min_max) from the user's subscription row.

    Delegates to market_billing.db_get_subscription so an expired temporary
    """
    sub = db_get_subscription(username)
    tier = (sub.get("tier") or "free").lower()
    defaults = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    daily = int(sub.get("req_limit_day") or defaults[0])
    per_min = int(sub.get("req_limit_min") or defaults[1])
    return daily, per_min


def check_user_rate_limit(username: str) -> None:
    """Apply per-user rate limiting based on subscription tier. Admin bypasses."""
    from market_core.platform_admin import is_platform_admin

    if is_platform_admin(username):
        return
    daily_max, min_max = _get_user_tier_limits(username)
    if daily_max <= 0 or min_max <= 0:
        return  # enterprise / unlimited tier
    try:
        check_rate_limit_sqlite(
            f"u:{username}",
            window_secs=RATE_LIMIT_WINDOW,
            max_req=min_max,
            daily_max=daily_max,
        )
    except Exception as exc:
        if getattr(exc, "status_code", 0) == 429:
            logger.warning("rate_limit.user user=%s", username)
        raise


def require_api_key(authorization: str | None) -> str:
    """Enforce API key auth + per-tier rate limiting on data endpoints.

    Accepts: sk-... API key or Bearer token (session token / MARKET_API_TOKEN).
    Applies the caller's subscription tier limits (starter: 120/min, pro: 300/min).
    Returns the resolved username.
    Raises 401 if no credentials, 429 if rate limited.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=(
                "API key required. Register at /auth/register to get a free key "
                "or upgrade to Pro at /billing/paypal."
            ),
        )
    token = authorization.replace("Bearer ", "").strip()
    if token.startswith("demo-"):
        from market_core.demo_tokens import consume_demo_request

        sess = consume_demo_request(token)
        if not sess:
            raise HTTPException(
                status_code=401,
                detail="Demo token expired or quota exhausted. Run: market demo",
            )
        return f"demo:{sess['session_id']}"
    username = auth_user(token)
    sub = db_get_subscription(username)
    # -1 means unlimited (enterprise); skip rate limiting entirely.
    if sub["req_limit_min"] != -1:
        check_rate_limit_sqlite(
            username,
            window_secs=RATE_LIMIT_WINDOW,
            max_req=sub["req_limit_min"],
            daily_max=sub["req_limit_day"] if sub["req_limit_day"] != -1 else 10_000_000,
        )
    return username


def require_starter(authorization: str | None) -> str:
    """Require Starter tier or higher."""
    from market_billing import db_get_subscription, price_label_for_plan
    from market_core.platform_admin import is_platform_admin

    username = require_api_key(authorization)
    if is_platform_admin(username):
        return username
    sub = db_get_subscription(username)
    if sub.get("tier", "free") not in ("starter", "pro", "pro_founding", "pro_annual", "enterprise", "builder"):
        raise HTTPException(
            status_code=403,
            detail=(
                f"This endpoint requires CLI Market Starter ({price_label_for_plan('starter')}) or higher. "
                "Run: market upgrade or visit /billing/pro-checkout"
            ),
        )
    return username


def require_pro(authorization: str | None) -> str:
    """Require Pro (or higher) tier for premium data endpoints."""
    from market_billing import db_get_subscription, price_label_for_plan
    from market_core.platform_admin import is_platform_admin

    username = require_api_key(authorization)
    if is_platform_admin(username):
        return username
    sub = db_get_subscription(username)
    if sub.get("tier", "free") not in ("pro", "pro_founding", "pro_annual", "enterprise", "builder"):
        raise HTTPException(
            status_code=403,
            detail=(
                f"This endpoint requires CLI Market Pro ({price_label_for_plan('pro')}). "
                "Run: market upgrade or visit /billing/pro-checkout"
            ),
        )
    return username


def require_enterprise(authorization: str | None) -> str:
    """Require Enterprise tier for bulk procurement and similar endpoints."""
    from market_billing import db_get_subscription, price_label_for_plan
    from market_core.platform_admin import is_platform_admin

    username = require_api_key(authorization)
    if is_platform_admin(username):
        return username
    sub = db_get_subscription(username)
    if sub.get("tier", "free") != "enterprise":
        raise HTTPException(
            status_code=403,
            detail=(
                f"This endpoint requires CLI Market Enterprise ({price_label_for_plan('enterprise')}). "
                "Contact sales at hello@cli-market.dev"
            ),
        )
    return username


# Core-mounted /v1 routes whose MCP twins are in mcp_http._PRE_CHECK_TIER.
# World-native routers (data_v1, intel) enforce tier in their own handlers.
_CORE_V1_TIER_ROUTES: dict[tuple[str, str], str] = {
    ("GET", "/v1/receipts"): "pro",
    ("GET", "/v1/quality/scores"): "pro",
    ("POST", "/v1/missions/optimize-purchase"): "pro",
    ("GET", "/v1/intel/procurement-signal"): "pro",
    ("GET", "/v1/intel/basket-stress"): "pro",
    ("GET", "/v1/intel/pulse"): "pro",
    ("GET", "/v1/intel/forecast"): "pro",
    ("GET", "/v1/intel/arbitrage"): "pro",
    ("GET", "/v1/intel/price-risk"): "pro",
    ("GET", "/v1/intel/informal-signal"): "pro",
    ("GET", "/v1/intel/promo-detector"): "pro",
    ("GET", "/v1/intel/retailer-scorecard"): "pro",
    ("GET", "/v1/ecosystem/launches"): "pro",
    # Regression: dab77652 (2026-07-21) originally gated these two behind
    # auth via the now-retired _CORE_INTEL_AUTH_PATHS set (per-retailer
    # scraper freshness/uptime is competitive intel, not public). That set
    # required only a valid key, not Pro specifically; when core v1 routes
    # moved to this tiered dict, both paths were dropped entirely, leaving
    # them auth-only again (confirmed live: any free key gets 200 with full
    # per-retailer freshness/error-rate data). Re-gated behind Pro here.
    ("GET", "/v1/health/slas"): "pro",
    ("GET", "/v1/health/slas-summary"): "pro",
    ("GET", "/v1/household"): "starter",
    ("GET", "/v1/household/summary"): "starter",
    ("PUT", "/v1/household"): "pro",
    ("PATCH", "/v1/household"): "pro",
    ("POST", "/v1/intel/procurement-bulk"): "enterprise",
}

_request_ctx: ContextVar[Request | None] = ContextVar("request_ctx", default=None)
_core_v1_gate_user: ContextVar[str | None] = ContextVar("core_v1_gate_user", default=None)


class RequestContextMiddleware:
    """Expose the current request to pluggable Core auth without task splits.

    ``BaseHTTPMiddleware`` may run the downstream application in a separate
    task. That makes the ContextVar intermittently unavailable to FastAPI
    dependencies under a full concurrent test run, which could bypass a
    tier-specific Core route gate. A minimal ASGI wrapper keeps the request
    context in the same task as the dependency evaluation.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        token = _request_ctx.set(request)
        gate_token = _core_v1_gate_user.set(None)
        try:
            tier = _CORE_V1_TIER_ROUTES.get((request.method.upper(), request.url.path))
            if tier == "enterprise":
                _core_v1_gate_user.set(require_enterprise(request.headers.get("authorization")))
            elif tier == "pro":
                _core_v1_gate_user.set(require_pro(request.headers.get("authorization")))
            elif tier == "starter":
                _core_v1_gate_user.set(require_starter(request.headers.get("authorization")))
            await self.app(scope, receive, send)
        except HTTPException as exc:
            response = JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )
            await response(scope, receive, send)
        finally:
            _core_v1_gate_user.reset(gate_token)
            _request_ctx.reset(token)


def require_v1_core_auth(authorization: str | None) -> str:
    """Tier-aware auth for cli-market-core api_routes (_auth_fn hook)."""
    # The ASGI middleware enforces gated Core paths before dispatch. Reuse the
    # resolved user so the dependency cannot bypass the tier check nor consume
    # a second rate-limit slot.
    gated_username = _core_v1_gate_user.get()
    if gated_username:
        return gated_username
    request = _request_ctx.get()
    if request is not None:
        tier = _CORE_V1_TIER_ROUTES.get((request.method.upper(), request.url.path))
        if tier == "enterprise":
            return require_enterprise(authorization)
        if tier == "pro":
            return require_pro(authorization)
        if tier == "starter":
            return require_starter(authorization)
    return require_api_key(authorization)


def require_export(authorization: str | None) -> str:
    """Require Starter+ with export enabled (CSV/JSON data moat pulls)."""
    from market_billing import TIERS, db_get_subscription, price_label_for_plan
    from market_core.platform_admin import is_platform_admin

    username = require_api_key(authorization)
    if is_platform_admin(username):
        return username
    sub = db_get_subscription(username)
    tier = sub.get("tier", "free")
    if not TIERS.get(tier, TIERS["free"]).get("export"):
        raise HTTPException(
            status_code=403,
            detail=(
                f"Data export requires CLI Market Starter ({price_label_for_plan('starter')}) or higher. "
                "Run: market upgrade --plan starter"
            ),
        )
    return username


def require_checkout_access(username: str) -> None:
    """Raise 403 if user's tier cannot use checkout (unless legacy bypass)."""
    from market_core import user_can_checkout
    from market_billing import checkout_upgrade_detail
    from market_core.demo_tokens import is_demo_username

    if is_demo_username(username):
        raise HTTPException(
            status_code=403,
            detail="Demo tokens cannot checkout. Run: market init",
        )
    if user_can_checkout(username):
        return
    raise HTTPException(
        status_code=403,
        detail=checkout_upgrade_detail(),
    )


# ── HORECA session extensions ─────────────────────────────────────────────────


def get_horeca_session(whatsapp_number: str) -> dict:
    """Obtiene la sesión HORECA de un usuario."""
    from market_core import get_db
    
    db = get_db()
    try:
        row = db.execute(
            "SELECT * FROM horeca_profiles WHERE whatsapp_number = ?",
            (whatsapp_number,)
        ).fetchone()
        return dict(row) if row else {}
    finally:
        db.close()


def update_horeca_session(whatsapp_number: str, data: dict) -> bool:
    """Actualiza datos de sesión HORECA."""
    from market_core import get_db
    
    db = get_db()
    try:
        # Actualizar campos relevantes
        updates = []
        values = []
        
        for key, value in data.items():
            if key in ['business_name', 'business_type', 'last_search_category']:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(whatsapp_number)
            db.execute(
                f"UPDATE horeca_profiles SET {', '.join(updates)} WHERE whatsapp_number = ?",
                values
            )
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error updating horeca session: {e}")
        return False
    finally:
        db.close()
