#!/usr/bin/env python3
"""COL-7 — probe US DTC stores (casper, parachute, brooklinen, alo_yoga).

Hits /v1/sources/health for those four and (optionally) their public homepages
to distinguish WAF vs empty seed vs live catalog.

Usage:
  python3 ops/collector_us_dtc_probe.py
  python3 ops/collector_us_dtc_probe.py --json
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import httpx

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
TARGETS = ("casper", "parachute", "brooklinen", "alo_yoga")
HOMEPAGES = {
    "casper": "https://casper.com",
    "parachute": "https://www.parachutehome.com",
    "brooklinen": "https://www.brooklinen.com",
    "alo_yoga": "https://www.aloyoga.com",
}


def decide(store: dict, http_status: int | None) -> str:
    success = float(store.get("success_pct") or 0)
    fresh = bool(store.get("fresh_24h"))
    if http_status and http_status >= 400:
        return "gha_bypass"
    if success >= 70 and fresh:
        return "keep"
    if 20 <= success < 70 and fresh:
        return "delist_from_gate"
    if success < 20:
        return "fix_seed"
    return "delist_from_gate"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-http", action="store_true")
    args = ap.parse_args()

    headers = {}
    token = os.getenv("MARKET_API_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    health = httpx.get(
        f"{API_BASE.rstrip('/')}/v1/sources/health",
        headers=headers,
        timeout=45.0,
    )
    health.raise_for_status()
    by_id = {s["store"]: s for s in (health.json().get("stores") or [])}

    rows = []
    for sid in TARGETS:
        store = by_id.get(sid, {"store": sid, "missing": True})
        http_status = None
        http_bytes = None
        if not args.skip_http:
            url = HOMEPAGES.get(sid)
            try:
                r = httpx.get(
                    url,
                    timeout=20.0,
                    follow_redirects=True,
                    headers={"User-Agent": "CLI-Market-Collector-Probe/1.0"},
                )
                http_status = r.status_code
                http_bytes = len(r.content or b"")
            except Exception as exc:
                http_status = None
                store = {**store, "http_error": str(exc)[:200]}
        decision = decide(store, http_status)
        rows.append(
            {
                "store": sid,
                "success_pct": store.get("success_pct"),
                "fresh_24h": store.get("fresh_24h"),
                "coverage_7d_pct": store.get("coverage_7d_pct"),
                "state": store.get("state"),
                "http_status": http_status,
                "http_bytes": http_bytes,
                "decision": decision,
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stores": rows,
        "legend": {
            "gha_bypass": "WAF/block from Fly — collect from GHA like nutrition CA/PE",
            "fix_seed": "homepage ok but collector yield low — seed/query",
            "delist_from_gate": "keep in catalog, drop from coverage/gate denominator",
            "keep": "healthy enough for the gate",
        },
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"US DTC probe {report['generated_at']}")
        for row in rows:
            print(
                f"  {row['store']}: success={row['success_pct']} fresh={row['fresh_24h']} "
                f"http={row['http_status']} → {row['decision']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
