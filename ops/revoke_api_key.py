#!/usr/bin/env python3
"""Revoke a compromised API key via admin API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_API = "https://cli-market-api.fly.dev"


def main() -> int:
    p = argparse.ArgumentParser(description="Revoke leaked sk- API key")
    p.add_argument("api_key", help="Full sk-… key to revoke")
    p.add_argument("--api", default=os.getenv("MARKET_API_URL", DEFAULT_API), help="API base URL")
    args = p.parse_args()

    api_key = args.api_key.strip()
    if not api_key.startswith("sk-"):
        print(f"Invalid key prefix: {api_key[:12]}…", file=sys.stderr)
        return 1

    token = (os.getenv("MARKET_API_TOKEN") or "").strip()
    if not token:
        print("MARKET_API_TOKEN not set", file=sys.stderr)
        return 1

    url = f"{args.api.rstrip('/')}/v1/admin/revoke-api-key"
    req = urllib.request.Request(
        url,
        data=json.dumps({"api_key": api_key}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {err}", file=sys.stderr)
        return 1

    print(json.dumps(body, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
