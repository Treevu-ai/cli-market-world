"""Post messages to Slack channels (bot token or incoming webhook)."""

from __future__ import annotations

import os

import httpx

# CLI Market workspace — override via env if channels move
DEFAULT_CHANNEL_PUBLICACIONES = "C0B6ZJ1B9B8"  # publicaciones redes
DEFAULT_CHANNEL_BITACORA = "C0B6V3Y9ZSP"  # bitácora producto

MAX_SLACK_TEXT = 3900


def channel_publicaciones() -> str:
    return os.getenv("SLACK_CHANNEL_PUBLICACIONES", DEFAULT_CHANNEL_PUBLICACIONES)


def channel_bitacora() -> str:
    return os.getenv("SLACK_CHANNEL_BITACORA", DEFAULT_CHANNEL_BITACORA)


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


def _md_to_slack(text: str) -> str:
    """Lightweight markdown → Slack mrkdwn."""
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


def deliver_to_bitacora(text: str) -> None:
    deliver(
        text,
        channel=channel_bitacora(),
        webhook_url=os.getenv("SLACK_WEBHOOK_BITACORA", ""),
    )


def deliver_to_publicaciones(text: str) -> None:
    deliver(
        text,
        channel=channel_publicaciones(),
        webhook_url=os.getenv("SLACK_WEBHOOK_PUBLICACIONES", ""),
    )
