#!/usr/bin/env python3
"""COL-6 — classify catalog stores missing from the last collector cycle.

Buckets: in_cycle | skipped_cb | no_seeds | growth_deferred | waf_gha_only | inactive | unknown

Usage:
  python3 ops/collector_catalog_diff.py
  python3 ops/collector_catalog_diff.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
WAF_GHA_ONLY = frozenset({"smartnutrition_pe", "simplynaturalcanada_ca"})
CB_SKIP = int(os.getenv("CB_PERSIST_SKIP", "10"))


def _get(path: str) -> dict | list:
    url = f"{API_BASE.rstrip('/')}{path}"
    headers = {}
    token = os.getenv("MARKET_API_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = httpx.get(url, headers=headers, timeout=60.0)
    resp.raise_for_status()
    return resp.json()


def classify() -> dict:
    from market_core import STORES

    catalog = sorted(STORES.keys())
    health = _get("/v1/sources/health")
    collector = _get("/health/collector")
    by_health = {s["store"]: s for s in (health.get("stores") or [])}
    attempted = int(collector.get("stores_attempted") or 0)
    buckets: dict[str, str] = {}
    for sid in catalog:
        row = by_health.get(sid) or {}
        consec = int(row.get("consecutive_failures") or 0)
        if sid in WAF_GHA_ONLY:
            buckets[sid] = "waf_gha_only"
        elif consec >= CB_SKIP or row.get("state") == "circuit_open":
            buckets[sid] = "skipped_cb"
        elif row.get("state") == "dead" and not row.get("last_success"):
            buckets[sid] = "inactive"
        elif row.get("fresh_24h") or (row.get("coverage_7d_pct") or 0) > 0:
            buckets[sid] = "in_cycle"
        elif row.get("last_success"):
            buckets[sid] = "growth_deferred"
        else:
            buckets[sid] = "unknown"
    counts = dict(Counter(buckets.values()))
    counts["catalog_total"] = len(catalog)
    counts["collector_attempted"] = attempted
    by_class: dict[str, list[str]] = {}
    for sid, klass in buckets.items():
        by_class.setdefault(klass, []).append(sid)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
        "classes": {k: sorted(v) for k, v in by_class.items()},
        "sum_ok": sum(len(v) for v in by_class.values()) == len(catalog),
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Collector catalog gap",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "| class | n |",
        "|---|---:|",
    ]
    counts = report["counts"]
    for k, n in sorted(counts.items()):
        lines.append(f"| `{k}` | {n} |")
    lines += ["", f"sum_ok: **{report['sum_ok']}**", ""]
    for klass, ids in sorted(report["classes"].items()):
        preview = ", ".join(ids[:12])
        extra = f" … +{len(ids)-12}" if len(ids) > 12 else ""
        lines.append(f"- **{klass}** ({len(ids)}): {preview}{extra}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = classify()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(to_markdown(report))
    return 0 if report.get("sum_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
