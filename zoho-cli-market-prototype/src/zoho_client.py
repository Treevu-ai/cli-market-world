"""
Zoho CRM API Client — OAuth2 + REST API v2.

Diferencia clave vs HubSpot: el access_token de Zoho vence en 1h.
Este cliente maneja el refresh automático en cada request (lazy refresh):
si el token no existe o la request devuelve 401, refresca y reintenta una vez.

Auth header: "Zoho-oauthtoken {access_token}"
Token endpoint: {ZOHO_API_DOMAIN}/oauth/v2/token (POST, form data)
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Módulos soportados
MODULES = ("Leads", "Deals", "Products", "Contacts", "Accounts")


class ZohoCRMClient:
    """
    Cliente async para la API de Zoho CRM v2.

    Manejo de tokens:
    - _access_token: en memoria (se pierde si el proceso reinicia)
    - _token_expires_at: timestamp UTC; refresca cuando queda < 60s
    - Si la API devuelve 401 se hace un refresh inmediato y se reintenta
    """

    def __init__(self) -> None:
        self.client_id = os.getenv("ZOHO_CLIENT_ID", "")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET", "")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN", "")
        self.api_domain = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com").rstrip("/")
        self.timeout = float(os.getenv("ZOHO_TIMEOUT", "30"))
        self.base_url = f"{self.api_domain}/crm/v2"

        self._access_token: str = ""
        self._token_expires_at: float = 0.0  # Unix timestamp

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.warning(
                "ZOHO_CLIENT_ID / ZOHO_CLIENT_SECRET / ZOHO_REFRESH_TOKEN no configurados — "
                "las operaciones CRM fallarán"
            )

    # ── OAuth2 ──────────────────────────────────────────────────────────────

    def _token_valid(self) -> bool:
        """True si el token existe y no vence en los próximos 60s."""
        return bool(self._access_token) and time.time() < (self._token_expires_at - 60)

    async def _refresh_access_token(self) -> str:
        """
        Obtiene un nuevo access_token usando el refresh_token.
        Zoho devuelve expires_in en segundos (típicamente 3600).
        """
        if not self.refresh_token:
            logger.error("ZOHO_REFRESH_TOKEN no configurado")
            return ""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"{self.api_domain}/oauth/v2/token",
                    data={
                        "refresh_token": self.refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                    },
                )
                r.raise_for_status()
                data = r.json()
                token = data.get("access_token", "")
                expires_in = int(data.get("expires_in", 3600))
                self._access_token = token
                self._token_expires_at = time.time() + expires_in
                logger.info("Zoho access_token refrescado (expires_in=%ds)", expires_in)
                return token
        except Exception as e:
            logger.error("Error refrescando token Zoho: %s", e)
            return ""

    async def _get_token(self) -> str:
        if not self._token_valid():
            await self._refresh_access_token()
        return self._access_token

    def _auth_header(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Zoho-oauthtoken {token}"}

    # ── Request helper con auto-retry en 401 ────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        token = await self._get_token()
        headers = self._auth_header(token)
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.request(
                    method, url, headers=headers, params=params, json=json, data=data
                )

                # Token expirado en carrera → refrescar y reintentar una vez
                if r.status_code == 401:
                    logger.warning("Zoho 401 en %s — refrescando token y reintentando", path)
                    token = await self._refresh_access_token()
                    headers = self._auth_header(token)
                    r = await client.request(
                        method, url, headers=headers, params=params, json=json, data=data
                    )

                if r.status_code == 404:
                    return {"error": "not_found", "path": path}
                if r.status_code >= 400:
                    logger.error("Zoho %s %s → %d: %s", method, path, r.status_code, r.text[:200])
                    return {"error": f"http_{r.status_code}", "path": path}

                return r.json() if r.content else {}

        except httpx.TimeoutException:
            logger.error("Timeout en Zoho %s %s", method, path)
            return {"error": "timeout", "path": path}
        except Exception as e:
            logger.error("Error en Zoho %s %s: %s", method, path, e)
            return {"error": str(e), "path": path}

    # ── CRUD ────────────────────────────────────────────────────────────────

    async def get_record(self, module: str, record_id: str) -> dict[str, Any]:
        """GET /crm/v2/{module}/{record_id}"""
        return await self._request("GET", f"/{module}/{record_id}")

    async def update_record(
        self, module: str, record_id: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        """
        PUT /crm/v2/{module}/{record_id}
        Zoho espera: {"data": [{...campos..., "id": record_id}]}
        """
        payload = {"data": [{**fields, "id": record_id}]}
        return await self._request("PUT", f"/{module}/{record_id}", json=payload)

    async def create_record(self, module: str, fields: dict[str, Any]) -> dict[str, Any]:
        """POST /crm/v2/{module}"""
        payload = {"data": [fields]}
        return await self._request("POST", f"/{module}", json=payload)

    async def search_records(
        self, module: str, criteria: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """GET /crm/v2/{module}/search?criteria=..."""
        result = await self._request(
            "GET", f"/{module}/search", params={"criteria": criteria, "per_page": limit}
        )
        return result.get("data", []) if not result.get("error") else []

    async def get_related_records(
        self, module: str, record_id: str, related_module: str
    ) -> list[dict[str, Any]]:
        """GET /crm/v2/{module}/{record_id}/{related_module}"""
        result = await self._request("GET", f"/{module}/{record_id}/{related_module}")
        return result.get("data", []) if not result.get("error") else []

    # ── Health ───────────────────────────────────────────────────────────────

    async def health_check(self) -> bool:
        """Verifica conectividad obteniendo un token válido."""
        token = await self._get_token()
        return bool(token)
