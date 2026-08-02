"""Zoho CRM client — unchanged from prototype."""
from __future__ import annotations
import logging, os, time
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class ZohoCRMClient:
    def __init__(self) -> None:
        self.client_id = os.getenv("ZOHO_CLIENT_ID", "")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET", "")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN", "")
        self.api_domain = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com").rstrip("/")
        self.timeout = float(os.getenv("ZOHO_TIMEOUT", "30"))
        self.base_url = f"{self.api_domain}/crm/v2"
        self._access_token: str = ""
        self._token_expires_at: float = 0.0
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.warning("Zoho OAuth credentials not fully configured")

    def _token_valid(self) -> bool:
        return bool(self._access_token) and time.time() < (self._token_expires_at - 60)

    async def _refresh_access_token(self) -> str:
        if not self.refresh_token: return ""
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                r = await c.post(f"{self.api_domain}/oauth/v2/token", data={"refresh_token": self.refresh_token, "client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "refresh_token"})
                r.raise_for_status(); data = r.json()
                self._access_token = data.get("access_token", "")
                self._token_expires_at = time.time() + int(data.get("expires_in", 3600))
                return self._access_token
        except Exception as e:
            logger.error("Error refreshing Zoho token: %s", e); return ""

    async def _get_token(self) -> str:
        if not self._token_valid(): await self._refresh_access_token()
        return self._access_token

    def _auth(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Zoho-oauthtoken {token}"}

    async def _request(self, method: str, path: str, *, params=None, json=None, data=None) -> dict[str, Any]:
        token = await self._get_token()
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.request(method, url, headers=self._auth(token), params=params, json=json, data=data)
                if r.status_code == 401:
                    token = await self._refresh_access_token()
                    r = await c.request(method, url, headers=self._auth(token), params=params, json=json, data=data)
                if r.status_code == 404: return {"error": "not_found", "path": path}
                if r.status_code >= 400:
                    logger.error("Zoho %s %s → %d", method, path, r.status_code); return {"error": f"http_{r.status_code}", "path": path}
                return r.json() if r.content else {}
        except httpx.TimeoutException: return {"error": "timeout", "path": path}
        except Exception as e: return {"error": str(e), "path": path}

    async def get_record(self, module: str, record_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/{module}/{record_id}")

    async def update_record(self, module: str, record_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PUT", f"/{module}/{record_id}", json={"data": [{**fields, "id": record_id}]})

    async def create_record(self, module: str, fields: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", f"/{module}", json={"data": [fields]})

    async def search_records(self, module: str, criteria: str, limit: int = 20) -> list[dict[str, Any]]:
        result = await self._request("GET", f"/{module}/search", params={"criteria": criteria, "per_page": limit})
        return result.get("data", []) if not result.get("error") else []

    async def health_check(self) -> bool:
        return bool(await self._get_token())
