"""Billing sub-router — /billing/* route handlers.

All POST /billing/* endpoints live here. payments.py is now a facade that
composes this router with routers/checkout/.
"""
from __future__ import annotations

import logging
import os
import re
import uuid

import httpx
from fastapi import APIRouter, Body, Header, HTTPException
from fastapi.responses import JSONResponse

from market_core import (
    db_create_subscription_request,
    db_find_subscription_request,
    db_get_user_email,
    db_mark_subscription_request_emailed,
    db_recent_subscription_request,
    db_save_billing_pending,
    db_update_subscription_request_payment_link,
)
from routers.billing.activation import (
    _pro_price_pen,
    _record_plan_funnel_event,
    _wallet_manual_transfer_fields,
    _wallet_payment_phone,
    process_pro_subscription_request,
    process_starter_subscription_request,
)
from routers.billing.notifications import (
    _slack_notify_build_pro,
    _slack_notify_subscription,
)
from routers.billing.pro_helpers import (
    duplicate_mp_checkout_payload,
    is_mp_billing_method,
    mp_pay_note,
    wallet_manual_fallback_enabled,
)
from server_deps import check_rate_limit, require_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payments"])

_PRO_BILLING_METHODS = frozenset({"paypal", "yape", "plin", "mercadopago"})
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.get("/v1/plans")
def list_plans(audience: str = "build"):
    """Canonical pricing — single source of truth for all clients.

    ?audience=build  → CLI Market developer plans (free/starter/pro/founding/annual)
    ?audience=procure → Procure Copilot B2B plans (free/starter/pro/builder/enterprise)
    """
    from market_billing import (
        PUBLIC_FREE_REQ_DAY,
        PUBLIC_STARTER_REQ_DAY,
        PUBLIC_PRO_REQ_DAY,
        PUBLIC_STARTER_PRICE_USD,
        PUBLIC_PRO_PRICE_USD,
        PUBLIC_PRO_FOUNDING_PRICE_USD,
        PUBLIC_PRO_ANNUAL_PRICE_USD,
        FOUNDING_SEAT_LIMIT,
    )
    from procure_billing import PROCURE_PLANS, PROCURE_TIER_LIMITS

    if audience == "procure":
        return {
            "audience": "procure",
            "currency": "USD",
            "plans": [
                {
                    "slug": "free",
                    "name": "Free",
                    "price": 0,
                    "period": None,
                    "limits": {"procurement_month": 5, "products_per_query": 3, "retailers_compare": 2, "checkout": False},
                },
                *(
                    {
                        "slug": slug,
                        "name": meta["label"],
                        "price": meta["amount"],
                        "period": "month",
                        "limits": {k: v for k, v in PROCURE_TIER_LIMITS.get(meta["tier"], {}).items()},
                    }
                    for slug, meta in PROCURE_PLANS.items()
                ),
                {
                    "slug": "enterprise",
                    "name": "Enterprise",
                    "price": None,
                    "period": "custom",
                    "limits": {"procurement_month": None, "products_per_query": 100, "retailers_compare": 38, "checkout": True},
                },
            ],
        }

    return {
        "audience": "build",
        "currency": "USD",
        "plans": [
            {"slug": "free", "name": "Free", "price": 0, "period": None, "req_day": PUBLIC_FREE_REQ_DAY, "checkout": False},
            {"slug": "starter", "name": "Starter", "price": PUBLIC_STARTER_PRICE_USD, "period": "month", "req_day": PUBLIC_STARTER_REQ_DAY, "checkout": False},
            {"slug": "pro", "name": "Pro", "price": PUBLIC_PRO_PRICE_USD, "period": "month", "req_day": PUBLIC_PRO_REQ_DAY, "checkout": True},
            {"slug": "pro_founding", "name": "Pro Founding", "price": PUBLIC_PRO_FOUNDING_PRICE_USD, "period": "month", "req_day": PUBLIC_PRO_REQ_DAY, "checkout": True, "seat_limit": FOUNDING_SEAT_LIMIT},
            {"slug": "pro_annual", "name": "Pro Annual", "price": PUBLIC_PRO_ANNUAL_PRICE_USD, "period": "year", "req_day": PUBLIC_PRO_REQ_DAY, "checkout": True},
            {"slug": "enterprise", "name": "Enterprise", "price": None, "period": "custom", "req_day": None, "checkout": True},
        ],
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
            detail = "Plan no disponible"
        raise HTTPException(status_code=400, detail=detail)


def _paypal_plan_labels(plan: str) -> tuple[str, str, float]:
    """Return (display_label, billing_kind, amount_usd) for PayPal checkout."""
    from market_billing import price_usd_for_plan

    p = _normalize_build_plan(plan)
    labels = {
        "starter": "Starter",
        "pro": "Pro",

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
    """PayPal subscription — CLI path (starter | pro | pro_annual)."""
    username = require_user(authorization)
    try:
        lang = (body.get("lang") or "en").strip().lower()[:2]
        plan = _normalize_build_plan(body.get("plan") or "pro")
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
    try:
        return await billing_pro_checkout(delegated, authorization)
    except HTTPException as exc:
        # Deprecated endpoint must always return ok for backwards compat (PAM: json_has [ok])
        return JSONResponse(
            status_code=exc.status_code,
            content={"ok": False, "error": exc.detail, "payment_method": "paypal"},
        )


@router.post("/billing/starter")
async def billing_starter(authorization: str | None = Header(None)):
    """PayPal Subscription for Build Starter ($9/mo) — authenticated CLI path."""
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
    """Build tier PayPal checkout from landing — starter | pro | pro_annual."""
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