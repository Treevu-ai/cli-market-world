"""Stable X-Agent-ID for CLI/MCP until cli-market-core>=1.9.34 is on PyPI."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from market_core import DATA_DIR


def get_agent_id() -> str:
    env_id = os.environ.get("MARKET_AGENT_ID", "").strip()
    if env_id:
        return env_id[:128]
    path = DATA_DIR / "agent_id"
    try:
        if path.is_file():
            stored = path.read_text(encoding="utf-8").strip()
            if stored:
                return stored[:128]
        new_id = f"cli_{uuid.uuid4().hex[:20]}"
        path.write_text(new_id, encoding="utf-8")
        return new_id
    except Exception:
        return ""


def patch_core_api_agent_header() -> None:
    """Attach X-Agent-ID to market_core.api() when core < 1.9.34."""
    import market_core.market_core as mc

    if getattr(mc, "_agent_id_header_patched", False):
        return

    original = mc.api

    def api(method: str, path: str, json_data: dict | None = None) -> dict:
        agent_id = get_agent_id()
        if not agent_id:
            return original(method, path, json_data)

        token = None
        if path not in mc._AUTH_PUBLIC_PATHS:
            token = mc.get_token()

        headers: dict[str, str] = {"X-Agent-ID": agent_id}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        timeout = mc._api_timeout(path, method)

        def _request(hdrs: dict[str, str]) -> Any:
            import httpx

            if method == "GET":
                return httpx.get(f"{mc.API}{path}", headers=hdrs, timeout=timeout)
            if method == "POST":
                return httpx.post(f"{mc.API}{path}", headers=hdrs, json=json_data, timeout=timeout)
            if method == "PUT":
                return httpx.put(f"{mc.API}{path}", headers=hdrs, json=json_data, timeout=timeout)
            if method == "DELETE":
                return httpx.delete(f"{mc.API}{path}", headers=hdrs, timeout=timeout)
            raise ValueError(f"Unknown method: {method}")

        try:
            resp = _request(headers)
            if (
                resp.status_code == 401
                and resp.headers.get("x-token-expired", "").lower() == "true"
                and path not in mc._AUTH_PUBLIC_PATHS
            ):
                new_token = mc._refresh_access_token()
                if new_token:
                    headers = dict(headers)
                    headers["Authorization"] = f"Bearer {new_token}"
                    resp = _request(headers)
            if resp.status_code >= 400:
                detail = resp.json().get("detail", resp.text)
                return {"error": detail, "status": resp.status_code}
            return resp.json()
        except Exception as exc:
            return {"error": str(exc)}

    mc.api = api
    mc._agent_id_header_patched = True
