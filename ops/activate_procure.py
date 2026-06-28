#!/usr/bin/env python3
"""Activate Procure tier after manual payment confirmation (PCS-/PCP-/PCB-)."""

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
    db_update_subscription_request_display_name,
    ensure_db_initialized,
)
from routers.billing.activation import _is_procure_subscription_request_id  # noqa: E402


def _print_activation_actions(actions: list[str]) -> int:
    activated = [a for a in actions if "_activated:" in a and not a.startswith("already_")]
    if activated:
        tier, username = activated[0].split("_activated:", 1)
        print(f"✓ {tier} activated for {username}")
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
        elif action.startswith("procure_magic_email:"):
            print(f"✓ Procure activation email sent to {action.split(':', 1)[1]}")
        elif action.startswith("activation_email_skipped:"):
            print(f"⚠ Email not sent: {action.split(':', 1)[1]}", file=sys.stderr)
        elif action == "activation_email_failed":
            print("⚠ Activation email failed", file=sys.stderr)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Activate Procure Copilot after manual payment")
    p.add_argument("request_id", nargs="?", help="Payment ref (PCS-/PCP-/PCB-XXXXXXXX)")
    p.add_argument("--request-id", dest="request_id_opt", help="Same as positional ref")
    p.add_argument("--display-name", dest="display_name", help="Friendly name for welcome email")
    p.add_argument(
        "--force",
        action="store_true",
        help="Override manual-payment guard (PayPal/MP requests — ops only)",
    )
    args = p.parse_args()

    request_id = (args.request_id_opt or args.request_id or "").strip().upper()
    if not request_id:
        p.error("Provide PCS-/PCP-/PCB-XXXXXXXX")
    if not _is_procure_subscription_request_id(request_id):
        print(
            f"✗ Invalid Procure ref: {request_id} (expected PCS-, PCP-, or PCB-)",
            file=sys.stderr,
        )
        return 1

    ensure_db_initialized()

    display_override = (args.display_name or "").strip()
    if display_override:
        if db_update_subscription_request_display_name(request_id, display_override):
            print(f"✓ Display name saved: {display_override}")

    req = db_find_subscription_request(request_id=request_id)
    if not req:
        print(f"✗ Request not found: {request_id}", file=sys.stderr)
        return 1

    from routers.payments import _activate_procure_from_request

    actions = _activate_procure_from_request(
        request_id,
        source="ops_manual",
        force=args.force,
    )
    code = _print_activation_actions(actions)
    if code == 0:
        print(
            "\nNext: customer opens magic link in email → procurecopilot.com/dashboard"
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
