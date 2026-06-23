"""Send reminder emails to users with pending Pro subscription requests.

Targets users who requested Pro (have a subscription_request with status=pending)
but haven't completed payment within 24-72 hours.

Usage:
    python ops/pro_payment_reminder.py [--dry-run] [--hours-min 24] [--hours-max 72]

Designed to run as a daily cron/scheduled GitHub Action.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("MARKET_DATA_DIR", "/tmp/market-data")

from market_core import get_db  # noqa: E402

logger = logging.getLogger(__name__)


def find_pending_pro_requests(*, hours_min: int = 24, hours_max: int = 72) -> list[dict]:
    """Find subscription requests that are pending and within the reminder window."""
    db = get_db()
    now = datetime.now(timezone.utc)
    window_start = (now - timedelta(hours=hours_max)).strftime("%Y-%m-%d %H:%M:%S")
    window_end = (now - timedelta(hours=hours_min)).strftime("%Y-%m-%d %H:%M:%S")

    rows = db.execute(
        """
        SELECT id, username, email, payment_link, created_at
        FROM subscription_requests
        WHERE status = 'pending'
          AND id LIKE 'PRO-%'
          AND created_at >= ?
          AND created_at <= ?
        ORDER BY created_at ASC
        """,
        (window_start, window_end),
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]


def send_reminder(request: dict, *, dry_run: bool = False) -> bool:
    """Send a payment reminder email for a pending Pro request."""
    email = (request.get("email") or "").strip()
    username = request.get("username") or ""
    payment_link = request.get("payment_link") or ""
    request_id = request.get("id") or ""

    if not email:
        logger.info("skip %s: no email", request_id)
        return False

    if dry_run:
        logger.info("[DRY-RUN] would email %s (%s) — link: %s", email, request_id, payment_link[:60])
        return True

    try:
        from market_connectors.email_outbound import _send, _smtp_configured
        if not _smtp_configured():
            logger.warning("SMTP not configured — cannot send reminder")
            return False

        subject = "Tu suscripción Pro está pendiente — CLI Market"
        text = (
            f"Hola {username},\n\n"
            "Notamos que iniciaste la suscripción Pro pero no completaste el pago.\n\n"
            f"Completa tu pago aquí: {payment_link}\n\n"
            "Con Pro obtienes:\n"
            "• Consultas ilimitadas\n"
            "• MCP tools completo\n"
            "• Checkout automatizado\n"
            "• Alertas de precio\n\n"
            f"Referencia: {request_id}\n\n"
            "Si tienes dudas, responde a este email.\n\n"
            "— Ricardo · CLI Market\n"
            "hello@cli-market.dev"
        )
        html = (
            "<h2 style='color:#3afecf;'>Tu Pro está pendiente</h2>"
            f"<p>Hola <b>{username}</b>,</p>"
            "<p>Iniciaste la suscripción Pro pero no completaste el pago.</p>"
            f"<p><a href='{payment_link}' style='color:#002118;background:#3afecf;"
            "padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:bold;'>"
            "Completar pago →</a></p>"
            "<p><b>Pro incluye:</b></p>"
            "<ul>"
            "<li>Consultas ilimitadas</li>"
            "<li>MCP tools completo</li>"
            "<li>Checkout automatizado</li>"
            "<li>Alertas de precio</li>"
            "</ul>"
            f"<p><small>Ref: {request_id}</small></p>"
        )
        result = _send(email, subject, text, html)
        return result.get("sent", False)
    except Exception:
        logger.exception("Failed to send reminder to %s", email)
        return False


def notify_slack_summary(sent: int, total: int, dry_run: bool = False) -> None:
    """Post summary to Slack."""
    try:
        from billing_slack import _post_to_slack
        prefix = "[DRY-RUN] " if dry_run else ""
        _post_to_slack(
            f"{prefix}📧 Pro payment reminders: {sent}/{total} emails sent "
            f"(pending requests in 24-72h window)"
        )
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Send Pro payment reminders")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send emails")
    parser.add_argument("--hours-min", type=int, default=24, help="Min hours since request (default 24)")
    parser.add_argument("--hours-max", type=int, default=72, help="Max hours since request (default 72)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    pending = find_pending_pro_requests(hours_min=args.hours_min, hours_max=args.hours_max)
    logger.info("Found %d pending Pro requests in %d-%dh window", len(pending), args.hours_min, args.hours_max)

    if not pending:
        print("No pending Pro requests in reminder window.")
        return 0

    sent = 0
    for req in pending:
        if send_reminder(req, dry_run=args.dry_run):
            sent += 1

    notify_slack_summary(sent, len(pending), dry_run=args.dry_run)
    print(f"Done: {sent}/{len(pending)} reminders {'would be ' if args.dry_run else ''}sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
