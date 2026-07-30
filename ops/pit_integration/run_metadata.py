"""Phase 3b — payload that should be stored on a PIT research-run.

CLI Market produces this document. PIT should accept and persist it (today
OpenAPI has no free-form metadata field on ResearchRunCreate; until then we
write ``last-pit-run-metadata.json`` as the contract + local audit sidecar).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


METADATA_SCHEMA_VERSION = "0.1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_pit_run_metadata(
    package: dict[str, Any],
    *,
    pit_run_id: str | None = None,
    trace_id: str | None = None,
    mode: str = "mock",
) -> dict[str, Any]:
    """Build the market_evidence_ref block for a PIT research-run.

    Intended storage (PIT-side, when API allows)::

        research_run.metadata.market_evidence_ref = <this payload>
        # or top-level field market_evidence_ref on the run document
    """
    req = package.get("request") or {}
    consumer = package.get("consumer_ref") or {}
    run_id = pit_run_id or consumer.get("pit_run_id")
    package_id = package.get("package_id")
    as_of = package.get("as_of")
    gen = package.get("generated_by") or {}
    price = package.get("price_summary") or {}
    coverage = package.get("coverage") or {}

    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "kind": "cli_market.market_evidence_ref",
        "created_at": utc_now_iso(),
        "mode": mode,
        "pit_run_id": run_id,
        "trace_id": trace_id,
        "package_id": package_id,
        "as_of": as_of,
        "market_api_base": gen.get("api_base"),
        "request": {
            "query": req.get("query"),
            "country": req.get("country"),
            "line": req.get("line"),
            "application": req.get("application"),
            "hs_code": req.get("hs_code"),
        },
        "price_summary": {
            "currency": price.get("currency"),
            "min": price.get("min"),
            "max": price.get("max"),
            "median": price.get("median"),
            "n": price.get("n"),
        },
        "coverage": {
            "retailers_with_price": coverage.get("retailers_with_price"),
            "items_returned": coverage.get("items_returned"),
        },
        "audit_statement": (
            f"Este precio salió de este corte: package_id={package_id} "
            f"as_of={as_of} pit_run_id={run_id or 'null'}"
        ),
        "disclaimers": list(package.get("disclaimers") or []),
        "pit_api_note": (
            "PIT OpenAPI v0.1.0 has no metadata field on ResearchRunCreate. "
            "Persist this object on the run when the API adds "
            "market_evidence_ref or metadata.cli_market support."
        ),
    }


def validate_pit_run_metadata(meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "kind", "package_id", "as_of", "audit_statement"):
        if not meta.get(key):
            errors.append(f"missing or empty: {key}")
    if meta.get("schema_version") != METADATA_SCHEMA_VERSION:
        errors.append(f"schema_version must be {METADATA_SCHEMA_VERSION!r}")
    if meta.get("kind") != "cli_market.market_evidence_ref":
        errors.append("kind must be cli_market.market_evidence_ref")
    return errors


def proposed_research_run_create_extension(
    query: str,
    *,
    target_market: str,
    application: str,
    market_evidence_ref: dict[str, Any],
    hs_code: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    """Illustrative body for a future PIT API that accepts market_evidence_ref."""
    body: dict[str, Any] = {
        "query": query,
        "target_market": target_market.upper(),
        "application": application,
        "from_publication_date": "2021-01-01",
        "limit": limit,
        "market_evidence_ref": market_evidence_ref,
    }
    if hs_code:
        body["hs_code"] = hs_code
    return body
