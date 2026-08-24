#!/usr/bin/env python3
"""COL-11 — verify price_history (or snapshots) for WAF-bypass GHA stores.

Stores: smartnutrition_pe, simplynaturalcanada_ca (workflow collect-egress-blocked-stores).

Usage:
  python3 ops/verify_waf_price_history.py
  python3 ops/verify_waf_price_history.py --json
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import httpx

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
STORES = ("smartnutrition_pe", "simplynaturalcanada_ca")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
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
    ok = True
    for sid in STORES:
        s = by_id.get(sid) or {}
        has_history = bool(s.get("last_seen") or s.get("coverage_7d_pct"))
        fresh = bool(s.get("fresh_24h"))
        row = {
            "store": sid,
            "found": sid in by_id,
            "fresh_24h": fresh,
            "coverage_7d_pct": s.get("coverage_7d_pct"),
            "last_seen": s.get("last_seen"),
            "last_success": s.get("last_success"),
            "history_present": has_history,
        }
        if not has_history:
            ok = False
        rows.append(row)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": ok,
        "stores": rows,
        "action_if_empty": "re-run collect-egress-blocked-stores.yml and confirm collect_prices writes price_history",
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WAF history check:", "OK" if ok else "MISSING HISTORY")
        for r in rows:
            print(
                f"  {r['store']}: history={r['history_present']} "
                f"fresh={r['fresh_24h']} cov7={r['coverage_7d_pct']}"
            )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
