"""
Kommo CRM API Client — v4 REST + OAuth2.

Diferencias clave vs HubSpot/Zoho:
  1. Base URL es por subdominio: https://{subdomain}.kommo.com/api/v4/
  2. Auth: Bearer token. Para integración privada se puede usar long-lived token
     (sin refresh). Para integración pública, refresh_token + redirect_uri obligatorio.
  3. Custom fields NO son props nombradas — son objetos {field_id, values:[{value}]}.
     Para escribir inteligencia de mercado necesitamos los IDs de los campos custom.
  4. Update leads/contacts: PATCH /api/v4/leads con array de objetos.
  5. Token refresh igual que Zoho pero con redirect_uri requerido.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class KommoClient:
    """
    Cliente async para Kommo CRM API v4.

    Modos de auth:
    - Long-lived token (integración privada): setear solo KOMMO_LONG_LIVED_TOKEN.
      No necesita refresh. Recomendado para demos y clientes single-account.
    - OAuth2 (integración pública): setear CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN,
      REDIRECT_URI. El access_token vence en ~24h; se refresca automáticamente.
    """

    def __init__(self) -> None:
        subdomain = os.getenv("KOMMO_SUBDOMAIN", "")
        if not subdomain:
            logger.warning("KOMMO_SUBDOMAIN no configurado")
        self.base_url = f"https://{subdomain}.kommo.com/api/v4" if subdomain else ""

        # Long-lived token tiene prioridad (integración privada)
        self._long_lived_token = os.getenv("KOMMO_LONG_LIVED_TOKEN", "")

        # OAuth2 para integración pública
        self.client_id      = os.getenv("KOMMO_CLIENT_ID", "")
        self.client_secret  = os.getenv("KOMMO_CLIENT_SECRET", "")
        self._refresh_token = os.getenv("KOMMO_REFRESH_TOKEN", "")
        self.redirect_uri   = os.getenv("KOMMO_REDIRECT_URI", "")

        self.timeout = float(os.getenv("KOMMO_TIMEOUT", "30"))

        # Cache de access_token para OAuth2
        self._access_token: str = ""
        self._token_expires_at: float = 0.0

        if not self._long_lived_token and not all([self.client_id, self.client_secret, self._refresh_token]):
            logger.warning("Kommo: ni KOMMO_LONG_LIVED_TOKEN ni credenciales OAuth2 configurados")

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _token_valid(self) -> bool:
        return bool(self._access_token) and time.time() < (self._token_expires_at - 60)

    async def _refresh_access_token(self) -> str:
        """Refresca el access_token usando refresh_token + redirect_uri."""
        token_url = f"https://{os.getenv('KOMMO_SUBDOMAIN','')}.kommo.com/oauth2/access_token"
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(token_url, json={
                    "client_id":     self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type":    "refresh_token",
                    "refresh_token": self._refresh_token,
                    "redirect_uri":  self.redirect_uri,
                })
                r.raise_for_status()
                data = r.json()
                self._access_token = data.get("access_token", "")
                self._refresh_token = data.get("refresh_token", self._refresh_token)  # Kommo rota el refresh token
                expires_in = int(data.get("expires_in", 86400))
                self._token_expires_at = time.time() + expires_in
                logger.info("Kommo access_token refrescado (expires_in=%ds)", expires_in)
                return self._access_token
        except Exception as e:
            logger.error("Error refrescando token Kommo: %s", e)
            return ""

    async def _get_token(self) -> str:
        """Retorna el token activo según el modo de auth configurado."""
        if self._long_lived_token:
            return self._long_lived_token
        if not self._token_valid():
            await self._refresh_access_token()
        return self._access_token

    def _auth(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    # ── Request helper ────────────────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> dict[str, Any]:
        token = await self._get_token()
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.request(method, url, headers=self._auth(token), params=params, json=json)

                if r.status_code == 401 and not self._long_lived_token:
                    logger.warning("Kommo 401 — refrescando token y reintentando")
                    token = await self._refresh_access_token()
                    r = await c.request(method, url, headers=self._auth(token), params=params, json=json)

                if r.status_code == 204:
                    return {"status": "no_content"}
                if r.status_code == 404:
                    return {"error": "not_found", "path": path}
                if r.status_code >= 400:
                    logger.error("Kommo %s %s → %d: %s", method, path, r.status_code, r.text[:200])
                    return {"error": f"http_{r.status_code}", "path": path}
                return r.json() if r.content else {}
        except httpx.TimeoutException:
            return {"error": "timeout", "path": path}
        except Exception as e:
            return {"error": str(e), "path": path}

    # ── Leads ─────────────────────────────────────────────────────────────────

    async def get_lead(self, lead_id: int | str, with_: list[str] | None = None) -> dict[str, Any]:
        """GET /api/v4/leads/{id}?with=custom_fields_values,contacts"""
        params: dict[str, Any] = {}
        if with_:
            params["with"] = ",".join(with_)
        return await self._request("GET", f"/leads/{lead_id}", params=params)

    async def update_lead(self, lead_id: int | str, fields: dict[str, Any]) -> dict[str, Any]:
        """PATCH /api/v4/leads/{id}"""
        return await self._request("PATCH", f"/leads/{lead_id}", json=fields)

    async def update_leads_bulk(self, leads: list[dict[str, Any]]) -> dict[str, Any]:
        """PATCH /api/v4/leads — bulk update (array de objetos con id)."""
        return await self._request("PATCH", "/leads", json=leads)

    # ── Contacts ──────────────────────────────────────────────────────────────

    async def get_contact(self, contact_id: int | str, with_: list[str] | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if with_:
            params["with"] = ",".join(with_)
        return await self._request("GET", f"/contacts/{contact_id}", params=params)

    async def update_contact(self, contact_id: int | str, fields: dict[str, Any]) -> dict[str, Any]:
        """PATCH /api/v4/contacts/{id}"""
        return await self._request("PATCH", f"/contacts/{contact_id}", json=fields)

    # ── Custom fields schema ──────────────────────────────────────────────────

    async def get_lead_custom_fields(self) -> list[dict[str, Any]]:
        """GET /api/v4/leads/custom_fields — lista de campos custom de leads."""
        result = await self._request("GET", "/leads/custom_fields")
        return result.get("_embedded", {}).get("custom_fields", [])

    async def create_lead_custom_field(self, name: str, field_type: str = "text") -> dict[str, Any]:
        """
        POST /api/v4/leads/custom_fields — crear campo custom.
        field_type: text | numeric | checkbox | select | multiselect | date | url | textarea | radiobutton
        """
        return await self._request(
            "POST", "/leads/custom_fields",
            json=[{"name": name, "type": field_type}],
        )

    # ── Pipelines ─────────────────────────────────────────────────────────────

    async def get_pipelines(self) -> list[dict[str, Any]]:
        """GET /api/v4/leads/pipelines"""
        result = await self._request("GET", "/leads/pipelines")
        return result.get("_embedded", {}).get("pipelines", [])

    # ── Health ────────────────────────────────────────────────────────────────

    async def health_check(self) -> bool:
        """GET /api/v4/account — verifica conectividad."""
        token = await self._get_token()
        if not token or not self.base_url:
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.get(f"{self.base_url}/account", headers=self._auth(token))
                return r.status_code == 200
        except Exception:
            return False
