#!/usr/bin/env python3
"""Activate Pro tier after manual payment confirmation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

OPS = Path(__file__).resolve().parent
ROOT = OPS.parent
sys.path.insert(0, str(OPS))
sys.path.insert(0, str(ROOT))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

from market_core import (  # noqa: E402
    db_find_subscription_request,
    db_mark_subscription_request_activated,
    db_set_subscription,
    db_update_subscription_request_display_name,
    ensure_db_initialized,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Activate CLI Market Pro after payment")
    p.add_argument("username", nargs="?", help="CLI username (from market login)")
    p.add_argument("--email", help="Lookup latest Pro request by subscriber email")
    p.add_argument("--request-id", dest="request_id", help="Pro request ref (PRO-XXXXXXXX)")
    p.add_argument("--display-name", dest="display_name", help="Friendly name for welcome email")
    args = p.parse_args()

    ensure_db_initialized()

    username = (args.username or "").strip()
    request_id = (args.request_id or "").strip()
    req = None

    if request_id:
        req = db_find_subscription_request(request_id=request_id)
        if not req:
            print(f"✗ Request not found: {request_id}", file=sys.stderr)
            return 1
        if not username:
            username = req["username"]

    if args.email and not username:
        req = db_find_subscription_request(email=args.email)
        if req:
            username = req["username"]
            if not request_id:
                request_id = req["id"]

    if not username:
        p.error("Provide username, --email, or --request-id")

    result = db_set_subscription(username, "pro")
    print(f"✓ Pro activated for {result['username']}")

    try:
        from market_funnel import record_funnel_event

        record_funnel_event(
            "activated",
            username=username,
            meta={"source": "ops_manual", "request_id": request_id or None},
            dedupe=True,
        )
    except Exception:
        pass

    if not request_id and req:
        request_id = req.get("id", "")
    display_override = (args.display_name or "").strip()
    if request_id and display_override:
        if db_update_subscription_request_display_name(request_id, display_override):
            print(f"✓ Display name saved: {display_override}")
            if req:
                req["display_name"] = display_override
    if request_id:
        db_mark_subscription_request_activated(request_id, username)
        print(f"✓ Request {request_id} marked activated")

    customer_email = ""
    if req:
        customer_email = (req.get("email") or "").strip()
    if not customer_email and args.email:
        customer_email = args.email.strip()

    pay_method = "yape"
    if req:
        pay_url = (req.get("payment_link") or "").strip().lower()
        if pay_url.startswith("plin:"):
            pay_method = "plin"
        elif pay_url.startswith("mercadopago"):
            pay_method = "mercadopago"

    if customer_email:
        try:
            from account_service import build_pro_email_context, provision_pro_login_credentials
            from market_connectors.email_outbound import send_pro_activated_email

            login_password = provision_pro_login_credentials(username)
            ctx = build_pro_email_context(
                username,
                email=customer_email,
                password=login_password,
                display_name=display_override or (req.get("display_name") if req else "") or "",
                request_id=request_id,
                lang="es",
                payment_method=pay_method,
            )
            mail = send_pro_activated_email(
                to_email=ctx["email"] or customer_email,
                username=ctx["username"],
                lang=ctx["lang"],
                request_id=ctx["request_id"],
                payment_method=ctx["payment_method"],
                source="ops_manual",
                password=ctx["password"],
                display_name=ctx["display_name"],
            )
            if mail.get("sent"):
                print(f"✓ Activation email sent to {customer_email}")
            if mail.get("gmail_draft"):
                print(f"✓ Gmail draft created for {customer_email}")
            elif mail.get("ops_notified"):
                print("✓ Draft reply sent to hello@cli-market.dev")
            elif not mail.get("sent"):
                print(f"⚠ Email not sent: {mail.get('reason', 'unknown')}", file=sys.stderr)
        except Exception as exc:
            print(f"⚠ Activation email failed: {exc}", file=sys.stderr)

    try:
        from billing_slack import notify_pro_subscription

        notify_pro_subscription(
            status="activated",
            username=username,
            email=customer_email,
            request_id=request_id,
            source="ops_manual",
            payment_method=pay_method,
        )
    except Exception:
        pass

    print("\nNext: ask customer to run `market login` once, then `market` — Pro shows in the top bar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
