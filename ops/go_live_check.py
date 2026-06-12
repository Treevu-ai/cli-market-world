#!/usr/bin/env python3
"""CLI Market — Go-live check (founder daily ops).

Prints 3 KPIs + alerts. Optionally posts critical/warn alerts to Slack bitácora.

Usage:
  python ops/go_live_check.py
  python ops/go_live_check.py --json
  python ops/go_live_check.py --slack
  python ops/go_live_check.py --days 7
  python ops/go_live_check.py --spike
  python ops/go_live_check.py --spike --json

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

from load_env import load_repo_env  # noqa: E402

load_repo_env()

from market_golive import (  # noqa: E402
    go_live_markdown,
    go_live_slack_lines,
    go_live_spike_markdown,
    go_live_summary,
)

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
    parser.add_argument("--days", type=int, default=None, help="Funnel window (1-90)")
    parser.add_argument("--spike", action="store_true", help="Spike D+7 report (default 7d window)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--slack", action="store_true", help="Post to Slack bitácora if alerts")
    parser.add_argument("--remote", action="store_true", help="Fetch moat KPIs from production API")
    args = parser.parse_args()

    days = args.days if args.days is not None else (7 if args.spike else 30)
    dash = _fetch_dashboard_remote() if args.remote else None
    summary = go_live_summary(days=days, dashboard_data=dash)

    if args.remote:
        try:
            pr = httpx.get(f"{API_BASE}/paypal-status", timeout=15)
            if pr.status_code == 200:
                ps = pr.json()
                summary["paypal"] = ps
                alerts = summary.setdefault("alerts", [])
                if not ps.get("configured"):
                    alerts.append(
                        {
                            "severity": "warn",
                            "code": "paypal_not_configured",
                            "message": "PayPal no configurado en prod — ver docs/ops/GO-LIVE-CHECKOUT.md",
                        }
                    )
                elif ps.get("sandbox"):
                    alerts.append(
                        {
                            "severity": "warn",
                            "code": "paypal_sandbox_mode",
                            "message": "PayPal en sandbox — go-live pendiente (PAYPAL_SANDBOX=false)",
                        }
                    )
                elif not ps.get("webhook_configured"):
                    alerts.append(
                        {
                            "severity": "warn",
                            "code": "paypal_webhook_missing",
                            "message": "PAYPAL_WEBHOOK_ID vacío — auto-activación Pro no funcionará",
                        }
                    )
        except Exception:
            pass

    if args.remote:
        try:
            token = os.getenv("MARKET_API_TOKEN", "")
            if token:
                sr = httpx.get(
                    f"{API_BASE}/admin/observatory/streak",
                    params={"days": 7},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=20,
                )
                if sr.status_code == 200:
                    streak = sr.json()
                    summary["observatory_streak"] = streak
                    if not streak.get("ok"):
                        summary.setdefault("alerts", []).append(
                            {
                                "severity": "warn",
                                "code": "observatory_streak",
                                "message": (
                                    f"Observatory snapshots {streak.get('snapshots_found')}/"
                                    f"{streak.get('target')} — meta 7d consecutivos (PRD §13)"
                                ),
                            }
                        )
        except Exception:
            pass

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    elif args.spike:
        print(go_live_spike_markdown(days=days, dashboard_data=dash))
    else:
        print(go_live_markdown(days=days, dashboard_data=dash))

    if args.slack and summary.get("alerts"):
        actionable = [
            a for a in summary["alerts"] if a["severity"] in ("critical", "warn")
        ]
        if actionable:
            from slack_notify import deliver_to_bitacora

            lines = go_live_slack_lines(days=days, dashboard_data=dash)
            deliver_to_bitacora("\n".join(lines))
            print("Slack → bitácora (go-live alerts).", file=sys.stderr)

    return 1 if summary["overall_status"] == "critical" else 0


if __name__ == "__main__":
    raise SystemExit(main())