"""Slack notifications for Build Pro subscriptions → #cli-market-pro."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

_BUILD_PRO_TIERS = frozenset({"pro"})


def _slack_ready() -> bool:
    return bool(
        os.getenv("SLACK_BOT_TOKEN", "").strip()
        or os.getenv("SLACK_WEBHOOK_CLI_MARKET_PRO", "").strip()
    )


def format_pro_subscription_message(
    *,
    status: str,
    username: str = "",
    email: str = "",
    request_id: str = "",
    source: str = "",
    payment_method: str = "",
    amount_pen: float | None = None,
    amount_usd: float | None = None,
) -> str:
    """Human-readable Slack mrkdwn for #cli-market-pro."""
    st = (status or "activated").strip().lower()
    user = (username or "—").strip()
    mail = (email or "—").strip()
    ref = (request_id or "—").strip()
    src = (source or "—").strip()
    method = (payment_method or "—").strip()
    lines: list[str]

    if st == "pending":
        lines = [
            "⏳ *CLI Market Pro* — pago pendiente",
            f"• ref: `{ref}`",
            f"• usuario CLI: `{user}`",
            f"• email: {mail}",
            f"• método: {method}",
        ]
        if amount_pen is not None:
            lines.append(f"• monto: S/ {amount_pen:.2f}")
        if amount_usd is not None:
            lines.append(f"• plan: ${amount_usd:.0f}/mes")
        lines.append(
            f"• activar tras confirmar: `python ops/slack_cli.py activate-pro {ref}`"
        )
        return "\n".join(lines)

    lines = [
        "✅ *CLI Market Pro* — suscripción activa",
        f"• usuario: `{user}`",
        f"• email: {mail}",
        f"• ref: `{ref}`",
        f"• método: {method}",
        f"• fuente: {src}",
        "• verificar: `market whoami` → tier pro",
    ]
    return "\n".join(lines)


def pro_pending_slack_blocks(
    *,
    username: str = "",
    email: str = "",
    request_id: str = "",
    payment_method: str = "",
    amount_pen: float | None = None,
) -> list:
    """Slack blocks with Activar button (requires bot token + SLACK_SIGNING_SECRET)."""
    ref = (request_id or "—").strip()
    user = (username or "—").strip()
    mail = (email or "—").strip()
    method = (payment_method or "—").strip()
    lines = [
        "⏳ *CLI Market Pro* — pago pendiente",
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


def notify_pro_subscription(
    *,
    status: str = "activated",
    username: str = "",
    email: str = "",
    request_id: str = "",
    source: str = "",
    payment_method: str = "",
    amount_pen: float | None = None,
    amount_usd: float | None = None,
) -> bool:
    """Post to #cli-market-pro. Never raises — billing must not fail on Slack."""
    if not _slack_ready():
        logger.debug("Slack not configured; skip CLI Market Pro notify")
        return False
    try:
        from slack_notify import deliver_to_cli_market_pro

        text = format_pro_subscription_message(
            status=status,
            username=username,
            email=email,
            request_id=request_id,
            source=source,
            payment_method=payment_method,
            amount_pen=amount_pen,
            amount_usd=amount_usd,
        )
        blocks = None
        if (status or "").strip().lower() == "pending" and os.getenv("SLACK_BOT_TOKEN", "").strip():
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
        logger.warning("CLI Market Pro Slack notify failed: %s", exc)
        return False


def notify_build_pro_tier_activated(
    *,
    tier: str,
    username: str,
    email: str = "",
    request_id: str = "",
    source: str = "",
    payment_method: str = "",
) -> bool:
    """Only Build Pro ($39) — not Procure or Starter."""
    if (tier or "").strip().lower() not in _BUILD_PRO_TIERS:
        return False
    return notify_pro_subscription(
        status="activated",
        username=username,
        email=email,
        request_id=request_id,
        source=source,
        payment_method=payment_method,
    )