#!/usr/bin/env python3
"""Configure #suscripciones-cli-pro for all tier subscription notifications.

The bot needs chat:write and must be /invite'd to the channel.

Usage:
  python ops/setup_slack_pro_channel.py --channel-id C0B90LCEK0V
  python ops/setup_slack_pro_channel.py --test
  railway variables set SLACK_CHANNEL_CLI_MARKET_PRO=C0B90LCEK0V
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ops"))

from load_env import load_repo_env  # noqa: E402

load_repo_env()


def main() -> int:
    p = argparse.ArgumentParser(description="Setup #suscripciones-cli-pro Slack channel")
    p.add_argument("--channel-id", help="Channel ID (C0...) from Slack channel details")
    p.add_argument("--test", action="store_true", help="Send test Pro activation message")
    args = p.parse_args()

    if args.channel_id:
        cid = args.channel_id.strip().upper()
        if not cid.startswith("C"):
            print("✗ Channel ID must start with C", file=sys.stderr)
            return 1
        print(f"Set on Railway:")
        print(f"  railway variables set SLACK_CHANNEL_CLI_MARKET_PRO={cid}")
        print(f"Set locally in .env:")
        print(f"  SLACK_CHANNEL_CLI_MARKET_PRO={cid}")
        os.environ["SLACK_CHANNEL_CLI_MARKET_PRO"] = cid

    if args.test or args.channel_id:
        from billing_slack import notify_pro_subscription

        ok = notify_pro_subscription(
            status="activated",
            username="setup-test",
            email="hello@cli-market.dev",
            request_id="PRO-SETUP",
            source="ops_setup",
            payment_method="yape",
        )
        if ok:
            print("✓ Test message posted to #suscripciones-cli-pro")
            return 0
        print("✗ Post failed — /invite @cli_market_dev_bot in #suscripciones-cli-pro", file=sys.stderr)
        return 1

    print(
        "Canal: #suscripciones-cli-pro (C0B90LCEK0V)\n"
        "1. /invite @cli_market_dev_bot en el canal\n"
        "2. python ops/setup_slack_pro_channel.py --channel-id C0B90LCEK0V --test\n"
        "3. railway variables set SLACK_CHANNEL_CLI_MARKET_PRO=C0B90LCEK0V"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())