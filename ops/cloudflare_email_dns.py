#!/usr/bin/env python3
"""Add SPF + DMARC TXT records for cli-market.dev (Google Workspace SMTP).

Usage:
  set CLOUDFLARE_API_TOKEN=...
  python ops/cloudflare_email_dns.py
  python ops/cloudflare_email_dns.py --dry-run

Token permissions: Zone → DNS → Edit, Zone → Zone → Read
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.cloudflare.com/client/v4"
ZONE_NAME = "cli-market.dev"

RECORDS = (
    {
        "name": ZONE_NAME,
        "type": "TXT",
        "content": "v=spf1 include:_spf.google.com ~all",
        "comment": "CLI Market SPF — Google Workspace outbound",
    },
    {
        "name": f"_dmarc.{ZONE_NAME}",
        "type": "TXT",
        "content": "v=DMARC1; p=none; rua=mailto:hello@cli-market.dev",
        "comment": "CLI Market DMARC — monitor deliverability",
    },
)


def _token() -> str:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "CLOUDFLARE_API_TOKEN is required. "
            "Create a token with Zone:Read + DNS:Edit for cli-market.dev."
        )
    return token


def _request(method: str, path: str, body: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Cloudflare API {method} {path} failed ({exc.code}): {payload}") from exc


def _zone_id() -> str:
    cached = os.environ.get("CLOUDFLARE_ZONE_ID", "").strip()
    if cached:
        return cached
    q = urllib.parse.urlencode({"name": ZONE_NAME})
    data = _request("GET", f"/zones?{q}")
    zones = data.get("result") or []
    if not zones:
        raise SystemExit(f"Zone not found: {ZONE_NAME}")
    return zones[0]["id"]


def _find_txt(zid: str, name: str, needle: str) -> dict | None:
    q = urllib.parse.urlencode({"type": "TXT", "name": name})
    data = _request("GET", f"/zones/{zid}/dns_records?{q}")
    for rec in data.get("result") or []:
        content = (rec.get("content") or "").strip('"')
        if needle in content:
            return rec
    return None


def _upsert(zid: str, spec: dict, *, dry_run: bool) -> str:
    name = spec["name"]
    needle = spec["content"].split()[0]
    existing = _find_txt(zid, name, needle)
    if existing:
        if existing.get("content", "").strip('"') == spec["content"]:
            return f"skip  {name} (already correct)"
        if dry_run:
            return f"would update {name}"
        body = {
            "type": "TXT",
            "name": name,
            "content": spec["content"],
            "comment": spec["comment"],
        }
        _request("PUT", f"/zones/{zid}/dns_records/{existing['id']}", body)
        return f"update {name}"

    if dry_run:
        return f"would create {name}"
    body = {
        "type": "TXT",
        "name": name,
        "content": spec["content"],
        "comment": spec["comment"],
        "ttl": 3600,
    }
    _request("POST", f"/zones/{zid}/dns_records", body)
    return f"create {name}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Upsert SPF + DMARC for cli-market.dev")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    zid = _zone_id()
    print(f"zone {ZONE_NAME} → {zid}")
    for spec in RECORDS:
        print(_upsert(zid, spec, dry_run=args.dry_run))
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())