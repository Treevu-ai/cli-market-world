#!/usr/bin/env python3
"""COL-5 — weekly probe of circuit_open stores.

Reads GET /v1/sources/health, lists stores in state=circuit_open, and optionally
forces a one-shot catalog pull via collect_prices.py --catalog-store.

Usage:
  python3 ops/collector_circuit_probe.py
  python3 ops/collector_circuit_probe.py --probe-collect   # requires DATABASE_URL
  python3 ops/collector_circuit_probe.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")


def fetch_circuit_open(timeout: float = 45.0) -> list[dict]:
    url = f"{API_BASE.rstrip('/')}/v1/sources/health"
    headers = {}
    token = os.getenv("MARKET_API_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = httpx.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    stores = payload.get("stores") or []
    return [s for s in stores if s.get("state") == "circuit_open"]


def probe_collect(store_id: str) -> dict:
    cmd = [sys.executable, str(ROOT / "collect_prices.py"), "--catalog-store", store_id]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
    return {
        "store": store_id,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-1500:],
        "stderr_tail": (proc.stderr or "")[-800:],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe collector circuit_open stores")
    ap.add_argument("--probe-collect", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    opened = fetch_circuit_open()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api": API_BASE,
        "circuit_open_count": len(opened),
        "stores": [
            {
                "store": s.get("store"),
                "consecutive_failures": s.get("consecutive_failures"),
                "success_pct": s.get("success_pct"),
                "last_success": s.get("last_success"),
                "last_error": s.get("last_error"),
            }
            for s in opened
        ],
        "probes": [],
        "note": (
            "If a probe returns 200+ prices, reset consecutive_failures in store_health "
            "for that store (collector will resume next cycle)."
        ),
    }
    if args.probe_collect:
        for s in opened:
            sid = s.get("store")
            if not sid:
                continue
            report["probes"].append(probe_collect(sid))

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"circuit_open: {report['circuit_open_count']}")
        for s in report["stores"]:
            print(
                f"  {s['store']}: consec={s['consecutive_failures']} "
                f"success={s['success_pct']} last_success={s['last_success']}"
            )
        if not report["stores"]:
            print("  (none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
