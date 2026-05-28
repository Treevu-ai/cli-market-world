"""Payment-gateway-specific checkout endpoints.

Each endpoint:
  1. Creates an order in `pending` status.
  2. Calls the relevant payment connector (Lemon, PayPal, Wise, Stripe).
  3. Returns the gateway's approve/redirect URL or QR data.
  4. The /checkout/webhook endpoint receives status updates.

These are intentionally separate from /checkout (default, no gateway) which
lives in routers/orders.py. /checkout (default) is the auth-flow entrypoint
used by the CLI and the tests; the per-gateway endpoints are user-facing
payment flows triggered from the web UI.

Endpoints:
  POST /checkout/yape       Yape/Plin QR (Peru)
  POST /checkout/lemon      Lemon Cash checkout URL (Argentina)
  POST /checkout/paypal     PayPal approval URL
  POST /checkout/wise       Wise pay-link + QR
  POST /checkout/webhook    Mark order as paid/failed (called by gateway)
  GET  /checkout/rates      FX rates with PEN base (Wise; fallback if down)
  POST /billing/checkout    Stripe Checkout for Pro subscription
"""

from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Header, HTTPException

from market_core import db_clear_cart, db_create_order, db_get_cart, get_db
from server_deps import require_user

router = APIRouter(tags=["payments"])


def _cart_total(cart: list[dict]) -> float:
    return round(sum(i["price"] * i["quantity"] for i in cart), 2)


def _prepare_pending_order(username: str, method: str, currency_hint: str = "") -> tuple[list[dict], float, str]:
    """Common preamble: get cart, compute total, create pending order, clear cart.
    Returns (cart, total, order_id)."""
    cart = db_get_cart(username)
    if not cart:
        raise HTTPException(status_code=400, detail="Carrito vacío")
    total = _cart_total(cart)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_create_order(username, cart, method, total, status="pending", order_id=order_id)
    db_clear_cart(username)
    return cart, total, order_id


@router.post("/checkout/yape")
def checkout_yape(authorization: str | None = Header(None)):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "yape")
    qr_ref = f"yape-{order_id.lower()}"
    return {
        "order_id": order_id, "total": total, "currency": "PEN",
        "payment_method": "yape",
        "qr_reference": qr_ref,
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_ref}",
        "status": "pending",
        "message": "Escanea el QR con Yape/Plin para completar el pago.",
    }


@router.post("/checkout/lemon")
async def checkout_lemon(authorization: str | None = Header(None)):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "lemon")
    from market_connectors.lemon_payments import create_checkout
    try:
        lc = await create_checkout(total, "ARS", f"CLI-Market-{order_id}")
        if "checkout_url" in lc:
            return {
                "order_id": order_id, "total": total, "currency": "ARS",
                "payment_method": "lemon", "status": "pending",
                "lemon_checkout_id": lc["checkout_id"],
                "checkout_url": lc["checkout_url"],
                "qr_url": lc.get("qr_url", ""),
                "message": "Completa el pago con Lemon.",
            }
        raise HTTPException(status_code=502, detail=lc.get("error", "Lemon error"))
    except Exception:
        raise HTTPException(status_code=501, detail="Lemon no configurado. Set LEMON_API_KEY.")


@router.post("/checkout/paypal")
async def checkout_paypal(authorization: str | None = Header(None)):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "paypal")
    from market_connectors.paypal_payments import create_order
    try:
        pp = await create_order(total, "USD", f"CLI-Market-{order_id}")
        if "approve_url" in pp:
            return {
                "order_id": order_id, "total": total, "currency": "USD",
                "payment_method": "paypal", "status": "pending",
                "paypal_order_id": pp["order_id"],
                "approve_url": pp["approve_url"],
                "message": "Completa el pago en PayPal.",
            }
        raise HTTPException(status_code=502, detail=pp.get("error", "PayPal error"))
    except ValueError:
        raise HTTPException(
            status_code=501,
            detail="PayPal no configurado. Set PAYPAL_CLIENT_ID y PAYPAL_CLIENT_SECRET.",
        )


@router.post("/checkout/wise")
async def checkout_wise(authorization: str | None = Header(None)):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "wise")
    from market_connectors.wise_payments import WISE_API_TOKEN  # noqa: F401 — used for the bool below
    wise_ok = bool(WISE_API_TOKEN)
    wise_pay_me = os.getenv("WISE_PAY_ME_URL", "https://wise.com/pay/me/ricardoantonioc68")
    return {
        "order_id": order_id, "total": total, "currency": "PEN",
        "payment_method": "wise", "status": "pending",
        "wise_available": wise_ok,
        "wise_pay_link": wise_pay_me,
        "wise_qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={wise_pay_me}",
        "instructions": {
            "pay_link": wise_pay_me,
            "reference": f"CLI-Market-{order_id}",
            "amount_usd": round(total * 0.27, 2),
        } if wise_ok else None,
        "message": "Escanea el QR o usa el link de Wise para pagar",
    }


@router.post("/checkout/paypal-webhook")
async def paypal_webhook(request: dict):
    """Receive PayPal payment notifications (IPN/webhook)."""
    # In production, verify the webhook signature with PayPal's API
    event_type = request.get("event_type", "")
    resource = request.get("resource", {})
    order_id = resource.get("id", "")
    state = resource.get("state", resource.get("status", ""))
    print(f"PayPal webhook: {event_type} — {order_id} → {state}")
    return {"received": True, "order_id": order_id, "state": state}

@router.post("/checkout/webhook")
def checkout_webhook(order_id: str = "", status: str = "paid"):
    """Mark an order as paid/failed/etc. Called by external gateways."""
    if not order_id:
        raise HTTPException(status_code=400, detail="order_id required")
    db = get_db()
    db.execute("UPDATE app_orders SET status=? WHERE order_id=?", (status, order_id))
    db.commit()
    db.close()
    return {"order_id": order_id, "status": status, "message": f"Payment {status}"}


@router.get("/checkout/rates")
async def checkout_rates():
    """FX rates with PEN as base. Falls back to a static table if Wise is unreachable."""
    try:
        from market_connectors.wise_payments import get_rates
        rates = await get_rates("PEN")
        return {"base": "PEN", "rates": rates}
    except Exception:
        return {
            "base": "PEN",
            "rates": {
                "USD": 0.27, "EUR": 0.25, "ARS": 0.0027, "BRL": 0.27,
                "MXN": 0.078, "COP": 0.00035, "CLP": 0.0014, "PEN": 1.0,
            },
            "source": "fallback",
        }


@router.post("/billing/paypal")
async def billing_paypal(authorization: str | None = Header(None)):
    """PayPal Subscription for Pro plan ($49/mo)."""
    username = require_user(authorization)
    try:
        from market_connectors.paypal_payments import create_subscription
        sub = await create_subscription()
        if "approve_url" in sub:
            return {"subscription_id": sub["subscription_id"], "approve_url": sub["approve_url"], "plan": "Pro", "amount": "$49/mo"}
        raise HTTPException(status_code=502, detail=sub.get("error", "PayPal error"))
    except ValueError:
        raise HTTPException(status_code=501, detail="PayPal no configurado")

@router.post("/billing/checkout")
def billing_checkout(authorization: str | None = Header(None)):
    """Stripe Checkout for Pro subscription upgrade."""
    username = require_user(authorization)
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not stripe_key:
        raise HTTPException(status_code=501, detail="Stripe not configured")
    try:
        import stripe
        stripe.api_key = stripe_key
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": os.getenv("STRIPE_PRICE_PRO", "price_pro"), "quantity": 1}],
            mode="subscription",
            success_url="https://cli-market.dev?upgraded=true",
            cancel_url="https://cli-market.dev?upgraded=false",
            client_reference_id=username,
        )
        return {"url": session.url}
    except ImportError:
        raise HTTPException(status_code=501, detail="pip install stripe")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
