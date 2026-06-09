#!/usr/bin/env python3
"""Write .env from Railway linked project (no manual copy-paste).

Requires: railway CLI linked in repo root (`railway status`).

  python ops/pull_railway_env.py
  python ops/pull_railway_env.py --stdout   # print only, no file
  python ops/pull_railway_env.py --service collector
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_KEYS = frozenset({"RAILWAY_ENVIRONMENT", "RAILWAY_ENVIRONMENT_ID", "RAILWAY_PROJECT_ID"})

# Content-ops vars — not API runtime; keep canonical even if Railway has old values.
CAMPAIGN_ENV_OVERRIDES = {
    "LINKEDIN_CAMPAIGN_START": "2026-06-01",
    "LINKEDIN_PERSONAL_DAY_OFFSET": "0",
    "LINKEDIN_COMPANY_DAY_OFFSET": "-1",
}


def _railway_cmd() -> str:
    return "railway.cmd" if sys.platform == "win32" else "railway"


def fetch_variables(*, service: str = "") -> dict[str, str]:
    cmd = [_railway_cmd(), "variables", "--json"]
    if service:
        cmd.extend(["--service", service])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=90)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "railway variables failed")
    raw = json.loads(result.stdout)
    return {k: str(v).strip() for k, v in raw.items() if v is not None and str(v).strip()}


def build_env_lines(vars_map: dict[str, str]) -> list[str]:
    db_public = vars_map.get("DATABASE_PUBLIC_URL", "")
    lines: list[str] = ["# AUTO-GENERATED — python ops/pull_railway_env.py", ""]
    for key in sorted(vars_map):
        if key in SKIP_KEYS:
            continue
        if key == "DATABASE_URL" and db_public:
            continue
        val = vars_map[key].replace("\n", "\\n")
        lines.append(f"{key}={val}")
    if db_public:
        lines.append(f"DATABASE_URL={db_public}")
    for key, val in sorted(CAMPAIGN_ENV_OVERRIDES.items()):
        lines.append(f"{key}={val}")
    return lines


def main() -> int:
    p = argparse.ArgumentParser(description="Pull Railway variables into .env")
    p.add_argument("--stdout", action="store_true", help="Print to stdout instead of writing .env")
    p.add_argument("--service", default="", help="Railway service name (default: linked service)")
    p.add_argument("--out", type=Path, default=ROOT / ".env", help="Output path (default: .env)")
    args = p.parse_args()

    try:
        vars_map = fetch_variables(service=args.service)
    except Exception as exc:
        print(f"✗ {exc}", file=sys.stderr)
        print("Tip: cd cli-market-world && railway link", file=sys.stderr)
        return 1

    lines = build_env_lines(vars_map)
    body = "\n".join(lines) + "\n"
    if args.stdout:
        sys.stdout.write(body)
        return 0

    args.out.write_text(body, encoding="utf-8")
    print(f"✓ Wrote {args.out} ({len(lines) - 2} variables)")
    if vars_map.get("DATABASE_PUBLIC_URL"):
        print("  DATABASE_URL → DATABASE_PUBLIC_URL (reachable from your PC)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())