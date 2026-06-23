"""PayPal subscription reconcile — webhook fallback when polling PayPal."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_core import (
    db_get_subscription,
    db_save_billing_pending,
    db_save_user,
    ensure_db_initialized,
)
from server_deps import hash_password


@pytest.fixture(autouse=True)
def _db():
    ensure_db_initialized()
    yield


def test_reconcile_activates_active_paypal_subscription(monkeypatch):
    from routers.billing.paypal_reconcile import reconcile_paypal_subscriptions_for_user

    username = "reconcile-user"
    db_save_user(username, hash_password("x"), "sess-1")
    db_save_billing_pending("I-RECONCILE", "paypal", username, "pro")

    monkeypatch.setattr(
        "routers.billing.paypal_reconcile.fetch_paypal_subscription_status",
        AsyncMock(return_value={"ok": True, "status": "ACTIVE", "custom_id": username}),
    )
    monkeypatch.setattr(
        "market_connectors.email_outbound.send_pro_activated_email",
        lambda **kw: {"sent": False, "reason": "smtp_not_configured"},
    )

    result = asyncio.run(reconcile_paypal_subscriptions_for_user(username, lang="en"))
    assert result["ok"] is True
    assert result["activated"] == 1
    assert "pro_activated:reconcile-user" in result["actions"]
    assert db_get_subscription(username)["tier"] == "pro"


def test_reconcile_skips_approval_pending(monkeypatch):
    from routers.billing.paypal_reconcile import reconcile_paypal_subscriptions_for_user

    username = "pending-user"
    db_save_user(username, hash_password("x"), "sess-2")
    db_save_billing_pending("I-PENDING", "paypal", username, "pro")

    monkeypatch.setattr(
        "routers.billing.paypal_reconcile.fetch_paypal_subscription_status",
        AsyncMock(return_value={"ok": True, "status": "APPROVAL_PENDING", "custom_id": username}),
    )

    result = asyncio.run(reconcile_paypal_subscriptions_for_user(username, lang="en"))
    assert result["ok"] is True
    assert result.get("activated", 0) == 0
    assert db_get_subscription(username)["tier"] == "free"


def test_activate_paypal_subscription_records_funnel_event():
    from market_funnel import ensure_funnel_schema, funnel_summary
    from routers.billing.activation import activate_paypal_subscription

    ensure_funnel_schema()
    username = "activate-fn-user"
    db_save_user(username, hash_password("x"), "sess-3")
    db_save_billing_pending("I-FN", "paypal", username, "pro")

    with patch(
        "market_connectors.email_outbound.send_pro_activated_email",
        lambda **kw: {"sent": False, "reason": "smtp_not_configured"},
    ):
        actions = activate_paypal_subscription(
            username=username,
            sub_id="I-FN",
            kind="pro",
            source="paypal_reconcile",
            lang="en",
        )

    assert f"pro_activated:{username}" in actions
    assert db_get_subscription(username)["tier"] == "pro"
    summary = funnel_summary(days=30)
    assert summary["unique_users"]["activated"] >= 1
