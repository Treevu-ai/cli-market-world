"""Funnel vs revenue Slack routing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from billing_slack import (
    format_funnel_digest_message,
    format_funnel_message,
    format_subscription_message,
    notify_funnel_event,
)


def test_revenue_messages_have_prefix():
    text = format_subscription_message(
        tier="pro",
        status="pending",
        username="u1",
        request_id="PRO-1",
    )
    assert "[REVENUE]" in text


def test_funnel_messages_have_prefix():
    text = format_funnel_message(event="register", username="u2")
    assert "[FUNNEL]" in text


def test_funnel_register_off_by_default_without_realtime(monkeypatch):
    monkeypatch.delenv("SLACK_FUNNEL_REALTIME", raising=False)
    monkeypatch.delenv("SLACK_FUNNEL_VERBOSE", raising=False)
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    assert notify_funnel_event(event="register", username="newuser") is False


def test_funnel_register_realtime_to_funnel_channel(monkeypatch):
    posted: list[str] = []

    monkeypatch.setenv("SLACK_FUNNEL_REALTIME", "1")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")

    import slack_notify

    monkeypatch.setattr(slack_notify, "deliver_to_funnel", lambda t: posted.append(t))
    monkeypatch.setattr(slack_notify, "channel_funnel", lambda: "C_FUNNEL")

    assert notify_funnel_event(event="register", username="newuser") is True
    assert posted and "[FUNNEL]" in posted[0]
    assert "newuser" in posted[0]


def test_funnel_digest_message_shape(monkeypatch):
    monkeypatch.setattr(
        "market_funnel.funnel_digest_counts",
        lambda hours=24, exclude_noise=True: {
            "register": 2,
            "request_pro": 1,
            "first_search": 0,
            "starter_subscribe": 0,
            "starter_request": 0,
            "procure_subscribe": 0,
            "activated": 0,
        },
    )
    monkeypatch.setattr(
        "market_funnel.funnel_recent_events",
        lambda hours=24, exclude_noise=True: [
            {"event": "register", "username": "alice", "meta": {}, "created_at": "x"},
        ],
    )
    monkeypatch.setattr(
        "market_funnel.funnel_summary",
        lambda days=1, exclude_noise=True: {
            "conversion": {"register_to_search": 0.5},
            "ttfv_median_minutes": 12.0,
        },
    )

    text = format_funnel_digest_message(hours=24)
    assert "[FUNNEL DIGEST]" in text
    assert "registros: 2" in text
    assert "alice" in text