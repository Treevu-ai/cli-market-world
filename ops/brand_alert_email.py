#!/usr/bin/env python3
"""Email brand owners when a registered SKU deviates >10% from its PVP.

Requires DATABASE_URL (prod Postgres) and SMTP_* for delivery.

Reuses routers.brand_intel.compute_brand_alerts() so the email path can't
drift from the GET /v1/brand-monitor/alerts endpoint's own logic — this
script only adds the >10% email threshold and the delivery/scheduling glue
around it (the endpoint itself flags anything above +5% or below -15%).

No cross-run dedup/cooldown yet: the daily cron cadence is the only spam
mitigation for now. Revisit with per-SKU suppression if this gets noisy
during the pilot.

Usage:
    python ops/brand_alert_email.py --dry-run
    python ops/brand_alert_email.py
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EMAIL_THRESHOLD_PCT = 10.0


def _mask_email(email: str) -> str:
    """Redact for CI logs — never print a usable address or api_key there."""
    user, _, domain = email.partition("@")
    return f"{user[:2]}***@{domain}" if domain else "***"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brand Intelligence PVP-deviation email alerts")
    parser.add_argument(
        "--threshold", type=float, default=EMAIL_THRESHOLD_PCT,
        help=f"Absolute deviation %% required to email (default {EMAIL_THRESHOLD_PCT})",
    )
    parser.add_argument("--dry-run", action="store_true", help="List targets without sending")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    if not os.getenv("DATABASE_URL", "").strip():
        msg = "DATABASE_URL not set — skipping brand alert emails"
        if args.json:
            print(json.dumps({"skipped": True, "reason": msg}))
        else:
            print(msg, file=sys.stderr)
        return 0

    from market_core import db_get_user_email, ensure_db_initialized, get_db
    from market_connectors.email_outbound import _send
    from routers.brand_intel import compute_brand_alerts

    ensure_db_initialized()

    db = get_db()
    try:
        rows = db.execute(
            "SELECT DISTINCT api_key, brand_slug FROM brand_intel_config"
        ).fetchall()
    except Exception:
        rows = []
    db.close()

    sent = 0
    skipped = 0
    results: list[dict] = []

    for row in rows:
        r = dict(row)
        api_key, brand_slug = r["api_key"], r["brand_slug"]

        db = get_db()
        alerts_data = compute_brand_alerts(db, api_key, brand_slug)
        db.close()

        alerts = [
            a for a in alerts_data.get("alerts", [])
            if abs(a.get("pvp_deviation_pct", 0)) > args.threshold
        ]
        if not alerts:
            continue

        email = db_get_user_email(api_key)
        if not email:
            skipped += 1
            # Never print the raw api_key (it's a live bearer credential) — CI logs
            # (GitHub Actions) retain stdout, and this is a usable secret otherwise.
            results.append({"brand_slug": brand_slug, "status": "skipped_no_email", "count": len(alerts)})
            continue

        if args.dry_run:
            results.append({"brand_slug": brand_slug, "email": _mask_email(email), "status": "dry_run", "count": len(alerts)})
            continue

        subject = f"[CLI Market Brand Intel] {len(alerts)} desvío(s) de PVP en {brand_slug}"
        lines = [f"Se detectaron {len(alerts)} SKU(s) de '{brand_slug}' con desvío > {args.threshold}% vs el PVP registrado:\n"]
        for a in alerts:
            lines.append(
                f"- {a['name']} ({a['store_name']}): S/ {a['price']} vs PVP S/ {a['pvp_suggested']} "
                f"({a['pvp_deviation_pct']:+.1f}%, {a['pvp_alert']})"
            )
        text = "\n".join(lines)
        html_body = "<pre>" + html.escape(text) + "</pre>"

        outcome = _send(email, subject, text, html_body)
        if outcome.get("sent"):
            sent += 1
            results.append({"brand_slug": brand_slug, "email": _mask_email(email), "status": "sent", "count": len(alerts)})
        else:
            results.append({"brand_slug": brand_slug, "email": _mask_email(email), "status": "failed", "reason": outcome.get("reason"), "count": len(alerts)})

    summary = {
        "brands_checked": len(rows),
        "sent": sent,
        "skipped_no_email": skipped,
        "dry_run": args.dry_run,
        "threshold_pct": args.threshold,
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"brand alert emails: brands_checked={len(rows)} sent={sent} "
            f"skipped_no_email={skipped} dry_run={args.dry_run}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
