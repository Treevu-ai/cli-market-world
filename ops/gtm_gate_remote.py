#!/usr/bin/env python3
"""Remote data-gate check against production /dashboard/data.

Usage:
  python3 ops/gtm_gate_remote.py
  MARKET_API_URL=https://... python3 ops/gtm_gate_remote.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

COVERAGE_THRESHOLD = 80.0


def fetch_dashboard(url_base: str) -> dict:
    url = url_base.rstrip("/") + "/dashboard/data"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode())


def evaluate_gate(data: dict) -> dict:
    moat = data.get("moat_summary") or {}
    kpis = data.get("kpis") or {}
    coverage = float(moat.get("coverage_7d_pct") or kpis.get("coverage_7d_pct") or 0)
    gate_pass = bool(moat.get("marketing_gate_pass"))
    ok = gate_pass and coverage >= COVERAGE_THRESHOLD
    return {
        "ok": ok,
        "marketing_gate_pass": gate_pass,
        "coverage_7d_pct": coverage,
        "threshold_pct": COVERAGE_THRESHOLD,
        "total_indexed": moat.get("total_indexed") or kpis.get("total_indexed"),
        "stores_indexed": moat.get("stores_indexed") or kpis.get("stores_indexed"),
        "generated_at": data.get("generated_at"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Remote GTM data-gate (prod dashboard)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    base = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    try:
        payload = evaluate_gate(fetch_dashboard(base))
    except urllib.error.URLError as exc:
        print(f"gate-remote failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif payload["ok"]:
        print(
            f"gate-remote OK — coverage={payload['coverage_7d_pct']}% "
            f"indexed={payload['total_indexed']}"
        )
    else:
        print(
            f"gate-remote FAIL — marketing_gate_pass={payload['marketing_gate_pass']} "
            f"coverage={payload['coverage_7d_pct']}% (need >={COVERAGE_THRESHOLD}%)",
            file=sys.stderr,
        )

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
