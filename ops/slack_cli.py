#!/usr/bin/env python3
"""CLI para que Cursor (o el usuario) publique en Slack sin recordar IDs.

Usage:
  python3 ops/slack_cli.py briefing              # daily_briefing + Slack
  python3 ops/slack_cli.py briefing --dry-run    # solo archivos
  python3 ops/slack_cli.py post --bitacora "Hola"
  python3 ops/slack_cli.py post --publicaciones --file ops/daily/2026-05-29-content.md
  python3 ops/slack_cli.py verify [--send-test]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slack_notify import (  # noqa: E402
    channel_bitacora,
    channel_publicaciones,
    deliver,
    deliver_to_bitacora,
    deliver_to_publicaciones,
)

ROOT = Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cmd_verify(send_test: bool) -> int:
    args = [sys.executable, str(ROOT / "ops" / "verify_slack.py")]
    if send_test:
        args.append("--send-test")
    return subprocess.call(args)


def cmd_post(channel: str, text: str | None, file: Path | None) -> int:
    if file:
        body = _read_text(file)
        header = f"📎 *{file.relative_to(ROOT).as_posix()}*\n\n"
        text = header + body
    if not text or not text.strip():
        print("Error: provide MESSAGE or --file", file=sys.stderr)
        return 1

    if channel == "bitacora":
        deliver_to_bitacora(text)
        print(f"OK → bitácora ({channel_bitacora()})")
    elif channel == "publicaciones":
        deliver_to_publicaciones(text)
        print(f"OK → publicaciones ({channel_publicaciones()})")
    else:
        deliver(text, channel=channel)
        print(f"OK → {channel}")
    return 0


def cmd_briefing(dry_run: bool) -> int:
    args = [sys.executable, str(ROOT / "ops" / "daily_briefing.py")]
    if dry_run:
        args.append("--dry-run")
    return subprocess.call(args, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market Slack helper for Cursor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="Test SLACK_BOT_TOKEN")
    p_verify.add_argument("--send-test", action="store_true")

    p_post = sub.add_parser("post", help="Post message to a channel")
    p_post.add_argument("--bitacora", action="store_true", help="Bitácora producto")
    p_post.add_argument("--publicaciones", action="store_true", help="Publicaciones redes")
    p_post.add_argument("--channel", help="Raw channel ID (override)")
    p_post.add_argument("--file", type=Path, help="Markdown file to post")
    p_post.add_argument("message", nargs="?", help="Message text")

    p_brief = sub.add_parser("briefing", help="Run daily briefing (+ Slack unless --dry-run)")
    p_brief.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "verify":
        return cmd_verify(args.send_test)
    if args.command == "briefing":
        return cmd_briefing(args.dry_run)
    if args.command == "post":
        if args.channel:
            ch = args.channel
        elif args.bitacora:
            ch = "bitacora"
        elif args.publicaciones:
            ch = "publicaciones"
        else:
            print("Error: use --bitacora, --publicaciones, or --channel ID", file=sys.stderr)
            return 1
        return cmd_post(ch, args.message, args.file)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
