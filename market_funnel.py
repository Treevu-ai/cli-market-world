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
        "procure_subscribe",
        "onboarding_complete",
        "tutorial_completed",
        "mcp_setup_completed",
        "mcp_connect",
        "use_case_demo",
        "demo_session_created",
        "demo_first_tool_call",
        "mcp_tool_call",
        "activated",
        # P1: granular CLI dropoff tracking (install → register)
        "cli_command_attempted",
        "cli_command_result",
        "cli_auth_wall_hit",
        # Procure checkout LATAM funnel
        "procure_subscribe_click",
        "procure_magic_exchange_ok",
        "procure_magic_exchange_fail",
    }
)

_DIGEST_EVENTS = frozenset(
    {
        "register",
        "first_search",
        "starter_subscribe",
        "starter_request",
        "request_pro",
        "procure_subscribe",
        "onboarding_complete",
        "tutorial_completed",
        "mcp_setup_completed",
        "use_case_demo",
        "demo_session_created",
        "demo_first_tool_call",
        "activated",
    }
)

_NOISE_PREFIXES = ("smoke", "deploy-test", "shiptest", "test-", "pam-")

# Confirmed CI/test accounts — NOT a blanket pattern.  Public registrations
# also produce user-<hex12> usernames; those are real users and must NOT be
# excluded.  Add specific IDs here only after manual verification.
_NOISE_USER_IDS: frozenset[str] = frozenset((
    "user-87db316c7763",
    "user-a8d64197d3a4",
    "user-ce7da4a4e021",
    "user-cf8b473f4e64",
))


_NOISE_META_SOURCES = frozenset(("test", "ci", "smoke", "deploy-test", "integration-test"))


def is_noise_username(username: str | None) -> bool:
    """CI/smoke/known-test accounts — exclude from founder adoption views.

    NOTE: user-<hex> usernames from public /auth/register are real users.
    Only explicitly listed test IDs are filtered, not the pattern.
    """
    u = (username or "").strip().lower()
    if not u:
        return False
    if any(u.startswith(p) for p in _NOISE_PREFIXES):
        return True
    return u in _NOISE_USER_IDS


def is_noise_meta(meta: dict[str, Any] | str | None) -> bool:
    """Return True if event meta indicates test/CI traffic (source field)."""
    if not meta:
        return False
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except (json.JSONDecodeError, TypeError):
            return False
    if not isinstance(meta, dict):
        return False
    source = (meta.get("source") or "").strip().lower()
    return source in _NOISE_META_SOURCES


def _parse_meta(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value:
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


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


def funnel_recent_events(
    *,
    hours: int = 24,
    exclude_noise: bool = True,
) -> list[dict[str, Any]]:
    """Recent funnel rows for Slack digest (newest first)."""
    ensure_funnel_schema()
    hours = max(1, min(hours, 168))
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    db = get_db()
    rows = db.execute(
        """
        SELECT event, username, meta, created_at
        FROM funnel_events
        WHERE created_at >= ? AND event IN ({})
        ORDER BY created_at DESC
        """.format(",".join("?" * len(_DIGEST_EVENTS))),
        (since, *_DIGEST_EVENTS),
    ).fetchall()
    db.close()
    out: list[dict[str, Any]] = []
    for row in rows:
        user = row["username"] or ""
        if exclude_noise and is_noise_username(user):
            continue
        meta_raw = row["meta"] or "{}"
        try:
            meta = json.loads(meta_raw) if isinstance(meta_raw, str) else {}
        except json.JSONDecodeError:
            meta = {}
        if exclude_noise and is_noise_meta(meta):
            continue
        out.append(
            {
                "event": row["event"],
                "username": user,
                "meta": meta if isinstance(meta, dict) else {},
                "created_at": row["created_at"],
            }
        )
    return out


def funnel_digest_counts(*, hours: int = 24, exclude_noise: bool = True) -> dict[str, int]:
    """Event counts in the digest window."""
    counts = {e: 0 for e in _DIGEST_EVENTS}
    for row in funnel_recent_events(hours=hours, exclude_noise=exclude_noise):
        ev = row.get("event", "")
        if ev in counts:
            counts[ev] += 1
    return counts


def funnel_recent_users(
    *,
    hours: int = 168,
    limit: int = 50,
    exclude_noise: bool = True,
) -> list[dict[str, Any]]:
    """Per-user adoption trail for admin dashboards (newest activity first)."""
    ensure_funnel_schema()
    hours = max(1, min(hours, 24 * 90))
    limit = max(1, min(limit, 200))
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    db = get_db()
    rows = db.execute(
        """
        SELECT username, event, created_at, meta
        FROM funnel_events
        WHERE created_at >= ? AND username IS NOT NULL AND username != ''
        ORDER BY created_at DESC
        """,
        (since,),
    ).fetchall()
    tiers: dict[str, str] = {}
    try:
        for row in db.execute("SELECT username, tier FROM subscriptions").fetchall():
            tiers[row["username"]] = row["tier"] or "free"
    except Exception:
        pass
    db.close()

    users: dict[str, dict[str, Any]] = {}
    noise_users: set[str] = set()
    for row in rows:
        user = (row["username"] or "").strip()
        if not user or (exclude_noise and is_noise_username(user)):
            continue
        ev = row["event"]
        ts = row["created_at"]
        meta_raw = row["meta"] or "{}"
        try:
            meta = json.loads(meta_raw) if isinstance(meta_raw, str) else {}
        except json.JSONDecodeError:
            meta = {}
        if exclude_noise and is_noise_meta(meta):
            noise_users.add(user)
            continue
        entry = users.setdefault(
            user,
            {
                "username": user,
                "tier": tiers.get(user, "free"),
                "events": {},
                "sources": [],
                "last_activity_at": ts,
            },
        )
        if ev not in entry["events"]:
            entry["events"][ev] = ts
        src = (meta.get("source") or "").strip() if isinstance(meta, dict) else ""
        if src and src not in entry["sources"]:
            entry["sources"].append(src)
    # Remove users whose ONLY events are noise-sourced
    for u in noise_users:
        if u not in users:
            continue
        # User had some non-noise events, keep them

    out: list[dict[str, Any]] = []
    for entry in users.values():
        evs = entry["events"]
        out.append(
            {
                "username": entry["username"],
                "tier": entry["tier"],
                "registered_at": evs.get("register"),
                "first_search_at": evs.get("first_search"),
                "onboarding_complete_at": evs.get("onboarding_complete"),
                "request_pro_at": evs.get("request_pro"),
                "activated_at": evs.get("activated"),
                "last_activity_at": entry["last_activity_at"],
                "sources": entry["sources"][:5],
                "has_search": "first_search" in evs,
                "has_onboarding_complete": "onboarding_complete" in evs,
            }
        )
    out.sort(key=lambda u: str(u.get("last_activity_at") or ""), reverse=True)
    return out[:limit]


def funnel_summary(*, days: int = 30, exclude_noise: bool = False) -> dict[str, Any]:
    ensure_funnel_schema()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    rows = db.execute(
        "SELECT event, username, meta, created_at FROM funnel_events WHERE created_at >= ?",
        (since,),
    ).fetchall()
    db.close()

    events: dict[str, int] = {e: 0 for e in FUNNEL_EVENTS}
    by_user: dict[str, dict[str, datetime]] = {}

    for row in rows:
        ev = row["event"]
        user = row["username"]
        if user and exclude_noise and is_noise_username(user):
            continue
        if exclude_noise and is_noise_meta(row["meta"]):
            continue
        events[ev] = events.get(ev, 0) + 1
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


def mcp_analytics(*, days: int = 30, include_test: bool = False) -> dict[str, Any]:
    """MCP connection and tool-call analytics grouped by client."""
    ensure_funnel_schema()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    rows = db.execute(
        "SELECT event, username, meta, created_at FROM funnel_events WHERE event IN (?, ?) AND created_at >= ?",
        ("mcp_connect", "mcp_tool_call", since),
    ).fetchall()
    db.close()

    connects_by_client: dict[str, int] = {}
    tool_calls_by_client: dict[str, int] = {}
    tool_calls_by_tool: dict[str, int] = {}
    tool_calls_by_client_tool: dict[str, dict[str, int]] = {}
    unique_tokens: set[str] = set()
    unique_tokens_by_client: dict[str, set[str]] = {}
    protocol_versions: dict[str, int] = {}
    unknown_raw_samples: list[str] = []

    for row in rows:
        meta = _parse_meta(row["meta"])
        username = row["username"] or ""
        if not include_test and is_noise_username(username):
            continue

        client = meta.get("client") or "unknown"
        event = row["event"]

        if event == "mcp_connect":
            connects_by_client[client] = connects_by_client.get(client, 0) + 1
            if username:
                unique_tokens.add(username)
                unique_tokens_by_client.setdefault(client, set()).add(username)
            proto = meta.get("protocol_version") or "unknown"
            protocol_versions[proto] = protocol_versions.get(proto, 0) + 1
            if client == "unknown":
                raw = (meta.get("client_raw") or "").strip()
                if raw and raw not in unknown_raw_samples:
                    unknown_raw_samples.append(raw)
        elif event == "mcp_tool_call":
            tool = meta.get("tool") or "unknown"
            tool_calls_by_client[client] = tool_calls_by_client.get(client, 0) + 1
            tool_calls_by_tool[tool] = tool_calls_by_tool.get(tool, 0) + 1
            tool_calls_by_client_tool.setdefault(client, {})
            tool_calls_by_client_tool[client][tool] = (
                tool_calls_by_client_tool[client].get(tool, 0) + 1
            )

    total_connects = sum(connects_by_client.values())
    total_tool_calls = sum(tool_calls_by_client.values())

    result: dict[str, Any] = {
        "window_days": days,
        "connections": {
            "total": total_connects,
            "unique_tokens": len(unique_tokens),
            "by_client": dict(sorted(connects_by_client.items(), key=lambda x: -x[1])),
            "unique_by_client": {
                k: len(v)
                for k, v in sorted(
                    unique_tokens_by_client.items(), key=lambda x: -len(x[1])
                )
            },
            "by_protocol_version": dict(
                sorted(protocol_versions.items(), key=lambda x: -x[1])
            ),
        },
        "tool_calls": {
            "total": total_tool_calls,
            "by_client": dict(sorted(tool_calls_by_client.items(), key=lambda x: -x[1])),
            "by_tool": dict(sorted(tool_calls_by_tool.items(), key=lambda x: -x[1])),
            "by_client_and_tool": {
                k: dict(sorted(v.items(), key=lambda x: -x[1]))
                for k, v in sorted(
                    tool_calls_by_client_tool.items(),
                    key=lambda x: -sum(x[1].values()),
                )
            },
        },
        "includes_test_traffic": include_test,
    }
    if unknown_raw_samples:
        result["unknown_client_raw_samples"] = unknown_raw_samples[:20]
    return result


def maybe_first_search(username: str, *, query: str = "") -> None:
    result = record_funnel_event(
        "first_search",
        username=username,
        meta={"query": query[:80]} if query else None,
        dedupe=True,
    )
    if result.get("ok") and not result.get("deduped"):
        try:
            import sys as _sys
            from pathlib import Path as _Path
            _ops = str(_Path(__file__).resolve().parent / "ops")
            if _ops not in _sys.path:
                _sys.path.insert(0, _ops)
            from billing_slack import notify_first_search
            notify_first_search(username=username, query=query)
        except Exception:
            pass


def _is_auto_activate_link(payment_link: str) -> bool:
    link = (payment_link or "").lower()
    return "billing/subscriptions" in link or "/subscriptions?" in link


def dropoff_summary(*, days: int = 30, include_test: bool = False) -> dict[str, Any]:
    """P1: Granular CLI dropoff analysis — install → register funnel."""
    ensure_funnel_schema()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    rows = db.execute(
        """
        SELECT event, username, session_id, meta, created_at
        FROM funnel_events
        WHERE event IN ('cli_command_attempted','cli_command_result','cli_auth_wall_hit')
          AND created_at >= ?
        """,
        (since,),
    ).fetchall()
    db.close()

    attempted: dict[str, dict] = {}
    results: list[dict] = []
    auth_wall_hits: list[dict] = []
    excluded = 0

    for row in rows:
        meta = _parse_meta(row["meta"])
        user = row["username"]
        if not include_test and (is_noise_username(user) or is_noise_meta(meta)):
            excluded += 1
            continue

        ev = row["event"]
        sid = row["session_id"] or ""
        cmd = (meta.get("command") or "unknown").strip()

        if ev == "cli_command_attempted":
            attempted[sid] = {"command": cmd, "ts": row["created_at"], "username": user}
        elif ev == "cli_command_result":
            results.append({
                "session_id": sid,
                "command": cmd,
                "success": bool(meta.get("success")),
                "elapsed_ms": meta.get("elapsed_ms"),
                "error_type": meta.get("error_type"),
                "username": user,
            })
        elif ev == "cli_auth_wall_hit":
            auth_wall_hits.append({"session_id": sid, "command": cmd, "username": user})

    total_attempted = len(attempted)
    total_auth_wall = len(auth_wall_hits)
    converted_after_wall = sum(1 for h in auth_wall_hits if h.get("username"))

    cmd_counts: dict[str, int] = {}
    for v in attempted.values():
        cmd_counts[v["command"]] = cmd_counts.get(v["command"], 0) + 1

    wall_cmd_counts: dict[str, int] = {}
    for h in auth_wall_hits:
        wall_cmd_counts[h["command"]] = wall_cmd_counts.get(h["command"], 0) + 1

    total_results = len(results)
    success_n = sum(1 for r in results if r["success"])
    failure_n = total_results - success_n
    error_types: dict[str, int] = {}
    for r in results:
        et = r.get("error_type") or ("none" if r["success"] else "unknown")
        error_types[et] = error_types.get(et, 0) + 1

    elapsed_vals = [r["elapsed_ms"] for r in results if r.get("elapsed_ms") is not None]
    median_elapsed = _median_minutes(elapsed_vals) if elapsed_vals else None

    def _pct(n: int, d: int) -> float | None:
        return round(n / d * 100, 1) if d > 0 else None

    return {
        "window_days": days,
        "cli_sessions": {
            "attempted": total_attempted,
            "hit_auth_wall": total_auth_wall,
            "auth_wall_pct": _pct(total_auth_wall, total_attempted),
            "converted_after_wall": converted_after_wall,
            "wall_conversion_pct": _pct(converted_after_wall, total_auth_wall),
        },
        "command_distribution": dict(sorted(cmd_counts.items(), key=lambda x: -x[1])),
        "auth_wall_by_command": dict(sorted(wall_cmd_counts.items(), key=lambda x: -x[1])),
        "command_results": {
            "total": total_results,
            "success": success_n,
            "failure": failure_n,
            "success_pct": _pct(success_n, total_results),
            "median_elapsed_ms": median_elapsed,
            "error_types": dict(sorted(error_types.items(), key=lambda x: -x[1])),
        },
        "excluded_test_events": excluded,
        "includes_test_traffic": include_test,
    }


def render_dropoff_html(*, days: int = 30) -> str:
    """P1: HTML dashboard for CLI install → register dropoff analysis."""
    import html as _html

    data = dropoff_summary(days=days, include_test=False)
    s = data["cli_sessions"]
    cmd_dist = data["command_distribution"]
    wall_cmds = data["auth_wall_by_command"]
    res = data["command_results"]

    def _bar(count: int, total: int, color: str = "#38bdf8") -> str:
        pct = round(count / total * 100) if total > 0 else 0
        return (
            f'<div style="background:#1e293b;border-radius:4px;height:8px;margin-top:4px">'
            f'<div style="width:{pct}%;background:{color};height:8px;border-radius:4px"></div>'
            f"</div>"
        )

    def _cmd_rows(mapping: dict[str, int]) -> str:
        total = sum(mapping.values()) or 1
        rows = ""
        for cmd, n in list(mapping.items())[:10]:
            rows += (
                f"<tr><td>{_html.escape(cmd)}</td><td style='text-align:right'>{n}</td>"
                f"<td style='width:120px'>{_bar(n, total)}</td></tr>"
            )
        return rows or "<tr><td colspan='3' style='color:#64748b'>Sin datos</td></tr>"

    wall_pct = s.get("auth_wall_pct") or 0
    wall_color = "#ef4444" if wall_pct > 50 else "#eab308" if wall_pct > 20 else "#22c55e"
    success_pct = res.get("success_pct") or 0
    succ_color = "#22c55e" if success_pct >= 80 else "#eab308" if success_pct >= 50 else "#ef4444"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>CLI Market · Dropoff P1</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background:#0a0a0a; color:#e2e8f0; margin:0; padding:24px; }}
    h1 {{ margin:0 0 4px; font-size:1.4rem; }}
    .sub {{ color:#64748b; font-size:0.85rem; margin-bottom:20px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin-bottom:24px; }}
    .card {{ background:#111; border:1px solid #333; border-radius:8px; padding:16px; }}
    .card h2 {{ margin:0 0 10px; font-size:0.9rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; }}
    .big {{ font-size:2rem; font-weight:700; line-height:1; }}
    .label {{ font-size:0.75rem; color:#64748b; margin-top:4px; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
    td {{ padding:6px 4px; border-bottom:1px solid #1e293b; vertical-align:middle; }}
    tr:last-child td {{ border-bottom:none; }}
    .section {{ background:#111; border:1px solid #333; border-radius:8px; padding:16px; margin-bottom:16px; }}
    .section h2 {{ margin:0 0 12px; font-size:0.9rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; }}
    .meta {{ color:#64748b; font-size:0.8rem; margin-top:20px; }}
    a {{ color:#38bdf8; }}
  </style>
</head>
<body>
  <h1>CLI Market · Dropoff dashboard (P1)</h1>
  <p class="sub">install → auth wall → register · ventana {days}d · {ts}</p>

  <div class="grid">
    <div class="card">
      <h2>Sesiones CLI</h2>
      <div class="big">{s['attempted']}</div>
      <div class="label">comandos intentados</div>
    </div>
    <div class="card">
      <h2>Auth wall hit</h2>
      <div class="big" style="color:{wall_color}">{s['hit_auth_wall']}</div>
      <div class="label">{s.get('auth_wall_pct') or 0}% de sesiones</div>
    </div>
    <div class="card">
      <h2>Convirtieron post-wall</h2>
      <div class="big" style="color:#22c55e">{s['converted_after_wall']}</div>
      <div class="label">{s.get('wall_conversion_pct') or 0}% de los que chocaron el muro</div>
    </div>
    <div class="card">
      <h2>Éxito de comando</h2>
      <div class="big" style="color:{succ_color}">{success_pct}%</div>
      <div class="label">{res['success']} ok / {res['failure']} fail de {res['total']}</div>
    </div>
    <div class="card">
      <h2>Latencia mediana</h2>
      <div class="big">{res.get('median_elapsed_ms') or '—'}</div>
      <div class="label">ms por comando</div>
    </div>
  </div>

  <div class="section">
    <h2>Primer comando intentado (distribución)</h2>
    <table>
      <tr><td style="color:#64748b">Comando</td><td style="color:#64748b;text-align:right">N</td><td></td></tr>
      {_cmd_rows(cmd_dist)}
    </table>
  </div>

  <div class="section">
    <h2>Auth wall — comandos que más lo disparan</h2>
    <table>
      <tr><td style="color:#64748b">Comando</td><td style="color:#64748b;text-align:right">N</td><td></td></tr>
      {_cmd_rows(wall_cmds)}
    </table>
  </div>

  <div class="section">
    <h2>Tipos de error</h2>
    <table>
      {''.join(f"<tr><td>{_html.escape(k)}</td><td style='text-align:right'>{v}</td></tr>" for k,v in (res.get('error_types') or {{}}).items()) or "<tr><td colspan='2' style='color:#64748b'>Sin datos</td></tr>"}
    </table>
  </div>

  <p class="meta">
    JSON: <a href="/dashboard/dropoff?days={days}">/dashboard/dropoff</a> ·
    Público: <a href="/analytics/dropoff">/analytics/dropoff</a> ·
    Go-live: <a href="/dashboard/go-live/page">/dashboard/go-live/page</a>
  </p>
</body>
</html>"""


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
