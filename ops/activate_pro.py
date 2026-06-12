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
    db_set_subscription,
    db_update_subscription_request_display_name,
    ensure_db_initialized,
)


def _print_activation_actions(actions: list[str]) -> int:
    if any(a.startswith("pro_activated:") for a in actions):
        username = next(a.split(":", 1)[1] for a in actions if a.startswith("pro_activated:"))
        print(f"✓ Pro activated for {username}")
    elif any(a.startswith("already_activated:") for a in actions):
        print(f"✗ Already activated: {actions[0]}", file=sys.stderr)
        return 1
    elif any(a.startswith("payment_not_manual:") for a in actions):
        print(
            "✗ Refuses to activate: payment is PayPal/Mercado Pago — wait for webhook "
            "or pass --force after manual verification.",
            file=sys.stderr,
        )
        return 1
    elif any(a.startswith("request_not_found:") for a in actions):
        print(f"✗ {actions[0]}", file=sys.stderr)
        return 1
    else:
        print(f"✗ Activation failed: {', '.join(actions)}", file=sys.stderr)
        return 1

    for action in actions:
        if action.startswith("request_closed:"):
            print(f"✓ Request {action.split(':', 1)[1]} marked activated")
        elif action.startswith("activation_email:"):
            print(f"✓ Activation email sent to {action.split(':', 1)[1]}")
        elif action.startswith("activation_draft_notify:"):
            print("✓ Draft reply sent to hello@cli-market.dev")
        elif action.startswith("activation_email_skipped:"):
            print(f"⚠ Email not sent: {action.split(':', 1)[1]}", file=sys.stderr)
        elif action == "activation_email_failed":
            print("⚠ Activation email failed", file=sys.stderr)
    return 0


def _activate_username_only(
    username: str,
    *,
    customer_email: str,
    request_id: str,
    display_name: str,
    pay_method: str,
) -> int:
    """Activate Pro without a PRO- billing request (comps / legacy ops)."""
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

    actions: list[str] = [f"pro_activated:{username}"]
    if customer_email:
        from routers.payments import _append_pro_activation_email_actions

        _append_pro_activation_email_actions(
            actions,
            username=username,
            email=customer_email,
            request_id=request_id,
            payment_method=pay_method,
            source="ops_manual",
            display_name=display_name,
        )
        for action in actions:
            if action.startswith("activation_email:"):
                print(f"✓ Activation email sent to {action.split(':', 1)[1]}")
            elif action.startswith("activation_draft_notify:"):
                print("✓ Draft reply sent to hello@cli-market.dev")
            elif action.startswith("activation_email_skipped:"):
                print(f"⚠ Email not sent: {action.split(':', 1)[1]}", file=sys.stderr)
            elif action == "activation_email_failed":
                print("⚠ Activation email failed", file=sys.stderr)

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

    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Activate CLI Market Pro after payment")
    p.add_argument("username", nargs="?", help="CLI username (from market login)")
    p.add_argument("--email", help="Lookup latest Pro request by subscriber email")
    p.add_argument("--request-id", dest="request_id", help="Pro request ref (PRO-XXXXXXXX)")
    p.add_argument("--display-name", dest="display_name", help="Friendly name for welcome email")
    p.add_argument(
        "--force",
        action="store_true",
        help="Override manual-payment guard (PayPal/MP requests — ops only)",
    )
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

    display_override = (args.display_name or "").strip()
    if request_id:
        if display_override:
            if db_update_subscription_request_display_name(request_id, display_override):
                print(f"✓ Display name saved: {display_override}")
                if req:
                    req["display_name"] = display_override

        from routers.payments import _activate_pro_from_request

        actions = _activate_pro_from_request(
            request_id,
            source="ops_manual",
            force=args.force,
        )
        code = _print_activation_actions(actions)
        if code == 0:
            print("\nNext: ask customer to run `market login` once, then `market` — Pro shows in the top bar.")
        return code

    customer_email = ""
    if req:
        customer_email = (req.get("email") or "").strip()
    if not customer_email and args.email:
        customer_email = args.email.strip()

    pay_method = "yape"
    if req:
        from routers.payments import _pro_payment_method_from_request

        pay_method = _pro_payment_method_from_request(req)
    elif customer_email:
        pay_method = "yape"

    code = _activate_username_only(
        username,
        customer_email=customer_email,
        request_id=request_id,
        display_name=display_override or (req.get("display_name") if req else "") or "",
        pay_method=pay_method,
    )
    if code == 0:
        print("\nNext: ask customer to run `market login` once, then `market` — Pro shows in the top bar.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
