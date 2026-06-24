"""Post messages to Slack channels (bot token or incoming webhook).

5-channel architecture (as of 2026-06-24):
  #command-control-cli-market  — CEO daily briefing: moat + post del día + KPIs
  #publicaciones               — post listo copy/paste (all networks consolidated here)
  #bitácora                    — ops logs: gate checks, CI, metrics updates
  #alertas                     — gate failures, critical errors (SLACK_CHANNEL_ALERTAS; defaults to bitácora)
  #revenue                     — subscriptions + funnel (SLACK_CHANNEL_REVENUE; defaults to funnel ID)

All per-network channel functions (linkedin, twitter, devto, etc.) are deprecated aliases
that now route to #publicaciones. Callers do not need to change.
"""

from __future__ import annotations

import os
import re

import httpx

# ── Canonical channel IDs ─────────────────────────────────────────────────────
DEFAULT_CHANNEL_PUBLICACIONES = "C0B6ZJ1B9B8"   # #publicaciones
DEFAULT_CHANNEL_BITACORA = "C0B6V3Y9ZSP"        # #bitácora
DEFAULT_CHANNEL_REVENUE = "C0B9G3T0T0A"         # #revenue (formerly funnel-cli-market)
COMMAND_CONTROL_CHANNEL_NAME = "command-control-cli-market"
REVENUE_CHANNEL_NAME = "revenue"

# ── Legacy channel IDs (kept for env-var overrides; routing consolidated above) ─
DEFAULT_CHANNEL_LINKEDIN_PERSONAL = "C0B96T74RE3"
DEFAULT_CHANNEL_LINKEDIN_COMPANY = "C0B9Q70C64R"
DEFAULT_CHANNEL_TWITTER = "C0B9NBU8X7C"
DEFAULT_CHANNEL_DEVTO = "C0B96TJC3CP"
DEFAULT_CHANNEL_REDDIT = "C0B9ND493GS"
DEFAULT_CHANNEL_HN = "C0BAGP1EHPA"
DEFAULT_CHANNEL_THREADS = "C0B9G1GA7PV"
DEFAULT_CHANNEL_INSTAGRAM = "C0B9S2WQ6SG"
DEFAULT_CHANNEL_WHATSAPP = "C0B9NELR490"
DEFAULT_CHANNEL_NEWSLETTER = "C0BAGNR374Y"
DEFAULT_CHANNEL_OUTBOUND = "C0B9NEEB97U"
DEFAULT_CHANNEL_REVISIONES_CURSOR = "C0B723TQS78"
DEFAULT_CHANNEL_CLI_MARKET_PRO = "C0B90LCEK0V"  # legacy; routes to #revenue
DEFAULT_CHANNEL_FUNNEL = "C0B9G3T0T0A"          # legacy; routes to #revenue
DEFAULT_CHANNEL_CEO_METRICS = "C0B9W7794BD"     # legacy; routes to #command-control
CLI_MARKET_PRO_CHANNEL_NAME = "suscripciones-cli-pro"
FUNNEL_CHANNEL_NAME = "funnel-cli-market"

MAX_SLACK_TEXT = 3900


# ── Canonical channel resolvers ───────────────────────────────────────────────

def channel_publicaciones() -> str:
    return os.getenv("SLACK_CHANNEL_PUBLICACIONES", DEFAULT_CHANNEL_PUBLICACIONES)


def channel_bitacora() -> str:
    return os.getenv("SLACK_CHANNEL_BITACORA", DEFAULT_CHANNEL_BITACORA)


def channel_alertas() -> str:
    """#alertas — gate failures and critical errors. Falls back to #bitácora if not configured."""
    return os.getenv("SLACK_CHANNEL_ALERTAS", "") or channel_bitacora()


def channel_revenue() -> str:
    """#revenue — subscriptions and funnel events."""
    return os.getenv("SLACK_CHANNEL_REVENUE", DEFAULT_CHANNEL_REVENUE)


def channel_revisiones_cursor() -> str:
    return os.getenv("SLACK_CHANNEL_REVISIONES_CURSOR", DEFAULT_CHANNEL_REVISIONES_CURSOR)


def _resolve_channel_by_name(token: str, name: str) -> str | None:
    """Lookup channel ID by name (needs channels:read or groups:read)."""
    cursor = ""
    for _ in range(20):
        payload: dict = {
            "types": "public_channel,private_channel",
            "limit": 200,
            "exclude_archived": True,
        }
        if cursor:
            payload["cursor"] = cursor
        r = httpx.post(
            "https://slack.com/api/conversations.list",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        body = r.json()
        if not body.get("ok"):
            return None
        for ch in body.get("channels", []):
            if ch.get("name") == name:
                return ch.get("id")
        cursor = (body.get("response_metadata") or {}).get("next_cursor", "")
        if not cursor:
            break
    return None


def channel_command_control() -> str:
    explicit = os.getenv("SLACK_CHANNEL_COMMAND_CONTROL", "").strip()
    if explicit:
        return explicit
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if token:
        resolved = _resolve_channel_by_name(token, COMMAND_CONTROL_CHANNEL_NAME)
        if resolved:
            return resolved
    raise ValueError(
        "Command & Control channel not configured. Set SLACK_CHANNEL_COMMAND_CONTROL "
        f"to the ID of #{COMMAND_CONTROL_CHANNEL_NAME}, or grant channels:read to the bot."
    )


# ── Deprecated channel aliases (all route to #publicaciones) ─────────────────

def channel_linkedin_personal() -> str:
    return channel_publicaciones()


def channel_linkedin_company() -> str:
    return channel_publicaciones()


def channel_twitter() -> str:
    return channel_publicaciones()


def channel_devto() -> str:
    return channel_publicaciones()


def channel_reddit() -> str:
    return channel_publicaciones()


def channel_hn() -> str:
    return channel_publicaciones()


def channel_threads() -> str:
    return channel_publicaciones()


def channel_instagram() -> str:
    return channel_publicaciones()


def channel_whatsapp() -> str:
    return channel_publicaciones()


def channel_newsletter() -> str:
    return channel_publicaciones()


def channel_outbound() -> str:
    return channel_publicaciones()


def channel_ceo_metrics() -> str:
    """Deprecated — CEO metrics now delivered to #command-control."""
    return channel_command_control()


def channel_funnel() -> str:
    """Deprecated — funnel events now delivered to #revenue."""
    return channel_revenue()


def channel_cli_market_pro() -> str:
    """Deprecated — pro subscription events now delivered to #revenue."""
    return channel_revenue()


def slack_channel_for_gtm_label(label: str) -> str | None:  # noqa: ARG001
    """All GTM network labels now route to #publicaciones."""
    return channel_publicaciones()


# ── Transport layer ───────────────────────────────────────────────────────────

def _chunk_text(text: str, limit: int = MAX_SLACK_TEXT) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for line in text.splitlines(keepends=True):
        if size + len(line) > limit and buf:
            chunks.append("".join(buf))
            buf = []
            size = 0
        buf.append(line)
        size += len(line)
    if buf:
        chunks.append("".join(buf))
    return chunks


def _md_to_slack_plain(text: str) -> str:
    """Lightweight markdown → Slack mrkdwn (non-fenced regions only)."""
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("### "):
            out.append(f"*{line[4:].strip()}*")
        elif line.startswith("## "):
            out.append(f"*{line[3:].strip()}*")
        elif line.startswith("# "):
            out.append(f"*{line[2:].strip()}*")
        elif line.startswith("|") and "---" not in line:
            out.append(line.replace("|", " ").strip())
        else:
            out.append(line.replace("**", "*"))
    return "\n".join(out)


def _md_to_slack(text: str) -> str:
    """Markdown → Slack mrkdwn; fenced ``` blocks pass through for copy-paste."""
    parts = re.split(r"(```[\s\S]*?```)", text)
    out: list[str] = []
    for part in parts:
        if part.startswith("```") and part.endswith("```"):
            out.append(part)
        else:
            transformed = _md_to_slack_plain(part)
            if transformed:
                out.append(transformed)
    return "\n".join(out)


def post_via_webhook(webhook_url: str, text: str) -> None:
    for chunk in _chunk_text(text):
        r = httpx.post(webhook_url, json={"text": chunk}, timeout=15)
        r.raise_for_status()


def post_via_bot(token: str, channel: str, text: str) -> None:
    slack_text = _md_to_slack(text)
    chunks = _chunk_text(slack_text)
    for i, chunk in enumerate(chunks):
        prefix = f"_(parte {i + 1}/{len(chunks)})_\n\n" if len(chunks) > 1 else ""
        r = httpx.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "text": prefix + chunk, "mrkdwn": True},
            timeout=15,
        )
        r.raise_for_status()
        body = r.json()
        if not body.get("ok"):
            raise RuntimeError(f"Slack API error: {body.get('error', body)}")


def post_blocks_via_bot(token: str, channel: str, *, text: str, blocks: list) -> None:
    r = httpx.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}"},
        json={"channel": channel, "text": text, "blocks": blocks, "mrkdwn": True},
        timeout=15,
    )
    r.raise_for_status()
    body = r.json()
    if not body.get("ok"):
        raise RuntimeError(f"Slack API error: {body.get('error', body)}")


def deliver(
    text: str,
    *,
    channel: str,
    webhook_url: str = "",
    bot_token: str = "",
) -> None:
    """Send text to a channel using bot token (preferred) or webhook."""
    token = bot_token or os.getenv("SLACK_BOT_TOKEN", "")
    hook = webhook_url.strip()

    if token:
        post_via_bot(token, channel, text)
        return
    if hook:
        post_via_webhook(hook, text)
        return
    raise ValueError(
        "Slack not configured: set SLACK_BOT_TOKEN or a channel-specific webhook URL"
    )


# ── Canonical deliver helpers ─────────────────────────────────────────────────

def deliver_to_bitacora(text: str) -> None:
    deliver(text, channel=channel_bitacora(), webhook_url=os.getenv("SLACK_WEBHOOK_BITACORA", ""))


def deliver_to_publicaciones(text: str) -> None:
    deliver(text, channel=channel_publicaciones(), webhook_url=os.getenv("SLACK_WEBHOOK_PUBLICACIONES", ""))


def deliver_to_alertas(text: str) -> None:
    """Send to #alertas (gate failures, critical errors). Falls back to #bitácora."""
    deliver(text, channel=channel_alertas(), webhook_url=os.getenv("SLACK_WEBHOOK_ALERTAS", ""))


def deliver_to_revenue(text: str, *, blocks: list | None = None) -> None:
    """Send subscription and funnel events to #revenue."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    channel = channel_revenue()
    if blocks and token:
        post_blocks_via_bot(token, channel, text=text, blocks=blocks)
        return
    deliver(text, channel=channel, webhook_url=os.getenv("SLACK_WEBHOOK_REVENUE", ""))


def deliver_to_command_control(text: str) -> None:
    deliver(text, channel=channel_command_control(), webhook_url=os.getenv("SLACK_WEBHOOK_COMMAND_CONTROL", ""))


def deliver_to_revisiones_cursor(text: str) -> None:
    deliver(text, channel=channel_revisiones_cursor(), webhook_url=os.getenv("SLACK_WEBHOOK_REVISIONES_CURSOR", ""))


def deliver_to_gtm_channel(label: str, text: str) -> str:
    """Post GTM copy to #publicaciones (all networks consolidated). Returns channel ID."""
    channel_id = channel_publicaciones()
    deliver(text, channel=channel_id, webhook_url=os.getenv("SLACK_WEBHOOK_PUBLICACIONES", ""))
    return channel_id


# ── Deprecated deliver aliases (callers unchanged, routing consolidated) ──────

def deliver_to_ceo_metrics(text: str) -> None:
    """Deprecated — CEO metrics now go to #command-control."""
    deliver_to_command_control(text)


def deliver_to_funnel(text: str) -> None:
    """Deprecated — funnel events now go to #revenue."""
    deliver_to_revenue(text)


def deliver_to_cli_market_pro(text: str, *, blocks: list | None = None) -> None:
    """Deprecated — pro subscription events now go to #revenue."""
    deliver_to_revenue(text, blocks=blocks)
