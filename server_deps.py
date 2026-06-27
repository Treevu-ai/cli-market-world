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
import os
import time

from fastapi import HTTPException

from market_core import (
    check_rate_limit_sqlite,
    db_get_users,
    db_validate_api_key,
)
from market_billing import db_get_subscription


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
    raise HTTPException(status_code=401, detail="Token inválido. Usá 'market login'.")


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}:{h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if ":" not in stored:
        raise HTTPException(
            status_code=500,
            detail="Legacy plaintext password detected. Contact admin.",
        )
    salt, h = stored.split(":", 1)
    return h == hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()


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
    """Common pattern: Authorization header → username. Raises 401 if absent."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    return auth_user(authorization.replace("Bearer ", ""))


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


def require_api_key(authorization: str | None) -> str:
    """Enforce API key auth + per-tier rate limiting on data endpoints.

    Accepts: sk-... API key or Bearer token (session token / MARKET_API_TOKEN).
    Applies the caller's subscription tier limits (free: 60/min, pro: 300/min).
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

    username = require_api_key(authorization)
    sub = db_get_subscription(username)
    if sub.get("tier", "free") not in ("starter", "pro", "enterprise"):
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

    username = require_api_key(authorization)
    sub = db_get_subscription(username)
    if sub.get("tier", "free") not in ("pro", "enterprise"):
        raise HTTPException(
            status_code=403,
            detail=(
                f"This endpoint requires CLI Market Pro ({price_label_for_plan('pro')}). "
                "Run: market upgrade or visit /billing/pro-checkout"
            ),
        )
    return username


def require_export(authorization: str | None) -> str:
    """Require Starter+ with export enabled (CSV/JSON data moat pulls)."""
    from market_billing import TIERS, db_get_subscription, price_label_for_plan

    username = require_api_key(authorization)
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
