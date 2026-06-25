"""Payment vault ownership bindings — prevent cross-user token/customer access (IDOR).

Used by PayPal Vault (customer_id, payment_token_id) and MercadoPago saved cards (customer_id).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from market_core import USE_PG, get_db

logger = logging.getLogger("market").getChild("vault")

_VAULT_DDL_PG = """
CREATE TABLE IF NOT EXISTS vault_bindings (
    id               BIGSERIAL PRIMARY KEY,
    username         TEXT NOT NULL,
    customer_id      TEXT,
    payment_token_id TEXT UNIQUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

_VAULT_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS vault_bindings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT NOT NULL,
    customer_id      TEXT,
    payment_token_id TEXT UNIQUE,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_schema_ready = False


def ensure_vault_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return
    db = get_db()
    db.execute(_VAULT_DDL_PG if USE_PG else _VAULT_DDL_SQLITE)
    for idx in (
        "CREATE INDEX IF NOT EXISTS idx_vault_bindings_user ON vault_bindings(username)",
        "CREATE INDEX IF NOT EXISTS idx_vault_bindings_customer ON vault_bindings(customer_id)",
    ):
        db.execute(idx)
    db.commit()
    db.close()
    _schema_ready = True


def bind_vault_customer(username: str, customer_id: str) -> None:
    """Record that customer_id belongs to username (vault-setup)."""
    if not customer_id:
        return
    ensure_vault_schema()
    db = get_db()
    if USE_PG:
        db.execute(
            "INSERT INTO vault_bindings (username, customer_id) "
            "SELECT %s, %s WHERE NOT EXISTS ("
            "  SELECT 1 FROM vault_bindings WHERE username = %s AND customer_id = %s"
            ")",
            (username, customer_id, username, customer_id),
        )
    else:
        db.execute(
            "INSERT INTO vault_bindings (username, customer_id) "
            "SELECT ?, ? WHERE NOT EXISTS ("
            "  SELECT 1 FROM vault_bindings WHERE username = ? AND customer_id = ?"
            ")",
            (username, customer_id, username, customer_id),
        )
    db.commit()
    db.close()


def bind_vault_payment_token(username: str, customer_id: str, payment_token_id: str) -> None:
    """Record payment token ownership after vault-confirm."""
    if not payment_token_id:
        return
    ensure_vault_schema()
    db = get_db()
    if USE_PG:
        db.execute(
            "INSERT INTO vault_bindings (username, customer_id, payment_token_id) "
            "VALUES (%s, %s, %s) "
            "ON CONFLICT (payment_token_id) DO UPDATE SET "
            "username = EXCLUDED.username, customer_id = EXCLUDED.customer_id",
            (username, customer_id or None, payment_token_id),
        )
    else:
        db.execute(
            "INSERT OR REPLACE INTO vault_bindings (username, customer_id, payment_token_id) "
            "VALUES (?, ?, ?)",
            (username, customer_id or None, payment_token_id),
        )
    db.commit()
    db.close()


def vault_customer_owned(username: str, customer_id: str) -> bool:
    """True if customer_id was bound to username at setup/confirm."""
    if not customer_id:
        return False
    ensure_vault_schema()
    db = get_db()
    ph = "%s" if USE_PG else "?"
    row = db.execute(
        f"SELECT 1 FROM vault_bindings WHERE username = {ph} AND customer_id = {ph} LIMIT 1",
        (username, customer_id),
    ).fetchone()
    db.close()
    return row is not None


def vault_customer_bound_to_other(username: str, customer_id: str) -> bool:
    """True if customer_id is bound to a different user."""
    if not customer_id:
        return False
    ensure_vault_schema()
    db = get_db()
    ph = "%s" if USE_PG else "?"
    row = db.execute(
        f"SELECT 1 FROM vault_bindings WHERE customer_id = {ph} AND username != {ph} LIMIT 1",
        (customer_id, username),
    ).fetchone()
    db.close()
    return row is not None


def vault_customer_owner(customer_id: str) -> str | None:
    """Return username that owns customer_id, or None if unbound."""
    if not customer_id:
        return None
    ensure_vault_schema()
    db = get_db()
    ph = "%s" if USE_PG else "?"
    row = db.execute(
        f"SELECT username FROM vault_bindings WHERE customer_id = {ph} LIMIT 1",
        (customer_id,),
    ).fetchone()
    db.close()
    if not row:
        return None
    return row["username"] if isinstance(row, dict) else row[0]


def vault_payment_token_owner(payment_token_id: str) -> str | None:
    """Return username that owns payment_token_id, or None if unbound."""
    if not payment_token_id:
        return None
    ensure_vault_schema()
    db = get_db()
    ph = "%s" if USE_PG else "?"
    row = db.execute(
        f"SELECT username FROM vault_bindings WHERE payment_token_id = {ph} LIMIT 1",
        (payment_token_id,),
    ).fetchone()
    db.close()
    if not row:
        return None
    return row["username"] if isinstance(row, dict) else row[0]


def _parse_audit_detail(detail: Any) -> dict[str, Any]:
    if detail is None:
        return {}
    if isinstance(detail, dict):
        return detail
    if isinstance(detail, str):
        try:
            parsed = json.loads(detail)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def backfill_vault_bindings_from_audit() -> dict[str, int]:
    """Populate vault_bindings from historical audit_log (save_card, vault_confirm).

    Idempotent — safe on every startup. First audit entry wins on customer_id conflicts.
    """
    from market_audit import ensure_audit_schema

    ensure_audit_schema()
    ensure_vault_schema()
    db = get_db()
    rows = db.execute(
        "SELECT username, action, detail, created_at FROM audit_log "
        "WHERE action IN ('save_card', 'vault_confirm') "
        "ORDER BY created_at ASC"
    ).fetchall()
    db.close()

    stats = {
        "customers_bound": 0,
        "tokens_bound": 0,
        "customers_skipped": 0,
        "tokens_skipped": 0,
    }

    for row in rows:
        username = (row["username"] if isinstance(row, dict) else row[0] or "").strip()
        action = row["action"] if isinstance(row, dict) else row[1]
        detail = _parse_audit_detail(row["detail"] if isinstance(row, dict) else row[2])
        if not username:
            continue

        customer_id = (detail.get("customer_id") or "").strip()
        if customer_id:
            owner = vault_customer_owner(customer_id)
            if owner is None:
                bind_vault_customer(username, customer_id)
                stats["customers_bound"] += 1
            elif owner != username:
                stats["customers_skipped"] += 1

        if action != "vault_confirm":
            continue

        payment_token_id = (
            detail.get("payment_token_id") or detail.get("payment_token") or ""
        ).strip()
        if not payment_token_id:
            continue
        token_owner = vault_payment_token_owner(payment_token_id)
        if token_owner is None:
            bind_vault_payment_token(username, customer_id, payment_token_id)
            stats["tokens_bound"] += 1
        elif token_owner != username:
            stats["tokens_skipped"] += 1

    if any(stats.values()):
        logger.info("vault_bindings backfill from audit: %s", stats)
    return stats


def vault_payment_token_owned(username: str, payment_token_id: str) -> bool:
    """True if payment_token_id was confirmed by username."""
    if not payment_token_id:
        return False
    ensure_vault_schema()
    db = get_db()
    ph = "%s" if USE_PG else "?"
    row = db.execute(
        f"SELECT 1 FROM vault_bindings WHERE username = {ph} AND payment_token_id = {ph} LIMIT 1",
        (username, payment_token_id),
    ).fetchone()
    db.close()
    return row is not None
