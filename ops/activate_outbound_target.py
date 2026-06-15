"""Cross-platform helper to activate an outbound target via the admin API.

Usage (works on Linux, macOS, and PowerShell/Windows):
    python ops/activate_outbound_target.py --target-id tottus-pe --start-date 2026-06-15
    py     ops/activate_outbound_target.py --target-id tottus-pe --start-date 2026-06-15

Reads MARKET_API_URL and MARKET_API_TOKEN from environment (or .env file).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def _load_env() -> None:
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def main() -> int:
    _load_env()

    parser = argparse.ArgumentParser(
        description="Activate an outbound target (mark Day 1 sent)"
    )
    parser.add_argument("--target-id", required=True, help="e.g. tottus-pe")
    parser.add_argument(
        "--start-date",
        required=True,
        help="Date Day 1 was sent, YYYY-MM-DD (e.g. 2026-06-15)",
    )
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument(
        "--api-url",
        default=os.getenv("MARKET_API_URL", "https://cli-market-production.up.railway.app"),
    )
    parser.add_argument("--api-token", default=os.getenv("MARKET_API_TOKEN", ""))
    args = parser.parse_args()

    if not args.api_token:
        print("ERROR: set MARKET_API_TOKEN env var or pass --api-token", file=sys.stderr)
        return 1

    url = f"{args.api_url.rstrip('/')}/admin/ops/activate-outbound-target"
    payload = json.dumps(
        {"target_id": args.target_id, "start_date": args.start_date, "notes": args.notes}
    ).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {args.api_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(f"ERROR {exc.code}: {body}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    dates = result.get("sequence_dates", {})
    if dates:
        print("\nFechas de seguimiento:")
        for day, dt in dates.items():
            print(f"  Día {day}: {dt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
