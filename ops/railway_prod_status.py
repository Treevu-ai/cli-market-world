#!/usr/bin/env python3
"""Check Railway production API version and Observatory P0 gate."""

from __future__ import annotations

import argparse
import json
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

PROD_API = "https://cli-market-production.up.railway.app"
STUCK_VERSION = "1.9.30"
ROOT = Path(__file__).resolve().parent.parent


def _parse_version(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            break
    return tuple(parts) or (0,)


def _world_version() -> str:
    try:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        return str(data["project"]["version"])
    except Exception:
        return ""


def _fetch_json(path: str, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(f"{PROD_API}{path}", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def snapshot() -> dict:
    openapi = _fetch_json("/openapi.json")
    version = (openapi.get("info") or {}).get("version", "?")
    observatory: dict = {}
    try:
        observatory = _fetch_json("/analytics/observatory?days=30")
    except urllib.error.HTTPError:
        pass
    tools = [t.get("name") for t in observatory.get("top_tools", [])]
    index_stats = "index_stats" in tools
    return {
        "version": version,
        "index_stats_in_top_tools": index_stats,
        "top_tools": tools[:8],
        "observatory_p0_ok": not index_stats,
    }


def _meets_target(data: dict, *, min_version: str, observatory_p0: bool) -> bool:
    if observatory_p0 and data.get("index_stats_in_top_tools"):
        return False
    if min_version:
        ver = _parse_version(str(data.get("version", "")))
        target = _parse_version(min_version)
        if ver < target:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Railway prod status")
    parser.add_argument("--wait", action="store_true", help="Poll until gate passes")
    parser.add_argument("--min-version", default="", help="Fail if OpenAPI version is below this")
    parser.add_argument(
        "--min-version-from-pyproject",
        action="store_true",
        help="Use pyproject.toml project.version as --min-version",
    )
    parser.add_argument(
        "--observatory-p0",
        action="store_true",
        help="Require index_stats absent from observatory top_tools (P0 gate)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    min_version = args.min_version
    if args.min_version_from_pyproject:
        min_version = _world_version() or min_version

    if args.wait:
        for attempt in range(1, 41):
            try:
                _fetch_json("/health", timeout=15)
                data = snapshot()
                print(
                    f"Attempt {attempt}: health OK, version={data.get('version')}, "
                    f"observatory_p0={'PASS' if data.get('observatory_p0_ok') else 'FAIL'}"
                )
                if _meets_target(
                    data,
                    min_version=min_version,
                    observatory_p0=args.observatory_p0,
                ):
                    break
            except Exception as exc:
                print(f"Attempt {attempt}: {exc}")
            time.sleep(30)
        else:
            print("ERROR: prod did not pass gate after 40 attempts (~20 min)", file=sys.stderr)
            return 1
        time.sleep(5)

    try:
        data = snapshot()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"Prod version: {data['version']}")
        print(f"index_stats in top_tools: {data['index_stats_in_top_tools']}")
        print(f"top_tools: {data['top_tools']}")
        print(f"Observatory P0: {'PASS' if data['observatory_p0_ok'] else 'FAIL'}")

    if args.observatory_p0 and data["index_stats_in_top_tools"]:
        print("ERROR: index_stats still in observatory top_tools (pre-P0 build)", file=sys.stderr)
        return 1
    if min_version and _parse_version(data["version"]) < _parse_version(min_version):
        print(
            f"ERROR: version {data['version']} < required {min_version}",
            file=sys.stderr,
        )
        if data["version"] == STUCK_VERSION and data.get("observatory_p0_ok"):
            print(
                "::warning::Observatory P0 OK but OpenAPI still reports core PACKAGE_VERSION; "
                "redeploy after market_server pyproject version fix",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
