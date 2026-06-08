"""Onboarding funnel events — P3 instrumentation."""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta, timezone
from typing import Any

from market_core import USE_PG, get_db

FUNNEL_EVENTS = frozenset(
    {
        "install",
        "login",
        "register",
        "first_search",
        "starter_subscribe",
        "starter_request",
        "request_pro",
        "activated",
    }
)

_FUNNEL_DDL_PG = """
CREATE TABLE IF NOT EXISTS funnel_events (
    id SERIAL PRIMARY KEY,
    event TEXT NOT NULL,
    username TEXT,
    session_id TEXT,
    meta TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

_FUNNEL_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS funnel_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    username TEXT,
    session_id TEXT,
    meta TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


def ensure_funnel_schema() -> None:
    db = get_db()
    db.execute(_FUNNEL_DDL_PG if USE_PG else _FUNNEL_DDL_SQLITE)
    for idx_sql in (
        "CREATE INDEX IF NOT EXISTS idx_funnel_event ON funnel_events(event)",
        "CREATE INDEX IF NOT EXISTS idx_funnel_user ON funnel_events(username)",
        "CREATE INDEX IF NOT EXISTS idx_funnel_created ON funnel_events(created_at)",
    ):
        db.execute(idx_sql)
    db.commit()
    db.close()


def record_funnel_event(
    event: str,
    *,
    username: str | None = None,
    session_id: str | None = None,
    meta: dict[str, Any] | None = None,
    dedupe: bool = False,
) -> dict[str, Any]:
    """Persist one funnel event. dedupe=True skips if same user+event exists."""
    event = (event or "").strip().lower()
    if event not in FUNNEL_EVENTS:
        return {"ok": False, "error": f"unknown event: {event}"}

    ensure_funnel_schema()
    user = (username or "").strip() or None
    sid = (session_id or "").strip() or None

    if dedupe:
        db = get_db()
        row = None
        if user:
            row = db.execute(
                "SELECT id FROM funnel_events WHERE event=? AND username=? LIMIT 1",
                (event, user),
            ).fetchone()
        elif sid and event == "install":
            row = db.execute(
                "SELECT id FROM funnel_events WHERE event=? AND session_id=? LIMIT 1",
                (event, sid),
            ).fetchone()
        db.close()
        if row:
            return {"ok": True, "deduped": True, "event": event}

    db = get_db()
    db.execute(
        """
        INSERT INTO funnel_events (event, username, session_id, meta)
        VALUES (?, ?, ?, ?)
        """,
        (event, user, sid, json.dumps(meta or {}, ensure_ascii=False)),
    )
    db.commit()
    db.close()
    return {"ok": True, "event": event, "username": user}


def _parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str):
        value = str(value)
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _median_minutes(pairs: list[float]) -> float | None:
    if not pairs:
        return None
    return round(statistics.median(pairs), 1)


def funnel_summary(*, days: int = 30) -> dict[str, Any]:
    ensure_funnel_schema()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    rows = db.execute(
        "SELECT event, username, created_at FROM funnel_events WHERE created_at >= ?",
        (since,),
    ).fetchall()
    db.close()

    events: dict[str, int] = {e: 0 for e in FUNNEL_EVENTS}
    by_user: dict[str, dict[str, datetime]] = {}

    for row in rows:
        ev = row["event"]
        events[ev] = events.get(ev, 0) + 1
        user = row["username"]
        if not user:
            continue
        ts = _parse_ts(row["created_at"])
        if not ts:
            continue
        by_user.setdefault(user, {})[ev] = ts

    register_n = events.get("register", 0) or len(
        {u for u, evs in by_user.items() if "register" in evs}
    )
    search_users = {u for u, evs in by_user.items() if "first_search" in evs}
    starter_sub_users = {u for u, evs in by_user.items() if "starter_subscribe" in evs}
    pro_users = {u for u, evs in by_user.items() if "request_pro" in evs}
    activated_users = {u for u, evs in by_user.items() if "activated" in evs}

    ttfv: list[float] = []
    for evs in by_user.values():
        if "register" in evs and "first_search" in evs:
            delta = (evs["first_search"] - evs["register"]).total_seconds() / 60
            if delta >= 0:
                ttfv.append(delta)

    ttc: list[float] = []
    for evs in by_user.values():
        if "request_pro" in evs and "activated" in evs:
            delta = (evs["activated"] - evs["request_pro"]).total_seconds() / 3600
            if delta >= 0:
                ttc.append(delta)

    def conv(num: int, den: int) -> float | None:
        if den <= 0:
            return None
        return round(num / den, 3)

    starter_sub_n = max(events.get("starter_subscribe", 0), len(starter_sub_users))
    steps = [
        ("install", events.get("install", 0)),
        ("register", max(register_n, events.get("register", 0))),
        ("first_search", len(search_users)),
        ("starter_subscribe", starter_sub_n),
        ("request_pro", len(pro_users)),
        ("activated", len(activated_users)),
    ]
    funnel_steps = []
    prev = None
    for name, count in steps:
        drop = None
        if prev is not None and prev > 0:
            drop = round((1 - count / prev) * 100, 1) if count <= prev else 0.0
        funnel_steps.append({"step": name, "count": count, "drop_off_pct": drop})
        if count > 0:
            prev = count

    return {
        "window_days": days,
        "events": events,
        "unique_users": {
            "with_search": len(search_users),
            "with_starter_subscribe": len(starter_sub_users),
            "with_pro_request": len(pro_users),
            "activated": len(activated_users),
        },
        "conversion": {
            "register_to_search": conv(len(search_users), register_n),
            "search_to_starter": conv(starter_sub_n, len(search_users)),
            "search_to_pro": conv(len(pro_users), len(search_users)),
            "pro_to_activated": conv(len(activated_users), len(pro_users)),
        },
        "ttfv_median_minutes": _median_minutes(ttfv),
        "ttc_median_hours": _median_minutes(ttc),
        "funnel_steps": funnel_steps,
    }


def maybe_first_search(username: str, *, query: str = "") -> None:
    record_funnel_event(
        "first_search",
        username=username,
        meta={"query": query[:80]} if query else None,
        dedupe=True,
    )


def _is_auto_activate_link(payment_link: str) -> bool:
    link = (payment_link or "").lower()
    return "billing/subscriptions" in link or "/subscriptions?" in link


def activation_summary(*, days: int = 30) -> dict[str, Any]:
    """Pro activation path: webhook auto vs manual hosted-button queue."""
    ensure_funnel_schema()
    days = max(1, min(days, 90))
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    req_rows = db.execute(
        """
        SELECT status, payment_link FROM subscription_requests
        WHERE created_at >= ? AND id LIKE 'PRO-%'
        """,
        (since,),
    ).fetchall()
    act_rows = db.execute(
        """
        SELECT username, meta FROM funnel_events
        WHERE event = 'activated' AND created_at >= ?
        """,
        (since,),
    ).fetchall()
    db.close()

    pending_auto = 0
    pending_manual = 0
    requests_activated = 0
    for row in req_rows:
        status = row["status"]
        link = row["payment_link"] or ""
        if status == "activated":
            requests_activated += 1
        elif status == "pending":
            if _is_auto_activate_link(link):
                pending_auto += 1
            else:
                pending_manual += 1

    webhook_activated = 0
    manual_activated = 0
    other_activated = 0
    activated_users: set[str] = set()
    for row in act_rows:
        user = row["username"]
        if user:
            activated_users.add(user)
        try:
            meta = json.loads(row["meta"] or "{}")
        except json.JSONDecodeError:
            meta = {}
        src = str(meta.get("source") or "")
        if src == "paypal_webhook":
            webhook_activated += 1
        elif src in ("ops_manual", "manual", "activate_pro"):
            manual_activated += 1
        else:
            other_activated += 1

    total_activated_events = webhook_activated + manual_activated + other_activated

    def conv(num: int, den: int) -> float | None:
        if den <= 0:
            return None
        return round(num / den, 4)

    webhook_share = conv(webhook_activated, total_activated_events)

    unified = pending_manual == 0 and (
        total_activated_events == 0 or (webhook_share or 0) >= 0.8
    )

    return {
        "window_days": days,
        "subscription_requests": {
            "pending_auto": pending_auto,
            "pending_manual": pending_manual,
            "activated": requests_activated,
            "total": len(req_rows),
        },
        "activated_events": {
            "webhook": webhook_activated,
            "manual": manual_activated,
            "other": other_activated,
            "unique_users": len(activated_users),
            "total": total_activated_events,
        },
        "webhook_share": webhook_share,
        "unified_webhook": unified,
        "conversion": {
            "webhook_of_activated": webhook_share,
        },
    }