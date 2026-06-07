#!/usr/bin/env python3
"""Rotate CLI Market secrets after repo privatization.

Auto-rotates (Railway + GitHub where applicable):
  - MARKET_API_TOKEN
  - CHECKOUT_WEBHOOK_SECRET

Manual rotation required (documented in output):
  - PEPY_API_KEY, SLACK_*, CLOUDFLARE_*, GH_PAT
  - PAYPAL_*, MERCADOPAGO_*, SMTP_*, ANTHROPIC_API_KEY, DATABASE_URL

Usage:
  python ops/rotate_secrets.py --apply
  python ops/rotate_secrets.py --apply --dry-run
"""

from __future__ import annotations

import argparse
import secrets
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "Treevu-ai/cli-market-world"
LOCAL_FILE = Path(__file__).resolve().parent / ".rotation-local.txt"


def _gen_market_token() -> str:
    return str(uuid.uuid4())


def _gen_webhook_secret() -> str:
    return "chk_ws_" + secrets.token_urlsafe(32)


def _resolve_exe(name: str) -> str:
    path = shutil.which(name) or shutil.which(f"{name}.cmd") or shutil.which(f"{name}.exe")
    if not path:
        raise FileNotFoundError(name)
    return path


def _run(cmd: list[str], *, input_text: str | None = None, cwd: Path | None = None) -> None:
    if cmd:
        cmd = [_resolve_exe(cmd[0]) if "/" not in cmd[0] and "\\" not in cmd[0] else cmd[0], *cmd[1:]]
    subprocess.run(
        cmd,
        input=input_text,
        text=True,
        check=True,
        cwd=cwd or ROOT,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply rotation")
    parser.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = parser.parse_args()

    if not args.apply:
        print("Pass --apply to rotate MARKET_API_TOKEN + CHECKOUT_WEBHOOK_SECRET")
        return 0

    market = _gen_market_token()
    checkout = _gen_webhook_secret()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    actions = [
        ("railway", ["railway", "variables", "--set", f"MARKET_API_TOKEN={market}"]),
        ("railway", ["railway", "variables", "--set", f"CHECKOUT_WEBHOOK_SECRET={checkout}"]),
        ("gh-secret", ["gh", "secret", "set", "MARKET_API_TOKEN", "-R", REPO]),
    ]

    if args.dry_run:
        print("DRY RUN — would rotate:")
        for kind, cmd in actions:
            print(f"  {kind}: {' '.join(cmd[:4])}...")
        return 0

    errors: list[str] = []
    for kind, cmd in actions:
        try:
            if kind == "gh-secret":
                _run(cmd, input_text=market + "\n")
            else:
                _run(cmd)
            print(f"OK {kind}")
        except subprocess.CalledProcessError as e:
            errors.append(f"{kind}: {(e.stderr or e.stdout or str(e)).strip()}")

    LOCAL_FILE.write_text(
        "\n".join(
            [
                f"# Rotated {ts} — gitignored, founder only",
                f"MARKET_API_TOKEN={market}",
                f"CHECKOUT_WEBHOOK_SECRET={checkout}",
                "",
                "# Update local shell:",
                '# $env:MARKET_API_TOKEN = "<value above>"',
            ]
        ),
        encoding="utf-8",
    )
    print(f"Local copy: {LOCAL_FILE}")

    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("Rotation applied. Railway restarts on variable change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())