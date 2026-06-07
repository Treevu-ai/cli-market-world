#!/usr/bin/env python3
"""CLI Market — Go-live check (founder daily ops).

Prints 3 KPIs + alerts. Optionally posts critical/warn alerts to Slack bitácora.

Usage:
  python ops/go_live_check.py
  python ops/go_live_check.py --json
  python ops/go_live_check.py --slack
  python ops/go_live_check.py --days 7

Env:
  DASHBOARD_DATA_URL   — production dashboard JSON (optional; uses local DB if unset)
  MARKET_API_TOKEN     — only needed for remote dashboard fetch via API
  SLACK_BOT_TOKEN      — for --slack
  SLACK_WEBHOOK_BITACORA
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

from market_golive import go_live_markdown, go_live_slack_lines, go_live_summary  # noqa: E402

DASHBOARD_URL = os.getenv(
    "DASHBOARD_DATA_URL",
    "https://cli-market-production.up.railway.app/dashboard/data",
)
API_BASE = os.getenv(
    "MARKET_API_URL",
    DASHBOARD_URL.rsplit("/dashboard/data", 1)[0] or "https://cli-market-production.up.railway.app",
)


def _fetch_dashboard_remote() -> dict | None:
    token = os.getenv("MARKET_API_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = httpx.get(DASHBOARD_URL, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) and "error" not in data else None
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Go-live KPI check")
    parser.add_argument("--days", type=int, default=30, help="Funnel window (1-90)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--slack", action="store_true", help="Post to Slack bitácora if alerts")
    parser.add_argument("--remote", action="store_true", help="Fetch moat KPIs from production API")
    args = parser.parse_args()

    dash = _fetch_dashboard_remote() if args.remote else None
    summary = go_live_summary(days=args.days, dashboard_data=dash)

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(go_live_markdown(days=args.days, dashboard_data=dash))

    if args.slack and summary.get("alerts"):
        actionable = [
            a for a in summary["alerts"] if a["severity"] in ("critical", "warn")
        ]
        if actionable:
            from slack_notify import deliver_to_bitacora

            lines = go_live_slack_lines(days=args.days, dashboard_data=dash)
            deliver_to_bitacora("\n".join(lines))
            print("Slack → bitácora (go-live alerts).", file=sys.stderr)

    return 1 if summary["overall_status"] == "critical" else 0


if __name__ == "__main__":
    raise SystemExit(main())