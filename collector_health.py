"""Collector SLA + catalog identity helpers (no FastAPI / DB imports)."""

from __future__ import annotations

import os
from datetime import datetime, timezone

WAF_GHA_ONLY_STORES = ("smartnutrition_pe", "simplynaturalcanada_ca")

# COL-7: US DTC without a working collector (probe 2026-08-24). Stay in catalog
# as future connectors; exclude from dashboard / data-gate coverage denominator.
GATE_DELIST_STORES = frozenset({"casper", "parachute", "brooklinen"})
GATE_WATCH_STORES = frozenset({"alo_yoga"})


def filter_gate_denominator(store_ids):
    """Active-catalog IDs that count toward coverage / freshness / health %. """
    return [s for s in store_ids if s not in GATE_DELIST_STORES]

CB_PERSIST_SKIP_DEFAULT = 10


def _age_hours(timestamp_str: str | datetime | None) -> float | None:
    if timestamp_str is None:
        return None
    if isinstance(timestamp_str, datetime):
        dt = timestamp_str
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    if not timestamp_str:
        return None
    try:
        s = str(timestamp_str).replace("Z", "+00:00")
        if " " in s and "T" not in s:
            s = s.replace(" ", "T", 1)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return None


def circuit_skip_threshold() -> int:
    try:
        return max(1, int(os.getenv("CB_PERSIST_SKIP", str(CB_PERSIST_SKIP_DEFAULT))))
    except (TypeError, ValueError):
        return CB_PERSIST_SKIP_DEFAULT


def derive_collector_status(**kwargs) -> tuple[str, float | None]:
    """ok | empty | degraded | stale | dead | running | unknown."""
    finished_at = kwargs.get("finished_at", kwargs.get("finished_at"))
    prices_collected = kwargs.get("prices_collected", kwargs.get("prices_collected"))
    moat_age_h = kwargs.get("moat_age_h", kwargs.get("moat_age_h"))
    if finished_at is None:
        return "running", None
    age_h = _age_hours(finished_at)
    if age_h is None:
        return "unknown", None
    collected = int(prices_collected or 0)
    if age_h > 24 or (moat_age_h is not None and moat_age_h >= 24):
        return "dead", age_h
    if age_h > 8 or (moat_age_h is not None and moat_age_h >= 8):
        return "stale", age_h
    if age_h > 5 or (moat_age_h is not None and moat_age_h >= 6):
        return "degraded", age_h
    if collected > 0:
        return "ok", age_h
    return "empty", age_h


def build_collector_catalog_identity(
    *,
    catalog_ids: list[str] | tuple[str, ...],
    attempted: int,
    succeeded: int,
    circuit_open: list[str],
    inactive: list[str],
    waf_gha_only: list[str] | tuple[str, ...] = WAF_GHA_ONLY_STORES,
) -> dict:
    """COL-3: total = attempted + skipped_circuit + inactive + unclassified."""
    total = len(catalog_ids)
    skipped_circuit = len(circuit_open)
    inactive_n = len(inactive)
    unclassified = max(0, total - int(attempted or 0) - skipped_circuit - inactive_n)
    return {
        "total": total,
        "attempted": int(attempted or 0),
        "succeeded": int(succeeded or 0),
        "skipped_circuit": skipped_circuit,
        "inactive": inactive_n,
        "unclassified": unclassified,
        "identity_ok": (
            int(attempted or 0) + skipped_circuit + inactive_n + unclassified == total
        ),
        "circuit_open": list(circuit_open),
        "waf_gha_only": [s for s in waf_gha_only if s in set(catalog_ids)],
        "inactive_ids": list(inactive),
    }
