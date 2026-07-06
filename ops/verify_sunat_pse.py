#!/usr/bin/env python3
"""Verify Nubefact PSE credentials from local env (no secrets printed).

Fly.io secrets can't be read back via CLI (unlike Railway) — export the
relevant vars (SINAPSIS_RUC, CLAVE_SOL_TOKEN, PSE_SUNAT_ID, PSE_SUNAT_PASSWORD,
SUNAT_PSE_API_URL, SUNAT_PSE_PROVIDER, SUNAT_MODE, ...) into the shell before
running this, e.g. via `.env` + `ops/load_env.py`.
"""
from __future__ import annotations

import asyncio
import json
import os


def _default_sunat_mode() -> None:
    if os.environ.get("PSE_SUNAT_ID") and not os.environ.get("SUNAT_MODE"):
        os.environ["SUNAT_MODE"] = "production"


async def main() -> int:
    _default_sunat_mode()
    from market_connectors.sunat_invoicing import sunat_config_status, verify_pse_connection

    print("SUNAT config:", json.dumps(sunat_config_status(), indent=2))
    result = await verify_pse_connection()
    print("PSE verify:", json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
