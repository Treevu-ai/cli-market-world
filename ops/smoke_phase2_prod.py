#!/usr/bin/env python3
"""Smoke Phase 2 indicators on production API."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env

load_repo_env()

PHASE2_KEYS = [
    "commodity_input_pressure",
    "real_wage_basket_ratio",
    "ipp_food_co",
    "gtrends_search_momentum",
    "bcrp_shelf_gap",
    "commodity_transmission_lag",
]

BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")


def _token() -> str:
    # Fly.io secrets can't be read back via CLI (unlike Railway) — export it directly.
    return (os.getenv("MARKET_API_TOKEN") or "").strip()


def main() -> int:
    token = _token()
    if not token:
        print("FAIL: MARKET_API_TOKEN not set")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.get(f"{BASE}/v1/intel/indicators", headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"FAIL: GET /v1/intel/indicators -> {r.status_code} {r.text[:200]}")
        return 1

    data = r.json()
    catalog = data if isinstance(data, list) else data.get("catalog") or data.get("indicators") or []
    if isinstance(catalog, dict):
        keys = list(catalog.keys())
        by_key = catalog
    else:
        keys = [row.get("key") or row.get("id") for row in catalog]
        by_key = {(row.get("key") or row.get("id")): row for row in catalog}

    print(f"catalog_count: {len(keys)}")
    if len(keys) < 44:
        print(f"WARN: expected >=44 indicator definitions, got {len(keys)}")

    missing = [k for k in PHASE2_KEYS if k not in keys]
    if missing:
        print(f"FAIL: missing Phase 2 keys: {missing}")
        return 1

    print("Phase 2 keys present: OK")
    for key in PHASE2_KEYS:
        detail = httpx.get(
            f"{BASE}/v1/intel/indicators/{key}",
            headers=headers,
            timeout=30,
        )
        if detail.status_code != 200:
            print(f"  {key}: FAIL status={detail.status_code}")
            continue
        row = detail.json()
        val = row.get("value") if isinstance(row, dict) else None
        status = row.get("status") if isinstance(row, dict) else None
        source = row.get("source") if isinstance(row, dict) else None
        print(f"  {key}: value={val} status={status} source={source}")

    meta = by_key.get("commodity_input_pressure") if isinstance(by_key, dict) else None
    if isinstance(meta, dict) and meta.get("name"):
        print(f"sample_meta: {meta.get('key')} / {meta.get('name')}")

    print("PASS: Phase 2 smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
