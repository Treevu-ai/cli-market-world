"""COL-1/2/4 overlay so world can ship observability before the core pin bumps.

Idempotent if cli-market-core already computed circuit_open / COALESCE freshness.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

_DEFAULT_CB_PERSIST_SKIP = 10


def circuit_skip_threshold() -> int:
    try:
        return max(1, int(os.getenv("CB_PERSIST_SKIP", str(_DEFAULT_CB_PERSIST_SKIP))))
    except (TypeError, ValueError):
        return _DEFAULT_CB_PERSIST_SKIP


def _age_hours(timestamp, now: datetime | None = None) -> float | None:
    _now = now or datetime.now(timezone.utc)
    if timestamp is None:
        return None
    if isinstance(timestamp, datetime):
        dt = timestamp
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (_now - dt).total_seconds() / 3600
    if not timestamp:
        return None
    try:
        s = str(timestamp).replace("Z", "+00:00")
        if " " in s and "T" not in s:
            s = s.replace(" ", "T", 1)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (_now - dt).total_seconds() / 3600
    except Exception:
        return None


def _first(store: dict, *keys):
    for key in keys:
        if key in store and store[key] is not None:
            return store[key]
    return None


def apply_sources_health_overlay(payload: dict, *, now: datetime | None = None) -> dict:
    """Patch /v1/sources/health payload for COL-1, COL-2, COL-4."""
    if not payload or not isinstance(payload, dict):
        return payload
    skip = circuit_skip_threshold()
    stores = payload.get("stores") or []
    now = now or datetime.now(timezone.utc)
    for store in stores:
        coverage = _first(store, "coverage_7d_pct", "coverage_7d_pct") or 0.0
        store["coverage_7d_pct"] = coverage
        store["coverage_7d_pct"] = coverage
        store["store_day_hit_rate_7d_pct"] = coverage
        store["store_day_hit_rate_7d_pct"] = coverage

        consec = int(_first(store, "consecutive_failures", "consecutive_failures") or 0)
        if consec >= skip:
            store["state"] = "circuit_open"

        already_fresh = bool(_first(store, "fresh_24h", "fresh_24h"))
        if not already_fresh:
            age_seen = _age_hours(_first(store, "last_seen", "last_seen"), now)
            age_ok = _age_hours(_first(store, "last_success", "last_success"), now)
            fresh = (age_seen is not None and age_seen < 24) or (
                age_ok is not None and age_ok < 24
            )
            store["fresh_24h"] = fresh
            store["fresh_24h"] = fresh

    summary = {"ok": 0, "partial": 0, "dead": 0, "circuit_open": 0, "total": len(stores)}
    any_data = 0
    for store in stores:
        state = store.get("state") or "dead"
        if state not in summary:
            summary[state] = 0
        summary[state] += 1
        if store.get("fresh_24h") or store.get("fresh_24h") or (store.get("coverage_7d_pct") or 0) > 0:
            any_data += 1
    n = summary["total"]
    summary["coverage_7d_any_data_pct"] = round(any_data / n * 100, 1) if n else 0.0
    payload["summary"] = summary
    payload["circuit_skip"] = skip
    return payload
