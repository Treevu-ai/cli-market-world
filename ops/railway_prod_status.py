#!/usr/bin/env python3
"""Check Railway production API version and Observatory P0 gate."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

PROD_API = "https://cli-market-production.up.railway.app"
STUCK_VERSION = "1.9.30"


def _parse_version(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            break
    return tuple(parts) or (0,)


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
    return {
        "version": version,
        "index_stats_in_top_tools": "index_stats" in tools,
        "top_tools": tools[:8],
        "observatory_ok": "index_stats" not in tools and version != STUCK_VERSION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Railway prod status")
    parser.add_argument("--wait", action="store_true", help="Poll /health until ready")
    parser.add_argument("--min-version", default="", help="Fail if OpenAPI version is below this")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.wait:
        target = _parse_version(args.min_version) if args.min_version else None
        for attempt in range(1, 41):
            try:
                _fetch_json("/health", timeout=15)
                data = snapshot()
                ver = _parse_version(str(data.get("version", "")))
                print(f"Attempt {attempt}: health OK, version={data.get('version')}")
                if target is None or ver >= target:
                    break
            except Exception as exc:
                print(f"Attempt {attempt}: {exc} — sleep 30s")
                time.sleep(30)
        else:
            print("ERROR: prod did not reach target version after 40 attempts", file=sys.stderr)
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
        print(f"P0 observatory gate: {'PASS' if data['observatory_ok'] else 'FAIL'}")

    if args.min_version and data["version"] == STUCK_VERSION:
        print(
            f"::warning::Still on {STUCK_VERSION} — Railway may need RAILWAY_TOKEN secret + redeploy",
            file=sys.stderr,
        )
    if args.min_version and _parse_version(data["version"]) < _parse_version(args.min_version):
        print(
            f"ERROR: version {data['version']} < required {args.min_version}",
            file=sys.stderr,
        )
        return 1
    if args.min_version and data["index_stats_in_top_tools"]:
        print("ERROR: index_stats still in observatory top_tools (old build)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
