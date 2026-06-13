from __future__ import annotations
import logging
import os
import uuid
from fastapi import APIRouter, Body, Header, HTTPException
from market_core import (
    db_clear_cart,
    db_create_order,
    db_find_order_by_gateway_ref,
    db_get_cart,
    db_set_order_gateway_ref,
    db_update_order_status,
)
from pre_checkout_validate import pre_checkout_validate
from server_deps import require_api_key, require_checkout_access, require_user
from routers.billing.activation import _wallet_manual_transfer_fields, _wallet_payment_phone
from routers.billing.notifications import _notify_procure_payment

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payments"])

_QR_SERVICE_URL = os.getenv("QR_SERVICE_URL", "https://api.qrserver.com/v1/create-qr-code/")


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
        "wise_qr_url": f"{_QR_SERVICE_URL}?size=250x250&data={wise_pay_me}" if _QR_SERVICE_URL else None,
        "instructions": {
            "pay_link": wise_pay_me,
            "reference": order_id,
            "amount_pen": total,
        },
        "message": "Escanea el QR o usa el link de Wise. Referencia obligatoria.",
    }


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
