from __future__ import annotations
import logging
import os
import httpx
from market_core import (
    db_find_subscription_request,
    db_get_subscription,
    db_get_user_email,
)
logger = logging.getLogger(__name__)


def _slack_notify_subscription(
    *,
    tier: str,
    status: str = "activated",
    username: str = "",
    email: str = "",
    request_id: str = "",
    source: str = "",
    payment_method: str = "",
    amount_pen: float | None = None,
    amount_usd: float | None = None,
    plan: str = "",
) -> None:
    """Post subscription events to #suscripciones-cli-pro (best-effort)."""
    try:
        import sys
        from pathlib import Path

        ops_dir = Path(__file__).resolve().parent.parent.parent / "ops"
        if str(ops_dir) not in sys.path:
            sys.path.insert(0, str(ops_dir))
        from billing_slack import (
            notify_build_pro_tier_activated,
            notify_subscription,
            notify_subscription_cancelled,
        )

        if status == "pending":
            notify_subscription(
                tier=tier,
                status="pending",
                username=username,
                email=email,
                request_id=request_id,
                source=source,
                payment_method=payment_method,
                amount_pen=amount_pen,
                amount_usd=amount_usd,
                plan=plan,
            )
            return
        if status == "cancelled":
            notify_subscription_cancelled(
                tier=tier,
                username=username,
                email=email,
                request_id=request_id,
                event_type=source,
                payment_method=payment_method,
            )
            return
        notify_build_pro_tier_activated(
            tier=tier,
            username=username,
            email=email,
            request_id=request_id,
            source=source,
            payment_method=payment_method,
        )
    except Exception as exc:
        logger.warning("subscriptions Slack notify skipped: %s", exc)


def _slack_notify_build_pro(**kwargs) -> None:
    """Backward-compat shim — Build Pro only."""
    kwargs.setdefault("tier", "pro")
    _slack_notify_subscription(**kwargs)


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


def _pro_payment_method_from_request(req: dict) -> str:
    pay_url = (req.get("payment_link") or "").strip().lower()
    if pay_url.startswith("plin:"):
        return "plin"
    if pay_url.startswith("mercadopago") or "mercadopago.com" in pay_url:
        return "mercadopago"
    if pay_url.startswith("paypal") or "paypal.com" in pay_url:
        return "paypal"
    if pay_url.startswith("yape:"):
        return "yape"
    return "yape"


def _send_pro_activated_email_with_credentials(**kwargs) -> dict:
    """Provision fresh CLI login password and email it to the Pro subscriber."""
    from account_service import build_pro_email_context, provision_pro_login_credentials
    from market_connectors.email_outbound import send_pro_activated_email

    username = (kwargs.get("username") or "").strip()
    password = provision_pro_login_credentials(username)
    ctx = build_pro_email_context(
        username,
        email=kwargs.get("to_email") or kwargs.get("email") or "",
        password=password,
        display_name=kwargs.get("display_name") or "",
        request_id=kwargs.get("request_id") or "",
        lang=kwargs.get("lang") or "es",
        payment_method=kwargs.get("payment_method") or "paypal",
    )
    return send_pro_activated_email(
        to_email=ctx["email"] or kwargs.get("to_email", ""),
        username=ctx["username"],
        lang=ctx["lang"],
        payment_method=ctx["payment_method"],
        request_id=ctx["request_id"],
        password=ctx["password"],
        display_name=ctx["display_name"],
        notify_ops=kwargs.get("notify_ops", True),
        source=kwargs.get("source", ""),
        subscription_id=kwargs.get("subscription_id", ""),
    )


def _append_pro_activation_email_actions(
    actions: list[str],
    *,
    username: str,
    email: str,
    request_id: str,
    payment_method: str,
    source: str,
    display_name: str = "",
    lang: str = "es",
    subscription_id: str = "",
) -> dict:
    """Send Pro welcome email; append audit tokens and log SMTP outcome."""
    billing_ref = request_id or subscription_id or "-"
    if not email:
        actions.append("activation_email_skipped:no_email")
        logger.warning(
            "Pro activation email skipped (no email) username=%s billing_ref=%s source=%s",
            username,
            billing_ref,
            source,
        )
        return {"sent": False, "reason": "no_email"}

    try:
        mail = _send_pro_activated_email_with_credentials(
            to_email=email,
            username=username,
            lang=lang,
            request_id=request_id,
            payment_method=payment_method,
            source=source,
            display_name=display_name,
            subscription_id=subscription_id,
        )
        if mail.get("sent"):
            actions.append(f"activation_email:{email}")
            logger.info(
                "Pro activation email sent to=%s username=%s billing_ref=%s source=%s",
                email,
                username,
                billing_ref,
                source,
            )
        else:
            reason = mail.get("reason", "err")
            actions.append(f"activation_email_skipped:{reason}")
            logger.warning(
                "Pro activation email skipped to=%s username=%s billing_ref=%s reason=%s source=%s",
                email,
                username,
                billing_ref,
                reason,
                source,
            )
        if mail.get("ops_notified"):
            actions.append(f"activation_draft_notify:{email}")
        return mail
    except Exception:
        logger.exception(
            "Pro activation email failed username=%s billing_ref=%s source=%s",
            username,
            billing_ref,
            source,
        )
        actions.append("activation_email_failed")
        return {"sent": False, "reason": "exception"}


def resend_pro_activation_email(
    request_id: str,
    *,
    source: str = "admin_resend",
    email_override: str = "",
) -> list[str]:
    """Resend Pro welcome email for an already-activated billing request."""
    req = db_find_subscription_request(request_id=request_id)
    if not req:
        return [f"request_not_found:{request_id}"]
    if (req.get("status") or "").lower() != "activated":
        return [f"request_not_activated:{request_id}"]

    username = (req.get("username") or "").strip()
    if not username:
        return [f"request_no_user:{request_id}"]

    sub = db_get_subscription(username) or {}
    if (sub.get("tier") or "").lower() != "pro":
        return [f"user_not_pro:{username}"]

    email = (
        (email_override or "").strip()
        or (req.get("email") or "").strip()
        or db_get_user_email(username)
        or ""
    )
    actions: list[str] = [f"resend:{request_id}"]
    _append_pro_activation_email_actions(
        actions,
        username=username,
        email=email,
        request_id=request_id,
        payment_method=_pro_payment_method_from_request(req),
        source=source,
        display_name=(req.get("display_name") or "").strip(),
    )
    return actions
