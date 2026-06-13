"""Payments facade — composes billing and checkout sub-routers.

External callers (market_server.py, admin.py, slack_ops.py, retailers.py,
ops/activate_pro.py) continue using `from routers.payments import ...` unchanged.
"""
from __future__ import annotations

from fastapi import APIRouter

from routers.billing.routes import router as _billing_routes_router
from routers.checkout.routes import router as _checkout_routes_router
from routers.checkout.webhooks import router as _checkout_webhooks_router

# Re-exports: backward-compat for external importers
from routers.billing.activation import (  # noqa: F401
    _activate_pro_from_request,
    _parse_pro_request_ref,
    process_pro_subscription_request,
    process_starter_subscription_request,
)
from routers.billing.notifications import (  # noqa: F401
    _append_pro_activation_email_actions,
    _pro_payment_method_from_request,
    resend_pro_activation_email,
)
router = APIRouter(tags=["payments"])
router.include_router(_billing_routes_router)
router.include_router(_checkout_routes_router)
router.include_router(_checkout_webhooks_router)
