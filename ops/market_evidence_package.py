#!/usr/bin/env python3
"""Market Evidence Package — thin glue for PIT ↔ CLI Market (phases 1–3).

Builds the JSON contract defined in docs/PIT-INTEGRATION.md:
  - --mode mock   → deterministic fixture (no network)
  - --mode live   → assembles package from CLI Market API
  - --merge-ficha → attaches package to a PIT-like ficha stub
  - --write-trace → phase-3 audit receipt (package_id + as_of + pit_run_id)
  - --create-pit-run / --fetch-pit-run → optional PIT API calls when token set

Usage:
  python ops/market_evidence_package.py --mode mock --merge-ficha --write-trace
  python ops/market_evidence_package.py --mode live --query "arandanos" --country PE --pit-run-id demo-run
  python ops/market_evidence_package.py --mode mock --create-pit-run --merge-ficha --write-trace

Env:
  MARKET_API_URL     default https://cli-market-api.fly.dev
  MARKET_API_TOKEN   Bearer token (required for live intel; search may work with free key)
  PIT_API_URL        default https://cli-market-pit-backend.fly.dev
  PIT_API_TOKEN      optional session/API token for PIT research-runs
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]

OPS_DIR = Path(__file__).resolve().parent
ROOT = OPS_DIR.parent
if str(OPS_DIR) not in sys.path:
    sys.path.insert(0, str(OPS_DIR))

from pit_integration.pit_client import DEFAULT_PIT_URL, PitClient  # noqa: E402
from pit_integration.run_metadata import (  # noqa: E402
    build_pit_run_metadata,
    validate_pit_run_metadata,
)
from pit_integration.trace import build_trace_receipt, validate_trace_receipt  # noqa: E402

MOCKS_DIR = OPS_DIR / "pit_integration" / "mocks"
OUT_DIR = OPS_DIR / "generated" / "pit"
SCHEMA_VERSION = "0.1"
DEFAULT_API = "https://cli-market-api.fly.dev"

DEFAULT_DISCLAIMERS = [
    (
        "Inflación y precios observados desde góndola online (retail formal). "
        "No reemplaza IPC oficial (INEI, DANE, INDEC, IBGE, etc.)."
    ),
    (
        "Este paquete no constituye scouting tecnológico ni revisión de literatura."
    ),
]

DEFAULT_CAVEATS = [
    "Retail formal online only; not national CPI.",
    "Not informal market coverage.",
]


# ── Pure package helpers ─────────────────────────────────────────────────────


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_package_id() -> str:
    return f"mep_{uuid.uuid4().hex[:16]}"


def price_summary(assortment: list[dict[str, Any]]) -> dict[str, Any]:
    prices = [
        float(item["price"])
        for item in assortment
        if item.get("price") is not None
    ]
    currencies = {item.get("currency") for item in assortment if item.get("currency")}
    currency = next(iter(currencies), None) if len(currencies) == 1 else (
        "MIXED" if len(currencies) > 1 else None
    )
    if not prices:
        return {
            "currency": currency,
            "min": None,
            "max": None,
            "median": None,
            "n": 0,
            "method": "simple_on_returned_items",
        }
    return {
        "currency": currency,
        "min": round(min(prices), 4),
        "max": round(max(prices), 4),
        "median": round(float(statistics.median(prices)), 4),
        "n": len(prices),
        "method": "simple_on_returned_items",
    }


def build_package(
    query: str,
    country: str,
    *,
    line: str = "supermercados",
    application: str = "functional foods and beverages",
    hs_code: str | None = None,
    pit_run_id: str | None = None,
    request_id: str | None = None,
    assortment: list[dict[str, Any]] | None = None,
    signals: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
    tools_used: list[str] | None = None,
    api_base: str = DEFAULT_API,
    as_of: str | None = None,
    package_id: str | None = None,
    layer: str = "unknown",
    extra_notes: list[str] | None = None,
) -> dict[str, Any]:
    """Assemble a Market Evidence Package dict (schema v0.1)."""
    items = list(assortment or [])
    cov = dict(coverage or {})
    cov.setdefault("retailers_with_price", len({i.get("store") for i in items if i.get("store")}))
    cov.setdefault("items_returned", len(items))
    cov.setdefault("freshness_pct_under_24h", None)
    cov.setdefault("data_confidence", None)
    notes = list(cov.get("notes") or [])
    if extra_notes:
        notes.extend(extra_notes)
    if not items:
        notes.append("No assortment rows; treat as coverage gap, not zero price.")
    cov["notes"] = notes

    package: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "package_id": package_id or new_package_id(),
        "as_of": as_of or utc_now_iso(),
        "generated_by": {
            "system": "cli-market",
            "api_base": api_base.rstrip("/"),
            "tools_used": list(tools_used or []),
        },
        "consumer_ref": {
            "pit_run_id": pit_run_id,
            "request_id": request_id,
        },
        "request": {
            "query": query,
            "country": country.upper(),
            "line": line,
            "application": application,
            "hs_code": hs_code,
            "max_items": max(len(items), 25) if items else 25,
        },
        "coverage": cov,
        "assortment": items,
        "price_summary": price_summary(items),
        "signals": signals if signals is not None else {},
        "quality": {
            "layer": layer,
            "caveats": list(DEFAULT_CAVEATS),
        },
        "citations": {
            "methodology_ref": "docs/methodology.md | docs/PIT-INTEGRATION.md",
            "cite_snippet": (
                f"CLI Market. Shelf prices / shelf inflation — retail formal online. "
                f"Corte: {as_of or 'as_of'}, país: {country.upper()}."
            ),
        },
        "disclaimers": list(DEFAULT_DISCLAIMERS),
    }
    return package


MVP_REQUIRED_TOP = (
    "schema_version",
    "package_id",
    "as_of",
    "generated_by",
    "consumer_ref",
    "request",
    "coverage",
    "assortment",
    "price_summary",
    "quality",
    "disclaimers",
)


def validate_package(package: dict[str, Any]) -> list[str]:
    """Return list of validation errors (empty = OK for MVP)."""
    errors: list[str] = []
    for key in MVP_REQUIRED_TOP:
        if key not in package:
            errors.append(f"missing top-level key: {key}")
    if package.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    req = package.get("request") or {}
    if not req.get("query"):
        errors.append("request.query required")
    if not req.get("country"):
        errors.append("request.country required")
    if not isinstance(package.get("assortment"), list):
        errors.append("assortment must be a list")
    else:
        for i, row in enumerate(package["assortment"]):
            for field in ("name", "store", "price", "currency"):
                if field not in row:
                    errors.append(f"assortment[{i}] missing {field}")
    if not package.get("disclaimers"):
        errors.append("disclaimers must be non-empty")
    quality = package.get("quality") or {}
    if not quality.get("caveats"):
        errors.append("quality.caveats must be non-empty")
    gen = package.get("generated_by") or {}
    if "tools_used" not in gen:
        errors.append("generated_by.tools_used required")
    return errors


def merge_ficha(
    ficha_stub: dict[str, Any],
    package: dict[str, Any],
) -> dict[str, Any]:
    """Thin merge: PIT-like ficha + market evidence block (does not call PIT)."""
    merged = dict(ficha_stub)
    market_block = {
        "source": "cli-market-market-evidence-package",
        "schema_version": package.get("schema_version"),
        "package_id": package.get("package_id"),
        "as_of": package.get("as_of"),
        "country": (package.get("request") or {}).get("country"),
        "query": (package.get("request") or {}).get("query"),
        "price_summary": package.get("price_summary"),
        "coverage": package.get("coverage"),
        "assortment_sample": (package.get("assortment") or [])[:10],
        "signals": package.get("signals") or {},
        "disclaimers": package.get("disclaimers") or [],
        "citations": package.get("citations") or {},
    }
    merged["market_evidence"] = market_block
    merged["market_evidence_package_id"] = package.get("package_id")
    # Narrative helpers for agents / PDF glue
    ps = package.get("price_summary") or {}
    n = ps.get("n") or 0
    if n:
        merged["market_headline"] = (
            f"Góndola {market_block['country']}: n={n}, "
            f"min={ps.get('min')} max={ps.get('max')} median={ps.get('median')} "
            f"{ps.get('currency') or ''}".strip()
        )
    else:
        merged["market_headline"] = (
            f"Sin cobertura de precios en góndola para "
            f"{market_block.get('query')!r} / {market_block.get('country')}"
        )
    return merged


def ficha_to_markdown(merged: dict[str, Any]) -> str:
    """Human-readable ficha for demos (science stub + market evidence)."""
    me = merged.get("market_evidence") or {}
    lines = [
        "# Ficha de oportunidad (merge delgado)",
        "",
        f"**Segmento:** {merged.get('segment', '—')}",
        f"**Etapa:** {merged.get('stage', '—')}",
        f"**Market label:** {merged.get('market_label', '—')}",
        f"**PIT run (ref):** {merged.get('pit_run_id', '—')}",
        f"**Headline mercado:** {merged.get('market_headline', '—')}",
        "",
        "## Evidencia científica / tech (stub PIT)",
        "",
        merged.get("science_summary")
        or "_No hay report PIT en este merge; rellenar desde research-run._",
        "",
        "## Evidencia de mercado (CLI Market)",
        "",
        f"- Package: `{me.get('package_id')}`",
        f"- as_of: `{me.get('as_of')}`",
        f"- País / query: `{me.get('country')}` / `{me.get('query')}`",
        f"- Price summary: `{json.dumps(me.get('price_summary'), ensure_ascii=False)}`",
        f"- Cobertura: `{json.dumps(me.get('coverage'), ensure_ascii=False)}`",
        "",
        "### Muestra de surtido",
        "",
    ]
    sample = me.get("assortment_sample") or []
    if not sample:
        lines.append("_Sin ítems._")
    else:
        lines.append("| Producto | Tienda | Precio | Moneda |")
        lines.append("|---|---|---:|---|")
        for row in sample:
            lines.append(
                f"| {row.get('name', '')} | {row.get('store', '')} | "
                f"{row.get('price', '')} | {row.get('currency', '')} |"
            )
    trace = merged.get("trace") or {}
    if trace:
        lines.extend(
            [
                "",
                "### Trazabilidad (fase 3)",
                "",
                f"- package_id: `{trace.get('package_id')}`",
                f"- as_of: `{trace.get('as_of')}`",
                f"- pit_run_id: `{trace.get('pit_run_id')}`",
            ]
        )
    lines.extend(["", "### Disclaimers", ""])
    for d in me.get("disclaimers") or []:
        lines.append(f"- {d}")
    lines.append("")
    return "\n".join(lines)


# ── Mock fixtures ────────────────────────────────────────────────────────────


def load_mock_package(
    query: str | None = None,
    country: str | None = None,
    pit_run_id: str | None = None,
) -> dict[str, Any]:
    path = MOCKS_DIR / "market_evidence_package.example.json"
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if query:
            data.setdefault("request", {})["query"] = query
        if country:
            data.setdefault("request", {})["country"] = country.upper()
        if pit_run_id is not None:
            data.setdefault("consumer_ref", {})["pit_run_id"] = pit_run_id
        data["as_of"] = utc_now_iso()
        data["package_id"] = new_package_id()
        return data

    # Fallback if fixture missing
    return build_package(
        query=query or "arandanos blueberries",
        country=country or "PE",
        pit_run_id=pit_run_id,
        assortment=[
            {
                "product_id": "mock-wong-1",
                "name": "Arándanos bandeja 125g",
                "brand": "Mock",
                "store": "wong",
                "country": "PE",
                "price": 9.9,
                "currency": "PEN",
                "unit": "125g",
                "url": None,
                "observed_at": utc_now_iso(),
            }
        ],
        tools_used=["mock"],
        layer="mock",
        signals={"intel_brief_headline": "Mock package (fixture missing)"},
    )


def load_mock_ficha_stub(pit_run_id: str | None = None) -> dict[str, Any]:
    path = MOCKS_DIR / "pit_ficha_stub.example.json"
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if pit_run_id:
            data["pit_run_id"] = pit_run_id
        return data
    return {
        "pit_run_id": pit_run_id or "mock-run-local",
        "segment": "exportadores y retail premium",
        "stage": "concepto",
        "market_label": "PE functional beverages",
        "science_summary": (
            "Stub: evidencia científica vendría del research-run / report de PIT "
            "(literatura, application, enrich domains)."
        ),
        "hypothesis": "Bebida funcional a base de arándano viable en retail premium PE.",
    }


# ── Live API assembly ────────────────────────────────────────────────────────


def _auth_headers(token: str) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _normalize_product(raw: dict[str, Any], country: str) -> dict[str, Any] | None:
    name = raw.get("name") or raw.get("title") or raw.get("product_name")
    price = raw.get("price")
    if price is None and isinstance(raw.get("prices"), dict):
        price = raw["prices"].get("current") or raw["prices"].get("value")
    store = (
        raw.get("store")
        or raw.get("retailer")
        or raw.get("store_id")
        or raw.get("source")
    )
    currency = raw.get("currency") or raw.get("currency_code") or "PEN"
    if name is None or price is None or store is None:
        return None
    try:
        price_f = float(price)
    except (TypeError, ValueError):
        return None
    return {
        "product_id": str(raw.get("product_id") or raw.get("id") or ""),
        "name": str(name),
        "brand": raw.get("brand"),
        "store": str(store),
        "country": country.upper(),
        "price": price_f,
        "currency": str(currency),
        "unit": raw.get("unit") or raw.get("size"),
        "url": raw.get("url") or raw.get("product_url"),
        "observed_at": raw.get("observed_at") or raw.get("updated_at") or raw.get("timestamp"),
    }


def _extract_products(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("products", "results", "items", "data"):
        val = payload.get(key)
        if isinstance(val, list):
            return [p for p in val if isinstance(p, dict)]
        if isinstance(val, dict) and isinstance(val.get("products"), list):
            return [p for p in val["products"] if isinstance(p, dict)]
    return []


def fetch_live_package(
    query: str,
    country: str,
    *,
    line: str = "supermercados",
    application: str = "functional foods and beverages",
    hs_code: str | None = None,
    pit_run_id: str | None = None,
    limit: int = 25,
    api_url: str | None = None,
    token: str | None = None,
    timeout: float = 45.0,
) -> dict[str, Any]:
    if httpx is None:
        raise RuntimeError("httpx is required for --mode live (pip install httpx)")

    base = (api_url or os.getenv("MARKET_API_URL") or DEFAULT_API).rstrip("/")
    tok = token if token is not None else os.getenv("MARKET_API_TOKEN", "")
    headers = _auth_headers(tok)
    tools_used: list[str] = []
    notes: list[str] = []
    signals: dict[str, Any] = {}
    assortment: list[dict[str, Any]] = []

    with httpx.Client(base_url=base, headers=headers, timeout=timeout) as client:
        # Search
        try:
            r = client.post(
                "/products/search",
                json={
                    "query": query,
                    "country": country.upper(),
                    "line": line,
                    "limit": limit,
                },
            )
            tools_used.append("POST /products/search")
            if r.status_code == 200:
                for raw in _extract_products(r.json()):
                    row = _normalize_product(raw, country)
                    if row:
                        assortment.append(row)
            else:
                notes.append(f"search HTTP {r.status_code}: {r.text[:200]}")
        except Exception as exc:  # noqa: BLE001 — surface in package notes
            notes.append(f"search error: {exc}")

        # Compare as fallback / enrichment if search empty
        if not assortment:
            try:
                r = client.post(
                    "/products/compare",
                    json={
                        "query": query,
                        "country": country.upper(),
                        "line": line,
                        "limit": limit,
                    },
                )
                tools_used.append("POST /products/compare")
                if r.status_code == 200:
                    for raw in _extract_products(r.json()):
                        row = _normalize_product(raw, country)
                        if row:
                            assortment.append(row)
                else:
                    notes.append(f"compare HTTP {r.status_code}: {r.text[:200]}")
            except Exception as exc:  # noqa: BLE001
                notes.append(f"compare error: {exc}")

        # Intel brief
        try:
            r = client.get(
                "/v1/intel/brief",
                params={"country": country.upper(), "line": line},
            )
            tools_used.append("GET /v1/intel/brief")
            if r.status_code == 200:
                brief = r.json()
                signals["intel_brief_headline"] = (
                    brief.get("headline")
                    or brief.get("summary")
                    or (brief.get("brief") or {}).get("headline")
                )
                signals["intel_brief"] = brief
            else:
                notes.append(f"intel/brief HTTP {r.status_code}")
                signals["intel_brief"] = {"error": r.status_code, "detail": r.text[:300]}
        except Exception as exc:  # noqa: BLE001
            notes.append(f"intel/brief error: {exc}")

        # Scores
        try:
            r = client.get(
                "/v1/intel/scores",
                params={"country": country.upper()},
            )
            tools_used.append("GET /v1/intel/scores")
            if r.status_code == 200:
                signals["scores"] = r.json()
            else:
                notes.append(f"intel/scores HTTP {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"intel/scores error: {exc}")

        # Inflation (best-effort)
        try:
            r = client.get(
                "/v1/intel/inflation",
                params={"country": country.upper(), "line": line},
            )
            tools_used.append("GET /v1/intel/inflation")
            if r.status_code == 200:
                signals["inflation"] = r.json()
            else:
                notes.append(f"intel/inflation HTTP {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"intel/inflation error: {exc}")

    layer = "clean" if assortment else "unknown"
    if not tok:
        notes.append("No MARKET_API_TOKEN; intel endpoints may return 401.")

    return build_package(
        query=query,
        country=country,
        line=line,
        application=application,
        hs_code=hs_code,
        pit_run_id=pit_run_id,
        assortment=assortment[:limit],
        signals=signals,
        tools_used=tools_used,
        api_base=base,
        layer=layer,
        extra_notes=notes,
        coverage={
            "retailers_with_price": len({i.get("store") for i in assortment if i.get("store")}),
            "items_returned": len(assortment[:limit]),
            "freshness_pct_under_24h": None,
            "data_confidence": None,
            "notes": [],
        },
    )


# ── CLI ──────────────────────────────────────────────────────────────────────


def _write_outputs(
    package: dict[str, Any],
    merge: bool,
    pit_run_id: str | None,
    out_dir: Path,
    *,
    write_trace: bool = False,
    mode: str = "mock",
    pit_api_base: str | None = None,
    pit_create_status: dict[str, Any] | None = None,
    pit_fetch_status: dict[str, Any] | None = None,
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    pkg_path = out_dir / "last-market-evidence-package.json"
    pkg_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["package"] = pkg_path

    if merge:
        stub = load_mock_ficha_stub(pit_run_id or (package.get("consumer_ref") or {}).get("pit_run_id"))
        merged = merge_ficha(stub, package)
        # Phase-3: embed audit pointer on merged ficha
        merged["trace"] = {
            "package_id": package.get("package_id"),
            "as_of": package.get("as_of"),
            "pit_run_id": pit_run_id or (package.get("consumer_ref") or {}).get("pit_run_id"),
        }
        merged_path = out_dir / "last-ficha-merged.json"
        md_path = out_dir / "last-ficha-merged.md"
        merged_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_path.write_text(ficha_to_markdown(merged), encoding="utf-8")
        paths["ficha_json"] = merged_path
        paths["ficha_md"] = md_path

    receipt: dict[str, Any] | None = None
    if write_trace:
        artifact_paths = {k: str(v) for k, v in paths.items()}
        receipt = build_trace_receipt(
            package,
            pit_run_id=pit_run_id,
            pit_api_base=pit_api_base,
            mode=mode,
            artifact_paths=artifact_paths,
            pit_create_status=pit_create_status,
            pit_fetch_status=pit_fetch_status,
        )
        terrors = validate_trace_receipt(receipt)
        if terrors:
            raise ValueError("invalid trace receipt: " + "; ".join(terrors))
        trace_path = out_dir / "last-trace-receipt.json"
        trace_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["trace"] = trace_path

    # Always write run metadata when we have a package (sidecar for PIT persistence)
    if write_trace or pit_run_id or merge:
        meta = build_pit_run_metadata(
            package,
            pit_run_id=pit_run_id,
            trace_id=(receipt or {}).get("trace_id") if receipt else None,
            mode=mode,
        )
        merrors = validate_pit_run_metadata(meta)
        if merrors:
            raise ValueError("invalid run metadata: " + "; ".join(merrors))
        meta_path = out_dir / "last-pit-run-metadata.json"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["run_metadata"] = meta_path

    return paths


def _maybe_talk_to_pit(
    *,
    create_run: bool,
    fetch_run: bool,
    pit_run_id: str | None,
    query: str,
    country: str,
    application: str,
    hs_code: str | None,
    pit_url: str | None,
    pit_token: str | None,
    limit: int,
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None, str]:
    """Optional PIT API side effects. Returns (run_id, create_status, fetch_status, base_url)."""
    base = (pit_url or os.getenv("PIT_API_URL") or DEFAULT_PIT_URL).rstrip("/")
    if not create_run and not fetch_run:
        return pit_run_id, None, None, base

    client = PitClient(base_url=base, token=pit_token)
    create_status: dict[str, Any] | None = None
    fetch_status: dict[str, Any] | None = None
    run_id = pit_run_id

    if create_run:
        create_status = client.create_research_run(
            query,
            target_market=country,
            application=application,
            limit=min(limit, 25),
            hs_code=hs_code,
            full=bool(hs_code),
        )
        extracted = PitClient.extract_run_id(create_status)
        if extracted:
            run_id = extracted
        # Always record health/agents for ops diagnostics
        create_status = {
            **create_status,
            "health": client.health(),
            "agents": client.agents_status(),
        }

    if fetch_run and run_id:
        fetch_status = client.get_research_run(run_id)
    elif fetch_run and not run_id:
        fetch_status = {
            "ok": False,
            "status_code": None,
            "body": {"error": "no pit_run_id to fetch"},
        }

    return run_id, create_status, fetch_status, base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Market Evidence Package for PIT integration")
    parser.add_argument("--mode", choices=("mock", "live"), default="mock")
    parser.add_argument("--query", default="arandanos blueberries")
    parser.add_argument("--country", default="PE")
    parser.add_argument("--line", default="supermercados")
    parser.add_argument("--application", default="functional foods and beverages")
    parser.add_argument("--hs-code", default=None)
    parser.add_argument("--pit-run-id", default=None)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--merge-ficha", action="store_true", help="Merge with PIT ficha stub")
    parser.add_argument(
        "--write-trace",
        action="store_true",
        help="Write phase-3 last-trace-receipt.json (package_id + as_of + pit_run_id)",
    )
    parser.add_argument(
        "--create-pit-run",
        action="store_true",
        help="POST /v1/research-runs on PIT (requires auth; records status even on 401)",
    )
    parser.add_argument(
        "--fetch-pit-run",
        action="store_true",
        help="GET /v1/research-runs/{id} when pit_run_id is known",
    )
    parser.add_argument("--pit-url", default=None, help="Override PIT_API_URL")
    parser.add_argument("--pit-token", default=None, help="Override PIT_API_TOKEN")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--print", dest="do_print", action="store_true", help="Print package JSON to stdout")
    args = parser.parse_args(argv)

    pit_run_id = args.pit_run_id
    pit_create_status = None
    pit_fetch_status = None
    pit_base = (args.pit_url or os.getenv("PIT_API_URL") or DEFAULT_PIT_URL).rstrip("/")

    if args.create_pit_run or args.fetch_pit_run:
        pit_run_id, pit_create_status, pit_fetch_status, pit_base = _maybe_talk_to_pit(
            create_run=args.create_pit_run,
            fetch_run=args.fetch_pit_run,
            pit_run_id=pit_run_id,
            query=args.query,
            country=args.country,
            application=args.application,
            hs_code=args.hs_code,
            pit_url=args.pit_url,
            pit_token=args.pit_token,
            limit=args.limit,
        )
        if pit_run_id:
            print(f"pit_run_id={pit_run_id}")
        if pit_create_status is not None:
            print(
                f"pit_create status={pit_create_status.get('status_code')} "
                f"ok={pit_create_status.get('ok')}"
            )
        if pit_fetch_status is not None:
            print(
                f"pit_fetch status={pit_fetch_status.get('status_code')} "
                f"ok={pit_fetch_status.get('ok')}"
            )

    if args.mode == "mock":
        package = load_mock_package(
            query=args.query,
            country=args.country,
            pit_run_id=pit_run_id,
        )
        # Re-validate after overrides
        package = build_package(
            query=package["request"]["query"],
            country=package["request"]["country"],
            line=package["request"].get("line", args.line),
            application=package["request"].get("application", args.application),
            hs_code=package["request"].get("hs_code") or args.hs_code,
            pit_run_id=(package.get("consumer_ref") or {}).get("pit_run_id") or pit_run_id,
            assortment=package.get("assortment") or [],
            signals=package.get("signals") or {},
            coverage=package.get("coverage"),
            tools_used=package.get("generated_by", {}).get("tools_used") or ["mock"],
            api_base=package.get("generated_by", {}).get("api_base") or DEFAULT_API,
            as_of=package.get("as_of"),
            package_id=package.get("package_id"),
            layer=(package.get("quality") or {}).get("layer") or "mock",
        )
    else:
        package = fetch_live_package(
            query=args.query,
            country=args.country,
            line=args.line,
            application=args.application,
            hs_code=args.hs_code,
            pit_run_id=pit_run_id,
            limit=args.limit,
            api_url=args.api_url,
            token=args.token,
        )

    errors = validate_package(package)
    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    # Auto-trace when merge or explicit pit_run_id or PIT calls
    write_trace = bool(
        args.write_trace
        or args.merge_ficha
        or pit_run_id
        or args.create_pit_run
        or args.fetch_pit_run
    )

    try:
        paths = _write_outputs(
            package,
            merge=args.merge_ficha,
            pit_run_id=pit_run_id or (package.get("consumer_ref") or {}).get("pit_run_id"),
            out_dir=args.out_dir,
            write_trace=write_trace,
            mode=args.mode,
            pit_api_base=pit_base,
            pit_create_status=pit_create_status,
            pit_fetch_status=pit_fetch_status,
        )
    except ValueError as exc:
        print(f"TRACE ERROR: {exc}", file=sys.stderr)
        return 3

    print(f"package_id={package['package_id']}")
    print(f"mode={args.mode} country={package['request']['country']} query={package['request']['query']!r}")
    print(f"items={package['price_summary']['n']} retailers={package['coverage'].get('retailers_with_price')}")
    for label, path in paths.items():
        print(f"wrote {label}: {path}")

    if args.do_print:
        print(json.dumps(package, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
