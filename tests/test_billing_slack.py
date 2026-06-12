"""Subscription Slack message formatting."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from billing_slack import format_funnel_message, format_subscription_message, tier_label


def test_tier_labels():
    assert "Pro" in tier_label("pro")
    assert "Starter" in tier_label("starter")
    assert "Procure" in tier_label("procure_pro")


def test_format_pending_pro():
    text = format_subscription_message(
        tier="pro",
        status="pending",
        username="acubatruweb",
        email="a@outlook.com",
        request_id="PRO-ABC",
        payment_method="yape",
        amount_pen=144.3,
    )
    assert "CLI Market Pro" in text
    assert "[REVENUE]" in text
    assert "activate-pro" in text
    assert "market whoami" in text
    assert "hello@cli-market.dev" in text


def test_format_activated_procure():
    text = format_subscription_message(
        tier="procure_builder",
        status="activated",
        username="ops-user",
        email="ops@test.com",
        request_id="PCB-123",
        source="paypal_webhook",
        payment_method="paypal",
    )
    assert "Procure Builder" in text
    assert "tier procure_builder" in text


def test_format_funnel_install():
    text = format_funnel_message(
        event="install",
        username="",
        meta={"source": "hello"},
    )
    assert "pip install" in text
    assert "hello" in text


def test_format_cancelled():
    text = format_subscription_message(
        tier="pro",
        status="cancelled",
        username="acubatruweb",
        email="a@outlook.com",
        request_id="I-SUB123",
        source="BILLING.SUBSCRIPTION.CANCELLED",
    )
    assert "cancelada" in text
    assert "acubatruweb" in text


def test_funnel_install_quiet_by_default(monkeypatch):
    from billing_slack import notify_funnel_event

    monkeypatch.delenv("SLACK_FUNNEL_VERBOSE", raising=False)
    assert notify_funnel_event(event="install", meta={"source": "test"}) is False


def test_funnel_register_digest_mode_skips_realtime(monkeypatch):
    from billing_slack import notify_funnel_event

    monkeypatch.delenv("SLACK_FUNNEL_VERBOSE", raising=False)
    monkeypatch.delenv("SLACK_FUNNEL_REALTIME", raising=False)
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    assert notify_funnel_event(event="register", username="newuser") is False


def test_pending_pro_paypal_skips_activate_button(monkeypatch):
    from billing_slack import notify_subscription

    delivered: dict = {}

    def fake_deliver(text, blocks=None):
        delivered["text"] = text
        delivered["blocks"] = blocks
        return True

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setattr("slack_notify.deliver_to_cli_market_pro", fake_deliver)

    assert notify_subscription(
        tier="pro",
        status="pending",
        username="free-user",
        email="u@test.com",
        request_id="PRO-PAYPAL",
        payment_method="paypal",
    )
    assert delivered["blocks"] is None


def test_pending_pro_yape_includes_activate_button(monkeypatch):
    from billing_slack import notify_subscription

    delivered: dict = {}

    def fake_deliver(text, blocks=None):
        delivered["text"] = text
        delivered["blocks"] = blocks
        return True

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setattr("slack_notify.deliver_to_cli_market_pro", fake_deliver)

    assert notify_subscription(
        tier="pro",
        status="pending",
        username="pe-user",
        email="u@test.com",
        request_id="PRO-YAPE",
        payment_method="yape",
        amount_pen=144.3,
    )
    assert delivered["blocks"] is not None
    action_ids = [
        el.get("action_id")
        for block in delivered["blocks"]
        for el in (block.get("elements") or [])
    ]
    assert "activate_pro_request" in action_ids