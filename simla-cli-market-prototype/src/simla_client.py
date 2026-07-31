"""
Simla.com API Client
Cliente outbound para devolver respuestas por WhatsApp vía Simla.

Nota: los paths exactos de Simla dependen del tenant / plan (RetailCRM-based).
Ajustar SIMLA_API_URL y los path templates cuando se valide contra el tenant real.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class SimlaClient:
    """Cliente para la API de Simla.com (envío de mensajes WhatsApp)."""

    def __init__(self) -> None:
        self.api_url = os.getenv("SIMLA_API_URL", "https://simla.com").rstrip("/")
        self.api_key = os.getenv("SIMLA_API_KEY") or ""
        self.timeout = float(os.getenv("SIMLA_TIMEOUT", "30"))
        if not self.api_key:
            logger.warning("SIMLA_API_KEY no está configurada")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def send_whatsapp_message(
        self,
        phone_number: str,
        message: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Enviar mensaje de WhatsApp. Path configurable vía SIMLA_WHATSAPP_PATH."""
        path = os.getenv("SIMLA_WHATSAPP_PATH", "/api/v1/messages/whatsapp")
        payload: dict[str, Any] = {
            "message": {
                "phone": phone_number,
                "text": message,
            }
        }
        if conversation_id:
            payload["message"]["conversation_id"] = conversation_id

        if not self.api_key:
            logger.warning("SIMLA_API_KEY missing — dry-run only, message not sent")
            return {"status": "dry_run", "payload": payload}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}{path}",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                result = response.json() if response.content else {"status": "ok"}
                logger.info("WhatsApp message accepted by Simla for ***%s", phone_number[-4:])
                return result
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error sending WhatsApp message: %s", e)
            return {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error("Error sending WhatsApp message: %s", e)
            return {"error": str(e), "status": "failed"}

    async def update_customer_note(self, customer_id: str, note: str) -> dict[str, Any]:
        path = os.getenv("SIMLA_CUSTOMER_PATH", "/api/v1/customers/{id}").format(id=customer_id)
        payload = {"customer": {"id": customer_id, "notes": note}}
        if not self.api_key:
            return {"status": "dry_run", "payload": payload}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.api_url}{path}",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                return response.json() if response.content else {"status": "ok"}
        except Exception as e:
            logger.error("Error updating customer note: %s", e)
            return {"error": str(e), "status": "failed"}

    async def health_check(self) -> bool:
        """Best-effort. Many Simla tenants do not expose /api/v1/health."""
        path = os.getenv("SIMLA_HEALTH_PATH", "/api/v1/health")
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(f"{self.api_url}{path}")
                return response.status_code < 400
        except Exception as e:
            logger.debug("Simla health check failed: %s", e)
            return False
