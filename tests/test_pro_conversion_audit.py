"""Regression test: the Slack version of the Pro Conversion Audit must carry
the same "estimated, not measured" disclaimer the console version already
has.

build_audit() fabricates HOT/WARM/COLD segment counts from fixed industry
benchmark ratios (30/50/20%) when no per-user funnel data is available, and
sets estimated_segmentation=True. _fmt_console() checks that flag and prints
a disclaimer; _fmt_slack() never did — a founder reading Slack would
reasonably assume "23 HOT users" was real, measured data.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from pro_conversion_audit import _fmt_slack


def _fake_report(*, estimated: bool) -> dict:
    return {
        "generated_at": "2026-07-19T00:00:00+00:00",
        "window_days": 30,
        "funnel_aggregate": {
            "installs_30d": 100,
            "registrations": 40,
            "first_search": 30,
            "pro_requests": 20,
            "activated": 5,
            "unconverted_pro_requests": 15,
            "conversion_rate_pct": 25.0,
            "conversion_target_pct": 22.0,
            "gap_pp": -3.0,
        },
        "segments": {
            "HOT": {"count": 4, "cause": "checkout", "action": "Fix checkout UX"},
            "WARM": {"count": 8, "cause": "precio", "action": "Survey"},
            "COLD": {"count": 3, "cause": "otro", "action": "Nurture"},
        },
        "estimated_segmentation": estimated,
        "top_prospects": [],
    }


def test_slack_message_flags_estimated_segmentation():
    message = _fmt_slack(_fake_report(estimated=True))
    assert "estimad" in message.lower(), (
        "Slack message must warn segment counts are estimated from industry "
        "benchmarks, not measured per-user data"
    )


def test_slack_message_has_no_disclaimer_for_real_segmentation():
    message = _fmt_slack(_fake_report(estimated=False))
    assert "estimad" not in message.lower()
