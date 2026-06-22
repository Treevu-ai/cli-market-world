#!/usr/bin/env python3
"""Email users whose session access token expires within 7 days (P1-D).

Requires DATABASE_URL (prod Postgres) and SMTP_* for delivery.

Usage:
    python ops/auth_token_expiry_reminder.py --dry-run
    python ops/auth_token_expiry_reminder.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Session token expiry email reminders")
    parser.add_argument("--days", type=int, default=7, help="Window before expiry (default 7)")
    parser.add_argument("--dry-run", action="store_true", help="List targets without sending")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    if not os.getenv("DATABASE_URL", "").strip():
        msg = "DATABASE_URL not set — skipping prod reminders"
        if args.json:
            print(json.dumps({"skipped": True, "reason": msg}))
        else:
            print(msg, file=sys.stderr)
        return 0

    from market_core import db_get_user_email, ensure_db_initialized
    from market_core.auth_tokens import list_sessions_expiring_within, mark_expiry_reminder_sent
    from market_connectors.email_outbound import send_session_expiry_reminder

    ensure_db_initialized()

    pending = list_sessions_expiring_within(days=args.days)
    sent = 0
    skipped = 0
    results: list[dict] = []

    for row in pending:
        username = row["username"]
        email = db_get_user_email(username)
        if not email:
            skipped += 1
            results.append({**row, "status": "skipped_no_email"})
            continue
        if args.dry_run:
            results.append({**row, "email": email, "status": "dry_run"})
            continue
        outcome = send_session_expiry_reminder(
            to_email=email,
            username=username,
            expires_at=row["expires_at"],
            days_remaining=row["days_remaining"],
        )
        if outcome.get("sent"):
            mark_expiry_reminder_sent(username)
            sent += 1
            results.append({**row, "email": email, "status": "sent"})
        else:
            results.append({**row, "email": email, "status": "failed", "reason": outcome.get("reason")})

    summary = {
        "pending": len(pending),
        "sent": sent,
        "skipped_no_email": skipped,
        "dry_run": args.dry_run,
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"token expiry reminders: pending={len(pending)} sent={sent} "
            f"skipped_no_email={skipped} dry_run={args.dry_run}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
