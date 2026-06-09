#!/usr/bin/env python3
"""Post today's GTM copy to #publicaciones (Ricardo labels via publish_pack)."""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from publish_pack import (  # noqa: E402
    CAMPAIGN_START,
    build_slack_publish_messages,
    channels_for_date,
    marketing_metrics_from_dashboard,
)
from slack_notify import deliver_to_publicaciones  # noqa: E402

POST_UTC_HOUR = int(os.getenv("LINKEDIN_POST_UTC_HOUR", "13"))


def _campaign_day(for_date: date) -> int:
    start = date.fromisoformat(CAMPAIGN_START)
    return (for_date - start).days + 1


def _load_monday():
    path = Path(__file__).parent / "monday.py"
    spec = importlib.util.spec_from_file_location("monday_ops", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    args = parser.parse_args()
    for_date = date.fromisoformat(args.date)
    iso = for_date.isoformat()
    campaign_day = _campaign_day(for_date)

    if not channels_for_date(for_date, campaign_day):
        print(f"No channels scheduled for {iso}")
        return 1

    monday = _load_monday()
    print("Fetching dashboard...")
    data = monday.fetch_data()
    metrics = marketing_metrics_from_dashboard(data or {})

    msgs = build_slack_publish_messages(
        ds=iso,
        campaign_day=campaign_day,
        for_date=for_date,
        metrics=metrics,
        post_utc_hour=POST_UTC_HOUR,
    )
    for i, msg in enumerate(msgs, 1):
        prefix = f"📣 *Publicaciones ({i}/{len(msgs)})*\n\n" if len(msgs) > 1 else ""
        deliver_to_publicaciones(prefix + msg)

    print(f"Done — {len(msgs)} mensaje(s) enviado(s) a #publicaciones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())