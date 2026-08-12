#!/usr/bin/env python3
"""Configure #ventas-cli-market for sales digest.

1. Slack → Create channel `ventas-cli-market` (private recommended)
2. /invite @CLI Market (or your bot name)
3. Copy channel ID from channel details
4. python ops/setup_slack_ventas.py --channel-id C0XXXXXXXX --fly
5. python ops/slack_cli.py sales-digest

Usage:
  python ops/setup_slack_ventas.py
  python ops/setup_slack_ventas.py --channel-id C0XXXXXXXX --fly
  python ops/setup_slack_ventas.py --verify --send-test
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
    p = argparse.ArgumentParser(description="Setup Slack sales digest channel")
    p.add_argument(
        "--channel-id",
        default=os.getenv("SLACK_CHANNEL_VENTAS", ""),
        help="Slack channel ID for #ventas-cli-market",
    )
    p.add_argument("--fly", action="store_true", help="Set SLACK_CHANNEL_VENTAS on Fly.io")
    p.add_argument("--verify", action="store_true", help="Check bot can resolve channel")
    p.add_argument("--send-test", action="store_true", help="Post test digest")
    args = p.parse_args()

    print("Slack Ventas — pipeline y leads calientes\n")
    print("Canal objetivo: #ventas-cli-market")
    print("Contenido: [VENTAS] digest diario (leads, pipeline, deals)\n")

    channel_id = (args.channel_id or os.getenv("SLACK_CHANNEL_VENTAS", "")).strip()
    if channel_id:
        os.environ["SLACK_CHANNEL_VENTAS"] = channel_id
        print(f"SLACK_CHANNEL_VENTAS: {channel_id}")
        if args.fly:
            proc = subprocess.run(
                ["fly", "secrets", "set", f"SLACK_CHANNEL_VENTAS={channel_id}", "--app", "cli-market-api"],
                cwd=str(ROOT),
            )
            if proc.returncode != 0:
                return proc.returncode
            print("✓ Fly.io SLACK_CHANNEL_VENTAS actualizado")
    else:
        print(
            "SLACK_CHANNEL_VENTAS: pendiente\n"
            "  1. Crear #ventas-cli-market en Slack\n"
            "  2. /invite al bot\n"
            "  3. python ops/setup_slack_ventas.py --channel-id C0XXXXXXXX --fly"
        )

    if args.verify or args.send_test:
        if not channel_id:
            print("⚠ Necesitas --channel-id para verificar")
            return 1
        try:
            from slack_notify import deliver

            if args.send_test:
                text = (
                    "*[VENTAS]* Test digest\n"
                    "• Leads cold: 0\n"
                    "• Leads warm: 0\n"
                    "• Leads hot: 0\n"
                    "• Leads qualified: 0\n\n"
                    "— CLI Market Sales Funnel"
                )
                deliver(text, channel=channel_id)
                print("✓ Test post enviado")
        except Exception as e:
            print(f"Error: {e}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
