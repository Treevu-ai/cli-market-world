#!/usr/bin/env python3
"""Verify Slack bot can post to bitácora and publicaciones channels.

Requires Bot Token scopes: chat:write (and chat:write.public if needed).
Does NOT require channels:read — uses chat.postMessage only.

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

HINTS = {
    "not_in_channel": "En Slack, en ese canal: /invite @{bot}",
    "channel_not_found": "Revisa SLACK_CHANNEL_* o que el bot tenga acceso al canal.",
    "missing_scope": "OAuth & Permissions → añade chat:write → Reinstall to Workspace.",
    "is_archived": "El canal está archivado.",
}


def _call(token: str, method: str, **kwargs) -> dict:
    r = httpx.post(
        f"https://slack.com/api/{method}",
        headers={"Authorization": f"Bearer {token}"},
        json=kwargs,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def main() -> None:
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print("❌ Set SLACK_BOT_TOKEN (Bot User OAuth Token xoxb-..., not client secret).")
        sys.exit(1)

    send_test = "--send-test" in sys.argv

    auth = _call(token, "auth.test")
    if not auth.get("ok"):
        print(f"❌ auth.test: {auth.get('error', auth)}")
        sys.exit(1)

    bot_user = auth.get("user", "bot")
    team = auth.get("team", "?")
    team_id = auth.get("team_id", "")
    url = (auth.get("url") or "").rstrip("/")
    print(f"✅ Workspace: {team}" + (f" ({team_id})" if team_id else ""))
    if url:
        print(f"   URL: {url}/")
    print(f"   Bot user: {bot_user}")
    print(
        "\nSi este workspace no es el correcto, generá un token nuevo en la app "
        "instalada en el workspace deseado (api.slack.com/apps → Reinstall)."
    )

    failed = False
    for label, cid in (
        ("Bitácora", channel_bitacora()),
        ("Publicaciones", channel_publicaciones()),
    ):
        print(f"  {label} ({cid})")
        if not send_test:
            print("    → dry-run (usa --send-test para postear)")
            continue

        data = _call(
            token,
            "chat.postMessage",
            channel=cid,
            text=f"🧪 Test CLI Market daily briefing — canal *{label}* OK.",
            mrkdwn=True,
        )
        if data.get("ok"):
            print("    ✅ mensaje de prueba enviado")
        else:
            failed = True
            err = data.get("error", "unknown")
            hint = HINTS.get(err, "").format(bot=bot_user)
            print(f"    ❌ chat.postMessage: {err}")
            if hint:
                print(f"       {hint}")

    if not send_test:
        print("\nEnviar ping de prueba:")
        print("  python3 ops/verify_slack.py --send-test")
        return

    if failed:
        sys.exit(1)
    print("\n✅ Slack listo para daily_briefing.py")


if __name__ == "__main__":
    main()
