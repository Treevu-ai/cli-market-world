#!/usr/bin/env python3
"""Funnel digest → Slack #funnel-cli-market.

Adoption signals (register, checkout starts) leave #suscripciones-cli-pro and
land here once per day instead of real-time spam.

Usage:
  python ops/funnel_digest_daily.py              # print digest
  python ops/funnel_digest_daily.py --slack      # post to #funnel-cli-market
  python ops/funnel_digest_daily.py --hours 24   # window (default 24)

Env:
  SLACK_BOT_TOKEN
  SLACK_CHANNEL_FUNNEL            — ID or auto-resolve #funnel-cli-market
  SLACK_WEBHOOK_FUNNEL            — optional webhook for funnel channel
  SLACK_FUNNEL_REALTIME=1         — optional: also post each event live
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

from billing_slack import format_funnel_digest_message, notify_funnel_digest  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Funnel digest for Slack #funnel-cli-market")
    p.add_argument("--slack", action="store_true", help="Post digest to Slack")
    p.add_argument("--hours", type=int, default=24, help="Lookback window (default 24)")
    args = p.parse_args()

    text = format_funnel_digest_message(hours=args.hours)
    print(text)

    if args.slack:
        if notify_funnel_digest(hours=args.hours):
            print("Slack → funnel-cli-market", file=sys.stderr)
            return 0
        print("Slack funnel digest skipped (not configured)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())