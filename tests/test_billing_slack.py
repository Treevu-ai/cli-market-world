"""Subscription Slack message formatting."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from billing_slack import (
    _funnel_slack_ready,
    _subscription_slack_ready,
    format_funnel_message,
    format_subscription_message,
    tier_label,
)
from market_funnel import is_noise_email


def test_slack_credentials_are_scrubbed_in_test_session():
    """Regression: a developer's real SLACK_BOT_TOKEN, persisted as a Windows
    user-level env var (same class of leak as CLI_MARKET_API_KEY, see
    conftest.py), was never scrubbed by conftest.py the way MARKET_API_TOKEN
    is. Every local run of tests/test_server.py's unmocked /billing/pro-checkout
    tests (test_pro_checkout_persists_display_name,
    test_pro_checkout_yape_manual_transfer_fallback, ...) posted real fake-data
    "$49 pago pendiente" messages to the live production #revenue Slack channel.
    conftest.py must scrub every credential that gates a real Slack send,
    exactly like it already does for MARKET_API_TOKEN/CLI_MARKET_API_KEY."""
    # Assert truthiness, not equality — an equality assertion failure would
    # print the real secret value in the pytest diff output.
    assert not os.environ.get("SLACK_BOT_TOKEN", ""), "SLACK_BOT_TOKEN leaked into test env"
    assert not os.environ.get("SLACK_WEBHOOK_CLI_MARKET_PRO", "")
    assert not os.environ.get("SLACK_WEBHOOK_FUNNEL", "")
    assert _subscription_slack_ready() is False
    assert _funnel_slack_ready() is False


def test_tier_labels():
    assert "Pro" in tier_label("pro")
    assert "Starter" in tier_label("starter")


def test_procure_tier_labels_reflect_live_procure_plans_not_hardcoded():
    """Same staleness bug class as CLI Market Pro/Starter (already fixed once,
    see test_tier_label_reflects_live_price_not_a_stale_cache) — the Procure
    tier prices were still hardcoded literals ($29/$79/$149) instead of
    reading procure_billing.PROCURE_PLANS, so a price change there would
    silently go unreflected in every Slack revenue message."""
    import procure_billing

    original = {
        slug: cfg["amount"] for slug, cfg in procure_billing.PROCURE_PLANS.items()
    }
    try:
        procure_billing.PROCURE_PLANS["starter"]["amount"] = 35.0
        procure_billing.PROCURE_PLANS["pro"]["amount"] = 85.0
        procure_billing.PROCURE_PLANS["builder"]["amount"] = 155.0
        assert "$35" in tier_label("procure_starter")
        assert "$85" in tier_label("procure_pro")
        assert "$155" in tier_label("procure_builder")
    finally:
        for slug, amount in original.items():
            procure_billing.PROCURE_PLANS[slug]["amount"] = amount
    assert "Procure" in tier_label("procure_pro")


def test_tier_label_reflects_live_price_not_a_stale_cache(monkeypatch):
    """Regression pin: cli-market-backend incident 2026-07-08 — a module-level
    TIER_LABELS constant computed once at import time kept showing $49/$9 in
    every Slack revenue/funnel message (MercadoPago, PayPal, Yape, Plin — all
    payment methods funnel through this same formatter) for months after the
    real price changed, because it was never recomputed after the process
    started. tier_label() must read market_billing's price constants fresh on
    every call, not from any cached dict."""
    import market_billing

    monkeypatch.setattr(market_billing, "PUBLIC_PRO_PRICE_USD", 39)
    assert "$39" in tier_label("pro")

    monkeypatch.setattr(market_billing, "PUBLIC_PRO_PRICE_USD", 59)
    assert "$59" in tier_label("pro")
    assert "$39" not in tier_label("pro")


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


def test_is_noise_email():
    assert is_noise_email("pam-5ab994cc@pam.cli-market.dev")
    assert is_noise_email("pam+mp+abc123@cli-market.dev")
    assert is_noise_email("e2e+pp+deadbeef@cli-market.dev")
    assert is_noise_email("test+procure@example.com")
    assert not is_noise_email("founder@outlook.com")
    assert not is_noise_email("")
    assert not is_noise_email("hello@cli-market.dev")


def test_notify_new_registration_skips_pam_email(monkeypatch):
    from billing_slack import notify_new_registration

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    posted: list[str] = []
    monkeypatch.setattr(
        "slack_notify.post_blocks_via_bot",
        lambda *a, **kw: posted.append(kw.get("text", "")) or True,
    )
    assert (
        notify_new_registration(
            username="user-be06863af9ab",
            email="pam-5ab994cc@pam.cli-market.dev",
            api_key_prefix="sk-test",
        )
        is False
    )
    assert posted == []


def test_notify_new_registration_real_email(monkeypatch):
    from billing_slack import notify_new_registration

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    posted: list[str] = []
    monkeypatch.setattr(
        "slack_notify.post_blocks_via_bot",
        lambda *a, **kw: posted.append(kw.get("text", "")) or True,
    )
    assert (
        notify_new_registration(
            username="user-e1a725b9acac",
            email="founder@outlook.com",
            api_key_prefix="sk-real",
        )
        is True
    )
    assert posted and "founder@outlook.com" in posted[0]