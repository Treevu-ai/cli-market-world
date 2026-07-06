#!/usr/bin/env python3
"""Configure #funnel-cli-market for adoption digest (separate from #suscripciones-cli-pro).

1. Slack → Create channel `funnel-cli-market` (public)
2. /invite @CLI Market (or your bot name)
3. Copy channel ID from channel details
4. python ops/setup_slack_funnel.py --channel-id C0XXXXXXXX --fly
5. python ops/slack_cli.py funnel-digest

Usage:
  python ops/setup_slack_funnel.py
  python ops/setup_slack_funnel.py --channel-id C0XXXXXXXX --fly
  python ops/setup_slack_funnel.py --verify --send-test
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops"))

from load_env import load_repo_env  # noqa: E402

load_repo_env()


def main() -> int:
    p = argparse.ArgumentParser(description="Setup Slack funnel digest channel")
    p.add_argument(
        "--channel-id",
        default=os.getenv("SLACK_CHANNEL_FUNNEL", "C0B9G3T0T0A"),
        help="Slack channel ID for #funnel-cli-market",
    )
    p.add_argument("--fly", action="store_true", help="Set SLACK_CHANNEL_FUNNEL on Fly.io")
    p.add_argument("--verify", action="store_true", help="Check bot can resolve channel")
    p.add_argument("--send-test", action="store_true", help="Post test digest")
    args = p.parse_args()

    print("Slack Funnel — adopción separada de #suscripciones-cli-pro\n")
    print("Canal objetivo: #funnel-cli-market")
    print("Contenido: [FUNNEL DIGEST] diario (registro, checkout, conversión)")
    print("Dinero sigue en: #suscripciones-cli-pro [REVENUE]\n")

    channel_id = (args.channel_id or os.getenv("SLACK_CHANNEL_FUNNEL", "")).strip()
    if channel_id:
        os.environ["SLACK_CHANNEL_FUNNEL"] = channel_id
        print(f"SLACK_CHANNEL_FUNNEL: {channel_id}")
        if args.fly:
            proc = subprocess.run(
                ["fly", "secrets", "set", f"SLACK_CHANNEL_FUNNEL={channel_id}", "--app", "cli-market-api"],
                cwd=str(ROOT),
            )
            if proc.returncode != 0:
                return proc.returncode
            print("✓ Fly.io SLACK_CHANNEL_FUNNEL actualizado")
    else:
        print(
            "SLACK_CHANNEL_FUNNEL: pendiente\n"
            "  1. Crear #funnel-cli-market en Slack\n"
            "  2. /invite al bot\n"
            "  3. python ops/setup_slack_funnel.py --channel-id C0XXXXXXXX --fly"
        )

    if args.verify or args.send_test:
        if not channel_id:
            print("⚠ Necesitas --channel-id para verificar")
            return 1
        try:
            from slack_notify import deliver_to_funnel

            if args.send_test:
                from billing_slack import format_funnel_digest_message

                deliver_to_funnel(format_funnel_digest_message(hours=24))
                print("✓ Digest de prueba enviado")
            else:
                deliver_to_funnel("🧪 Test #funnel-cli-market — canal OK.")
                print("✓ Mensaje de prueba enviado")
        except Exception as exc:
            print(f"⚠ Error: {exc}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())