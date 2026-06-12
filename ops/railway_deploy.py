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
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"
PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID", "d0353d46-78c9-4949-a03f-3ecdb78f06aa")
ENVIRONMENT_ID = os.getenv("RAILWAY_ENVIRONMENT_ID", "036bd72a-f6d8-4c51-b2ab-50cfb261468b")
API_SERVICE_ID_DEFAULT = "6e74bc38-bbf2-4815-bac4-38092067d3b1"
COLLECTOR_SERVICE_ID_DEFAULT = "3813265a-1862-44a7-a723-62afa8a88dcf"


def _env_default(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip()


def _env_opt(name: str) -> str:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return ""
    return str(raw).strip()


COLLECTOR_DEFAULT = _env_default("RAILWAY_COLLECTOR_SERVICE_ID", COLLECTOR_SERVICE_ID_DEFAULT)
API_SERVICE_ID_FALLBACK = API_SERVICE_ID_DEFAULT
API_SERVICE_NAME_FALLBACK = _env_default("RAILWAY_API_SERVICE_NAME", "cli-market-production")
SKIP_NAME_PARTS = ("postgres", "redis", "database", "db", "collector")
API_NAME_PREFS = ("cli-market-production", "production", "api", "world", "backend", "web")
_PROJECT_TOKEN_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _is_project_token(token: str) -> bool:
    return bool(_PROJECT_TOKEN_RE.match(token))


def _tokens() -> tuple[str, str]:
    """Return (account_token, project_token)."""
    account = (os.getenv("RAILWAY_API_TOKEN") or "").strip()
    project = (os.getenv("RAILWAY_TOKEN") or os.getenv("RAILWAY_PROJECT_TOKEN") or "").strip()
    if account and _is_project_token(account) and not project:
        project = account
        account = ""
    elif account and _is_project_token(account) and project:
        account = ""
    return account, project


def _any_token() -> str:
    account, project = _tokens()
    return account or project


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


def _cli_env(project_token: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("RAILWAY_API_TOKEN", None)
    env["RAILWAY_TOKEN"] = project_token
    return env


def _run_railway_json(args: list[str], project_token: str, *, timeout: int = 120) -> object:
    _ensure_railway_cli()
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        env=_cli_env(project_token),
        cwd=str(Path(__file__).resolve().parent.parent),
        timeout=timeout,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[:800]
        raise RuntimeError(f"railway CLI failed ({proc.returncode}): {detail}")
    raw = (proc.stdout or "").strip()
    if not raw:
        raise RuntimeError("railway CLI returned empty stdout")
    return json.loads(raw)


def list_services_cli(project_token: str) -> list[dict[str, str]]:
    payload = _run_railway_json(
        [
            "railway",
            "service",
            "list",
            f"--project={PROJECT_ID}",
            f"--environment={ENVIRONMENT_ID}",
            "--json",
        ],
        project_token,
    )
    rows: list[dict] = []
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        for key in ("services", "data", "items"):
            if isinstance(payload.get(key), list):
                rows = payload[key]
                break
        if not rows and payload.get("id") and payload.get("name"):
            rows = [payload]
    out: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("id") or row.get("serviceId") or "").strip()
        name = str(row.get("name") or row.get("serviceName") or "").strip()
        if sid:
            out.append({"id": sid, "name": name or sid})
    return out


def _pick_api_service(services: list[dict[str, str]]) -> str:
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


def resolve_api_service_ref(token: str, *, project_token: str = "") -> str:
    explicit = _env_default("RAILWAY_API_SERVICE_ID", "")
    if explicit:
        return explicit
    services: list[dict[str, str]] = []
    if account := (token if token and not _is_project_token(token) else ""):
        try:
            services = list_services(account)
        except RuntimeError:
            services = []
    if not services and project_token:
        services = list_services_cli(project_token)
    if services:
        return _pick_api_service(services)
    if project_token:
        return API_SERVICE_DEFAULT or API_SERVICE_NAME_FALLBACK
    raise RuntimeError(
        "Could not resolve API service. Set RAILWAY_API_SERVICE_ID or use a token that can list services."
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


def _ensure_railway_cli() -> str:
    path = shutil.which("railway")
    if path:
        return path
    subprocess.run(["npm", "install", "-g", "@railway/cli"], check=True, timeout=300)
    path = shutil.which("railway")
    if not path:
        raise RuntimeError("railway CLI not found after npm install")
    return path


def deploy_up_cli(service_ref: str, project_token: str) -> None:
    """Upload checked-out repo to Railway (works with project token)."""
    root = Path(__file__).resolve().parent.parent
    _ensure_railway_cli()
    env = _cli_env(project_token)
    subprocess.run(
        [
            "railway",
            "up",
            "--detach",
            "--ci",
            f"--service={service_ref}",
            f"--project={PROJECT_ID}",
            f"--environment={ENVIRONMENT_ID}",
        ],
        cwd=str(root),
        env=env,
        check=True,
        timeout=900,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy Railway services")
    parser.add_argument("--target", choices=("api", "collector", "both"), default="api")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list-services", action="store_true")
    parser.add_argument("--use-cli", action="store_true", help="Force railway up instead of GraphQL")
    args = parser.parse_args()

    account_token, project_token = _tokens()
    if not account_token and not project_token:
        print(
            "ERROR: Set RAILWAY_API_TOKEN (account) and/or RAILWAY_TOKEN (project).\n"
            "  Account (GraphQL latest commit): https://railway.com/account/tokens\n"
            "  Project (railway up from CI): Railway project → Settings → Tokens\n"
            "  GitHub: Settings → Secrets → Actions",
            file=sys.stderr,
        )
        return 1

    list_token = account_token or project_token
    if args.list_services:
        services: list[dict[str, str]] = []
        if account_token:
            try:
                services = list_services(account_token)
            except RuntimeError as exc:
                print(f"GraphQL list failed: {exc}", file=sys.stderr)
        if not services and project_token:
            services = list_services_cli(project_token)
        if not services:
            print("No services listed — set RAILWAY_API_SERVICE_ID", file=sys.stderr)
            return 1
        for s in services:
            print(f"{s['id']}\t{s['name']}")
        return 0

    targets: list[tuple[str, str]] = []
    if args.target in ("api", "both"):
        api_ref = resolve_api_service_ref(list_token, project_token=project_token)
        targets.append(("api", api_ref))
    if args.target in ("collector", "both"):
        targets.append(("collector", COLLECTOR_DEFAULT))

    use_cli_only = args.use_cli or (not account_token and bool(project_token))

    for label, service_ref in targets:
        print(f"Deploy {label}: service={service_ref}")
        if args.dry_run:
            continue
        if use_cli_only:
            if not project_token:
                raise RuntimeError(
                    f"CLI deploy for {label} requires RAILWAY_TOKEN (project token)"
                )
            deploy_up_cli(service_ref, project_token)
            print(f"  railway up OK ({label})")
            continue
        try:
            deploy_graphql(account_token, service_ref, latest_commit=True)
            print(f"  GraphQL serviceInstanceDeploy OK ({label})")
        except RuntimeError as exc:
            msg = str(exc)
            if project_token and (
                "Not Authorized" in msg or "not authorized" in msg.lower()
            ):
                print("  GraphQL denied — falling back to railway up...", file=sys.stderr)
                deploy_up_cli(service_ref, project_token)
                print(f"  railway up OK ({label})")
            else:
                raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
