from __future__ import annotations
import logging
import os
import re
from market_core import (
    db_create_subscription_request,
    db_delete_billing_pending,
    db_find_subscription_request,
    db_get_user_email,
    db_mark_subscription_request_activated,
    db_mark_subscription_request_emailed,
    db_mark_subscription_requests_activated_for_user,
    db_recent_subscription_request,
    db_set_subscription,
)
from routers.billing.pro_helpers import is_manual_wallet_pro_payment_link
from routers.billing.notifications import (
    _append_pro_activation_email_actions,
    _append_procure_activation_email_actions,
    _pro_payment_method_from_request,
    _slack_notify_build_pro,
    _slack_notify_subscription,
)
logger = logging.getLogger(__name__)

STARTER_CHECKOUT_URL = os.getenv(
    "STARTER_PAYMENT_URL",
    "https://cli-market.dev/#pro-checkout",
)  # legacy env name kept for compat; value now points to Pro (pricing simplified)

_MANUAL_PRO_ACTIVATION_SOURCES = frozenset({"slack_interaction", "admin_api", "ops_manual"})

_PRO_REF_RE = re.compile(r"CLI-Market-(PRO-[A-Z0-9]+)", re.I)
_SUBSCRIPTION_REF_RE = re.compile(
    r"CLI-Market-(?P<id>(?:PRO|PCS|PCP|PCB|RGW)-[A-Z0-9]+)",
    re.I,
)
_BARE_SUBSCRIPTION_REF_RE = re.compile(r"^(PRO|PCS|PCP|PCB|RGW)-[A-Z0-9]+$", re.I)

RETAILER_GROWTH_PRICE_USD = 9


def _pro_price_pen() -> float:
    """USD Pro price converted to PEN for Yape/Plin/Mercado Pago."""
    from market_connectors.paypal_payments import PRO_PRICE_USD

    raw = os.getenv("PRO_PEN_PER_USD", "3.75")
    try:
        pen_per_usd = float(str(raw).strip())
    except (TypeError, ValueError):
        logger.warning("Invalid PRO_PEN_PER_USD=%r — using 3.7", raw)
        pen_per_usd = 3.7
    if pen_per_usd <= 0:
        pen_per_usd = 3.7
    return round(float(PRO_PRICE_USD) * pen_per_usd, 2)


def _retailer_growth_price_pen() -> float:
    """USD Retailer Growth price ($9) converted to PEN — reuses the Pro FX rate env var."""
    raw = os.getenv("PRO_PEN_PER_USD", "3.75")
    try:
        pen_per_usd = float(str(raw).strip())
    except (TypeError, ValueError):
        pen_per_usd = 3.7
    if pen_per_usd <= 0:
        pen_per_usd = 3.7
    return round(float(RETAILER_GROWTH_PRICE_USD) * pen_per_usd, 2)


def _wallet_payment_phone() -> str:
    return (os.getenv("YAPE_PLIN_NUMBER") or os.getenv("PLIN_NUMBER") or "").strip()


def _wallet_manual_transfer_fields(
    *,
    method: str,
    amount_pen: float,
    reference: str,
    lang: str,
    phone: str = "",
) -> dict:
    """Yape/Plin: in-app transfer (phone + amount + ref). QR deep-links are unreliable from web."""
    payment_label = "plin" if method == "plin" else "yape"
    app = "Plin" if method == "plin" else "Yape"
    verb_es = "Transfiere con Plin" if method == "plin" else "Yapea"
    verb_en = "Transfer with Plin" if method == "plin" else "Send via Yape"
    phone_line_es = (
        f"{verb_es} al número {phone}."
        if phone
        else "Usa el número que te enviamos por email (hello@cli-market.dev)."
    )
    phone_line_en = (
        f"{verb_en} to {phone}."
        if phone
        else "Use the phone number we email you (hello@cli-market.dev)."
    )
    if lang == "es":
        steps = [
            f"Abre la app {app} en tu celular.",
            phone_line_es,
            f"Monto exacto: S/ {amount_pen:.2f}",
            f"En mensaje o nota escribe: {reference}",
            "Pro se activa ≤24 h hábiles tras confirmar el pago.",
        ]
        message = (
            f"Paga con {app}: S/ {amount_pen:.2f} · ref {reference}. "
            + (f"Número: {phone}. " if phone else "")
            + "Copia los datos abajo o revisa tu email."
        )
    else:
        steps = [
            f"Open the {app} app on your phone.",
            phone_line_en,
            f"Exact amount: S/ {amount_pen:.2f}",
            f"In message or note write: {reference}",
            "Pro activates within 24 business hours after payment confirmation.",
        ]
        message = (
            f"Pay with {app}: S/ {amount_pen:.2f} · ref {reference}. "
            + (f"Phone: {phone}. " if phone else "")
            + "Copy the details below or check your email."
        )
    return {
        "payment_method": payment_label,
        "payment_mode": "manual_transfer",
        "payment_phone": phone or None,
        "manual_steps": steps,
        "message": message,
        "qr_url": None,
    }


def _parse_subscription_request_ref(external_reference: str) -> str | None:
    """Parse CLI-Market subscription billing refs: PRO-, PCS-, PCP-, PCB-."""
    ref = (external_reference or "").strip()
    if not ref:
        return None
    if _BARE_SUBSCRIPTION_REF_RE.match(ref):
        return ref.upper()
    m = _SUBSCRIPTION_REF_RE.search(ref)
    if m:
        return m.group("id").upper()
    m = _PRO_REF_RE.search(ref)
    return m.group(1).upper() if m else None


def _parse_pro_request_ref(external_reference: str) -> str | None:
    rid = _parse_subscription_request_ref(external_reference)
    if rid and rid.startswith("PRO-"):
        return rid
    ref = (external_reference or "").strip()
    if ref.upper().startswith("PRO-"):
        return ref.upper()
    m = _PRO_REF_RE.search(ref)
    return m.group(1).upper() if m else None


def _is_procure_subscription_request_id(request_id: str) -> bool:
    prefix = (request_id or "").split("-", 1)[0].upper()
    return prefix in ("PCS", "PCP", "PCB")


def _is_retailer_growth_subscription_request_id(request_id: str) -> bool:
    prefix = (request_id or "").split("-", 1)[0].upper()
    return prefix == "RGW"


def _activate_retailer_growth_from_request(request_id: str, *, source: str, force: bool = False) -> list[str]:
    """Mark a Retailer Growth ($9/mo) subscription request paid.

    Deliberately does NOT call db_set_subscription(...) — retailers have no
    CLI user/plan concept today. The team activates the Growth tier for the
    retailer's listing manually (same manual-verification pattern already
    used for the free listing flow), triggered by the Slack notification
    below rather than an automatic DB upgrade.
    """
    req = db_find_subscription_request(request_id=request_id)
    if not req:
        return [f"request_not_found:{request_id}"]
    if (req.get("status") or "").lower() == "activated" and not force:
        return [f"already_activated:{request_id}"]

    username = (req.get("username") or "").strip()
    db_mark_subscription_request_activated(request_id, username)
    actions = [f"retailer_growth_paid:{request_id}"]

    email = (req.get("email") or "").strip()
    _slack_notify_subscription(
        tier="retailer_growth",
        status="activated",
        username=username,
        email=email,
        request_id=request_id,
        source=source,
        amount_usd=float(RETAILER_GROWTH_PRICE_USD),
    )

    return actions


def tier_from_billing_kind(kind: str) -> str:
    """Map billing_pending.kind → subscriptions.tier."""
    k = (kind or "").strip().lower()
    if k.startswith("procure_"):
        return k
    if k == "starter":
        return "starter"
    return "pro"


def activate_paypal_subscription(
    *,
    username: str,
    sub_id: str,
    kind: str = "subscription",
    source: str = "paypal_webhook",
    lang: str = "es",
) -> list[str]:
    """Upgrade tier after PayPal subscription is ACTIVE (webhook or reconcile)."""
    username = (username or "").strip()
    if not username:
        return [f"subscription_no_user:{sub_id}"]

    tier = tier_from_billing_kind(kind)
    db_set_subscription(username, tier, paypal_subscription_id=sub_id or "")
    if sub_id:
        db_delete_billing_pending(sub_id)
    marked = db_mark_subscription_requests_activated_for_user(username)
    actions: list[str] = [f"{tier}_activated:{username}"]
    try:
        from market_funnel import record_funnel_event

        record_funnel_event(
            "activated",
            username=username,
            meta={"source": source, "tier": tier, "subscription_id": sub_id or None},
            dedupe=True,
        )
    except Exception:
        pass
    if marked:
        actions.append(f"requests_closed:{marked}")

    lang = (lang or "es").strip().lower()[:2]
    if lang not in ("es", "en"):
        lang = "es"
    email = db_get_user_email(username) or ""
    if tier in ("procure_starter", "procure_pro", "procure_builder"):
        _append_procure_activation_email_actions(
            actions,
            username=username,
            email=email,
            tier=tier,
            request_id=sub_id or "",
            payment_method="paypal",
            source=source,
            lang=lang,
        )
    elif tier in ("starter",):
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
            source=source,
            lang=lang,
            subscription_id=sub_id or "",
        )
    _slack_notify_subscription(
        tier=tier,
        username=username,
        email=email,
        request_id=sub_id or "",
        source=source,
        payment_method="paypal",
    )
    logger.info(
        "paypal subscription activated username=%s tier=%s subscription_id=%s source=%s actions=%s",
        username,
        tier,
        sub_id,
        source,
        actions,
    )
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
            dedupe=event in ("request_pro", "starter_subscribe"),
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
        subject = "Tu acceso Starter — CLI Market"
        text = f"""Hola {username or ''},

Recibimos tu solicitud de CLI Market Starter.

Plan Starter — {STARTER_PRICE_LABEL}
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
        subject = "Your Starter access — CLI Market"
        text = f"""Hi {username or ''},

We received your CLI Market Starter request.

Starter plan — {STARTER_PRICE_LABEL}
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
<h2 style="color:#3afecf;">CLI Market Starter</h2>
<p><a href="{checkout_url}" style="color:#002118;background:#3afecf;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:bold;">Starter checkout →</a></p>
</body></html>"""
    return _send(to_email, subject, text, html)


def _activate_pro_from_request(request_id: str, *, source: str, force: bool = False) -> list[str]:
    """Mark subscription request paid and upgrade user to Pro."""
    req = db_find_subscription_request(request_id=request_id)
    if not req:
        return [f"request_not_found:{request_id}"]
    if (req.get("status") or "").lower() == "activated":
        return [f"already_activated:{request_id}"]

    payment_link = (req.get("payment_link") or "").strip()
    if source in _MANUAL_PRO_ACTIVATION_SOURCES and not force:
        if not is_manual_wallet_pro_payment_link(payment_link):
            return [f"payment_not_manual:{request_id}"]

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

    method = _pro_payment_method_from_request(req)
    email = (req.get("email") or "").strip() or db_get_user_email(username) or ""
    _append_pro_activation_email_actions(
        actions,
        username=username,
        email=email,
        request_id=request_id,
        payment_method=method,
        source=source,
        display_name=(req.get("display_name") or "").strip(),
    )
    _slack_notify_build_pro(
        username=username,
        email=(req.get("email") or "").strip() or db_get_user_email(username) or "",
        request_id=request_id,
        source=source,
        payment_method=method,
    )

    return actions


def _activate_procure_from_request(request_id: str, *, source: str, force: bool = False) -> list[str]:
    """Mark Procure subscription request paid and upgrade user to procure_* tier."""
    from procure_billing import procure_tier_from_request_id

    req = db_find_subscription_request(request_id=request_id)
    if not req:
        return [f"request_not_found:{request_id}"]
    if (req.get("status") or "").lower() == "activated":
        return [f"already_activated:{request_id}"]

    payment_link = (req.get("payment_link") or "").strip()
    if source in _MANUAL_PRO_ACTIVATION_SOURCES and not force:
        if not is_manual_wallet_pro_payment_link(payment_link):
            return [f"payment_not_manual:{request_id}"]

    username = (req.get("username") or "").strip()
    if not username:
        return [f"request_no_user:{request_id}"]

    tier = procure_tier_from_request_id(request_id)
    if not tier:
        return [f"unknown_procure_request:{request_id}"]

    db_set_subscription(username, tier)
    db_mark_subscription_request_activated(request_id, username)
    actions = [f"{tier}_activated:{username}", f"request_closed:{request_id}"]

    try:
        from market_funnel import record_funnel_event

        record_funnel_event(
            "activated",
            username=username,
            meta={"source": source, "request_id": request_id, "tier": tier},
            dedupe=True,
        )
    except Exception:
        pass

    method = _pro_payment_method_from_request(req)
    email = (req.get("email") or "").strip() or db_get_user_email(username) or ""
    lang = "es"
    _append_procure_activation_email_actions(
        actions,
        username=username,
        email=email,
        tier=tier,
        request_id=request_id,
        payment_method=method,
        source=source,
        lang=lang,
    )

    _slack_notify_subscription(
        tier=tier,
        username=username,
        email=email,
        request_id=request_id,
        source=source,
        payment_method=method,
    )

    return actions


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

    _slack_notify_subscription(
        tier="starter",
        status="pending",
        username=username,
        email=email,
        request_id=req["id"],
        source="request_starter",
        payment_method="paypal",
        amount_usd=29.0,
    )

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
    display_name: str = "",
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
    req = db_create_subscription_request(
        username, email, PRO_PAYMENT_URL, display_name=display_name,
    )
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
