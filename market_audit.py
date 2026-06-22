"""Audit log for admin and billing actions.

Records who did what, when, and from where. All admin endpoints,
billing mutations, and subscription changes should call record_audit().
"""

from __future__ import annotations

import json
import logging
from typing import Any

from market_core import USE_PG, get_db

logger = logging.getLogger("market").getChild("audit")

_AUDIT_DDL_PG = """
CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    username    TEXT NOT NULL,
    action      TEXT NOT NULL,
    resource    TEXT,
    detail      JSONB,
    ip          TEXT,
    user_agent  TEXT
);
"""

_AUDIT_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    username    TEXT NOT NULL,
    action      TEXT NOT NULL,
    resource    TEXT,
    detail      TEXT,
    ip          TEXT,
    user_agent  TEXT
);
"""

_schema_ready = False


def ensure_audit_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return
    db = get_db()
    db.execute(_AUDIT_DDL_PG if USE_PG else _AUDIT_DDL_SQLITE)
    for idx in (
        "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(username)",
        "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)",
        "CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at)",
    ):
        db.execute(idx)
    db.commit()
    db.close()
    _schema_ready = True


def record_audit(
    action: str,
    *,
    username: str = "",
    resource: str | None = None,
    detail: dict[str, Any] | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> None:
    """Persist one audit entry. Non-blocking — exceptions are logged, not raised."""
    try:
        ensure_audit_schema()
        db = get_db()
        detail_str = json.dumps(detail, default=str) if detail else None
        if USE_PG:
            db.execute(
                "INSERT INTO audit_log (username, action, resource, detail, ip, user_agent) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (username, action, resource, detail_str, ip, user_agent),
            )
        else:
            db.execute(
                "INSERT INTO audit_log (username, action, resource, detail, ip, user_agent) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (username, action, resource, detail_str, ip, user_agent),
            )
        db.commit()
        db.close()
    except Exception:
        logger.debug("audit record failed", exc_info=True)


def get_audit_log(
    limit: int = 100,
    username: str | None = None,
    action: str | None = None,
) -> list[dict[str, Any]]:
    """Query audit log with optional filters."""
    ensure_audit_schema()
    db = get_db()
    clauses: list[str] = []
    params: list[Any] = []
    ph = "%s" if USE_PG else "?"
    if username:
        clauses.append(f"username = {ph}")
        params.append(username)
    if action:
        clauses.append(f"action = {ph}")
        params.append(action)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(limit)
    rows = db.execute(
        f"SELECT * FROM audit_log{where} ORDER BY created_at DESC LIMIT {ph}",
        tuple(params),
    ).fetchall()
    db.close()
    return rows
