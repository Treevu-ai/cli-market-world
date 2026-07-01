#!/usr/bin/env python3
"""Enable Slack «Activar Pro» button (Interactivity + Signing Secret).

1. api.slack.com/apps → tu app → Basic Information → Signing Secret
2. Interactivity & Shortcuts → ON → Request URL:
   https://cli-market-api.fly.dev/slack/interactions
3. Set SLACK_SIGNING_SECRET=<secret> on the API's hosting platform (Fly.io: `fly secrets set`)

Usage (PowerShell: usar comillas, sin <>):
  python ops/setup_slack_interactivity.py
  python ops/setup_slack_interactivity.py --signing-secret "abc123..."
  python ops/setup_slack_interactivity.py --signing-secret "abc123..." --railway  # legacy: sets it on Railway instead
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ops"))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

API_BASE = os.getenv(
    "MARKET_API_URL",
    "https://cli-market-api.fly.dev",
).rstrip("/")
INTERACTIONS_URL = f"{API_BASE}/slack/interactions"


def main() -> int:
    p = argparse.ArgumentParser(description="Configure Slack interactivity for Pro activation")
    p.add_argument("--signing-secret", help="Slack app Signing Secret (from api.slack.com)")
    p.add_argument("--railway", action="store_true", help="Set SLACK_SIGNING_SECRET on Railway")
    p.add_argument("--verify", action="store_true", help="Probe interactions endpoint")
    args = p.parse_args()

    print("Slack Interactivity — Activar Pro desde #suscripciones-cli-pro\n")
    print(f"Request URL (pegar en Slack app):\n  {INTERACTIONS_URL}\n")

    secret = (args.signing_secret or os.getenv("SLACK_SIGNING_SECRET", "")).strip()
    if secret:
        print("SLACK_SIGNING_SECRET: configurado localmente")
        if args.railway:
            railway = "railway.cmd" if sys.platform == "win32" else "railway"
            proc = subprocess.run(
                [railway, "variables", "set", f"SLACK_SIGNING_SECRET={secret}"],
                cwd=str(ROOT),
            )
            if proc.returncode != 0:
                return proc.returncode
            print("✓ Railway SLACK_SIGNING_SECRET actualizado")
    else:
        print(
            "SLACK_SIGNING_SECRET: pendiente\n"
            "  api.slack.com/apps → Basic Information → App Credentials → Signing Secret\n"
            '  python ops/setup_slack_interactivity.py --signing-secret "TU_SECRET" --railway'
        )

    if args.verify or secret:
        try:
            import httpx

            r = httpx.post(INTERACTIONS_URL, data={"payload": "{}"}, timeout=15)
            if r.status_code == 503 and "SLACK_SIGNING_SECRET" in r.text:
                print(f"⚠ Endpoint vivo pero falta secret en servidor ({r.status_code})")
            elif r.status_code == 401:
                print("✓ Endpoint vivo — rechaza requests sin firma (esperado)")
            else:
                print(f"Endpoint respondió: {r.status_code}")
        except Exception as exc:
            print(f"⚠ No se pudo verificar endpoint: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())