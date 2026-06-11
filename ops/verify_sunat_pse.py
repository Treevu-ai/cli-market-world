#!/usr/bin/env python3
"""Verify Nubefact PSE credentials from Railway / local env (no secrets printed)."""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_railway_env() -> None:
    railway = "railway.cmd" if sys.platform == "win32" else "railway"
    try:
        proc = subprocess.run(
            [railway, "variables", "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
            shell=sys.platform == "win32",
        )
        if proc.returncode != 0:
            return
        data = json.loads(proc.stdout)
    except Exception:
        return
    keys = (
        "SINAPSIS_RUC",
        "CLAVE_SOL_TOKEN",
        "PASSWORD_SUNAT_SINAPSIS",
        "PSE_SUNAT_ID",
        "PSE_SUNAT_PASSWORD",
        "SUNAT_PSE_API_URL",
        "SUNAT_PSE_PROVIDER",
        "SUNAT_MODE",
    )
    import os

    for key in keys:
        val = data.get(key)
        if val:
            os.environ[key] = str(val)
    # Production PSE creds on Railway should hit api.nubefact.com, not legacy demo host.
    if os.environ.get("PSE_SUNAT_ID") and not os.environ.get("SUNAT_MODE"):
        os.environ["SUNAT_MODE"] = "production"


async def main() -> int:
    _load_railway_env()
    from market_connectors.sunat_invoicing import sunat_config_status, verify_pse_connection

    print("SUNAT config:", json.dumps(sunat_config_status(), indent=2))
    result = await verify_pse_connection()
    print("PSE verify:", json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
