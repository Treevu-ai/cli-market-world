#!/usr/bin/env python3
"""Configure www.cli-market.dev -> https://cli-market.dev (301) on Cloudflare.

Root cause: www currently proxies to a stale Vercel origin (DEPLOYMENT_NOT_FOUND).
This script adds a zone-level dynamic redirect so requests never reach Vercel.

Usage:
  set CLOUDFLARE_API_TOKEN=...
  python ops/cloudflare_www_redirect.py

Optional:
  CLOUDFLARE_ZONE_ID   — skip zone lookup
  CLOUDFLARE_ACCOUNT_ID — required to add Pages custom domain
  CLOUDFLARE_PAGES_PROJECT=cli-market-world
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.cloudflare.com/client/v4"
ZONE_NAME = "cli-market.dev"
WWW_HOST = "www.cli-market.dev"
APEX = "https://cli-market.dev"
RULE_DESC = "CLI Market www to apex"


def _token() -> str:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "CLOUDFLARE_API_TOKEN is required. "
            "Create a token with Zone:Read, Zone:Edit, Account:Read."
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


def _verify_token() -> None:
    data = _request("GET", "/user/tokens/verify")
    status = (data.get("result") or {}).get("status")
    if status != "active":
        raise SystemExit(f"Token verify failed: {data}")


def _list_accessible_zones(limit: int = 20) -> list[dict]:
    data = _request("GET", f"/zones?per_page={limit}")
    return list(data.get("result") or [])


def zone_id() -> str:
    cached = os.environ.get("CLOUDFLARE_ZONE_ID", "").strip()
    if cached:
        return cached

    _verify_token()

    for query in (
        f"/zones?name={ZONE_NAME}",
        f"/zones?name={ZONE_NAME}&status=active",
        f"/zones?name={ZONE_NAME}&status=pending",
    ):
        data = _request("GET", query)
        zones = data.get("result") or []
        if zones:
            return zones[0]["id"]

    visible = _list_accessible_zones()
    names = [z.get("name", "?") for z in visible]
    raise SystemExit(
        f"Zone not found for {ZONE_NAME}.\n"
        "Likely causes:\n"
        "  1) Token created on a different Cloudflare account than the zone\n"
        "  2) Token Zone Resources does not include cli-market.dev\n"
        "  3) Missing permission: Zone → Zone → Read\n\n"
        f"Zones this token can see ({len(names)}): {', '.join(names) or '(none)'}\n\n"
        "Fix: recreate token with Zone Resources → Include → Specific zone → cli-market.dev\n"
        "Or set CLOUDFLARE_ZONE_ID manually (Dashboard → cli-market.dev → Overview → right column)."
    )


def ensure_redirect_rule(zid: str) -> None:
    phase = "http_request_dynamic_redirect"
    entrypoint = _request("GET", f"/zones/{zid}/rulesets/phases/{phase}/entrypoint")
    ruleset = entrypoint.get("result") or {}
    rules = list(ruleset.get("rules") or [])

    for rule in rules:
        if rule.get("description") == RULE_DESC:
            print(f"Redirect rule already exists (id={rule.get('id')})")
            return

    rules.insert(
        0,
        {
            "description": RULE_DESC,
            "expression": f'(http.host eq "{WWW_HOST}")',
            "action": "redirect",
            "action_parameters": {
                "from_value": {
                    "status_code": 301,
                    "target_url": {
                        "expression": 'concat("https://cli-market.dev", http.request.uri.path)',
                    },
                    "preserve_query_string": True,
                }
            },
        },
    )

    if ruleset.get("id"):
        _request(
            "PUT",
            f"/zones/{zid}/rulesets/{ruleset['id']}",
            {"rules": rules},
        )
        print("Updated zone redirect ruleset")
    else:
        _request(
            "POST",
            f"/zones/{zid}/rulesets",
            {
                "name": "default",
                "kind": "zone",
                "phase": phase,
                "rules": rules,
            },
        )
        print("Created zone redirect ruleset")


def add_pages_www_domain() -> None:
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    project = os.environ.get("CLOUDFLARE_PAGES_PROJECT", "cli-market-world").strip()
    if not account:
        print("CLOUDFLARE_ACCOUNT_ID not set — skipping Pages custom domain attach")
        return

    existing = _request(
        "GET",
        f"/accounts/{account}/pages/projects/{project}/domains",
    )
    names = {d.get("name") for d in (existing.get("result") or [])}
    if WWW_HOST in names:
        print(f"Pages custom domain already attached: {WWW_HOST}")
        return

    _request(
        "POST",
        f"/accounts/{account}/pages/projects/{project}/domains",
        {"name": WWW_HOST},
    )
    print(f"Attached Pages custom domain: {WWW_HOST}")


def main() -> int:
    zid = zone_id()
    print(f"Zone: {ZONE_NAME} ({zid})")
    ensure_redirect_rule(zid)
    add_pages_www_domain()
    print(f"Done. Test: curl -I https://{WWW_HOST}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())