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
  POST /billing/build-checkout  Build tier checkout — starter | pro | pro_founding | pro_annual (landing)
  POST /billing/request-starter  Email Starter checkout link (fallback)
  POST /billing/paypal      PayPal Subscription (authenticated CLI)
  POST /billing/paypal-subscribe  PayPal Subscription (landing — auto-activate)
  POST /billing/procure-subscribe  Procure Copilot PayPal subscription (landing #procure)
  POST /billing/checkout    Stripe Checkout — DISABLED (no activation webhook yet)
  GET  /paypal-status       PayPal config diagnostic
  POST /checkout/mercadopago     Mercado Pago Checkout Pro (PEN)
  GET/POST /checkout/mercadopago-webhook  Mercado Pago IPN/webhooks
  GET  /mercadopago-status  Mercado Pago config diagnostic
  POST /checkout/validate   Pre-checkout price freshness gate (read-only)
"""

from __future__ import annotations

import logging
import os
import re
import uuid

import httpx
from fastapi import APIRouter, Body, Header, HTTPException, Request

from market_core import (
    db_claim_webhook_event,
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
    db_get_subscription,
    db_recent_subscription_request,
    db_update_subscription_request_payment_link,
    db_save_billing_pending,
    db_set_order_gateway_ref,
    db_set_subscription,
    db_update_order_status,
    db_clear_cart,
    db_create_order,
    db_get_cart,
)
from market_security import is_production_deploy, paypal_allow_unverified_webhooks
from routers.billing.pro_helpers import (
    duplicate_mp_checkout_payload,
    is_manual_wallet_pro_payment_link,
    is_mp_billing_method,
    mp_pay_note,
    wallet_manual_fallback_enabled,
)
from routers.billing.notifications import (
    _append_pro_activation_email_actions,
    _notify_procure_payment,
    _pro_payment_method_from_request,
    _send_pro_activated_email_with_credentials,
    _slack_notify_build_pro,
    _slack_notify_subscription,
    resend_pro_activation_email,
)
from routers.billing.activation import (
    _activate_pro_from_request,
    _parse_pro_request_ref,
    _pro_price_pen,
    _record_plan_funnel_event,
    _wallet_manual_transfer_fields,
    _wallet_payment_phone,
    process_pro_subscription_request,
    process_starter_subscription_request,
)
from pre_checkout_validate import pre_checkout_validate
from server_deps import check_rate_limit, require_api_key, require_checkout_access, require_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["payments"])

_ORDER_REF_RE = re.compile(r"CLI-Market-(ORD-[A-F0-9]+)", re.I)
_PRO_BILLING_METHODS = frozenset({"paypal", "yape", "plin", "mercadopago"})
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _cart_total(cart: list[dict]) -> float:
    return round(sum(i["price"] * i["quantity"] for i in cart), 2)


def _prepare_pending_order(
    username: str,
    method: str,
    idempotency_key: str | None = None,
) -> tuple[list[dict], float, str]:
    """Common preamble: get cart, compute total, create pending order, clear cart."""
    require_checkout_access(username)
    cart = db_get_cart(username)
    if not cart:
        raise HTTPException(status_code=400, detail="Carrito vacío")
    total = _cart_total(cart)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    idem = (idempotency_key or "").strip() or None
    created = db_create_order(
        username,
        cart,
        method,
        total,
        status="pending",
        order_id=order_id,
        idempotency_key=idem,
    )
    if created.get("idempotent_replay"):
        items = created.get("items") or cart
        if idem and abs(float(created.get("total", 0)) - total) > 0.01:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "idempotency_key_reused_with_different_cart",
                    "order_id": created["order_id"],
                },
            )
        return items, float(created["total"]), created["order_id"]
    db_clear_cart(username)
    return cart, total, created["order_id"]


@router.post("/checkout/validate")
def checkout_validate(authorization: str | None = Header(None)):
    """Validate cart prices and freshness without creating an order."""
    username = require_api_key(authorization)
    require_checkout_access(username)
    cart = db_get_cart(username)
    if not cart:
        raise HTTPException(status_code=400, detail="Carrito vacío")
    result = pre_checkout_validate(username, cart)
    if not result.ok:
        raise HTTPException(status_code=409, detail=result.to_dict())
    return result.to_dict()


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


def _tier_from_billing_kind(kind: str) -> str:
    """Map billing_pending.kind → subscriptions.tier."""
    k = (kind or "").strip().lower()
    if k.startswith("procure_"):
        return k
    if k == "starter":
        return "starter"
    return "pro"


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
            tier = _tier_from_billing_kind(kind)
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
            email = db_get_user_email(username) or ""
            lang = (resource.get("locale") or "es")[:2].lower()
            if lang not in ("es", "en"):
                lang = "es"
            if tier in ("starter", "procure_starter"):
                try:
                    if email:
                        from market_connectors.email_outbound import send_starter_activated_email

                        mail = send_starter_activated_email(
                            to_email=email,
                            username=username,
                            lang=lang,
                            subscription_id=sub_id,
                        )
                        if mail.get("sent"):
                            actions.append(f"activation_email:{email}")
                        else:
                            actions.append(f"activation_email_skipped:{mail.get('reason', 'err')}")
                    else:
                        actions.append("activation_email_skipped:no_email")
                except Exception:
                    logger.exception("%s activation email failed for %s", tier, username)
                    actions.append("activation_email_failed")
            else:
                _append_pro_activation_email_actions(
                    actions,
                    username=username,
                    email=email,
                    request_id="",
                    payment_method="paypal",
                    source="paypal_webhook",
                    lang=lang,
                    subscription_id=sub_id or "",
                )
            logger.info(
                "paypal_webhook subscription_activated username=%s tier=%s subscription_id=%s actions=%s",
                username,
                tier,
                sub_id,
                actions,
            )
            if (kind or "").strip().lower() == "pro_founding":
                try:
                    from market_billing import FOUNDING_PROMO_CODE, db_record_promo_redemption

                    db_record_promo_redemption(username, FOUNDING_PROMO_CODE, "pro_founding")
                    actions.append(f"founding_redeemed:{username}")
                except Exception:
                    logger.exception("founding promo redemption failed for %s", username)
            _slack_notify_subscription(
                tier=tier,
                username=username,
                email=db_get_user_email(username) or "",
                request_id=sub_id or "",
                source="paypal_webhook",
                payment_method="paypal",
            )
        else:
            actions.append(f"subscription_no_user:{sub_id}")

    elif event_type in ("BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.EXPIRED",
                        "BILLING.SUBSCRIPTION.SUSPENDED"):
        from market_core import db_get_subscription

        sub_id = resource.get("id", "")
        username = resource.get("custom_id") or ""
        pending = db_get_billing_pending(sub_id) if sub_id else None
        if not username and pending:
            username = (pending or {}).get("username", "")
        if username:
            prev_tier = (db_get_subscription(username) or {}).get("tier", "free")
            email = db_get_user_email(username) or ""
            if (prev_tier or "").strip().lower() not in ("", "free"):
                _slack_notify_subscription(
                    tier=prev_tier,
                    status="cancelled",
                    username=username,
                    email=email,
                    request_id=sub_id or "",
                    source=event_type,
                    payment_method="paypal",
                )
            db_set_subscription(username, "free", paypal_subscription_id="")
            if sub_id:
                db_delete_billing_pending(sub_id)
            actions.append(f"downgraded:{username}")

    return {"event_type": event_type, "actions": actions}


@router.post("/checkout/yape")
def checkout_yape(
    authorization: str | None = Header(None),
    body: dict | None = Body(None),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    username = require_user(authorization)
    payload = body or {}
    method = (payload.get("payment_method") or "yape").strip().lower()
    if method not in ("yape", "plin"):
        method = "yape"
    _, total, order_id = _prepare_pending_order(username, method, idempotency_key)
    phone = _wallet_payment_phone()
    lang = (payload.get("lang") or "es").strip().lower()[:2]
    wallet = _wallet_manual_transfer_fields(
        method=method,
        amount_pen=float(total),
        reference=order_id,
        lang=lang,
        phone=phone,
    )
    return {
        "order_id": order_id,
        "total": total,
        "currency": "PEN",
        "amount_pen": float(total),
        "request_id": order_id,
        "qr_reference": order_id,
        "status": "pending",
        "confirmation_mode": "manual",
        "capabilities": {"checkout_scope": "cli_market_internal"},
        "auto_activate": False,
        **wallet,
    }


@router.post("/checkout/lemon")
async def checkout_lemon(
    authorization: str | None = Header(None),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "lemon", idempotency_key)
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
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "paypal", idempotency_key)
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
async def checkout_wise(
    authorization: str | None = Header(None),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    username = require_user(authorization)
    _, total, order_id = _prepare_pending_order(username, "wise", idempotency_key)
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

    event_id = (
        body.get("id")
        or headers.get("paypal-transmission-id")
        or headers.get("PAYPAL-TRANSMISSION-ID")
        or ""
    )
    if event_id and not db_claim_webhook_event(str(event_id), "paypal"):
        logger.info("PayPal webhook duplicate ignored: %s", event_id)
        return {"received": True, "duplicate": True, "actions": []}

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
    event_key = f"checkout:{order_id}:{status}"
    if not db_claim_webhook_event(event_key, "checkout_webhook"):
        return {"order_id": order_id, "status": status, "duplicate": True, "message": "Already processed"}
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
        logger.info(
            "mercadopago_webhook pro_request_id=%s payment_id=%s actions=%s",
            pro_request_id,
            payment_id,
            actions,
        )
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


@router.post("/billing/request-pro", deprecated=True)
async def request_pro_subscription(body: dict, authorization: str | None = Header(None)):
    """Deprecated — use POST /billing/pro-checkout with payment_method=paypal."""
    logger.warning("DEPRECATED endpoint /billing/request-pro — use /billing/pro-checkout")
    check_rate_limit("billing-request-pro")
    delegated = {
        **body,
        "payment_method": body.get("payment_method") or "paypal",
        "resend": bool(body.get("resend")),
    }
    return await billing_pro_checkout(delegated, authorization)




def _start_pro_qr_checkout(
    username: str,
    email: str,
    *,
    method: str,
    lang: str,
    funnel_source: str,
    display_name: str = "",
) -> dict:
    """Yape/Plin QR for Pro — manual activation after payment confirmation."""
    from market_connectors.email_outbound import send_pro_payment_email, send_pro_request_notify
    from market_connectors.paypal_payments import PRO_PRICE_USD

    amount_pen = _pro_price_pen()
    payment_label = "plin" if method == "plin" else "yape"
    req = db_create_subscription_request(
        username, email, f"{payment_label}:S/{amount_pen:.2f}", display_name=display_name,
    )
    request_id = req["id"]
    phone = _wallet_payment_phone()
    wallet = _wallet_manual_transfer_fields(
        method=method,
        amount_pen=amount_pen,
        reference=request_id,
        lang=lang,
        phone=phone,
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

    _slack_notify_build_pro(
        status="pending",
        username=username,
        email=email,
        request_id=request_id,
        source=funnel_source,
        payment_method=payment_label,
        amount_pen=amount_pen,
        amount_usd=float(PRO_PRICE_USD),
    )

    return {
        "ok": True,
        "request_id": request_id,
        "username": username,
        "email": email,
        "amount_usd": float(PRO_PRICE_USD),
        "amount_pen": amount_pen,
        "currency": "PEN",
        "qr_reference": request_id,
        "auto_activate": False,
        "email_sent": sub_mail.get("sent", False),
        "email_error": sub_mail.get("reason") if not sub_mail.get("sent") else None,
        "notify_sent": notify_mail.get("sent", False),
        **wallet,
    }


async def _start_pro_mercadopago_checkout(
    username: str,
    email: str,
    *,
    lang: str,
    funnel_source: str,
    wallet_method: str = "",
    display_name: str = "",
) -> dict:
    from market_connectors.mercadopago_payments import create_preference
    from market_connectors.email_outbound import send_pro_payment_email, send_pro_request_notify
    from market_connectors.paypal_payments import PRO_PRICE_USD

    amount_pen = _pro_price_pen()
    wallet = (wallet_method or "").strip().lower()
    pay_note = mp_pay_note(wallet)
    req = db_create_subscription_request(username, email, pay_note, display_name=display_name)
    request_id = req["id"]

    mp_return = f"https://cli-market.dev/?mp=success&ref={request_id}#pricing"
    mp = await create_preference(
        amount_pen,
        "PEN",
        f"CLI-Market-{request_id}",
        title="CLI Market Pro",
        success_url=mp_return,
        pending_url=f"https://cli-market.dev/?mp=pending&ref={request_id}#pricing",
        failure_url=f"https://cli-market.dev/?mp=failure&ref={request_id}#pricing",
    )
    if not mp.get("checkout_url"):
        raise HTTPException(status_code=502, detail=mp.get("error", "Mercado Pago error"))

    checkout_url = mp["checkout_url"]
    db_update_subscription_request_payment_link(request_id, checkout_url)
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

    wallet_app = "Yape" if wallet == "yape" else "Plin" if wallet == "plin" else ""
    if lang == "es":
        if wallet_app:
            message = (
                f"Abre Mercado Pago y paga con {wallet_app} — S/ {amount_pen:.2f} "
                f"(USD {PRO_PRICE_USD:.0f}/mes). Pro se activa en minutos. Ref: {request_id}."
            )
        else:
            message = (
                f"Complete el pago en Mercado Pago — S/ {amount_pen:.2f} "
                f"(USD {PRO_PRICE_USD:.0f}/mes). Referencia: {request_id}."
            )
    else:
        if wallet_app:
            message = (
                f"Open Mercado Pago and pay with {wallet_app} — S/ {amount_pen:.2f} "
                f"(USD {PRO_PRICE_USD:.0f}/mo). Pro activates in minutes. Ref: {request_id}."
            )
        else:
            message = (
                f"Complete payment on Mercado Pago — S/ {amount_pen:.2f} "
                f"(USD {PRO_PRICE_USD:.0f}/mo). Reference: {request_id}."
            )

    display_method = wallet if wallet in ("yape", "plin") else "mercadopago"
    return {
        "ok": True,
        "request_id": request_id,
        "username": username,
        "email": email,
        "payment_method": display_method,
        "payment_rail": "mercadopago",
        "payment_mode": "mercadopago_checkout",
        "wallet_checkout": bool(wallet_app),
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

        auth_user = ""
        if authorization:
            try:
                auth_user = require_user(authorization)
            except HTTPException:
                auth_user = ""

        if not email and auth_user:
            email = (db_get_user_email(auth_user) or "").strip().lower()
        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        body_username = (body.get("username") or "").strip()
        if not auth_user and not body_username:
            raise HTTPException(
                status_code=400,
                detail=(
                    "username is required — run market login first or enter your CLI user"
                    if lang != "es"
                    else "usuario CLI requerido — ejecuta market login o ingresa tu usuario"
                ),
            )

        username = _resolve_pro_username(
            email,
            body_username=body_username,
            auth_username=auth_user,
        )
        display_name = (body.get("display_name") or body.get("name") or "").strip()

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
                if is_mp_billing_method(method):
                    dup = duplicate_mp_checkout_payload(recent, method=method, lang=lang)
                    if dup:
                        return dup

        if method == "paypal":
            plan = _normalize_build_plan(body.get("plan") or "pro")
            if plan == "pro_founding":
                _validate_founding_plan(username, body.get("promo_code") or "", lang=lang)
            try:
                out = await _start_paypal_subscription(
                    username,
                    email,
                    plan=plan,
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
                display_name=display_name,
                force=force,
            )
            out["payment_method"] = "paypal"
            out["approve_url"] = out.get("payment_link")
            return out

        manual_transfer = bool(body.get("manual_transfer")) and wallet_manual_fallback_enabled()

        if method in ("yape", "plin") and manual_transfer:
            return _start_pro_qr_checkout(
                username,
                email,
                method=method,
                lang=lang,
                funnel_source=f"landing_pro_checkout_{method}_manual",
                display_name=display_name,
            )

        if method in ("yape", "plin", "mercadopago"):
            wallet_method = method if method in ("yape", "plin") else ""
            return await _start_pro_mercadopago_checkout(
                username,
                email,
                lang=lang,
                funnel_source=f"landing_pro_checkout_{method}",
                wallet_method=wallet_method,
                display_name=display_name,
            )

        raise HTTPException(status_code=400, detail=f"unsupported payment_method: {method}")
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


async def _start_procure_subscription(
    username: str,
    email: str,
    *,
    plan_slug: str,
    lang: str = "en",
    funnel_source: str = "procure_subscribe",
) -> dict:
    """PayPal subscription for Procure Copilot tiers (kind = procure_* in billing_pending)."""
    from procure_billing import procure_plan_config
    from market_connectors.email_outbound import send_pro_subscribe_pending_email
    from market_connectors.paypal_payments import PAYPAL_API, _ensure_billing_plan, _get_access_token

    cfg = procure_plan_config(plan_slug)
    tier = cfg["tier"]
    amount = float(cfg["amount"])
    label = cfg["label"]
    prefix = cfg["request_prefix"]
    return_url = os.getenv(
        "PROCURE_SUBSCRIBE_RETURN_URL",
        "https://cli-market.dev/?sub=success&audience=procure#procure",
    )
    cancel_url = os.getenv(
        "PROCURE_SUBSCRIBE_CANCEL_URL",
        "https://cli-market.dev/?sub=cancelled&audience=procure#procure",
    )

    token = await _get_access_token()
    async with httpx.AsyncClient(timeout=15.0) as client:
        h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        plan_id = await _ensure_billing_plan(
            token,
            client,
            amount,
            "USD",
            env_plan_id=cfg["paypal_plan_id"],
            product_name=label,
            plan_name=f"{label} Monthly",
            description=f"${amount:.0f}/month — Procure Copilot",
        )
        p3 = await client.post(
            f"{PAYPAL_API}/v1/billing/subscriptions",
            json={
                "plan_id": plan_id,
                "custom_id": username,
                "application_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                    "brand_name": "Procure Copilot",
                    "user_action": "SUBSCRIBE_NOW",
                    "shipping_preference": "NO_SHIPPING",
                },
            },
            headers=h,
        )
        if p3.status_code not in (200, 201):
            return {"error": f"Subscription failed: {p3.text}"}
        data = p3.json()
        approve_link = next(
            (link["href"] for link in data.get("links", []) if link.get("rel") == "approve"),
            None,
        )
        sub_id = data["id"]

    db_save_billing_pending(sub_id, "paypal", username, tier)
    req = db_create_subscription_request(username, email, approve_link or "", prefix=prefix)
    mail = send_pro_subscribe_pending_email(
        to_email=email,
        username=username,
        approve_url=approve_link or "",
        request_id=req["id"],
        lang=lang,
    )
    if mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])
    try:
        from market_funnel import record_funnel_event

        record_funnel_event(
            "procure_subscribe",
            username=username,
            meta={"email": email, "source": funnel_source, "plan": plan_slug, "tier": tier},
            dedupe=False,
        )
    except Exception:
        pass
    _slack_notify_subscription(
        tier=tier,
        status="pending",
        username=username,
        email=email,
        request_id=req["id"],
        source=funnel_source,
        payment_method="paypal",
        amount_usd=amount,
        plan=label,
    )
    return {
        "ok": True,
        "subscription_id": sub_id,
        "approve_url": approve_link,
        "plan": label,
        "tier": tier,
        "procure_plan": plan_slug,
        "amount": f"${amount:.0f}/mo",
        "username": username,
        "auto_activate": True,
        "request_id": req["id"],
        "email_sent": mail.get("sent", False),
        "email_error": mail.get("reason") if not mail.get("sent") else None,
    }


def _normalize_build_plan(plan: str) -> str:
    from market_billing import normalize_billing_plan

    return normalize_billing_plan(plan)


def _validate_founding_plan(username: str, promo_code: str, *, lang: str) -> None:
    from market_billing import validate_founding_available

    ok, err = validate_founding_available(username, promo_code or "")
    if not ok:
        detail = err
        if lang == "es" and "full" in err.lower():
            detail = "Oferta Founding agotada (100 plazas)"
        raise HTTPException(status_code=400, detail=detail)


def _paypal_plan_labels(plan: str) -> tuple[str, str, float]:
    """Return (display_label, billing_kind, amount_usd) for PayPal checkout."""
    from market_billing import price_usd_for_plan

    p = _normalize_build_plan(plan)
    labels = {
        "starter": "Starter",
        "pro": "Pro",
        "pro_founding": "Pro Founding",
        "pro_annual": "Pro Annual",
    }
    return labels.get(p, "Pro"), p, price_usd_for_plan(p)


async def _start_paypal_subscription(
    username: str,
    email: str,
    *,
    plan: str = "pro",
    lang: str = "en",
    funnel_source: str = "paypal_subscribe",
) -> dict:
    from market_billing import price_label_for_plan, tier_for_billing_plan
    from market_connectors.paypal_payments import create_subscription
    from market_connectors.email_outbound import (
        send_pro_subscribe_pending_email,
        send_starter_subscribe_pending_email,
    )

    plan_slug = _normalize_build_plan(plan)
    plan_label, billing_kind, amount_usd = _paypal_plan_labels(plan_slug)
    tier = tier_for_billing_plan(plan_slug)
    amount_label = price_label_for_plan(plan_slug)
    return_url = os.getenv(
        "PRO_SUBSCRIBE_RETURN_URL",
        "https://cli-market.dev/?sub=success#pricing",
    )
    cancel_url = os.getenv(
        "PRO_SUBSCRIBE_CANCEL_URL",
        "https://cli-market.dev/?sub=cancelled#pricing",
    )
    result = await create_subscription(
        username=username,
        plan=plan_slug,
        return_url=return_url,
        cancel_url=cancel_url,
    )
    if "approve_url" not in result:
        return {"error": result.get("error", "PayPal error"), "details": result}
    sub_id = result["subscription_id"]
    approve = result["approve_url"]
    db_save_billing_pending(sub_id, "paypal", username, billing_kind)
    prefix = "STR" if plan_slug == "starter" else "PRO"
    req = db_create_subscription_request(username, email, approve, prefix=prefix)
    if plan_slug == "starter":
        mail = send_starter_subscribe_pending_email(
            to_email=email,
            username=username,
            approve_url=approve,
            request_id=req["id"],
            lang=lang,
        )
    else:
        mail = send_pro_subscribe_pending_email(
            to_email=email,
            username=username,
            approve_url=approve,
            request_id=req["id"],
            lang=lang,
        )
    if mail.get("sent"):
        db_mark_subscription_request_emailed(req["id"])
    _record_plan_funnel_event(
        tier,
        username=username,
        email=email,
        source=funnel_source,
    )
    _slack_notify_subscription(
        tier=tier,
        status="pending",
        username=username,
        email=email,
        request_id=req["id"],
        source=funnel_source,
        payment_method="paypal",
        amount_usd=amount_usd,
        plan=plan_label,
    )
    return {
        "ok": True,
        "subscription_id": sub_id,
        "approve_url": approve,
        "plan": plan_label,
        "tier": tier,
        "plan_slug": plan_slug,
        "amount": amount_label,
        "username": username,
        "auto_activate": True,
        "request_id": req["id"],
        "email_sent": mail.get("sent", False),
        "email_error": mail.get("reason") if not mail.get("sent") else None,
    }


@router.post("/billing/paypal")
async def billing_paypal(body: dict = Body(default={}), authorization: str | None = Header(None)):
    """PayPal subscription — CLI path (starter | pro | pro_founding | pro_annual)."""
    username = require_user(authorization)
    try:
        lang = (body.get("lang") or "en").strip().lower()[:2]
        plan = _normalize_build_plan(body.get("plan") or "pro")
        if plan == "pro_founding":
            _validate_founding_plan(username, body.get("promo_code") or "", lang=lang)
        email = db_get_user_email(username) or f"{username}@cli-market.dev"
        out = await _start_paypal_subscription(
            username,
            email,
            plan=plan,
            lang=lang,
            funnel_source="cli_billing_paypal",
        )
        if out.get("ok"):
            label = out.get("plan") or "Pro"
            out["message"] = (
                f"Confirme en PayPal; {label} se activa en segundos. Revise su email con el enlace."
                if lang == "es" and out.get("email_sent")
                else f"Confirme en PayPal; {label} se activa en segundos (email no enviado — SMTP)."
                if lang == "es"
                else f"Confirm on PayPal; {label} activates in seconds. Check your email for the link."
                if out.get("email_sent")
                else f"Confirm on PayPal; {label} activates in seconds (email not sent — SMTP)."
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


@router.post("/billing/paypal-subscribe", deprecated=True)
async def billing_paypal_subscribe(body: dict, authorization: str | None = Header(None)):
    """Deprecated — use POST /billing/pro-checkout with payment_method=paypal."""
    logger.warning("DEPRECATED endpoint /billing/paypal-subscribe — use /billing/pro-checkout")
    check_rate_limit("billing-paypal-subscribe")
    delegated = {**body, "payment_method": "paypal"}
    return await billing_pro_checkout(delegated, authorization)


@router.post("/billing/starter")
async def billing_starter(authorization: str | None = Header(None)):
    """PayPal Subscription for Build Starter ($24/mo) — authenticated CLI path."""
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


@router.post("/billing/procure-subscribe")
async def billing_procure_subscribe(body: dict, authorization: str | None = Header(None)):
    """Procure Copilot subscription from cli-market.dev/#procure — auto-activate via webhook."""
    try:
        check_rate_limit("billing-procure-subscribe")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        plan_slug = (body.get("plan") or "pro").strip().lower()

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

        out = await _start_procure_subscription(
            username,
            email,
            plan_slug=plan_slug,
            lang=lang,
            funnel_source="landing_procure_subscribe",
        )
        if not out.get("ok"):
            raise HTTPException(status_code=502, detail=out.get("error", "PayPal error"))

        if lang == "es":
            out["message"] = (
                "Confirme la suscripción Procure en PayPal. "
                + ("Le enviamos el enlace por email. " if out.get("email_sent") else "")
                + "Luego pegue su API key (market register → market account) en el dashboard Procure."
            )
        else:
            out["message"] = (
                "Confirm Procure subscription on PayPal. "
                + ("We emailed you the link. " if out.get("email_sent") else "")
                + "Then paste your API key (market register → market account) in the Procure dashboard."
            )
        return out
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("billing_procure_subscribe failed")
        raise HTTPException(status_code=503, detail=f"billing unavailable: {e}") from e


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


@router.post("/billing/build-checkout")
async def billing_build_checkout(body: dict, authorization: str | None = Header(None)):
    """Build tier PayPal checkout from landing — starter | pro | pro_founding | pro_annual."""
    try:
        check_rate_limit("billing-build-checkout")
        email = (body.get("email") or "").strip().lower()
        lang = (body.get("lang") or "en").strip().lower()[:2]
        method = (body.get("payment_method") or "paypal").strip().lower()
        plan = _normalize_build_plan(body.get("plan") or "pro")

        if method != "paypal":
            raise HTTPException(
                status_code=400,
                detail="build-checkout only supports payment_method=paypal",
            )
        if not email or not _EMAIL_RE.match(email):
            raise HTTPException(status_code=400, detail="valid email is required")

        auth_user = ""
        if authorization:
            try:
                auth_user = require_user(authorization)
            except HTTPException:
                auth_user = ""

        if plan != "starter" and not auth_user and not (body.get("username") or "").strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "username is required — run market login first or enter your CLI user"
                    if lang != "es"
                    else "usuario CLI requerido — ejecuta market login o ingresa tu usuario"
                ),
            )

        username = _resolve_pro_username(
            email,
            body_username=(body.get("username") or ""),
            auth_username=auth_user,
        )

        if plan == "pro_founding":
            _validate_founding_plan(username, body.get("promo_code") or "", lang=lang)

        out = await _start_paypal_subscription(
            username,
            email,
            plan=plan,
            lang=lang,
            funnel_source=f"landing_build_checkout_{plan}",
        )
        if not out.get("ok"):
            raise HTTPException(status_code=502, detail=out.get("error", "PayPal error"))

        label = out.get("plan") or "Pro"
        if lang == "es":
            out["message"] = (
                f"Confirme {label} en PayPal — se activa en segundos (webhook). "
                + ("Le enviamos el enlace por email. " if out.get("email_sent") else "")
                + "Luego: market whoami"
            )
        else:
            out["message"] = (
                f"Confirm {label} on PayPal — activates in seconds (webhook). "
                + ("We emailed you the link. " if out.get("email_sent") else "")
                + "Then: market whoami"
            )
        out["payment_method"] = "paypal"
        out["payment_link"] = out.get("approve_url") or out.get("payment_link")
        return out
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=501, detail=f"PayPal not configured: {e}") from e
    except Exception as e:
        logger.exception("billing_build_checkout failed")
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
