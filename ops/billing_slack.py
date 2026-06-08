"""Slack notifications for subscriptions → #suscripciones-cli-pro."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

TIER_LABELS: dict[str, str] = {
    "pro": "CLI Market Pro ($39)",
    "starter": "CLI Market Starter ($29)",
    "procure_starter": "Procure Starter ($29)",
    "procure_pro": "Procure Pro ($79)",
    "procure_builder": "Procure Builder ($149)",
}

_FUNNEL_LABELS: dict[str, str] = {
    "install": "pip install / primera ejecución",
    "register": "registro de cuenta",
    "login": "login CLI",
    "first_search": "primera búsqueda",
    "starter_subscribe": "checkout Starter iniciado",
    "starter_request": "solicitud Starter",
    "request_pro": "checkout Pro iniciado",
    "activated": "suscripción activada",
    "procure_subscribe": "checkout Procure iniciado",
}


def _slack_ready() -> bool:
    return bool(
        os.getenv("SLACK_BOT_TOKEN", "").strip()
        or os.getenv("SLACK_WEBHOOK_CLI_MARKET_PRO", "").strip()
    )


def tier_label(tier: str) -> str:
    key = (tier or "").strip().lower()
    return TIER_LABELS.get(key, key or "suscripción")


def format_subscription_message(
    *,
    tier: str,
    status: str,
    username: str = "",
    email: str = "",
    request_id: str = "",
    source: str = "",
    payment_method: str = "",
    amount_pen: float | None = None,
    amount_usd: float | None = None,
    plan: str = "",
) -> str:
    """Human-readable Slack mrkdwn for #suscripciones-cli-pro."""
    st = (status or "activated").strip().lower()
    label = tier_label(tier)
    if plan:
        label = f"{label} · {plan}"
    user = (username or "—").strip()
    mail = (email or "—").strip()
    ref = (request_id or "—").strip()
    src = (source or "—").strip()
    method = (payment_method or "—").strip()

    if st == "pending":
        lines = [
            f"⏳ *{label}* — pago pendiente",
            f"• ref: `{ref}`",
            f"• usuario CLI: `{user}`",
            f"• email: {mail}",
            f"• método: {method}",
        ]
        if amount_pen is not None:
            lines.append(f"• monto: S/ {amount_pen:.2f}")
        if amount_usd is not None:
            lines.append(f"• plan: ${amount_usd:.0f}/mes")
        if (tier or "").strip().lower() == "pro":
            lines.append(
                f"• activar tras confirmar: `python ops/slack_cli.py activate-pro {ref}`"
            )
        return "\n".join(lines)

    lines = [
        f"✅ *{label}* — suscripción activa",
        f"• usuario: `{user}`",
        f"• email: {mail}",
        f"• ref: `{ref}`",
        f"• método: {method}",
        f"• fuente: {src}",
        f"• verificar: `market whoami` → tier {(tier or 'pro').strip().lower()}",
    ]
    return "\n".join(lines)


def format_funnel_message(
    *,
    event: str,
    username: str = "",
    meta: dict | None = None,
) -> str:
    """Adoption funnel events (install, register, checkout starts)."""
    ev = (event or "").strip().lower()
    label = _FUNNEL_LABELS.get(ev, ev or "evento")
    user = (username or "—").strip()
    meta = meta or {}
    tier = (meta.get("tier") or meta.get("plan") or "").strip()
    email = (meta.get("email") or "").strip()
    source = (meta.get("source") or "").strip()
    lines = [f"📥 *{label}*", f"• usuario: `{user}`"]
    if tier:
        lines.append(f"• tier: {tier_label(tier) if tier in TIER_LABELS else tier}")
    if email:
        lines.append(f"• email: {email}")
    if source:
        lines.append(f"• fuente: {source}")
    return "\n".join(lines)


def pro_pending_slack_blocks(
    *,
    username: str = "",
    email: str = "",
    request_id: str = "",
    payment_method: str = "",
    amount_pen: float | None = None,
) -> list:
    """Slack blocks with Activar button (Pro manual Yape/Plin only)."""
    ref = (request_id or "—").strip()
    user = (username or "—").strip()
    mail = (email or "—").strip()
    method = (payment_method or "—").strip()
    lines = [
        "⏳ *CLI Market Pro ($39)* — pago pendiente",
        f"• ref: `{ref}` · usuario: `{user}`",
        f"• email: {mail} · método: {method}",
    ]
    if amount_pen is not None:
        lines.append(f"• monto: S/ {amount_pen:.2f}")
    lines.append(f"• CLI fallback: `python ops/slack_cli.py activate-pro {ref}`")
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(lines)}},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "action_id": "activate_pro_request",
                    "text": {"type": "plain_text", "text": "Activar Pro"},
                    "style": "primary",
                    "value": ref,
                }
            ],
        },
    ]


def notify_subscription(
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
) -> bool:
    """Post subscription event to #suscripciones-cli-pro. Never raises."""
    if not _slack_ready():
        logger.debug("Slack not configured; skip subscription notify")
        return False
    try:
        from slack_notify import deliver_to_cli_market_pro

        text = format_subscription_message(
            tier=tier,
            status=status,
            username=username,
            email=email,
            request_id=request_id,
            source=source,
            payment_method=payment_method,
            amount_pen=amount_pen,
            amount_usd=amount_usd,
            plan=plan,
        )
        blocks = None
        if (
            (status or "").strip().lower() == "pending"
            and (tier or "").strip().lower() == "pro"
            and os.getenv("SLACK_BOT_TOKEN", "").strip()
        ):
            blocks = pro_pending_slack_blocks(
                username=username,
                email=email,
                request_id=request_id,
                payment_method=payment_method,
                amount_pen=amount_pen,
            )
        deliver_to_cli_market_pro(text, blocks=blocks)
        return True
    except Exception as exc:
        logger.warning("Subscription Slack notify failed: %s", exc)
        return False


def notify_funnel_event(
    *,
    event: str,
    username: str = "",
    meta: dict | None = None,
) -> bool:
    """Post adoption funnel events (install, register, checkout) to subscriptions channel."""
    ev = (event or "").strip().lower()
    if ev not in _FUNNEL_LABELS:
        return False
    if not _slack_ready():
        return False
    try:
        from slack_notify import deliver_to_cli_market_pro

        deliver_to_cli_market_pro(
            format_funnel_message(event=ev, username=username, meta=meta),
        )
        return True
    except Exception as exc:
        logger.warning("Funnel Slack notify failed: %s", exc)
        return False


# Backward-compatible aliases
def format_pro_subscription_message(**kwargs) -> str:
    kwargs.setdefault("tier", "pro")
    return format_subscription_message(**kwargs)


def notify_pro_subscription(**kwargs) -> bool:
    kwargs.setdefault("tier", "pro")
    return notify_subscription(**kwargs)


def notify_build_pro_tier_activated(
    *,
    tier: str,
    username: str,
    email: str = "",
    request_id: str = "",
    source: str = "",
    payment_method: str = "",
) -> bool:
    """Activated subscription — any paid tier."""
    t = (tier or "").strip().lower()
    if t not in TIER_LABELS:
        return False
    return notify_subscription(
        tier=t,
        status="activated",
        username=username,
        email=email,
        request_id=request_id,
        source=source,
        payment_method=payment_method,
    )