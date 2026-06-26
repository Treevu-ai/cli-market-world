"""Signed one-time magic links for Procure dashboard onboarding (Sprint 3)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from typing import Any

from market_core import USE_PG, db_create_api_key, db_get_user_email, db_list_api_keys, get_db

logger = logging.getLogger(__name__)


def _ttl_seconds() -> int:
    try:
        return max(1, int(os.getenv("PROCURE_MAGIC_TTL_SECONDS", "900")))
    except (TypeError, ValueError):
        return 900


def procure_magic_enabled() -> bool:
    return bool((os.getenv("PROCURE_MAGIC_SECRET") or "").strip())


def _secret() -> bytes:
    raw = (os.getenv("PROCURE_MAGIC_SECRET") or "").strip()
    if not raw:
        raise ValueError("PROCURE_MAGIC_SECRET not configured")
    return raw.encode()


def procure_app_url() -> str:
    return (
        os.getenv("PROCURE_APP_URL")
        or os.getenv("NEXT_PUBLIC_PROCURE_APP_URL")
        or "https://procurecopilot.com/dashboard"
    ).rstrip("/")


def ensure_procure_magic_schema() -> None:
    db = get_db()
    if USE_PG:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS procure_magic_pending (
                jti_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                api_key TEXT NOT NULL,
                tier TEXT NOT NULL,
                exp INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS procure_magic_exchanges (
                jti_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                exchanged_at TIMESTAMP DEFAULT NOW()
            )
            """
        )
    else:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS procure_magic_pending (
                jti_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                api_key TEXT NOT NULL,
                tier TEXT NOT NULL,
                exp INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS procure_magic_exchanges (
                jti_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                exchanged_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
    db.commit()
    db.close()


def provision_procure_api_key(username: str) -> str:
    """Create a read_write API key for Procure onboarding (secret shown once)."""
    name = (username or "").strip()
    if not name:
        raise ValueError("username required")
    existing = db_list_api_keys(name)
    label = "procure-onboard"
    if any((k.get("label") or "") == label for k in existing):
        result = db_create_api_key(name, "read_write", label)
    elif not existing:
        result = db_create_api_key(name, "read_write", label)
    else:
        result = db_create_api_key(name, "read_write", label)
    return result["key"]


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def _jti_hash(jti: str) -> str:
    return hashlib.sha256(jti.encode()).hexdigest()


def create_procure_magic_token(*, username: str, api_key: str, tier: str) -> str:
    """Return signed opaque token (jti + exp only). Credentials stored server-side."""
    if not procure_magic_enabled():
        raise ValueError("PROCURE_MAGIC_SECRET not configured")
    name = (username or "").strip()
    key = (api_key or "").strip()
    tier_norm = (tier or "").strip().lower()
    if not name or not key or not tier_norm:
        raise ValueError("username, api_key, and tier required")
    jti = secrets.token_urlsafe(16)
    exp = int(time.time()) + _ttl_seconds()
    ensure_procure_magic_schema()
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO procure_magic_pending (jti_hash, username, api_key, tier, exp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (_jti_hash(jti), name, key, tier_norm, exp),
        )
        db.commit()
    finally:
        db.close()
    payload = {"jti": jti, "exp": exp}
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = _b64url(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def build_procure_magic_url(token: str) -> str:
    from urllib.parse import urlencode

    base = procure_app_url()
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode({'token': token})}"


def _parse_token(token: str) -> dict[str, Any]:
    raw = (token or "").strip()
    if not raw or "." not in raw:
        raise ValueError("invalid token")
    body, sig = raw.rsplit(".", 1)
    expected = _b64url(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, sig):
        raise ValueError("invalid token signature")
    try:
        payload = json.loads(_b64url_decode(body))
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("invalid token payload") from exc
    if not isinstance(payload, dict):
        raise ValueError("invalid token payload")
    exp = int(payload.get("exp") or 0)
    if exp < int(time.time()):
        raise ValueError("token expired")
    jti = (payload.get("jti") or "").strip()
    if not jti:
        raise ValueError("invalid token payload")
    return {"jti": jti, "exp": exp}


def _jti_used(jti: str) -> bool:
    ensure_procure_magic_schema()
    db = get_db()
    row = db.execute(
        "SELECT 1 FROM procure_magic_exchanges WHERE jti_hash=?",
        (_jti_hash(jti),),
    ).fetchone()
    db.close()
    return bool(row)


def _mark_jti_used(jti: str, username: str) -> None:
    ensure_procure_magic_schema()
    db = get_db()
    db.execute(
        "INSERT INTO procure_magic_exchanges (jti_hash, username) VALUES (?, ?)",
        (_jti_hash(jti), username),
    )
    db.commit()
    db.close()


def _load_pending_credentials(jti: str) -> dict[str, str]:
    ensure_procure_magic_schema()
    db = get_db()
    try:
        row = db.execute(
            """
            SELECT username, api_key, tier, exp
            FROM procure_magic_pending
            WHERE jti_hash=?
            """,
            (_jti_hash(jti),),
        ).fetchone()
        if not row:
            raise ValueError("invalid token")
        if int(row["exp"] or 0) < int(time.time()):
            db.execute("DELETE FROM procure_magic_pending WHERE jti_hash=?", (_jti_hash(jti),))
            db.commit()
            raise ValueError("token expired")
        db.execute("DELETE FROM procure_magic_pending WHERE jti_hash=?", (_jti_hash(jti),))
        db.commit()
        return {
            "username": (row["username"] or "").strip(),
            "api_key": (row["api_key"] or "").strip(),
            "tier": (row["tier"] or "").strip().lower(),
        }
    finally:
        db.close()


def exchange_procure_magic_token(token: str) -> dict[str, str]:
    """Validate token and return credentials once."""
    if not procure_magic_enabled():
        raise ValueError("PROCURE_MAGIC_SECRET not configured")
    parsed = _parse_token(token)
    if _jti_used(parsed["jti"]):
        raise ValueError("token already used")
    creds = _load_pending_credentials(parsed["jti"])
    if not creds["username"] or not creds["api_key"] or not creds["tier"]:
        raise ValueError("invalid token")
    _mark_jti_used(parsed["jti"], creds["username"])
    email = (db_get_user_email(creds["username"]) or "").strip().lower()
    return {
        "ok": True,
        "username": creds["username"],
        "api_key": creds["api_key"],
        "tier": creds["tier"],
        "email": email,
    }
