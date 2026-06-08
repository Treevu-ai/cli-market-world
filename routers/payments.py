"""Payment-gateway-specific checkout endpoints.

Each endpoint:
  1. Creates an order in `pending` status.
  2. Calls the relevant payment connector (Lemon, PayPal, Wise, Stripe).
  3. Returns the gateway's approve/redirect URL or QR data.
  4. Webhooks mark orders paid or upgrade subscription tier.

Endpoints:
  POST /checkout/yape       Yape/Plin QR (Peru)
  POST /checkout/lemon      Lemon Cash checkout URL (Argentina)
  POST /checkout/paypal     PayPal approval URL
  POST /checkout/wise       Wise pay-link + QR
  POST /checkout/paypal/capture  Capture approved PayPal order (return URL)
  POST /checkout/webhook    Generic mark order paid/failed
  POST /checkout/paypal-webhook  PayPal IPN/webhooks
  GET  /checkout/rates      FX rates with PEN base (Wise; fallback if down)
  POST /billing/request-pro  Email payment link (manual Pro — default)
  POST /billing/pro-checkout  Pro billing — PayPal / Mercado Pago / Yape / Plin (landing)
  POST /billing/request-starter  Email Starter checkout link (fallback)
  POST /billing/paypal      PayPal Subscription (authenticated CLI)
  POST /billing/paypal-subscribe  PayPal Subscription (landing — auto-activate)
  POST /billing/checkout    Stripe Checkout — DISABLED (no activation webhook yet)
  GET  /paypal-status       PayPal config diagnostic
  POST /checkout/mercadopago     Mercado Pago Checkout Pro (PEN)
  GET/POST /checkout/mercadopago-webhook  Mercado Pago IPN/webhooks
  GET  /mercadopago-status  Mercado Pago config diagnostic
"""

from __future__ import annotations

import logging
import os
import re
import uuid

import httpx
from fastapi import APIRouter, Body, Header, HTTPException, Request

from market_core import (
    db_delete_billing_pending,
    db_find_order_by_gateway_ref,
    db_find_order_by_id,
    db_get_billing_pending,
    db_get_user_email,
    db_create_subscription_request,
    db_mark_subscription_request_activated,
    db_mark_subscription_request_emailed,
    db_mark_subscription_requests_activated_for_user,
    db_find_subscription_request,
    db_recent_subscription_request,
    db_save_billing_pending,
    db_set_order_gateway_ref,
    db_set_subscription,
    db_update_order_status,
    db_clear_cart,
    db_create_order,
    db_get_cart,
)
from market_security import is_production_deploy, paypal_allow_unverified_webhooks
from server_deps import check_rate_limit, require_checkout_access, require_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["payments"])

_ORDER_REF_RE = re.compile(r"CLI-Market-(ORD-[A-F0-9]+)", re.I)
_PRO_REF_RE = re.compile(r"CLI-Market-(PRO-[A-Z0-9]+)", re.I)
_PRO_BILLING_METHODS = frozenset({"paypal", "yape", "plin", "mercadopago"})
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _cart_total(cart: list[dict]) -> float:
    return round(sum(i["price"] * i["quantity"] for i in cart), 2)


def _notify_procure_payment(order_id: str, status: str) -> str | None:
    """Forward payment status to Procure Copilot when PROCURE_WEBHOOK_URL is set."""
    url = os.getenv("PROCURE_WEBHOOK_URL", "").strip()
    secret = os.getenv("PROCURE_WEBHOOK_SECRET", "").strip()
    if not url:
        return None
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                url,
                json={"orderId": order_id, "status": status, "secret": secret},
            )
            if r.is_success:
                return "procure_notified"
    except Exception as exc:
        logger.warning("Procure webhook notify failed for %s: %s", order_id, exc)
    return None


def _prepare_pending_order(username: str, method: str) -> tuple[list[dict], float, str]:
    """Common preamble: get cart, compute total, create pending order, clear cart."""
    require_checkout_access(username)
    cart = db_get_cart(username)
    if not cart:
        raise HTTPException(status_code=400, detail="Carrito vacío")
    total = _cart_total(cart)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_create_order(username, cart, method, total, status="pending", order_id=order_id)
    db_clear_cart(username)
    return cart, total, order_id


def _parse_market_order_ref(resource: dict) -> str | None:
    """Extract ORD-xxx from PayPal purchase unit reference_id."""
    units = resource.get("purchase_units") or []
    for unit in units:
        ref = unit.get("reference_id") or unit.get("custom_id") or ""
        m = _ORDER_REF_RE.search(ref)
        if m:
            return m.group(1).upper()
    ref = resource.get("custom_id") or ""
    m = _ORDER_REF_RE.search(ref)
    return m.group(1).upper() if m else None


async def _handle_paypal_event(event: dict) -> dict:
    event_type = event.get("event_type", "")
    resource = event.get("resource") or {}
    actions: list[str] = []

    if event_type == "CHECKOUT.ORDER.APPROVED":
        paypal_order_id = resource.get("id", "")
        if paypal_order_id:
            from market_connectors.paypal_payments import capture_order

            cap = await capture_order(paypal_order_id)
            actions.append(f"capture:{cap.get('status', cap.get('error', 'err'))}")
            market_order_id = _parse_market_order_ref(resource)
            if market_order_id:
                db_set_order_gateway_ref(market_order_id, paypal_order_id)

    elif event_type in ("PAYMENT.CAPTURE.COMPLETED", "CHECKOUT.ORDER.COMPLETED"):
        paypal_order_id = (
            resource.get("supplementary_data", {})
            .get("related_ids", {})
            .get("order_id")
            or resource.get("id", "")
        )
        order_row = db_find_order_by_gateway_ref(paypal_order_id)
        if not order_row:
            market_order_id = _parse_market_order_ref(resource)
            if market_order_id:
                order_row = db_find_order_by_id(market_order_id)
                if order_row and paypal_order_id:
                    db_set_order_gateway_ref(market_order_id, paypal_order_id)
        if order_row:
            db_update_order_status(order_row["order_id"], "paid")
            actions.append(f"order_paid:{order_row['order_id']}")
            notified = _notify_procure_payment(order_row["order_id"], "paid")
            if notified:
                actions.append(notified)
        else:
            actions.append(f"order_not_found:{paypal_order_id}")

    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        sub_id = resource.get("id", "")
        username = resource.get("custom_id") or ""
        pending = db_get_billing_pending(sub_id) if sub_id else None
        if not username and pending:
            username = pending.get("username", "")
        if username:
            kind = (pending or {}).get("kind", "subscription")
            tier = "starter" if kind == "starter" else "pro"
            db_set_subscription(username, tier, paypal_subscription_id=sub_id)
            if sub_id:
                db_delete_billing_pending(sub_id)
            marked = db_mark_subscription_requests_activated_for_user(username)
            actions.append(f"{tier}_activated:{username}")
            try:
                from market_funnel import record_funnel_event
                record_funnel_event(
                    "activated",
                    username=username,
                    meta={"source": "paypal_webhook", "tier": tier},
                    dedupe=True,
                )
            except Exception:
                pass
            if marked:
                actions.append(f"requests_closed:{marked}")
            try:
                email = db_get_user_email(username) or ""
                if email:
                    lang = (resource.get("locale") or "es")[:2].lower()
                    if lang not in ("es", "en"):
                        lang = "es"
                    if tier == "starter":
                        from market_connectors.email_outbound import send_starter_activated_email
                        mail = send_starter_activated_email(
                            to_email=email,
                            username=username,
                            lang=lang,
                            subscription_id=sub_id,
                        )
                    else:
                        from market_connectors.email_outbound import send_pro_activated_email
                        mail = send_pro_activated_email(
                            to_email=email,
                            username=username,
                            lang=lang,
                            subscription_id=sub_id,
                        )
                    if mail.get("sent"):
                        actions.append(f"activation_email:{email}")
                    else:
                        actions.append(f"activation_email_skipped:{mail.get('reason', 'err')}")
            except Exception:
                logger.exception("%s activation email failed for %s", tier, username)
                actions.append("activation_email_failed")
        else:
            actions.append(f"subscription_no_user:{sub_id}")

    elif event_type in ("BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.EXPIRED",
                        "BILLING.SUBSCRIPTION.SUSPENDED"):
        sub_id = resource.get("id", "")
        username = resource.get("custom_id") or ""
        if not username and sub_id:
            pending = db_get_billing_pending(sub_id)
            username = (pending or {}).get("username", "")
        if username:
            db_set_subscription(username, "free", paypal_subscription_id="")
            if sub_id:
                db_delete_billing_pending(sub_id)
            actions.append(f"downgraded:{username}")

    return {"event_type": event_type, "actions": actions}


@router.post("/checkout/yape")
def checkout_yape(authorization: str | None = Header(None)):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "yape")
    yape_number = os.getenv("YAPE_PLIN_NUMBER", "")
    qr_data = yape_number or f"yape-{order_id.lower()}"
    if yape_number:
        qr_data = f"yape://pay?phone={yape_number}&amount={total:.2f}&ref={order_id}"
    return {
        "order_id": order_id,
        "total": total,
        "currency": "PEN",
        "payment_method": "yape",
        "qr_reference": order_id,
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}",
        "status": "pending",
        "message": (
            f"Escanea con Yape/Plin. Monto: S/ {total:.2f}. Referencia: {order_id}. "
            "Confirmación manual hasta integrar agregador."
        ),
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
                "order_id": order_id,
                "total": total,
                "currency": "ARS",
                "payment_method": "lemon",
                "status": "pending",
                "lemon_checkout_id": lc["checkout_id"],
                "checkout_url": lc["checkout_url"],
                "qr_url": lc.get("qr_url", ""),
                "message": "Completa el pago con Lemon.",
            }
        raise HTTPException(status_code=502, detail=lc.get("error", "Lemon error"))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=501, detail="Lemon no configurado. Set LEMON_API_KEY.")


@router.post("/checkout/paypal")
async def checkout_paypal(
    body: dict = Body(default_factory=dict),
    authorization: str | None = Header(None),
):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "paypal")
    from market_connectors.paypal_payments import create_order

    return_url = (body.get("return_url") or "").strip() or "https://cli-market.dev?order=success"
    cancel_url = (body.get("cancel_url") or "").strip() or "https://cli-market.dev?order=cancelled"

    try:
        pp = await create_order(
            total,
            "USD",
            f"CLI-Market-{order_id}",
            return_url=return_url,
            cancel_url=cancel_url,
        )
        if "approve_url" in pp:
            db_set_order_gateway_ref(order_id, pp["order_id"])
            return {
                "order_id": order_id,
                "total": total,
                "currency": "USD",
                "payment_method": "paypal",
                "status": "pending",
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


@router.post("/checkout/paypal/capture")
async def checkout_paypal_capture(
    paypal_order_id: str = "",
    authorization: str | None = Header(None),
):
    """Capture after buyer returns from PayPal (backup if webhook is delayed)."""
    require_user(authorization)
    if not paypal_order_id:
        raise HTTPException(status_code=400, detail="paypal_order_id required")
    from market_connectors.paypal_payments import capture_order

    cap = await capture_order(paypal_order_id)
    if not cap.get("ok"):
        raise HTTPException(status_code=502, detail=cap.get("error", "Capture failed"))
    row = db_find_order_by_gateway_ref(paypal_order_id)
    procure_action = None
    if row:
        db_update_order_status(row["order_id"], "paid")
        procure_action = _notify_procure_payment(row["order_id"], "paid")
    payload = {"ok": True, "paypal_order_id": paypal_order_id, "market_order": row}
    if procure_action:
        payload["procure"] = procure_action
    return payload


@router.post("/checkout/wise")
async def checkout_wise(authorization: str | None = Header(None)):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "wise")
    from market_connectors.wise_payments import WISE_API_TOKEN

    wise_ok = bool(WISE_API_TOKEN)
    wise_pay_me = os.getenv("WISE_PAY_ME_URL", "https://wise.com/pay/me/ricardoantonioc68")
    return {
        "order_id": order_id,
        "total": total,
        "currency": "PEN",
        "payment_method": "wise",
        "status": "pending",
        "wise_available": wise_ok,
        "wise_pay_link": wise_pay_me,
        "wise_qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={wise_pay_me}",
        "instructions": {
            "pay_link": wise_pay_me,
            "reference": order_id,
            "amount_pen": total,
        },
        "message": "Escanea el QR o usa el link de Wise. Referencia obligatoria.",
    }


@router.post("/checkout/paypal-webhook")
async def paypal_webhook(request: Request):
    """PayPal webhooks — verify signature, capture orders, upgrade Pro tier."""
    body = await request.json()
    headers = {k.lower(): v for k, v in request.headers.items()}
    from market_connectors.paypal_payments import PAYPAL_WEBHOOK_ID, verify_webhook_signature

    if not PAYPAL_WEBHOOK_ID:
        if is_production_deploy():
            raise HTTPException(
                status_code=503,
                detail="PAYPAL_WEBHOOK_ID required in production",
            )
        if not paypal_allow_unverified_webhooks():
            raise HTTPException(
                status_code=401,
                detail="PayPal webhook verification not configured",
            )
    else:
        verified = await verify_webhook_signature(headers, body)
        if not verified:
            logger.warning("PayPal webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    result = await _handle_paypal_event(body)
    logger.info("PayPal webhook processed: %s", result)
    return {"received": True, **result}


@router.post("/checkout/webhook")
def checkout_webhook(order_id: str = "", status: str = "paid", secret: str = ""):
    """Mark an order paid/failed. Requires CHECKOUT_WEBHOOK_SECRET in production."""
    expected = os.getenv("CHECKOUT_WEBHOOK_SECRET", "")
    if is_production_deploy():
        if not expected:
            raise HTTPException(
                status_code=503,
                detail="CHECKOUT_WEBHOOK_SECRET required in production",
            )
        if secret != expected:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
    elif expected and secret != expected:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    if not order_id:
        raise HTTPException(status_code=400, detail="order_id required")
    if not db_update_order_status(order_id, status):
        raise HTTPException(status_code=404, detail="Order not found")
    procure_action = None
    if status == "paid":
        procure_action = _notify_procure_payment(order_id, status)
    payload = {"order_id": order_id, "status": status, "message": f"Payment {status}"}
    if procure_action:
        payload["procure"] = procure_action
    return payload


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
                "USD": 0.27,
                "EUR": 0.25,
                "ARS": 0.0027,
                "BRL": 0.27,
                "MXN": 0.078,
                "COP": 0.00035,
                "CLP": 0.0014,
                "PEN": 1.0,
            },
            "source": "fallback",
        }


@router.get("/paypal-status")
async def paypal_status(test: bool = False):
    """Check if PayPal credentials are configured. ?test=1 verifies API auth."""
    client_id = os.getenv("PAYPAL_CLIENT_ID", "")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "")
    sandbox = os.getenv("PAYPAL_SANDBOX", "true").lower() == "true"
    out = {
        "configured": bool(client_id and client_secret),
        "sandbox": sandbox,
        "live": not sandbox and bool(client_id and client_secret),
        "webhook_configured": bool(os.getenv("PAYPAL_WEBHOOK_ID", "")),
        "plan_id_configured": bool(os.getenv("PAYPAL_PLAN_ID", "")),
        "starter_plan_id_configured": bool(os.getenv("PAYPAL_STARTER_PLAN_ID", "")),
        "api_url": "https://api-m.sandbox.paypal.com" if sandbox else "https://api-m.paypal.com",
        "webhook_url": "https://cli-market-production.up.railway.app/checkout/paypal-webhook",
        "setup_script": "python3 ops/paypal_sandbox_setup.py check",
        "endpoints": [
            "/checkout/paypal",
            "/checkout/paypal/capture",
            "/billing/paypal",
            "/billing/starter",
            "/billing/starter-subscribe",
            "/checkout/paypal-webhook",
        ],
    }
    if test and out["configured"]:
        try:
            from market_connectors.paypal_payments import check_connection

            out["auth_test"] = await check_connection()
        except Exception as e:
            out["auth_test"] = {"ok": False, "error": str(e)}
    return out



def _mercadopago_env_flags() -> dict[str, bool]:
    keys = (
        "MERCADOPAGO_ACCESS_TOKEN",
        "MERCADOPAGO_ACCESS_TOKEN_SANDBOX",
        "MERCADOPAGO_ACCESS_TOKEN_PRODUCTION",
        "MERCADO_PAGO_ACCESS_TOKEN",
        "MP_ACCESS_TOKEN",
        "MERCADOPAGO_PUBLIC_KEY",
        "MERCADOPAGO_SANDBOX",
        "MERCADOPAGO_WEBHOOK_URL",
        "MERCADOPAGO_WEBHOOK_SECRET",
        "MERCADOPAGO_WEBHOOK_TOKEN",
        "MERCADOPAGO_SECRET_SIGNATURE",
        "MP_WEBHOOK_SECRET",
        "RAILWAY_PUBLIC_DOMAIN",
    )
    return {k: bool(os.getenv(k, "").strip()) for k in keys}


@router.get("/mercadopago-status")
async def mercadopago_status(test: bool = False):
    """Check Mercado Pago credentials. ?test=1 verifies API auth."""
    from market_connectors.mercadopago_payments import (
        access_token,
        is_sandbox,
        notification_url,
        public_key,
        webhook_secret,
    )

    token = access_token()
    out = {
        "configured": bool(token),
        "sandbox": is_sandbox(),
        "public_key_configured": bool(public_key()),
        "currency": "PEN",
        "notification_url": notification_url(),
        "webhook_secret_configured": bool(webhook_secret()),
        "env_keys": _mercadopago_env_flags(),
        "endpoints": ["/checkout/mercadopago", "/checkout/mercadopago-webhook"],
    }
    if test and token:
        try:
            from market_connectors.mercadopago_payments import check_connection

            out["auth_test"] = await check_connection()
        except Exception as e:
            out["auth_test"] = {"ok": False, "error": str(e)}
    return out


@router.post("/checkout/mercadopago")
async def checkout_mercadopago(
    body: dict = Body(default_factory=dict),
    authorization: str | None = Header(None),
):
    """Mercado Pago Checkout Pro for PEN cart total."""
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "mercadopago")
    from market_connectors.mercadopago_payments import create_preference

    success_url = (
        (body.get("success_url") or body.get("return_url") or "").strip()
        or "https://cli-market.dev?mp=success"
    )
    failure_url = (
        (body.get("failure_url") or body.get("cancel_url") or "").strip()
        or "https://cli-market.dev?mp=failure"
    )
    pending_url = (body.get("pending_url") or "").strip() or success_url

    try:
        mp = await create_preference(
            total,
            "PEN",
            f"CLI-Market-{order_id}",
            title=f"CLI Market {order_id}",
            success_url=success_url,
            failure_url=failure_url,
            pending_url=pending_url,
        )
        if mp.get("checkout_url"):
            if mp.get("preference_id"):
                db_set_order_gateway_ref(order_id, str(mp["preference_id"]))
            return {
                "order_id": order_id,
                "total": total,
                "currency": "PEN",
                "payment_method": "mercadopago",
                "status": "pending",
                "preference_id": mp.get("preference_id", ""),
                "checkout_url": mp["checkout_url"],
                "sandbox": mp.get("sandbox", False),
                "message": "Complete el pago en Mercado Pago.",
            }
        raise HTTPException(status_code=502, detail=mp.get("error", "Mercado Pago error"))
    except ValueError:
        raise HTTPException(
            status_code=501,
            detail="Mercado Pago no configurado. Set MERCADOPAGO_ACCESS_TOKEN.",
        )


@router.api_route("/checkout/mercadopago-webhook", methods=["GET", "POST"])
async def mercadopago_webhook(request: Request):
    """Mercado Pago notifications — validate signature, mark order paid."""
    from market_connectors.mercadopago_payments import (
        get_payment,
        parse_external_order_id,
        parse_webhook_payment_id,
        validate_webhook_signature,
        webhook_secret,
    )

    query = dict(request.query_params)
    body: dict = {}
    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = {}

    x_sig = request.headers.get("x-signature", "")
    x_req = request.headers.get("x-request-id", "")
    payment_id, ntype = parse_webhook_payment_id(query_params=query, body=body)

    secret = webhook_secret()
    if secret:
        data_id = payment_id or str(query.get("data.id") or query.get("id") or "")
        if not validate_webhook_signature(
            x_signature=x_sig,
            x_request_id=x_req,
            data_id=data_id,
            secret=secret,
        ):
            raise HTTPException(status_code=401, detail="invalid x-signature")

    if request.method == "GET" and not payment_id:
        return {"ok": True, "message": "mercadopago webhook endpoint"}

    if not payment_id:
        return {"received": True, "action": "no_payment_id", "type": ntype}

    pay = await get_payment(payment_id)
    if pay.get("error"):
        return {"received": True, "payment_id": payment_id, "error": pay.get("error")}

    status = str(pay.get("status") or "").lower()
    ext_ref = str(pay.get("external_reference") or "")
    order_id = parse_external_order_id(ext_ref)
    actions: list[str] = []

    pro_request_id = _parse_pro_request_ref(ext_ref)
    if status == "approved" and pro_request_id:
        actions.extend(_activate_pro_from_request(pro_request_id, source="mercadopago_webhook"))
    elif status == "approved" and order_id:
        if db_update_order_status(order_id, "paid"):
            actions.append(f"paid:{order_id}")
            notified = _notify_procure_payment(order_id, "paid")
            if notified:
                actions.append(notified)
        else:
            actions.append(f"order_not_found:{order_id}")
    elif pro_request_id:
        actions.append(f"pro_status:{status}:{pro_request_id}")
    elif order_id:
        actions.append(f"status:{status}:{order_id}")

    return {
        "received": True,
        "payment_id": payment_id,
        "type": ntype,
        "status": status,
        "actions": actions,
    }


STARTER_CHECKOUT_URL = os.getenv(
    "STARTER_PAYMENT_URL",
    "https://cli-market.dev/#pro-checkout",
)  # legacy env name kept for compat; value now points to Pro (pricing simplified)


def _pro_price_pen() -> float:
    """USD Pro price converted to PEN for Yape/Plin/Mercado Pago."""
    from market_connectors.paypal_payments import PRO_PRICE_USD

    raw = os.getenv("PRO_PEN_PER_USD", "3.7")
    try:
        pen_per_usd = float(str(raw).strip())
    except (TypeError, ValueError):
        logger.warning("Invalid PRO_PEN_PER_USD=%r — using 3.7", raw)
        pen_per_usd = 3.7
    if pen_per_usd <= 0:
        pen_per_usd = 3.7
    return round(float(PRO_PRICE_USD) * pen_per_usd, 2)


def _parse_pro_request_ref(external_reference: str) -> str | None:
    ref = (external_reference or "").strip()
    if not ref:
        return None
    if ref.upper().startswith("PRO-"):
        return ref.upper()
    m = _PRO_REF_RE.search(ref)
    return m.group(1).upper() if m else None


def _activate_pro_from_request(request_id: str, *, source: str) -> list[str]:
    """Mark subscription request paid and upgrade user to Pro."""
    req = db_find_subscription_request(request_id=request_id)
    if not req:
        return [f"request_not_found:{request_id}"]
    if (req.get("status") or "").lower() == "activated":
        return [f"already_activated:{request_id}"]

    username = (req.get("username") or "").strip()
    if not username:
        return [f"request_no_user:{request_id}"]

    db_set_subscription(username, "pro")
    db_mark_subscription_request_activated(request_id, username)
    actions = [f"pro_activated:{username}", f"request_closed:{request_id}"]

    try:
        from market_funnel import record_funnel_event

        record_funnel_event(
            "activated",
            username=username,
            meta={"source": source, "request_id": request_id},
            dedupe=True,
        )
    except Exception:
        pass

    try:
        email = (req.get("email") or "").strip() or db_get_user_email(username) or ""
        if email:
            from market_connectors.email_outbound import send_pro_activated_email

            mail = send_pro_activated_email(
                to_email=email,
                username=username,
                lang="es",
                subscription_id=request_id,
            )
            if mail.get("sent"):
                actions.append(f"activation_email:{email}")
    except Exception:
        logger.exception("Pro activation email failed for %s", username)

    return actions


def _record_plan_funnel_event(
    plan: str,
    *,
    username: str = "",
    email: str = "",
    source: str = "billing",
) -> None:
    try:
        from market_funnel import record_funnel_event

        event = "starter_subscribe" if plan == "starter" else "request_pro"
        record_funnel_event(
            event,
            username=username or None,
            meta={"email": email, "source": source},
            dedupe=False,
        )
    except Exception:
        pass


def _send_starter_payment_email(
    *,
    to_email: str,
    username: str,
    request_id: str,
    lang: str = "en",
    checkout_url: str = STARTER_CHECKOUT_URL,
) -> dict:
    from market_connectors.email_outbound import STARTER_PRICE_LABEL, _send

    if lang == "es":
        subject = "Tu acceso Pro — CLI Market"
        text = f"""Hola {username or ''},

Recibimos tu solicitud de CLI Market Pro.

Plan Pro — {STARTER_PRICE_LABEL}
• 20.000 consultas API / día
• Alertas + full MCP + checkout
• Exportación / historial

CHECKOUT STARTER → {checkout_url}

Referencia: {request_id}

Tras pagar en PayPal, Starter se activa en segundos (webhook). Verifique: market whoami

— Ricardo · CLI Market
hello@cli-market.dev
"""
    else:
        subject = "Your Pro access — CLI Market"
        text = f"""Hi {username or ''},

We received your CLI Market Pro request.

Pro plan — {STARTER_PRICE_LABEL}
• 20,000 API requests / day
• Alerts + full MCP + checkout
• CSV export / history

STARTER CHECKOUT → {checkout_url}

Reference: {request_id}

After PayPal payment, Starter activates in seconds (webhook). Verify: market whoami

— Ricardo · CLI Market
hello@cli-market.dev
"""
    html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0a0b;color:#e5e2e3;padding:24px;">
<h2 style="color:#3afecf;">CLI Market Pro</h2>
<p><a href="{checkout_url}" style="color:#002118;background:#3afecf;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:bold;">Pro checkout →</a></p>
</body></html>"""
    return _send(to_email, subject, text, html)


def process_starter_subscription_request(
    *,
    email: str,
    lang: str = "en",
    username: str = "",
    force: bool = False,
    note: str = "",
) -> dict:
    """Starter fallback: email self-serve checkout link when PayPal API is unavailable."""
    from market_connectors.email_outbound import send_starter_request_notify

    email = email.strip().lower()
    lang = (lang or "en").strip().lower()[:2]

    if not username:
        username = email.split("@")[0]

    recent = db_recent_subscription_request(email)
    if recent and not force:
        link = recent.get("payment_link") or STARTER_CHECKOUT_URL
        return {
            "ok": True,
            "request_id": recent["id"],
            "username": recent["username"],
            "email": recent["email"],
            "payment_link": link,
            "approve_url": link,
            "email_sent": bool(recent.get("email_sent")),
            "message": (
                "Ya enviamos el checkout Starter recientemente. Revise su bandeja (y spam)."
                if lang == "es"
                else "We already sent the Starter checkout recently. Check inbox (and spam)."
            ),
            "duplicate": True,
            "tier": "starter",
        }

    _record_plan_funnel_event(
        "starter",
        username=username,
        email=email,
        source="request_starter",
    )
    req = db_create_subscription_request(username, email, STARTER_CHECKOUT_URL, prefix="STR")
    sub_mail = _send_starter_payment_email(
        to_email=email,
        username=username,
        request_id=req["id"],
        lang=lang,
    )
    notify_mail = send_starter_request_notify(
        subscriber_email=email,
        request_id=req["id"],
        note=(note or f"username={username} · starter checkout fallback"),
    )
    if sub_mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])

    if lang == "es":
        message = (
            f"Le enviamos el checkout Starter a {email}."
            if sub_mail.get("sent")
            else f"Checkout Starter: {STARTER_CHECKOUT_URL}"
        )
    elif sub_mail.get("sent"):
        message = f"We emailed the Starter checkout link to {email}."
    else:
        message = f"Starter checkout: {STARTER_CHECKOUT_URL}"

    return {
        "ok": True,
        "request_id": req["id"],
        "username": username,
        "email": email,
        "payment_link": STARTER_CHECKOUT_URL,
        "approve_url": STARTER_CHECKOUT_URL,
        "email_sent": sub_mail.get("sent", False),
        "email_error": sub_mail.get("reason") if not sub_mail.get("sent") else None,
        "notify_sent": notify_mail.get("sent", False),
        "notify_error": notify_mail.get("reason") if not notify_mail.get("sent") else None,
        "message": message,
        "tier": "starter",
        "auto_activate": True,
    }


def process_pro_subscription_request(
    *,
    email: str,
    lang: str = "en",
    username: str = "",
    force: bool = False,
    note: str = "",
) -> dict:
    """Shared Pro request flow: dedupe, persist, email subscriber + notify hello@."""
    from market_connectors.email_outbound import PRO_PAYMENT_URL, send_pro_payment_email, send_pro_request_notify

    email = email.strip().lower()
    lang = (lang or "en").strip().lower()[:2]

    if not username:
        username = email.split("@")[0]

    recent = db_recent_subscription_request(email)
    if recent and not force:
        return {
            "ok": True,
            "request_id": recent["id"],
            "username": recent["username"],
            "email": recent["email"],
            "payment_link": recent["payment_link"] or PRO_PAYMENT_URL,
            "email_sent": bool(recent.get("email_sent")),
            "message": (
                "Ya enviamos el link de pago recientemente. Revisa tu bandeja (y spam). "
                "Pasa resend: true para reenviar."
                if lang == "es"
                else "We already sent a payment link recently. Check inbox (and spam). "
                "Pass resend: true to send again."
            ),
            "duplicate": True,
        }

    _record_plan_funnel_event("pro", username=username, email=email, source="request_pro")
    req = db_create_subscription_request(username, email, PRO_PAYMENT_URL)
    sub_mail = send_pro_payment_email(
        to_email=email,
        username=username,
        request_id=req["id"],
        lang=lang,
    )
    notify_mail = send_pro_request_notify(
        subscriber_email=email,
        username=username,
        request_id=req["id"],
        note=note,
    )
    if sub_mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])

    if lang == "es":
        if sub_mail.get("sent"):
            message = f"Te enviamos el link de pago a {email}. Activa Pro tras confirmar el pago."
        else:
            message = (
                f"Link de pago: {PRO_PAYMENT_URL}. "
                "Configura SMTP en el servidor para envío automático por email."
            )
    elif sub_mail.get("sent"):
        message = f"We emailed the payment link to {email}."
    else:
        message = f"Payment link: {PRO_PAYMENT_URL}. Configure SMTP for automatic email."

    return {
        "ok": True,
        "request_id": req["id"],
        "username": username,
        "email": email,
        "payment_link": PRO_PAYMENT_URL,
        "email_sent": sub_mail.get("sent", False),
        "email_error": sub_mail.get("reason") if not sub_mail.get("sent") else None,
        "notify_sent": notify_mail.get("sent", False),
        "notify_error": notify_mail.get("reason") if not notify_mail.get("sent") else None,
        "message": message,
        "auto_activate": False,
    }


@router.post("/billing/request-starter")
def request_starter_subscription(body: dict, authorization: str | None = Header(None)):
    """Request Starter — emails self-serve checkout when PayPal API is unavailable."""
    try:
        check_rate_limit("billing-request-starter")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        force = bool(body.get("resend"))
        note = (body.get("note") or body.get("use_case") or "").strip()

        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        username = (body.get("username") or "").strip()
        if authorization:
            try:
                username = require_user(authorization)
            except HTTPException:
                if not username:
                    raise

        return process_starter_subscription_request(
            email=email,
            lang=lang,
            username=username,
            force=force,
            note=note,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("request-starter failed")
        raise HTTPException(status_code=503, detail=f"billing unavailable: {e}") from e


@router.post("/billing/request-pro")
async def request_pro_subscription(body: dict, authorization: str | None = Header(None)):
    """Request Pro — PayPal subscription (webhook auto-activate) when API is configured.

    Falls back to hosted payment link + manual activation only if PayPal REST is unavailable.
    """
    try:
        check_rate_limit("billing-request-pro")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        force = bool(body.get("resend"))
        note = (body.get("note") or body.get("use_case") or "").strip()

        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        auth_user = ""
        if authorization:
            try:
                auth_user = require_user(authorization)
            except HTTPException:
                auth_user = ""

        username = (body.get("username") or "").strip()
        if auth_user:
            username = auth_user

        if not force:
            recent = db_recent_subscription_request(email)
            if recent:
                link = recent.get("payment_link") or ""
                auto = "billing/subscriptions" in link.lower() or "/subscriptions?" in link.lower()
                return {
                    "ok": True,
                    "request_id": recent["id"],
                    "username": recent["username"],
                    "email": recent["email"],
                    "payment_link": link,
                    "approve_url": link if auto else None,
                    "auto_activate": auto,
                    "email_sent": bool(recent.get("email_sent")),
                    "message": (
                        "Ya enviamos el enlace recientemente. Revisa tu bandeja (y spam)."
                        if lang == "es"
                        else "We already sent a link recently. Check inbox (and spam)."
                    ),
                    "duplicate": True,
                }

        username = _resolve_pro_username(
            email,
            body_username=username,
            auth_username=auth_user,
        )

        try:
            out = await _start_paypal_subscription(
                username,
                email,
                plan="pro",
                lang=lang,
                funnel_source="request_pro",
            )
            if out.get("ok"):
                out["payment_link"] = out.get("approve_url") or out.get("payment_link")
                if lang == "es":
                    out["message"] = (
                        "Confirme la suscripción en PayPal — Pro se activa en segundos vía webhook. "
                        + ("Le enviamos el enlace por email. " if out.get("email_sent") else "")
                        + "Luego: market whoami"
                    )
                else:
                    out["message"] = (
                        "Confirm subscription in PayPal — Pro activates in seconds via webhook. "
                        + ("We emailed you the link. " if out.get("email_sent") else "")
                        + "Then: market whoami"
                    )
                return out
        except ValueError:
            logger.info("request-pro: PayPal not configured, using hosted-button fallback")
        except Exception as e:
            logger.warning("request-pro: subscription failed (%s), using hosted-button fallback", e)

        return process_pro_subscription_request(
            email=email,
            lang=lang,
            username=username,
            force=force,
            note=note,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("request-pro failed")
        raise HTTPException(status_code=503, detail=f"billing unavailable: {e}") from e




def _start_pro_qr_checkout(
    username: str,
    email: str,
    *,
    method: str,
    lang: str,
    funnel_source: str,
) -> dict:
    """Yape/Plin QR for Pro — manual activation after payment confirmation."""
    from market_connectors.email_outbound import send_pro_payment_email, send_pro_request_notify
    from market_connectors.paypal_payments import PRO_PRICE_USD

    amount_pen = _pro_price_pen()
    payment_label = "plin" if method == "plin" else "yape"
    req = db_create_subscription_request(username, email, f"{payment_label}:S/{amount_pen:.2f}")
    request_id = req["id"]
    yape_number = os.getenv("YAPE_PLIN_NUMBER", "")
    qr_data = yape_number or f"{payment_label}-{request_id.lower()}"
    if yape_number:
        qr_data = f"yape://pay?phone={yape_number}&amount={amount_pen:.2f}&ref={request_id}"
    qr_url = (
        "https://api.qrserver.com/v1/create-qr-code/?size=240x240&data="
        + qr_data.replace(" ", "%20")
    )

    sub_mail = send_pro_payment_email(
        to_email=email,
        username=username,
        request_id=request_id,
        lang=lang,
    )
    notify_mail = send_pro_request_notify(
        subscriber_email=email,
        username=username,
        request_id=request_id,
        note=f"method={payment_label} amount_pen={amount_pen:.2f} usd={PRO_PRICE_USD}",
    )
    if sub_mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])

    _record_plan_funnel_event("pro", username=username, email=email, source=funnel_source)

    if lang == "es":
        message = (
            f"Escanea con {payment_label.capitalize()}. Monto: S/ {amount_pen:.2f} "
            f"(USD {PRO_PRICE_USD:.0f}/mes). Referencia: {request_id}. "
            "Pro se activa ≤24 h tras confirmar el pago."
        )
    else:
        message = (
            f"Scan with {payment_label.capitalize()}. Amount: S/ {amount_pen:.2f} "
            f"(USD {PRO_PRICE_USD:.0f}/mo). Reference: {request_id}. "
            "Pro activates within 24h after payment confirmation."
        )

    return {
        "ok": True,
        "request_id": request_id,
        "username": username,
        "email": email,
        "payment_method": payment_label,
        "amount_usd": float(PRO_PRICE_USD),
        "amount_pen": amount_pen,
        "currency": "PEN",
        "qr_reference": request_id,
        "qr_url": qr_url,
        "auto_activate": False,
        "email_sent": sub_mail.get("sent", False),
        "email_error": sub_mail.get("reason") if not sub_mail.get("sent") else None,
        "notify_sent": notify_mail.get("sent", False),
        "message": message,
    }


async def _start_pro_mercadopago_checkout(
    username: str,
    email: str,
    *,
    lang: str,
    funnel_source: str,
) -> dict:
    from market_connectors.mercadopago_payments import create_preference
    from market_connectors.email_outbound import send_pro_payment_email, send_pro_request_notify
    from market_connectors.paypal_payments import PRO_PRICE_USD

    amount_pen = _pro_price_pen()
    req = db_create_subscription_request(username, email, "mercadopago:pending")
    request_id = req["id"]

    mp = await create_preference(
        amount_pen,
        "PEN",
        f"CLI-Market-{request_id}",
        title="CLI Market Pro",
    )
    if not mp.get("checkout_url"):
        raise HTTPException(status_code=502, detail=mp.get("error", "Mercado Pago error"))

    checkout_url = mp["checkout_url"]
    sub_mail = send_pro_payment_email(
        to_email=email,
        username=username,
        request_id=request_id,
        lang=lang,
    )
    notify_mail = send_pro_request_notify(
        subscriber_email=email,
        username=username,
        request_id=request_id,
        note=f"method=mercadopago amount_pen={amount_pen:.2f} url={checkout_url}",
    )
    if sub_mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])

    _record_plan_funnel_event("pro", username=username, email=email, source=funnel_source)

    if lang == "es":
        message = (
            f"Complete el pago en Mercado Pago — S/ {amount_pen:.2f} "
            f"(USD {PRO_PRICE_USD:.0f}/mes). Referencia: {request_id}."
        )
    else:
        message = (
            f"Complete payment on Mercado Pago — S/ {amount_pen:.2f} "
            f"(USD {PRO_PRICE_USD:.0f}/mo). Reference: {request_id}."
        )

    return {
        "ok": True,
        "request_id": request_id,
        "username": username,
        "email": email,
        "payment_method": "mercadopago",
        "amount_usd": float(PRO_PRICE_USD),
        "amount_pen": amount_pen,
        "currency": "PEN",
        "checkout_url": checkout_url,
        "approve_url": checkout_url,
        "preference_id": mp.get("preference_id", ""),
        "auto_activate": True,
        "email_sent": sub_mail.get("sent", False),
        "email_error": sub_mail.get("reason") if not sub_mail.get("sent") else None,
        "notify_sent": notify_mail.get("sent", False),
        "message": message,
    }


@router.post("/billing/pro-checkout")
async def billing_pro_checkout(body: dict, authorization: str | None = Header(None)):
    """Pro billing from landing — PayPal, Mercado Pago, Yape, or Plin."""
    try:
        check_rate_limit("billing-pro-checkout")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        method = (body.get("payment_method") or "paypal").strip().lower()
        force = bool(body.get("resend"))

        if method not in _PRO_BILLING_METHODS:
            raise HTTPException(
                status_code=400,
                detail=f"payment_method must be one of: {', '.join(sorted(_PRO_BILLING_METHODS))}",
            )
        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        auth_user = ""
        if authorization:
            try:
                auth_user = require_user(authorization)
            except HTTPException:
                auth_user = ""

        username = _resolve_pro_username(
            email,
            body_username=(body.get("username") or ""),
            auth_username=auth_user,
        )

        if not force:
            recent = db_recent_subscription_request(email)
            if recent:
                link = recent.get("payment_link") or ""
                if method == "paypal" and (
                    "billing/subscriptions" in link.lower() or "/subscriptions?" in link.lower()
                ):
                    return {
                        "ok": True,
                        "request_id": recent["id"],
                        "username": recent["username"],
                        "email": recent["email"],
                        "payment_method": "paypal",
                        "payment_link": link,
                        "approve_url": link,
                        "auto_activate": True,
                        "email_sent": bool(recent.get("email_sent")),
                        "duplicate": True,
                        "message": (
                            "Ya enviamos el enlace PayPal recientemente. Revisa tu bandeja (y spam)."
                            if lang == "es"
                            else "We already sent the PayPal link recently. Check inbox (and spam)."
                        ),
                    }

        if method == "paypal":
            try:
                out = await _start_paypal_subscription(
                    username,
                    email,
                    plan="pro",
                    lang=lang,
                    funnel_source="landing_pro_checkout_paypal",
                )
                if out.get("ok"):
                    out["payment_method"] = "paypal"
                    out["payment_link"] = out.get("approve_url") or out.get("payment_link")
                    if lang == "es":
                        out["message"] = (
                            "Confirme la suscripción en PayPal — Pro se activa en segundos (webhook). "
                            + ("Le enviamos el enlace por email. " if out.get("email_sent") else "")
                            + "Luego: market whoami"
                        )
                    else:
                        out["message"] = (
                            "Confirm subscription in PayPal — Pro activates in seconds (webhook). "
                            + ("We emailed you the link. " if out.get("email_sent") else "")
                            + "Then: market whoami"
                        )
                    return out
            except ValueError:
                logger.info("pro-checkout paypal: not configured, using hosted-button fallback")
            except Exception as e:
                logger.warning("pro-checkout paypal failed (%s), using hosted-button fallback", e)

            out = process_pro_subscription_request(
                email=email,
                lang=lang,
                username=username,
                force=force,
            )
            out["payment_method"] = "paypal"
            out["approve_url"] = out.get("payment_link")
            return out

        if method in ("yape", "plin"):
            return _start_pro_qr_checkout(
                username,
                email,
                method=method,
                lang=lang,
                funnel_source=f"landing_pro_checkout_{method}",
            )

        return await _start_pro_mercadopago_checkout(
            username,
            email,
            lang=lang,
            funnel_source="landing_pro_checkout_mercadopago",
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=501, detail=str(e)) from e
    except Exception as e:
        logger.exception("billing_pro_checkout failed")
        raise HTTPException(status_code=503, detail=f"billing unavailable: {e}") from e


def _resolve_pro_username(
    email: str,
    *,
    body_username: str = "",
    auth_username: str = "",
) -> str:
    if auth_username:
        return auth_username.strip()
    if body_username.strip():
        return body_username.strip()
    prior = db_find_subscription_request(email=email.strip().lower())
    if prior and prior.get("username"):
        return prior["username"]
    local = email.split("@")[0].lower()
    safe = re.sub(r"[^a-z0-9_-]", "", local)[:32]
    return safe or f"user-{uuid.uuid4().hex[:8]}"


async def _start_paypal_subscription(
    username: str,
    email: str,
    *,
    plan: str = "pro",
    lang: str = "en",
    funnel_source: str = "paypal_subscribe",
) -> dict:
    from market_connectors.paypal_payments import STARTER_PRICE_USD, PRO_PRICE_USD, create_subscription
    from market_connectors.email_outbound import (
        send_pro_subscribe_pending_email,
        send_starter_subscribe_pending_email,
    )

    plan_l = "starter" if plan == "starter" else "pro"
    result = await create_subscription(username=username, plan=plan_l)
    if "approve_url" not in result:
        return {"error": result.get("error", "PayPal error"), "details": result}
    sub_id = result["subscription_id"]
    approve = result["approve_url"]
    db_save_billing_pending(sub_id, "paypal", username, plan_l)
    prefix = "STR" if plan_l == "starter" else "PRO"
    req = db_create_subscription_request(username, email, approve, prefix=prefix)
    if plan_l == "starter":
        mail = send_starter_subscribe_pending_email(
            to_email=email,
            username=username,
            approve_url=approve,
            request_id=req["id"],
            lang=lang,
        )
        amount_label = f"${STARTER_PRICE_USD:.0f}/mo"
        plan_label = "Starter"
    else:
        mail = send_pro_subscribe_pending_email(
            to_email=email,
            username=username,
            approve_url=approve,
            request_id=req["id"],
            lang=lang,
        )
        amount_label = f"${PRO_PRICE_USD:.0f}/mo"
        plan_label = "Pro"
    if mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])
    _record_plan_funnel_event(
        plan_l,
        username=username,
        email=email,
        source=funnel_source,
    )
    return {
        "ok": True,
        "subscription_id": sub_id,
        "approve_url": approve,
        "plan": plan_label,
        "tier": plan_l,
        "amount": amount_label,
        "username": username,
        "auto_activate": True,
        "request_id": req["id"],
        "email_sent": mail.get("sent", False),
        "email_error": mail.get("reason") if not mail.get("sent") else None,
    }

@router.post("/billing/paypal")
async def billing_paypal(authorization: str | None = Header(None)):
    """PayPal Subscription for Pro plan ($39/mo) — authenticated CLI path."""
    username = require_user(authorization)
    try:
        email = db_get_user_email(username) or f"{username}@cli-market.dev"
        out = await _start_paypal_subscription(
            username, email, plan="pro", lang="en", funnel_source="cli_billing_paypal",
        )
        if out.get("ok"):
            out["message"] = (
                "Confirme en PayPal; Pro se activa en segundos. Revise su email con el enlace."
                if out.get("email_sent")
                else "Confirme en PayPal; Pro se activa en segundos (email no enviado — SMTP)."
            )
            return out
        raise HTTPException(status_code=502, detail=out.get("error", "PayPal error"))
    except ValueError as e:
        return {"error": "PayPal no configurado", "detail": str(e)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("billing_paypal failed")
        return {"error": str(e)}


@router.post("/billing/paypal-subscribe")
async def billing_paypal_subscribe(body: dict, authorization: str | None = Header(None)):
    """PayPal Subscription from landing — auto-activate via webhook."""
    try:
        check_rate_limit("billing-paypal-subscribe")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        auth_user = ""
        if authorization:
            try:
                auth_user = require_user(authorization)
            except HTTPException:
                auth_user = ""

        username = _resolve_pro_username(
            email,
            body_username=(body.get("username") or ""),
            auth_username=auth_user,
        )

        out = await _start_paypal_subscription(
            username, email, plan="pro", lang=lang, funnel_source="landing_paypal_subscribe",
        )
        if not out.get("ok"):
            raise HTTPException(status_code=502, detail=out.get("error", "PayPal error"))

        if lang == "es":
            out["message"] = (
                "Confirme la suscripción en PayPal. "
                + ("Le enviamos el enlace por email. " if out.get("email_sent") else "")
                + "Luego: market whoami"
            )
        else:
            out["message"] = (
                "Confirm subscription in PayPal. "
                + ("We emailed you the link. " if out.get("email_sent") else "")
                + "Then: market whoami"
            )
        return out
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=501, detail=f"PayPal not configured: {e}") from e
    except Exception as e:
        logger.exception("billing_paypal_subscribe failed")
        raise HTTPException(status_code=503, detail=f"billing unavailable: {e}") from e


@router.post("/billing/starter")
async def billing_starter(authorization: str | None = Header(None)):
    """PayPal Subscription for Starter ($29/mo) — authenticated CLI path."""
    username = require_user(authorization)
    try:
        email = db_get_user_email(username) or f"{username}@cli-market.dev"
        out = await _start_paypal_subscription(
            username, email, plan="starter", lang="en", funnel_source="cli_billing_starter",
        )
        if out.get("ok"):
            out["message"] = (
                "Confirm on PayPal; Pro activates in seconds. Check your email for the link."
                if out.get("email_sent")
                else "Confirm on PayPal; Pro activates in seconds (email not sent — SMTP)."
            )
            return out
        raise HTTPException(status_code=502, detail=out.get("error", "PayPal error"))
    except ValueError as e:
        return {"error": "PayPal not configured", "detail": str(e)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("billing_starter failed")
        return {"error": str(e)}


@router.post("/billing/starter-subscribe")
async def billing_starter_subscribe(body: dict, authorization: str | None = Header(None)):
    """PayPal Starter subscription from landing — auto-activate via webhook."""
    try:
        check_rate_limit("billing-starter-subscribe")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        auth_user = ""
        if authorization:
            try:
                auth_user = require_user(authorization)
            except HTTPException:
                auth_user = ""

        username = _resolve_pro_username(
            email,
            body_username=(body.get("username") or ""),
            auth_username=auth_user,
        )

        out = await _start_paypal_subscription(
            username, email, plan="starter", lang=lang, funnel_source="landing_starter_subscribe",
        )
        if not out.get("ok"):
            raise HTTPException(status_code=502, detail=out.get("error", "PayPal error"))

        if lang == "es":
            out["message"] = (
                "Confirme Starter en PayPal. "
                + ("Le enviamos el enlace por email. " if out.get("email_sent") else "")
                + "Luego: market whoami"
            )
        else:
            out["message"] = (
                "Confirm Starter on PayPal. "
                + ("We emailed you the link. " if out.get("email_sent") else "")
                + "Then: market whoami"
            )
        return out
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=501, detail=f"PayPal not configured: {e}") from e
    except Exception as e:
        logger.exception("billing_starter_subscribe failed")
        raise HTTPException(status_code=503, detail=f"billing unavailable: {e}") from e


@router.post("/billing/checkout")
def billing_checkout(authorization: str | None = Header(None)):
    """Stripe Checkout — DISABLED until the activation loop is complete.

    Intentionally disabled: a Stripe Checkout session has no corresponding
    webhook to run ``db_set_subscription(username, "pro")`` on
    ``checkout.session.completed``. Re-enabling it without that handler would
    charge customers without granting Pro. Use PayPal (/billing/paypal), whose
    BILLING.SUBSCRIPTION.ACTIVATED webhook closes the loop, until the Stripe
    webhook + ``stripe`` dependency + real price id are wired up.
    """
    require_user(authorization)
    raise HTTPException(
        status_code=501,
        detail="Stripe checkout is temporarily unavailable. Use PayPal at /billing/paypal for Pro.",
    )
