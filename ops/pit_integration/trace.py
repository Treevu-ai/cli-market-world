"""Phase 3 — cross-system audit receipt (pit_run_id ↔ market package as_of)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


TRACE_SCHEMA_VERSION = "0.1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_trace_id() -> str:
    return f"trc_{uuid.uuid4().hex[:16]}"


def build_trace_receipt(
    package: dict[str, Any],
    *,
    pit_run_id: str | None = None,
    pit_api_base: str | None = None,
    mode: str = "mock",
    artifact_paths: dict[str, str] | None = None,
    pit_create_status: dict[str, Any] | None = None,
    pit_fetch_status: dict[str, Any] | None = None,
    trace_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build an audit receipt linking a Market Evidence Package to a PIT run.

    This is the CLI Market side of phase-3 traceability. PIT may store the same
    ``package_id`` / ``as_of`` on the research-run metadata when its API allows.
    """
    req = package.get("request") or {}
    consumer = package.get("consumer_ref") or {}
    run_id = pit_run_id or consumer.get("pit_run_id")
    package_id = package.get("package_id")
    as_of = package.get("as_of")
    gen = package.get("generated_by") or {}

    audit = (
        f"Este precio salió de este corte: package_id={package_id} "
        f"as_of={as_of} pit_run_id={run_id or 'null'}"
    )

    receipt: dict[str, Any] = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "trace_id": trace_id or new_trace_id(),
        "created_at": created_at or utc_now_iso(),
        "mode": mode,
        "pit_run_id": run_id,
        "package_id": package_id,
        "as_of": as_of,
        "market_api_base": gen.get("api_base"),
        "pit_api_base": pit_api_base,
        "request": {
            "query": req.get("query"),
            "country": req.get("country"),
            "line": req.get("line"),
            "application": req.get("application"),
            "hs_code": req.get("hs_code"),
        },
        "price_summary": package.get("price_summary") or {},
        "coverage": {
            "retailers_with_price": (package.get("coverage") or {}).get("retailers_with_price"),
            "items_returned": (package.get("coverage") or {}).get("items_returned"),
        },
        "artifacts": dict(artifact_paths or {}),
        "pit": {
            "create": pit_create_status,
            "fetch": pit_fetch_status,
        },
        "audit_statement": audit,
        "disclaimers": list(package.get("disclaimers") or []),
    }
    return receipt


def validate_trace_receipt(receipt: dict[str, Any]) -> list[str]:
    """Return validation errors (empty = OK)."""
    errors: list[str] = []
    for key in (
        "schema_version",
        "trace_id",
        "created_at",
        "package_id",
        "as_of",
        "audit_statement",
    ):
        if not receipt.get(key):
            errors.append(f"missing or empty: {key}")
    if receipt.get("schema_version") != TRACE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {TRACE_SCHEMA_VERSION!r}")
    return errors
