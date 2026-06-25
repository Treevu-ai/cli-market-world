"""PayPal Vault ownership bindings — prevent cross-user token access (IDOR)."""

from __future__ import annotations

from market_core import USE_PG, get_db

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
