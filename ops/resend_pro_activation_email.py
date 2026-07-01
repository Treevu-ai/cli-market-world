#!/usr/bin/env python3
"""Resend Pro welcome email via admin API (new CLI password)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_API = "https://cli-market-api.fly.dev"


def main() -> int:
    p = argparse.ArgumentParser(description="Resend Pro activation email for PRO- request")
    p.add_argument("request_id", help="PRO-XXXXXXXX")
    p.add_argument("--email", default="", help="Optional override recipient email")
    p.add_argument("--api", default=os.getenv("MARKET_API_URL", DEFAULT_API), help="API base URL")
    args = p.parse_args()

    request_id = args.request_id.strip().upper()
    if not request_id.startswith("PRO-"):
        print(f"Invalid ref: {request_id}", file=sys.stderr)
        return 1

    token = (os.getenv("MARKET_API_TOKEN") or "").strip()
    if not token:
        print("MARKET_API_TOKEN not set", file=sys.stderr)
        return 1

    body = {"request_id": request_id}
    if args.email.strip():
        body["email"] = args.email.strip()

    url = f"{args.api.rstrip('/')}/admin/resend-pro-activation-email"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if payload.get("sent"):
        print(f"✓ Activation email sent to {payload.get('email')}")
        return 0
    print(f"⚠ Email not sent: {payload.get('reason') or payload.get('actions')}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
