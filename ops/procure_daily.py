"""Trigger Procure Copilot daily Slack summary (command-control + bitácora)."""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_PROCURE_URL = "https://procure-copilot.contacto-8e4.workers.dev"


def procure_daily_configured() -> bool:
    return bool(os.getenv("PROCUREMENT_WEBHOOK_SECRET", "").strip())


def trigger_procure_daily_summary(day: date | None = None) -> dict[str, Any]:
    """POST /api/procurement/daily-summary on the Procure Worker."""
    secret = os.getenv("PROCUREMENT_WEBHOOK_SECRET", "").strip()
    base = (
        os.getenv("PROCURE_PUBLIC_URL", DEFAULT_PROCURE_URL).strip().rstrip("/")
        or DEFAULT_PROCURE_URL
    )
    if not secret:
        return {"ok": False, "error": "PROCUREMENT_WEBHOOK_SECRET missing"}

    payload: dict[str, str] = {"secret": secret}
    if day is not None:
        payload["date"] = day.isoformat()

    req = Request(
        f"{base}/api/procurement/daily-summary",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": resp.status == 200 and bool(body.get("success")), **body}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "error": f"HTTP {exc.code}", "detail": detail}
    except URLError as exc:
        return {"ok": False, "error": str(exc.reason)}