#!/usr/bin/env python3
"""Activate Pro using Railway production env (public DB URL). One-off ops helper."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python ops/_activate_pro_railway.py PRO-XXXXXXXX", file=sys.stderr)
        return 1

    request_id = sys.argv[1].strip().upper()
    if not request_id.startswith("PRO-"):
        request_id = f"PRO-{request_id}"

    railway = "railway.cmd" if sys.platform == "win32" else "railway"
    result = subprocess.run(
        [railway, "variables", "--json"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=60,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return result.returncode

    vars_map = json.loads(result.stdout)
    db_url = vars_map.get("DATABASE_PUBLIC_URL") or vars_map.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_PUBLIC_URL not found in Railway variables", file=sys.stderr)
        return 1

    passthrough = (
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "SMTP_USE_TLS",
        "SLACK_BOT_TOKEN",
        "SLACK_CHANNEL_CLI_MARKET_PRO",
        "SLACK_CHANNEL_FUNNEL",
        "SLACK_SIGNING_SECRET",
        "MARKET_API_TOKEN",
        "MARKET_API_URL",
        "BILLING_NOTIFY_EMAIL",
        "BILLING_FROM_EMAIL",
    )
    for key in passthrough:
        val = vars_map.get(key)
        if val:
            os.environ[key] = str(val).strip()
    os.environ["DATABASE_URL"] = db_url
    if not os.environ.get("SMTP_PASS") and os.environ.get("SMTP_PASSWORD"):
        os.environ["SMTP_PASS"] = os.environ["SMTP_PASSWORD"]
    if not os.environ.get("SMTP_FROM"):
        os.environ["SMTP_FROM"] = (
            os.environ.get("BILLING_FROM_EMAIL") or os.environ.get("SMTP_USER") or ""
        )
    if not os.environ.get("BILLING_NOTIFY_EMAIL"):
        os.environ["BILLING_NOTIFY_EMAIL"] = os.environ.get("SMTP_USER", "")

    activate = ROOT / "ops" / "activate_pro.py"
    extra = sys.argv[2:]
    proc = subprocess.run(
        [sys.executable, str(activate), "--request-id", request_id, *extra],
        cwd=str(ROOT),
        env=os.environ,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())