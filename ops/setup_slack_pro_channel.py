#!/usr/bin/env python3
"""Configure #cli-market-pro for Build Pro billing notifications.

The bot needs chat:write and must be /invite'd to the channel.
Optional: channels:read on the Slack app to auto-resolve the channel ID.

Usage:
  python ops/setup_slack_pro_channel.py --channel-id C0XXXXXXXX
  python ops/setup_slack_pro_channel.py --test
  railway variables set SLACK_CHANNEL_CLI_MARKET_PRO=C0XXXXXXXX
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
    p = argparse.ArgumentParser(description="Setup #cli-market-pro Slack channel")
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
            print("✓ Test message posted to #cli-market-pro")
            return 0
        print("✗ Post failed — create #cli-market-pro, /invite @cli_market_dev_bot", file=sys.stderr)
        return 1

    print(
        "1. Slack → Create channel #cli-market-pro (public)\n"
        "2. In channel: /invite @cli_market_dev_bot\n"
        "3. Channel details → copy Channel ID (C0...)\n"
        "4. python ops/setup_slack_pro_channel.py --channel-id C0XXXXXXXX --test\n"
        "5. railway variables set SLACK_CHANNEL_CLI_MARKET_PRO=C0XXXXXXXX"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())