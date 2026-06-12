#!/usr/bin/env python3
"""Trigger nightly moat indicator refresh on production API.

Usage:
  python ops/indicators_daily.py
  python ops/indicators_daily.py --country PE
  python ops/indicators_daily.py --json

Env:
  MARKET_API_URL     — default https://cli-market-production.up.railway.app
  MARKET_API_TOKEN   — admin bearer (required)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env

load_repo_env()

BASE = os.getenv("MARKET_API_URL", "https://cli-market-production.up.railway.app").rstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh moat indicators on production API")
    parser.add_argument("--country", help="Single country code (default: all active countries)")
    parser.add_argument("--json", action="store_true", help="Print JSON response")
    args = parser.parse_args()

    token = (os.getenv("MARKET_API_TOKEN") or "").strip()
    if not token:
        print("FAIL: MARKET_API_TOKEN not set", file=sys.stderr)
        return 1

    params = {}
    if args.country:
        params["country"] = args.country.upper()

    r = httpx.post(
        f"{BASE}/admin/cron/indicators-refresh",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=300,
    )
    if r.status_code != 200:
        print(f"FAIL: HTTP {r.status_code} {r.text[:500]}", file=sys.stderr)
        return 1

    payload = r.json()
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        phase2 = payload.get("phase2_written", payload.get("per_country", {}))
        print(f"OK — phase2_written={phase2} countries={payload.get('countries', args.country or 'all')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
