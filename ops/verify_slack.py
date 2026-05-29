#!/usr/bin/env python3
"""Verify Slack bot can post to bitácora and publicaciones channels.

Usage:
  SLACK_BOT_TOKEN=xoxb-... python3 ops/verify_slack.py
  SLACK_BOT_TOKEN=xoxb-... python3 ops/verify_slack.py --send-test
"""

from __future__ import annotations

import os
import sys

import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slack_notify import channel_bitacora, channel_publicaciones


def _api(token: str, method: str, **kwargs) -> dict:
    r = httpx.post(
        f"https://slack.com/api/{method}",
        headers={"Authorization": f"Bearer {token}"},
        json=kwargs,
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"{method}: {data.get('error', data)}")
    return data


def main() -> None:
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print("❌ Set SLACK_BOT_TOKEN (Bot User OAuth Token xoxb-..., not client secret).")
        sys.exit(1)

    send_test = "--send-test" in sys.argv

    auth = _api(token, "auth.test")
    print(f"✅ Bot: {auth.get('user')} · team: {auth.get('team')}")

    for label, cid in (
        ("Bitácora", channel_bitacora()),
        ("Publicaciones", channel_publicaciones()),
    ):
        info = _api(token, "conversations.info", channel=cid)
        ch = info.get("channel", {})
        name = ch.get("name", "?")
        is_member = ch.get("is_member", False)
        status = "✅ en canal" if is_member else "⚠️ invita al bot: /invite @" + auth.get("user", "bot")
        print(f"  {label} #{name} ({cid}): {status}")

        if send_test and is_member:
            _api(
                token,
                "chat.postMessage",
                channel=cid,
                text=f"🧪 Test CLI Market daily briefing — canal *{label}* OK.",
                mrkdwn=True,
            )
            print(f"    → mensaje de prueba enviado")

    if not send_test:
        print("\nPara enviar un ping de prueba: python3 ops/verify_slack.py --send-test")


if __name__ == "__main__":
    main()
