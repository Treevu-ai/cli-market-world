#!/usr/bin/env python3
"""CLI para que Cursor (o el usuario) publique en Slack sin recordar IDs.

Usage:
  python3 ops/slack_cli.py briefing              # daily_briefing + Slack
  python3 ops/slack_cli.py briefing --dry-run    # solo archivos
  python3 ops/slack_cli.py campaign status       # día N, archivo, backlog
  python3 ops/slack_cli.py campaign sync         # sync_linkedin_metrics.py
  python3 ops/slack_cli.py post --bitacora "Hola"
  python3 ops/slack_cli.py post --publicaciones --file ops/daily/2026-05-29-content.md
  python3 ops/slack_cli.py post --revisiones-cursor "Resumen de PR"
  python3 ops/slack_cli.py command-control [--remote] [--dry-run]
  python3 ops/slack_cli.py verify [--send-test]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_env import load_repo_env  # noqa: E402

load_repo_env()

from slack_notify import (  # noqa: E402
    channel_bitacora,
    channel_publicaciones,
    channel_revisiones_cursor,
    deliver,
    deliver_to_bitacora,
    deliver_to_publicaciones,
    deliver_to_revisiones_cursor,
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
    elif channel == "revisiones_cursor":
        deliver_to_revisiones_cursor(text)
        print(f"OK → revisiones-cursor ({channel_revisiones_cursor()})")
    else:
        deliver(text, channel=channel)
        print(f"OK → {channel}")
    return 0


def cmd_briefing(dry_run: bool) -> int:
    args = [sys.executable, str(ROOT / "ops" / "daily_briefing.py")]
    if dry_run:
        args.append("--dry-run")
    return subprocess.call(args, cwd=ROOT)


def cmd_campaign_status() -> int:
    sys.path.insert(0, str(ROOT / "ops"))
    from content_paths import content_root, linkedin_dir, display_path  # noqa: E402

    start_s = os.getenv("LINKEDIN_CAMPAIGN_START", "2026-05-29")
    start = date.fromisoformat(start_s)
    today = date.today()
    day = (today - start).days + 1
    day_file = linkedin_dir() / f"Day-{day:02d}.md"
    root = content_root()
    print(f"LINKEDIN_CAMPAIGN_START={start_s}")
    print(f"Hoy {today.isoformat()} → Día {day} de 30")
    print(f"Content root: {root}")
    if day_file.is_file():
        print(f"Post: {display_path(day_file)}")
    else:
        print(f"Post: (no existe Day-{day:02d}.md en {linkedin_dir()})")
    catch_up = linkedin_dir() / "catch-up-plan.md"
    if catch_up.is_file():
        print(f"Plan: {display_path(catch_up)}")
    if not os.getenv("CLI_MARKET_CONTENT_DIR", "").strip():
        print(
            "Tip: export CLI_MARKET_CONTENT_DIR=/path/to/cli-market-content "
            "(o usa ../cli-market-content como sibling)"
        )
    print("Sync métricas: python3 ops/slack_cli.py campaign sync")
    return 0


def cmd_campaign_sync(dry_run: bool) -> int:
    args = [sys.executable, str(ROOT / "ops" / "sync_linkedin_metrics.py")]
    if dry_run:
        args.append("--dry-run")
    return subprocess.call(args, cwd=ROOT)


def cmd_command_control(dry_run: bool, remote: bool, slack: bool) -> int:
    args = [sys.executable, str(ROOT / "ops" / "command_control_daily.py")]
    if dry_run:
        args.append("--dry-run")
    if remote:
        args.append("--remote")
    if slack:
        args.append("--slack")
    return subprocess.call(args, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market Slack helper for Cursor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="Test SLACK_BOT_TOKEN")
    p_verify.add_argument("--send-test", action="store_true")

    p_post = sub.add_parser("post", help="Post message to a channel")
    p_post.add_argument("--bitacora", action="store_true", help="Bitácora producto")
    p_post.add_argument("--publicaciones", action="store_true", help="Publicaciones redes")
    p_post.add_argument(
        "--revisiones-cursor",
        action="store_true",
        dest="revisiones_cursor",
        help="Revisiones Cursor / Cloud Agent",
    )
    p_post.add_argument("--channel", help="Raw channel ID (override)")
    p_post.add_argument("--file", type=Path, help="Markdown file to post")
    p_post.add_argument("message", nargs="?", help="Message text")

    p_brief = sub.add_parser("briefing", help="Run daily briefing (+ Slack unless --dry-run)")
    p_brief.add_argument("--dry-run", action="store_true")

    p_camp = sub.add_parser("campaign", help="LinkedIn 30d campaign helpers")
    camp_sub = p_camp.add_subparsers(dest="camp_cmd", required=True)
    camp_sub.add_parser("status", help="Show campaign day and Day-XX file")
    p_sync = camp_sub.add_parser("sync", help="Refresh metrics in data-gate + Day-*.md")
    p_sync.add_argument("--dry-run", action="store_true")
    camp_sub.add_parser("assets", help="Regenerate all 30 LinkedIn PNG assets")
    camp_sub.add_parser("template-sync", help="Sync content template → content repo (incremental)")

    p_cc = sub.add_parser(
        "command-control",
        help="Founder ops panel → #command-control-cli-market",
    )
    p_cc.add_argument("--dry-run", action="store_true", help="Print only; no Slack/history")
    p_cc.add_argument("--remote", action="store_true", help="KPIs from production API")

    args = parser.parse_args()

    if args.command == "verify":
        return cmd_verify(args.send_test)
    if args.command == "briefing":
        return cmd_briefing(args.dry_run)
    if args.command == "campaign":
        if args.camp_cmd == "status":
            return cmd_campaign_status()
        if args.camp_cmd == "sync":
            return cmd_campaign_sync(args.dry_run)
        if args.camp_cmd == "assets":
            return subprocess.call(
                [sys.executable, str(ROOT / "ops" / "generate_all_linkedin_assets.py"), "--patch"],
                cwd=ROOT,
            )
        if args.camp_cmd == "template-sync":
            return subprocess.call(
                [sys.executable, str(ROOT / "ops" / "sync_content_template.py")],
                cwd=ROOT,
            )
    if args.command == "command-control":
        return cmd_command_control(
            dry_run=args.dry_run,
            remote=args.remote,
            slack=not args.dry_run,
        )
    if args.command == "post":
        if args.channel:
            ch = args.channel
        elif args.bitacora:
            ch = "bitacora"
        elif args.publicaciones:
            ch = "publicaciones"
        elif args.revisiones_cursor:
            ch = "revisiones_cursor"
        else:
            print(
                "Error: use --bitacora, --publicaciones, --revisiones-cursor, or --channel ID",
                file=sys.stderr,
            )
            return 1
        return cmd_post(ch, args.message, args.file)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
