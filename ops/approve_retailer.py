"""Retailer onboarding — apply + admin approval helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_core import ensure_db_initialized
from retailer_onboarding import (
    approve_retailer_application,
    db_list_retailer_applications,
    db_public_application,
    reject_retailer_application,
)
from store_credentials import get_default_stores


def cmd_list(args: argparse.Namespace) -> int:
    rows = db_list_retailer_applications(status=args.status or None)
    if args.json:
        print(json.dumps([db_public_application(r) for r in rows], indent=2))
    else:
        for row in rows:
            public = db_public_application(row)
            print(
                f"{public['id']}  {public['status']:9}  {public['store_name'][:30]:30}  "
                f"{public['platform']} {public['country']}  hint={public.get('api_token_hint', '')}"
            )
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    result = approve_retailer_application(
        args.application_id,
        store_id=args.store_id or None,
        magento_token=args.magento_token or "",
        storefront_token=args.storefront_token or "",
        vtex_app_key=args.vtex_app_key or "",
        vtex_app_token=args.vtex_app_token or "",
        review_notes=args.notes or "",
    )
    print(json.dumps(result, indent=2))
    print(f"Active catalog: {len(get_default_stores())} stores")
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    result = reject_retailer_application(args.application_id, review_notes=args.notes or "")
    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    ensure_db_initialized()
    parser = argparse.ArgumentParser(description="Retailer application ops")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List applications")
    p_list.add_argument("--status", default="pending")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_ok = sub.add_parser("approve", help="Approve application → store_credentials")
    p_ok.add_argument("application_id")
    p_ok.add_argument("--store-id", default="")
    p_ok.add_argument("--magento-token", default="")
    p_ok.add_argument("--storefront-token", default="")
    p_ok.add_argument("--vtex-app-key", default="")
    p_ok.add_argument("--vtex-app-token", default="")
    p_ok.add_argument("--notes", default="")
    p_ok.set_defaults(func=cmd_approve)

    p_no = sub.add_parser("reject", help="Reject application")
    p_no.add_argument("application_id")
    p_no.add_argument("--notes", default="")
    p_no.set_defaults(func=cmd_reject)

    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
