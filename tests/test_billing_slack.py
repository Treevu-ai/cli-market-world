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
    assert "activate-pro" in text


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