#!/usr/bin/env python3
"""Sales funnel digest → Slack.

Daily digest of sales pipeline, leads, and revenue metrics.

Usage:
  python ops/sales_funnel_digest.py              # print digest
  python ops/sales_funnel_digest.py --slack      # post to #ventas-cli-market
  python ops/sales_funnel_digest.py --hours 24   # lookback window

Env:
  SLACK_BOT_TOKEN
  SLACK_CHANNEL_VENTAS       — ID or auto-resolve #ventas-cli-market
  SLACK_WEBHOOK_VENTAS       — optional webhook
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

try:
    from slack_notify import deliver  # noqa: E402
except ImportError:
    deliver = None


def _load_sales_events(hours: int = 24) -> list[dict[str, object]]:
    """Load sales/lead events from generated JSONL file."""
    events_path = ROOT / "ops" / "generated" / "sales-funnel" / "events.jsonl"
    if not events_path.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    events: list[dict[str, object]] = []

    try:
        with open(events_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    ts_str = event.get("ts", "")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts >= cutoff:
                            events.append(event)
                except (json.JSONDecodeError, ValueError):
                    continue
    except OSError:
        pass

    events.sort(key=lambda e: e.get("ts", ""), reverse=True)
    return events


def _summarize(events: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {
        "total_events": len(events),
        "by_type": {},
        "leads": {"cold": 0, "warm": 0, "hot": 0, "qualified": 0},
        "channels": {},
        "top_events": [],
    }

    for event in events:
        evt_type = str(event.get("type", "unknown"))
        summary["by_type"][evt_type] = int(summary["by_type"].get(evt_type, 0)) + 1

        channel = str(event.get("channel", "unknown"))
        summary["channels"][channel] = int(summary["channels"].get(channel, 0)) + 1

        level = str(event.get("level", ""))
        if level in summary.get("leads", {}):
            summary["leads"][level] = int(summary["leads"].get(level, 0)) + 1

    top = sorted(
        summary["by_type"].items(), key=lambda x: x[1], reverse=True
    )[:10]
    summary["top_events"] = [{"event": k, "count": v} for k, v in top]

    return summary


def _format_digest(summary: dict[str, object], hours: int) -> str:
    lines = [
        f"*[VENTAS]* Sales digest (últimas {hours}h)",
        "",
        f"• Eventos totales: {summary.get('total_events', 0)}",
        "",
        "*Leads por nivel:*",
    ]

    leads = summary.get("leads", {})
    lines.append(f"  • Cold: {leads.get('cold', 0)}")
    lines.append(f"  • Warm: {leads.get('warm', 0)}")
    lines.append(f"  • Hot: {leads.get('hot', 0)}")
    lines.append(f"  • Qualified: {leads.get('qualified', 0)}")

    lines.append("")
    lines.append("*Top eventos:*")
    for item in summary.get("top_events", [])[:8]:
        lines.append(f"  • {item['event']}: {item['count']}")

    lines.append("")
    lines.append("*Canales:*")
    channels = summary.get("channels", {})
    for channel, count in sorted(channels.items(), key=lambda x: x[1], reverse=True)[:8]:
        lines.append(f"  • {channel}: {count}")

    lines.append("")
    lines.append("— CLI Market Sales Funnel")
    return "\n".join(lines)


def _get_channel() -> str:
    return os.getenv("SLACK_CHANNEL_VENTAS", "").strip()


def _post_to_slack(text: str) -> bool:
    channel = _get_channel()
    if not channel or not deliver:
        return False
    try:
        deliver(text, channel=channel)
        return True
    except Exception:
        return False


def main() -> int:
    p = argparse.ArgumentParser(description="Sales funnel digest for Slack")
    p.add_argument("--slack", action="store_true", help="Post digest to Slack")
    p.add_argument("--hours", type=int, default=24, help="Lookback window (default 24)")
    args = p.parse_args()

    events = _load_sales_events(hours=args.hours)
    summary = _summarize(events)
    text = _format_digest(summary, args.hours)
    print(text)

    if args.slack:
        if _post_to_slack(text):
            print("Slack → ventas-cli-market", file=sys.stderr)
            return 0
        print("Slack skipped (not configured)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
