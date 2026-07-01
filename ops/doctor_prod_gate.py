#!/usr/bin/env python3
"""Production gate aligned with `market doctor` critical checks (CI smoke)."""
from __future__ import annotations

import os
import sys

import httpx

API = os.environ.get("MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")
MIN_SNAPSHOTS = int(os.environ.get("DOCTOR_MIN_SNAPSHOTS", "1000"))
MIN_LINKAGE_PCT = float(os.environ.get("DOCTOR_MIN_LINKAGE_PCT", "50"))
MAX_DEAD_SOURCES = int(os.environ.get("DOCTOR_MAX_DEAD_SOURCES", "0"))


def run_gate() -> list[str]:
    errors: list[str] = []

    with httpx.Client(timeout=45) as client:
        try:
            r = client.get(f"{API}/health/db")
            if r.status_code != 200:
                errors.append(f"API health/db: HTTP {r.status_code}")
            else:
                snaps = int(r.json().get("snapshots") or 0)
                if snaps < MIN_SNAPSHOTS:
                    errors.append(f"API health/db: snapshots {snaps} < {MIN_SNAPSHOTS}")
        except Exception as exc:
            errors.append(f"API health/db: {exc}")

        try:
            r = client.get(f"{API}/v1/sources/health")
            if r.status_code != 200:
                errors.append(f"Sources health: HTTP {r.status_code}")
            else:
                body = r.json()
                if body.get("error"):
                    errors.append(f"Sources health: {body['error']}")
                else:
                    sm = body.get("summary") or {}
                    dead = int(sm.get("dead") or 0)
                    ok_n = int(sm.get("ok") or 0)
                    print(f"Sources health: {ok_n} ok · {dead} dead")
                    if dead > MAX_DEAD_SOURCES:
                        errors.append(f"Sources health: {dead} dead stores (max {MAX_DEAD_SOURCES})")
        except Exception as exc:
            errors.append(f"Sources health: {exc}")

        try:
            r = client.get(f"{API}/health/stats")
            if r.status_code != 200:
                errors.append(f"Golden linkage (/health/stats): HTTP {r.status_code}")
            else:
                body = r.json()
                linkage = body.get("golden_linkage_pct", body.get("linkage_pct"))
                if linkage is None:
                    errors.append("Golden linkage: missing golden_linkage_pct")
                else:
                    pct = float(linkage)
                    print(f"Golden linkage: {pct:.1f}%")
                    if pct < MIN_LINKAGE_PCT:
                        errors.append(f"Golden linkage: {pct:.1f}% < {MIN_LINKAGE_PCT}%")
        except Exception as exc:
            errors.append(f"Golden linkage: {exc}")

    return errors


def main() -> int:
    print(f"-> Doctor prod gate ({API})")
    errors = run_gate()
    if errors:
        for msg in errors:
            print(f"FAIL: {msg}", file=sys.stderr)
        return 1
    print("OK: Doctor prod gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
