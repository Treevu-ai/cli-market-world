"""Sprint 1 unit tests — no full market_server import required."""

from procure_billing import procure_price_pen, procure_tier_from_request_id
from routers.billing.activation import (
    _is_procure_subscription_request_id,
    _is_retailer_growth_subscription_request_id,
    _parse_pro_request_ref,
    _parse_subscription_request_ref,
)
from routers.billing.pro_helpers import procure_mp_checkout_enabled


def test_procure_price_pen_starter(monkeypatch):
    monkeypatch.setenv("PROCURE_PEN_PER_USD", "3.75")
    assert procure_price_pen("starter") == 108.75


def test_procure_tier_from_request_id():
    assert procure_tier_from_request_id("PCS-ABC123") == "procure_starter"
    assert procure_tier_from_request_id("PCP-XYZ789") == "procure_pro"
    assert procure_tier_from_request_id("PCB-FOO456") == "procure_builder"
    assert procure_tier_from_request_id("PRO-ABC123") is None


def test_parse_subscription_request_ref():
    assert _parse_subscription_request_ref("CLI-Market-PCS-ABC123") == "PCS-ABC123"
    assert _parse_subscription_request_ref("CLI-Market-PCP-XYZ789") == "PCP-XYZ789"
    assert _parse_subscription_request_ref("CLI-Market-PRO-OLD123") == "PRO-OLD123"
    assert _parse_pro_request_ref("CLI-Market-PCS-ABC123") is None
    assert _parse_pro_request_ref("CLI-Market-PRO-OLD123") == "PRO-OLD123"


def test_is_procure_subscription_request_id():
    assert _is_procure_subscription_request_id("PCS-ABC") is True
    assert _is_procure_subscription_request_id("PRO-ABC") is False


def test_retailer_growth_ref_does_not_leak_into_pro_activation():
    """Regression guard: an RGW- ref must never be treated as Pro or Procure.

    Before this, the webhook dispatch fell back to _activate_pro_from_request
    for any unrecognized prefix — an RGW payment would have incorrectly
    granted the payer a Pro (Build) subscription.
    """
    assert _parse_subscription_request_ref("CLI-Market-RGW-ABC123") == "RGW-ABC123"
    assert _is_retailer_growth_subscription_request_id("RGW-ABC123") is True
    assert _is_procure_subscription_request_id("RGW-ABC123") is False
    assert _is_retailer_growth_subscription_request_id("PRO-ABC123") is False


def test_procure_mp_checkout_flag(monkeypatch):
    monkeypatch.delenv("PROCURE_MP_CHECKOUT", raising=False)
    assert procure_mp_checkout_enabled() is False
    monkeypatch.setenv("PROCURE_MP_CHECKOUT", "1")
    assert procure_mp_checkout_enabled() is True
