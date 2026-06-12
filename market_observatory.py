"""Observatory — MCP/API telemetry (agent_events, MAA, retention).

Canonical implementation lives in cli-market-core. World and backend import
via ``market_observatory`` shim and register ``ObservatoryMiddleware``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import uuid
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from market_core import USE_PG, get_db

logger = logging.getLogger("market").getChild("observatory")

_NOISE_PREFIXES = ("smoke", "deploy-test", "shiptest", "test-", "pam-", "user-")
_NOISE_USER_HEX = re.compile(r"^user-[0-9a-f]{8,}$", re.I)
_METADATA_ALLOWLIST = frozenset({"client", "mcp_version", "cli_version", "identity_confidence"})
_SKIP_PATHS = frozenset({"/health", "/", "/docs", "/openapi.json", "/redoc", "/favicon.ico"})
_SKIP_PREFIXES = ("/admin/", "/static/", "/dashboard/observatory")
_INTERNAL_TOOLS = frozenset({"index_stats", "index_lookup", "index_resolve"})
_REST_TOOL_ALIASES: dict[str, str] = {
    "market_agent_ask": "market_ask",
    "market_agent_preferences": "market_preferences",
    "market_data_export": "market_export",
    "market_data_prices": "market_stats",
}

_EXACT_ROUTES: dict[tuple[str, str], tuple[str, str]] = {
    ("POST", "/products/search"): ("market_search", "search"),
    ("POST", "/products/compare"): ("market_compare", "compare"),
    ("POST", "/v1/basket/compare"): ("market_compare", "compare"),
    ("POST", "/agent/ask"): ("market_ask", "agent"),
    ("GET", "/agent/preferences"): ("market_preferences", "agent"),
}

_PREFIX_ROUTES: tuple[tuple[str, str, str], ...] = (
    ("/cart", "market_cart_update", "cart"),
    ("/checkout", "market_checkout", "checkout"),
    ("/payments", "market_checkout", "checkout"),
    ("/intel", "market_intel_brief", "intel"),
    ("/v1/data", "market_export", "data"),
    ("/v1/prices", "market_stats", "data"),
    ("/export", "market_export", "data"),
    ("/alerts", "market_price_alerts", "alerts"),
    ("/orders", "market_orders", "orders"),
)

_OBSERVATORY_DDL_PG = """
CREATE TABLE IF NOT EXISTS agent_events (
    id TEXT PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    route TEXT,
    country TEXT,
    organization_id TEXT,
    success BOOLEAN NOT NULL,
    latency_ms INTEGER,
    retailer TEXT,
    query_type TEXT,
    error_code TEXT,
    metadata TEXT
);
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    country TEXT,
    organization_id TEXT,
    identity_source TEXT NOT NULL,
    linked_username TEXT,
    metadata TEXT
);
CREATE TABLE IF NOT EXISTS daily_observatory_metrics (
    date DATE PRIMARY KEY,
    unique_agents INTEGER NOT NULL,
    daily_active_agents INTEGER NOT NULL,
    calls_total INTEGER NOT NULL,
    calls_success INTEGER NOT NULL,
    success_rate REAL,
    mcp_retention_7d REAL,
    mcp_retention_30d REAL,
    countries_active INTEGER,
    retailers_queried INTEGER,
    top_tools TEXT,
    top_retailers TEXT,
    top_countries TEXT,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

_OBSERVATORY_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS agent_events (
    id TEXT PRIMARY KEY,
    occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    route TEXT,
    country TEXT,
    organization_id TEXT,
    success INTEGER NOT NULL,
    latency_ms INTEGER,
    retailer TEXT,
    query_type TEXT,
    error_code TEXT,
    metadata TEXT
);
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    country TEXT,
    organization_id TEXT,
    identity_source TEXT NOT NULL,
    linked_username TEXT,
    metadata TEXT
);
CREATE TABLE IF NOT EXISTS daily_observatory_metrics (
    date TEXT PRIMARY KEY,
    unique_agents INTEGER NOT NULL,
    daily_active_agents INTEGER NOT NULL,
    calls_total INTEGER NOT NULL,
    calls_success INTEGER NOT NULL,
    success_rate REAL,
    mcp_retention_7d REAL,
    mcp_retention_30d REAL,
    countries_active INTEGER,
    retailers_queried INTEGER,
    top_tools TEXT,
    top_retailers TEXT,
    top_countries TEXT,
    computed_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def observatory_enabled() -> bool:
    return os.getenv("OBSERVATORY_TELEMETRY", "1").strip().lower() in {"1", "true", "yes", "on"}


def is_noise_agent(agent_id: str | None, username: str | None = None) -> bool:
    for value in (agent_id, username):
        u = (value or "").strip().lower()
        if not u:
            continue
        if u == "admin" or any(u.startswith(p) for p in _NOISE_PREFIXES):
            return True
        if _NOISE_USER_HEX.match(u):
            return True
        if u.startswith("demo_"):
            return True
    return False


def normalize_tool_name(tool_name: str) -> str:
    """Map REST aliases and legacy MCP names to registry canonical names."""
    from market_core.market_mcp_registry import resolve_tool_name

    aliased = _REST_TOOL_ALIASES.get(tool_name, tool_name)
    return resolve_tool_name(aliased) or aliased


def is_internal_tool(tool_name: str | None) -> bool:
    return (tool_name or "") in _INTERNAL_TOOLS


def is_public_telemetry_tool(tool_name: str | None) -> bool:
    return bool(tool_name) and not is_internal_tool(normalize_tool_name(tool_name or ""))


def instrumented_tool_names() -> frozenset[str]:
    from market_core.market_mcp_registry import list_tools

    return frozenset(t["name"] for t in list_tools("default"))


def classify_route(method: str, path: str) -> tuple[str | None, str | None]:
    method = (method or "GET").upper()
    norm = (path or "/").split("?")[0].rstrip("/") or "/"
    if norm in _SKIP_PATHS:
        return None, None
    if norm.startswith("/index/") or any(norm.startswith(p) for p in _SKIP_PREFIXES):
        return None, None
    hit = _EXACT_ROUTES.get((method, norm))
    if hit:
        return normalize_tool_name(hit[0]), hit[1]
    for prefix, tool, qtype in _PREFIX_ROUTES:
        if norm == prefix or norm.startswith(prefix + "/"):
            return normalize_tool_name(tool), qtype
    return None, None


def _country_from_store(store: str | None) -> str | None:
    if not store:
        return None
    try:
        from market_core.market_stores import STORES

        meta = STORES.get(store)
        if meta and meta.get("country"):
            return str(meta["country"]).upper()[:8]
    except Exception:
        pass
    if "-" in store:
        suffix = store.rsplit("-", 1)[-1].upper()
        if len(suffix) == 2 and suffix.isalpha():
            return suffix
    return None


def _extract_geo_retailer(
    *,
    headers: Any,
    query_params: Any,
    body: bytes | None,
) -> tuple[str | None, str | None]:
    """Best-effort retailer/country from headers, query, and JSON body."""
    country = (headers.get("X-Country") or query_params.get("country") or "").strip()
    retailer = (query_params.get("store") or query_params.get("retailer") or "").strip()

    if body:
        try:
            data = json.loads(body)
            if isinstance(data, dict):
                retailer = retailer or str(data.get("store") or data.get("retailer") or "").strip()
                stores = data.get("stores")
                if not retailer and isinstance(stores, list) and stores:
                    retailer = str(stores[0]).strip()
                country = country or str(data.get("country") or "").strip()
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    if retailer and not country:
        country = _country_from_store(retailer) or ""

    return (country[:8] or None), (retailer[:64] or None)


def _sanitize_metadata(meta: dict[str, Any] | None) -> dict[str, Any]:
    if not meta:
        return {}
    return {k: v for k, v in meta.items() if k in _METADATA_ALLOWLIST}


def _fingerprint_agent(client_host: str | None, user_agent: str | None) -> str:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw = f"{client_host or '-'}|{user_agent or '-'}|{day}"
    return "fp_" + hashlib.sha256(raw.encode()).hexdigest()[:24]


def resolve_agent_identity(
    *,
    x_agent_id: str | None = None,
    authorization: str | None = None,
    session_id: str | None = None,
    client_host: str | None = None,
    user_agent: str | None = None,
    auth_user_fn: Callable[[str], str] | None = None,
    api_key_fn: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Resolve stable agent_id with documented priority (PRD §6)."""
    xid = (x_agent_id or "").strip()
    if xid:
        return {
            "agent_id": xid[:128],
            "identity_source": "x_agent_id",
            "linked_username": None,
            "organization_id": None,
            "identity_confidence": "high",
        }

    token = ""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()

    if token.startswith("demo-"):
        return {
            "agent_id": f"demo_{hashlib.sha256(token.encode()).hexdigest()[:20]}",
            "identity_source": "demo",
            "linked_username": None,
            "organization_id": None,
            "identity_confidence": "medium",
        }

    if token and api_key_fn and token.startswith("sk-"):
        key_data = api_key_fn(token)
        if key_data:
            key_id = str(key_data.get("id") or key_data.get("key_id") or "")
            username = (key_data.get("username") or "").strip() or None
            agent_id = f"key_{hashlib.sha256(key_id.encode()).hexdigest()[:20]}" if key_id else f"key_{hashlib.sha256(token.encode()).hexdigest()[:20]}"
            return {
                "agent_id": agent_id,
                "identity_source": "api_key",
                "linked_username": username,
                "organization_id": username,
                "identity_confidence": "high",
            }

    if token and auth_user_fn:
        try:
            username = auth_user_fn(token)
            if username and username != "admin":
                return {
                    "agent_id": f"user_{username}",
                    "identity_source": "username",
                    "linked_username": username,
                    "organization_id": username,
                    "identity_confidence": "high",
                }
        except Exception:
            pass

    sid = (session_id or "").strip()
    if sid:
        return {
            "agent_id": f"session_{hashlib.sha256(sid.encode()).hexdigest()[:20]}",
            "identity_source": "session",
            "linked_username": None,
            "organization_id": None,
            "identity_confidence": "medium",
        }

    fp = _fingerprint_agent(client_host, user_agent)
    return {
        "agent_id": fp,
        "identity_source": "fingerprint",
        "linked_username": None,
        "organization_id": None,
        "identity_confidence": "low",
    }


def ensure_observatory_schema() -> None:
    db = get_db()
    ddl = _OBSERVATORY_DDL_PG if USE_PG else _OBSERVATORY_DDL_SQLITE
    db.executescript(ddl)
    for idx in (
        "CREATE INDEX IF NOT EXISTS idx_agent_events_occurred ON agent_events(occurred_at)",
        "CREATE INDEX IF NOT EXISTS idx_agent_events_agent ON agent_events(agent_id, occurred_at)",
        "CREATE INDEX IF NOT EXISTS idx_agent_events_tool ON agent_events(tool_name, occurred_at)",
    ):
        db.execute(idx)
    db.commit()
    db.close()


def _upsert_agent(
    db: Any,
    *,
    agent_id: str,
    identity_source: str,
    linked_username: str | None,
    organization_id: str | None,
    country: str | None,
    now: str,
) -> None:
    if USE_PG:
        db.execute(
            """
            INSERT INTO agents (agent_id, first_seen_at, last_seen_at, country, organization_id,
                                identity_source, linked_username, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (agent_id) DO UPDATE SET
                last_seen_at = EXCLUDED.last_seen_at,
                country = COALESCE(EXCLUDED.country, agents.country),
                organization_id = COALESCE(EXCLUDED.organization_id, agents.organization_id),
                linked_username = COALESCE(EXCLUDED.linked_username, agents.linked_username)
            """,
            (
                agent_id,
                now,
                now,
                country,
                organization_id,
                identity_source,
                linked_username,
                "{}",
            ),
        )
    else:
        db.execute(
            """
            INSERT INTO agents (agent_id, first_seen_at, last_seen_at, country, organization_id,
                                identity_source, linked_username, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                country = COALESCE(excluded.country, country),
                organization_id = COALESCE(excluded.organization_id, organization_id),
                linked_username = COALESCE(excluded.linked_username, linked_username)
            """,
            (
                agent_id,
                now,
                now,
                country,
                organization_id,
                identity_source,
                linked_username,
                "{}",
            ),
        )


def record_agent_event(
    *,
    agent_id: str,
    tool_name: str,
    success: bool,
    route: str | None = None,
    country: str | None = None,
    organization_id: str | None = None,
    latency_ms: int | None = None,
    retailer: str | None = None,
    query_type: str | None = None,
    error_code: str | None = None,
    identity_source: str = "unknown",
    linked_username: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist one telemetry event. Fail-open for callers."""
    if not observatory_enabled():
        return {"ok": False, "skipped": True, "reason": "disabled"}
    if is_noise_agent(agent_id, linked_username):
        return {"ok": False, "skipped": True, "reason": "noise"}

    tool_name = normalize_tool_name(tool_name)
    if is_internal_tool(tool_name):
        return {"ok": False, "skipped": True, "reason": "internal_tool"}

    ensure_observatory_schema()
    event_id = str(uuid.uuid4())
    now_dt = datetime.now(timezone.utc)
    now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    meta = _sanitize_metadata(metadata)

    try:
        db = get_db()
        _upsert_agent(
            db,
            agent_id=agent_id,
            identity_source=identity_source,
            linked_username=linked_username,
            organization_id=organization_id,
            country=country,
            now=now,
        )
        db.execute(
            """
            INSERT INTO agent_events (
                id, occurred_at, agent_id, tool_name, route, country, organization_id,
                success, latency_ms, retailer, query_type, error_code, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                now,
                agent_id,
                tool_name,
                route,
                country,
                organization_id,
                bool(success),
                latency_ms,
                retailer,
                query_type,
                error_code,
                json.dumps(meta, ensure_ascii=False),
            ),
        )
        db.commit()
        db.close()
        return {"ok": True, "id": event_id}
    except Exception as exc:
        logger.warning("agent_events insert failed (fail-open): %s", exc)
        return {"ok": False, "error": str(exc)}


def _parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text[:19] if "T" not in fmt else text[:19], fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _since_sql(days: int) -> str:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return since.strftime("%Y-%m-%d %H:%M:%S")


MAA_PUBLIC_THRESHOLD = 10


def count_maa(*, days: int = 30, exclude_noise: bool = True) -> int:
    ensure_observatory_schema()
    since = _since_sql(days)
    db = get_db()
    rows = db.execute(
        """
        SELECT DISTINCT agent_id FROM agent_events
        WHERE occurred_at >= ? AND success = ?
        """,
        (since, True),
    ).fetchall()
    db.close()
    agents: set[str] = set()
    for row in rows:
        aid = row.get("agent_id") if isinstance(row, dict) else row["agent_id"]
        if exclude_noise and is_noise_agent(aid):
            continue
        agents.add(aid)
    return len(agents)


def count_maa_proxy(*, days: int = 30) -> int:
    """Proxy when MAA < threshold: distinct API key owners active in window."""
    since = _since_sql(days)
    db = get_db()
    try:
        row = db.execute(
            """
            SELECT COUNT(DISTINCT username) AS n FROM api_keys
            WHERE last_used_at IS NOT NULL AND last_used_at != '' AND last_used_at >= ?
            """,
            (since,),
        ).fetchone()
        n = int(row["n"] or 0) if row else 0
        if n > 0:
            db.close()
            return n
        row2 = db.execute(
            """
            SELECT COUNT(DISTINCT linked_username) AS n FROM agent_events
            WHERE linked_username IS NOT NULL AND linked_username != '' AND occurred_at >= ?
            """,
            (since,),
        ).fetchone()
        db.close()
        return int(row2["n"] or 0) if row2 else 0
    except Exception:
        db.close()
        return 0


def mcp_retention_summary(*, days: int = 30, return_within_days: int = 7) -> dict[str, Any]:
    """Retention from first successful MCP/API call (PRD §5)."""
    ensure_observatory_schema()
    since = _since_sql(days)
    db = get_db()
    rows = db.execute(
        """
        SELECT agent_id, success, occurred_at FROM agent_events
        WHERE occurred_at >= ?
        ORDER BY occurred_at ASC
        """,
        (since,),
    ).fetchall()
    db.close()

    first_success: dict[str, datetime] = {}
    events_by_agent: dict[str, list[datetime]] = {}
    for row in rows:
        aid = row["agent_id"]
        if is_noise_agent(aid):
            continue
        ts = _parse_ts(row["occurred_at"])
        if not ts:
            continue
        events_by_agent.setdefault(aid, []).append(ts)
        if row["success"] and aid not in first_success:
            first_success[aid] = ts

    cohort = 0
    retained = 0
    window = return_within_days
    for aid, day0 in first_success.items():
        cohort += 1
        end = day0 + timedelta(days=window)
        for ts in events_by_agent.get(aid, []):
            if day0 < ts <= end:
                retained += 1
                break

    rate = round(retained / cohort, 4) if cohort else None
    return {
        "window_days": days,
        "return_within_days": return_within_days,
        "cohort_first_success": cohort,
        "retained": retained,
        "retention_rate": rate,
    }


def _weekly_agent_growth(day_agents: dict[str, set[str]]) -> float | None:
    """Week-over-week unique agents (last 7 days vs prior 7)."""
    if not day_agents:
        return None
    sorted_days = sorted(day_agents.keys())
    if len(sorted_days) < 7:
        return None
    last7 = sorted_days[-7:]
    prev_pool = [d for d in sorted_days if d < last7[0]]
    if not prev_pool:
        return None
    prev7 = prev_pool[-7:]
    a = sum(len(day_agents[d]) for d in last7)
    b = sum(len(day_agents[d]) for d in prev7)
    if b <= 0:
        return None
    return round((a - b) / b, 4)


def observatory_summary(*, days: int = 30) -> dict[str, Any]:
    """Public aggregate metrics for /analytics/observatory."""
    days = max(1, min(days, 90))
    ensure_observatory_schema()
    since = _since_sql(days)
    db = get_db()
    rows = db.execute(
        """
        SELECT agent_id, tool_name, country, retailer, success, occurred_at
        FROM agent_events WHERE occurred_at >= ?
        """,
        (since,),
    ).fetchall()
    db.close()

    calls_total = 0
    calls_success = 0
    agents: set[str] = set()
    tools: dict[str, int] = {}
    retailers: dict[str, int] = {}
    countries: dict[str, int] = {}
    day_agents: dict[str, set[str]] = {}

    for row in rows:
        aid = row["agent_id"]
        if is_noise_agent(aid):
            continue
        raw_tool = row["tool_name"] or "unknown"
        tool = normalize_tool_name(raw_tool)
        if is_internal_tool(tool):
            continue
        calls_total += 1
        if row["success"]:
            calls_success += 1
            agents.add(aid)
        tools[tool] = tools.get(tool, 0) + 1
        if row["retailer"]:
            retailers[row["retailer"]] = retailers.get(row["retailer"], 0) + 1
        if row["country"]:
            countries[row["country"]] = countries.get(row["country"], 0) + 1
        ts = _parse_ts(row["occurred_at"])
        if ts and row["success"]:
            day_key = ts.date().isoformat()
            day_agents.setdefault(day_key, set()).add(aid)

    maa = len(agents)
    maa_proxy = count_maa_proxy(days=days)
    telemetry_maturity = "established" if maa >= MAA_PUBLIC_THRESHOLD else "early"
    success_rate = round(calls_success / calls_total, 4) if calls_total else None
    retention_7 = mcp_retention_summary(days=days, return_within_days=7)
    retention_30 = mcp_retention_summary(days=days, return_within_days=30)

    def _top(counter: dict[str, int], n: int = 5) -> list[dict[str, Any]]:
        return [{"name": k, "count": v} for k, v in sorted(counter.items(), key=lambda x: -x[1])[:n]]

    weekly_growth = _weekly_agent_growth(day_agents)

    return {
        "window_days": days,
        "maa": maa,
        "maa_proxy": maa_proxy,
        "maa_display": maa if maa >= MAA_PUBLIC_THRESHOLD else maa_proxy,
        "telemetry_maturity": telemetry_maturity,
        "maa_public_threshold": MAA_PUBLIC_THRESHOLD,
        "unique_agents": maa,
        "calls_total": calls_total,
        "calls_success": calls_success,
        "success_rate": success_rate,
        "countries_active": len(countries),
        "retailers_queried": len(retailers),
        "mcp_retention_7d": retention_7,
        "mcp_retention_30d": retention_30,
        "weekly_agent_growth": weekly_growth,
        "top_tools": _top(tools),
        "top_retailers": _top(retailers),
        "top_countries": _top(countries),
        "telemetry_enabled": observatory_enabled(),
    }


def compute_daily_observatory_metrics(*, day: date | None = None) -> dict[str, Any]:
    """Upsert one daily snapshot row."""
    day = day or date.today()
    ensure_observatory_schema()
    summary = observatory_summary(days=30)
    retention_7 = summary["mcp_retention_7d"].get("retention_rate")
    retention_30 = summary["mcp_retention_30d"].get("retention_rate")
    day_str = day.isoformat()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    day_start = f"{day_str} 00:00:00"
    day_end = f"{day_str} 23:59:59"
    daa_row = db.execute(
        """
        SELECT COUNT(DISTINCT agent_id) AS n FROM agent_events
        WHERE occurred_at >= ? AND occurred_at <= ? AND success = ?
        """,
        (day_start, day_end, True),
    ).fetchone()
    daa = int(daa_row["n"] or 0) if daa_row else 0

    payload = {
        "date": day_str,
        "unique_agents": summary["maa"],
        "daily_active_agents": daa,
        "calls_total": summary["calls_total"],
        "calls_success": summary["calls_success"],
        "success_rate": summary["success_rate"],
        "mcp_retention_7d": retention_7,
        "mcp_retention_30d": retention_30,
        "countries_active": summary["countries_active"],
        "retailers_queried": summary["retailers_queried"],
        "top_tools": json.dumps(summary["top_tools"], ensure_ascii=False),
        "top_retailers": json.dumps(summary["top_retailers"], ensure_ascii=False),
        "top_countries": json.dumps(summary["top_countries"], ensure_ascii=False),
        "computed_at": now,
    }

    if USE_PG:
        db.execute(
            """
            INSERT INTO daily_observatory_metrics (
                date, unique_agents, daily_active_agents, calls_total, calls_success,
                success_rate, mcp_retention_7d, mcp_retention_30d, countries_active,
                retailers_queried, top_tools, top_retailers, top_countries, computed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (date) DO UPDATE SET
                unique_agents = EXCLUDED.unique_agents,
                daily_active_agents = EXCLUDED.daily_active_agents,
                calls_total = EXCLUDED.calls_total,
                calls_success = EXCLUDED.calls_success,
                success_rate = EXCLUDED.success_rate,
                mcp_retention_7d = EXCLUDED.mcp_retention_7d,
                mcp_retention_30d = EXCLUDED.mcp_retention_30d,
                countries_active = EXCLUDED.countries_active,
                retailers_queried = EXCLUDED.retailers_queried,
                top_tools = EXCLUDED.top_tools,
                top_retailers = EXCLUDED.top_retailers,
                top_countries = EXCLUDED.top_countries,
                computed_at = EXCLUDED.computed_at
            """,
            tuple(payload.values()),
        )
    else:
        db.execute(
            """
            INSERT OR REPLACE INTO daily_observatory_metrics (
                date, unique_agents, daily_active_agents, calls_total, calls_success,
                success_rate, mcp_retention_7d, mcp_retention_30d, countries_active,
                retailers_queried, top_tools, top_retailers, top_countries, computed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(payload.values()),
        )
    db.commit()
    db.close()
    return {"ok": True, **payload}


class ObservatoryMiddleware(BaseHTTPMiddleware):
    """HTTP middleware — records instrumented routes (fail-open)."""

    def __init__(
        self,
        app: Any,
        *,
        auth_user_fn: Callable[[str], str] | None = None,
        api_key_fn: Callable[[str], dict[str, Any] | None] | None = None,
    ) -> None:
        super().__init__(app)
        self._auth_user_fn = auth_user_fn
        self._api_key_fn = api_key_fn

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not observatory_enabled():
            return await call_next(request)

        tool_name, query_type = classify_route(request.method, request.url.path)
        if not tool_name:
            return await call_next(request)

        body = b""
        if request.method in {"POST", "PUT", "PATCH"}:
            body = await request.body()

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body, "more_body": False}

        downstream = Request(request.scope, receive) if body else request

        start = time.monotonic()
        response = await call_next(downstream)
        latency_ms = int((time.monotonic() - start) * 1000)
        success = 200 <= response.status_code < 400

        identity = resolve_agent_identity(
            x_agent_id=request.headers.get("X-Agent-ID"),
            authorization=request.headers.get("Authorization"),
            session_id=request.headers.get("X-Session-ID"),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            auth_user_fn=self._auth_user_fn,
            api_key_fn=self._api_key_fn,
        )

        country, retailer = _extract_geo_retailer(
            headers=request.headers,
            query_params=request.query_params,
            body=body,
        )

        import asyncio

        loop = asyncio.get_running_loop()
        loop.run_in_executor(
            None,
            lambda: record_agent_event(
                agent_id=identity["agent_id"],
                tool_name=tool_name,
                success=success,
                route=f"{request.method} {request.url.path}",
                country=country,
                organization_id=identity.get("organization_id"),
                latency_ms=latency_ms,
                retailer=retailer,
                query_type=query_type,
                error_code=str(response.status_code) if not success else None,
                identity_source=identity["identity_source"],
                linked_username=identity.get("linked_username"),
                metadata={"identity_confidence": identity.get("identity_confidence")},
            ),
        )
        return response
