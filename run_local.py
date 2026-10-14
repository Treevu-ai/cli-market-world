"""Run cli-market-api fully locally, decoupled from Fly.

Why this exists: cli-market-db (Postgres) on Fly is suspended, and its
DATABASE_URL (`cli-market-db.internal`) only resolves inside Fly's 6PN
network anyway. Resuming it costs money and touches shared infra, so this
runs against a local-only Postgres container instead:

    docker run -d --name cli-market-pg-local \\
      -e POSTGRES_USER=climarket -e POSTGRES_PASSWORD=localdevpass \\
      -e POSTGRES_DB=climarket -p 5433:5432 \\
      -v cli_market_pg_local_data:/var/lib/postgresql/data postgres:16-alpine

market_core.init_db() bootstraps the full schema with CREATE TABLE IF NOT
EXISTS on first connect, so an empty container is enough — no migration
step needed. This is local dev data only, not a copy of production.

Usage:
    .venv/Scripts/python.exe run_local.py
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(ROOT, ".env")
LOCAL_DATABASE_URL = "postgresql://climarket:localdevpass@127.0.0.1:5433/climarket"


def load_env_file(path: str, base_env: dict) -> dict:
    env = dict(base_env)
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
            if not m:
                continue
            key, val = m.group(1), m.group(2).strip()
            if val and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            env[key] = val
    return env


def main() -> None:
    env = load_env_file(ENV_PATH, os.environ)
    env.setdefault("PORT", "8080")
    env.setdefault("MARKET_DATA_DIR", os.path.join(ROOT, "data_local"))
    os.makedirs(env["MARKET_DATA_DIR"], exist_ok=True)

    # Local-only overrides — never pointed at Fly.
    env["DATABASE_URL"] = LOCAL_DATABASE_URL
    env["MARKET_API_URL"] = "http://127.0.0.1:" + env["PORT"]

    python = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
    # --reload is deliberately omitted: its file-watcher supervisor opens an
    # extra local socket for IPC that Windows sometimes refuses
    # (WinError 10013), especially with Defender/firewall policies present.
    # Restart the process manually after code changes instead.
    cmd = [
        python, "-m", "uvicorn", "market_server:app",
        "--host", "127.0.0.1", "--port", env["PORT"],
    ]
    subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    main()
