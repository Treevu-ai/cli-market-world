from __future__ import annotations
import logging
import os
import re
from fastapi import APIRouter, HTTPException, Request
from market_core import (
    db_claim_webhook_event,
    db_delete_billing_pending,
    db_find_order_by_gateway_ref,
    db_find_order_by_id,
    db_get_billing_pending,
    db_get_user_email,
    db_set_order_gateway_ref,
    db_set_subscription,
    db_update_order_status,
)
from market_security import is_production_deploy, paypal_allow_unverified_webhooks
from routers.billing.activation import (
    _activate_pro_from_request,
    _activate_procure_from_request,
    _activate_retailer_growth_from_request,
    _is_procure_subscription_request_id,
    _is_retailer_growth_subscription_request_id,
    _parse_subscription_request_ref,
    activate_paypal_subscription,
)
from routers.billing.notifications import (
    _notify_procure_payment,
    _slack_notify_subscription,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payments"])

_ORDER_REF_RE = re.compile(r"CLI-Market-(ORD-[A-F0-9]+)", re.I)


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
    from routers.billing.activation import tier_from_billing_kind

    return tier_from_billing_kind(kind)


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
            lang = (resource.get("locale") or "es")[:2].lower()
            if lang not in ("es", "en"):
                lang = "es"
            actions.extend(
                activate_paypal_subscription(
                    username=username,
                    sub_id=sub_id,
                    kind=kind,
                    source="paypal_webhook",
                    lang=lang,
                )
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


@router.api_route("/checkout/mercadopago-webhook", methods=["GET", "POST"], operation_id="mercadopago_webhook")
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

    # A real payment notification is about to be processed — require signature
    # verification in production instead of silently accepting an unsigned
    # payload when MERCADOPAGO_WEBHOOK_SECRET simply isn't configured.
    if not secret and is_production_deploy():
        raise HTTPException(status_code=503, detail="Mercado Pago webhook secret required in production")

    if not db_claim_webhook_event(f"mp:{payment_id}", "mercadopago"):
        logger.info("Mercado Pago webhook duplicate ignored: %s", payment_id)
        return {"received": True, "duplicate": True, "actions": []}

    pay = await get_payment(payment_id)
    if pay.get("error"):
        return {"received": True, "payment_id": payment_id, "error": pay.get("error")}

    status = str(pay.get("status") or "").lower()
    ext_ref = str(pay.get("external_reference") or "")
    order_id = parse_external_order_id(ext_ref)
    actions: list[str] = []

    pro_request_id = _parse_subscription_request_ref(ext_ref)
    if status == "approved" and pro_request_id:
        if _is_procure_subscription_request_id(pro_request_id):
            actions.extend(
                _activate_procure_from_request(pro_request_id, source="mercadopago_webhook")
            )
        elif _is_retailer_growth_subscription_request_id(pro_request_id):
            actions.extend(
                _activate_retailer_growth_from_request(pro_request_id, source="mercadopago_webhook")
            )
        else:
            actions.extend(_activate_pro_from_request(pro_request_id, source="mercadopago_webhook"))
        logger.info(
            "mercadopago_webhook subscription_request_id=%s payment_id=%s actions=%s",
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
