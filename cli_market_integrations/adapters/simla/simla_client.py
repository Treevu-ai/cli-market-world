"""Simla.com outbound client — unchanged from prototype."""
from __future__ import annotations
import logging, os
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class SimlaClient:
    def __init__(self) -> None:
        self.api_url = os.getenv("SIMLA_API_URL", "https://simla.com").rstrip("/")
        self.api_key = os.getenv("SIMLA_API_KEY") or ""
        self.timeout = float(os.getenv("SIMLA_TIMEOUT", "30"))
        if not self.api_key:
            logger.warning("SIMLA_API_KEY not set — dry-run mode")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "Accept": "application/json"}

    async def send_whatsapp_message(self, phone_number: str, message: str, conversation_id: str | None = None) -> dict[str, Any]:
        path = os.getenv("SIMLA_WHATSAPP_PATH", "/api/v1/messages/whatsapp")
        payload: dict[str, Any] = {"message": {"phone": phone_number, "text": message}}
        if conversation_id:
            payload["message"]["conversation_id"] = conversation_id
        if not self.api_key:
            return {"status": "dry_run", "payload": payload}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.post(f"{self.api_url}{path}", headers=self._headers(), json=payload)
                r.raise_for_status()
                return r.json() if r.content else {"status": "ok"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    async def health_check(self) -> bool:
        path = os.getenv("SIMLA_HEALTH_PATH", "/api/v1/health")
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as c:
                return (await c.get(f"{self.api_url}{path}")).status_code < 400
        except Exception:
            return False
