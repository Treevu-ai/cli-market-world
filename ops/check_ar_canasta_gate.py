#!/usr/bin/env python3
"""Check AR canasta LinkedIn gate against live dashboard/data.

Exit 0 when Carrefour, Jumbo and Vea AR each have >= min_items/10 in canasta_basica.
Prints suggested LinkedIn [X]% when gate passes.

Usage:
  python3 ops/check_ar_canasta_gate.py
  python3 ops/check_ar_canasta_gate.py --watch --interval 300
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request

DEFAULT_URL = "https://cli-market-production.up.railway.app/dashboard/data"
TRIO = ("Carrefour", "Jumbo", "Vea")


def fetch_dashboard(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def find_ar_row(canasta: list[dict], label: str) -> dict | None:
    key = label.lower()
    for row in canasta:
        name = (row.get("store_name") or "").lower()
        if key in name and "ar" in name:
            return row
    return None


def evaluate(data: dict, *, min_items: int = 6) -> dict:
    canasta = data.get("canasta_basica") or []
    rows = {label: find_ar_row(canasta, label) for label in TRIO}
    checks = []
    for label, row in rows.items():
        if not row:
            checks.append({"store": f"{label} AR", "status": "missing", "items": 0, "total": None})
        else:
            items = int(row.get("items") or 0)
            checks.append({
                "store": row.get("store_name") or f"{label} AR",
                "status": "pass" if items >= min_items else "fail",
                "items": items,
                "total": row.get("total"),
                "currency": row.get("currency"),
            })
    gate_pass = all(c["status"] == "pass" for c in checks)
    x_pct = None
    x_copy = None
    if gate_pass:
        ordered = sorted(
            (c for c in checks if c["total"] is not None),
            key=lambda c: float(c["total"]),
        )
        lo, hi = ordered[0], ordered[-1]
        if float(lo["total"]) > 0:
            x_pct = round((float(hi["total"]) - float(lo["total"])) / float(lo["total"]) * 100)
            x_copy = (
                f"{x_pct}% ({lo['store']} {lo['currency']} {float(lo['total']):,.0f} "
                f"→ {hi['store']} {hi['currency']} {float(hi['total']):,.0f})"
            )
    marketing_ars = [
        m for m in (data.get("marketing_spreads") or [])
        if m.get("currency") == "ARS"
    ]
    return {
        "generated_at": data.get("generated_at"),
        "min_items": min_items,
        "checks": checks,
        "gate_pass": gate_pass,
        "linkedin_x_pct": x_pct,
        "linkedin_x_copy": x_copy,
        "marketing_ars": marketing_ars,
        "suspect_discounts": len(data.get("suspect_discounts") or []),
    }


def print_report(report: dict) -> None:
    print("=== AR CANASTA GATE ===")
    print(f"generated_at: {report['generated_at']}")
    print(f"required: {report['min_items']}/10 per store")
    for c in report["checks"]:
        if c["status"] == "missing":
            print(f"  [MISSING] {c['store']}")
        elif c["status"] == "pass":
            print(f"  [PASS] {c['store']}: {c['items']}/10 · {c['currency']} {float(c['total']):,.0f}")
        else:
            print(f"  [FAIL] {c['store']}: {c['items']}/10 · {c['currency']} {float(c['total']):,.0f}")
    print(f"\nGATE: {'✅ PASSED — OK to fill LinkedIn [X]' if report['gate_pass'] else '❌ BLOCKED — do not publish Day-09-AR'}")
    if report["linkedin_x_copy"]:
        print(f"\nSuggested [X]: {report['linkedin_x_copy']}")
    if report["marketing_ars"]:
        print("\nmarketing_spreads ARS (per-item, not canasta total):")
        for m in report["marketing_ars"]:
            print(f"  {m.get('seed')}: {m.get('spread_ratio')}x · {m.get('stores')} stores")
    print(f"\nsuspect_discounts: {report['suspect_discounts']} (QA only; excluded from top_discounts)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AR canasta LinkedIn publish gate")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--min-items", type=int, default=6)
    parser.add_argument("--watch", action="store_true", help="Poll until gate passes")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between polls (default 300)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    while True:
        try:
            data = fetch_dashboard(args.url)
            report = evaluate(data, min_items=args.min_items)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            if not args.watch:
                return 2
            time.sleep(args.interval)
            continue

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report(report)

        if report["gate_pass"]:
            return 0
        if not args.watch:
            return 1
        print(f"\nWaiting {args.interval}s… (Ctrl+C to stop)\n")
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
