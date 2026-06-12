#!/usr/bin/env python3
"""Deploy CLI Market services on Railway.

Uses Railway GraphQL (account token) to trigger deploy from latest GitHub commit,
or falls back to `railway up` when CLI is available.

Required env (one of):
  RAILWAY_API_TOKEN  — account token (https://railway.com/account/tokens) — CAN deploy
  RAILWAY_TOKEN      — project token — read-only; CLI `railway up` may still work

Optional:
  RAILWAY_API_SERVICE_ID
  RAILWAY_COLLECTOR_SERVICE_ID (default: known collector UUID)
  RAILWAY_PROJECT_ID / RAILWAY_ENVIRONMENT_ID

Usage:
  python3 ops/railway_deploy.py --target api
  python3 ops/railway_deploy.py --target both --dry-run
  python3 ops/railway_deploy.py --list-services
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"
PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID", "d0353d46-78c9-4949-a03f-3ecdb78f06aa")
ENVIRONMENT_ID = os.getenv("RAILWAY_ENVIRONMENT_ID", "036bd72a-f6d8-4c51-b2ab-50cfb261468b")
COLLECTOR_DEFAULT = os.getenv("RAILWAY_COLLECTOR_SERVICE_ID", "3813265a-1862-44a7-a723-62afa8a88dcf")
SKIP_NAME_PARTS = ("postgres", "redis", "database", "db", "collector")
API_NAME_PREFS = ("cli-market-production", "production", "api", "world", "backend", "web")


def _token() -> str:
    for key in ("RAILWAY_API_TOKEN", "RAILWAY_TOKEN", "RAILWAY_PROJECT_TOKEN"):
        val = (os.getenv(key) or "").strip()
        if val:
            return val
    return ""


def _graphql(token: str, query: str, variables: dict | None = None) -> dict:
    body = {"query": query}
    if variables:
        body["variables"] = variables
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:500]
        raise RuntimeError(f"GraphQL HTTP {exc.code}: {detail}") from exc
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], indent=2))
    return payload.get("data") or {}


def list_services(token: str) -> list[dict[str, str]]:
    query = """
    query projectServices($id: String!) {
      project(id: $id) {
        services {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
    """
    data = _graphql(token, query, {"id": PROJECT_ID})
    edges = (((data.get("project") or {}).get("services") or {}).get("edges")) or []
    return [{"id": e["node"]["id"], "name": e["node"]["name"]} for e in edges if e.get("node")]


def resolve_api_service_id(token: str) -> str:
    explicit = (os.getenv("RAILWAY_API_SERVICE_ID") or "").strip()
    if explicit:
        return explicit
    services = list_services(token)
    candidates: list[tuple[str, str]] = []
    for s in services:
        sid, name = s["id"], s["name"]
        lname = name.lower()
        if sid == COLLECTOR_DEFAULT or any(x in lname for x in SKIP_NAME_PARTS):
            continue
        candidates.append((lname, sid))
    for pref in API_NAME_PREFS:
        for lname, sid in candidates:
            if pref in lname:
                return sid
    if len(candidates) == 1:
        return candidates[0][1]
    if candidates:
        return sorted(candidates)[0][1]
    raise RuntimeError(
        "Could not resolve API service. Set RAILWAY_API_SERVICE_ID. "
        f"Services seen: {services}"
    )


def deploy_graphql(token: str, service_id: str, *, latest_commit: bool = True) -> None:
    mutation = """
    mutation serviceInstanceDeploy($serviceId: String!, $environmentId: String!, $latestCommit: Boolean) {
      serviceInstanceDeploy(
        serviceId: $serviceId
        environmentId: $environmentId
        latestCommit: $latestCommit
      )
    }
    """
    _graphql(
        token,
        mutation,
        {
            "serviceId": service_id,
            "environmentId": ENVIRONMENT_ID,
            "latestCommit": latest_commit,
        },
    )


def deploy_cli(service_id: str) -> None:
    root = Path(__file__).resolve().parent.parent
    token = _token()
    env = {**os.environ, "RAILWAY_TOKEN": token} if token else os.environ.copy()
    subprocess.run(
        ["railway", "up", f"--service={service_id}", "--detach"],
        cwd=str(root),
        env=env,
        check=True,
        timeout=600,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy Railway services")
    parser.add_argument("--target", choices=("api", "collector", "both"), default="api")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list-services", action="store_true")
    parser.add_argument("--use-cli", action="store_true", help="Force railway up instead of GraphQL")
    args = parser.parse_args()

    token = _token()
    if not token:
        print(
            "ERROR: Set RAILWAY_API_TOKEN (account token, recommended) or RAILWAY_TOKEN.\n"
            "  Account token: https://railway.com/account/tokens → Team → No team\n"
            "  GitHub: Settings → Secrets → RAILWAY_API_TOKEN\n"
            "  Cursor Cloud: dashboard → Secrets → RAILWAY_API_TOKEN",
            file=sys.stderr,
        )
        return 1

    if args.list_services:
        for s in list_services(token):
            print(f"{s['id']}\t{s['name']}")
        return 0

    targets: list[tuple[str, str]] = []
    if args.target in ("api", "both"):
        api_id = resolve_api_service_id(token)
        targets.append(("api", api_id))
    if args.target in ("collector", "both"):
        targets.append(("collector", COLLECTOR_DEFAULT))

    for label, sid in targets:
        print(f"Deploy {label}: service_id={sid}")
        if args.dry_run:
            continue
        if args.use_cli:
            deploy_cli(sid)
        else:
            try:
                deploy_graphql(token, sid, latest_commit=True)
                print(f"  GraphQL serviceInstanceDeploy OK ({label})")
            except RuntimeError as exc:
                msg = str(exc)
                if "Not Authorized" in msg or "not authorized" in msg.lower():
                    print("  GraphQL deploy denied — retrying with railway CLI...", file=sys.stderr)
                    deploy_cli(sid)
                else:
                    raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
