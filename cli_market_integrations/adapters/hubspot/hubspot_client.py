"""HubSpot API client — unchanged from prototype."""
from __future__ import annotations
import logging, os
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class HubSpotClient:
    BASE_URL = "https://api.hubapi.com"

    def __init__(self) -> None:
        self.access_token = os.getenv("HUBSPOT_ACCESS_TOKEN") or os.getenv("HUBSPOT_API_KEY") or ""
        self.timeout = float(os.getenv("HUBSPOT_TIMEOUT", "30"))
        if not self.access_token:
            logger.warning("HUBSPOT_ACCESS_TOKEN not set")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json", "Accept": "application/json"}

    async def get_contact(self, contact_id: str, properties: list[str] | None = None) -> dict[str, Any]:
        params = {"properties": ",".join(properties)} if properties else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.get(f"{self.BASE_URL}/crm/v3/objects/contacts/{contact_id}", headers=self._headers(), params=params)
                r.raise_for_status(); return r.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"http_{e.response.status_code}", "contact_id": contact_id}
        except Exception as e:
            return {"error": str(e)}

    async def update_contact_properties(self, contact_id: str, properties: dict[str, str]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.patch(f"{self.BASE_URL}/crm/v3/objects/contacts/{contact_id}", headers=self._headers(), json={"properties": properties})
                r.raise_for_status(); return r.json() if r.content else {"status": "updated"}
        except httpx.HTTPStatusError as e:
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_deal(self, deal_id: str, properties: list[str] | None = None) -> dict[str, Any]:
        params = {"properties": ",".join(properties)} if properties else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.get(f"{self.BASE_URL}/crm/v3/objects/deals/{deal_id}", headers=self._headers(), params=params)
                r.raise_for_status(); return r.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"http_{e.response.status_code}", "deal_id": deal_id}
        except Exception as e:
            return {"error": str(e)}

    async def update_deal_properties(self, deal_id: str, properties: dict[str, str]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.patch(f"{self.BASE_URL}/crm/v3/objects/deals/{deal_id}", headers=self._headers(), json={"properties": properties})
                r.raise_for_status(); return r.json() if r.content else {"status": "updated"}
        except httpx.HTTPStatusError as e:
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def ensure_contact_property(self, name: str, label: str, field_type: str, prop_type: str) -> bool:
        payload = {"name": name, "label": label, "type": prop_type, "fieldType": field_type, "groupName": "cli_market_intelligence"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.post(f"{self.BASE_URL}/crm/v3/properties/contacts", headers=self._headers(), json=payload)
                if r.status_code == 409: return True
                r.raise_for_status(); return True
        except Exception as e:
            logger.error("Error creating contact property %s: %s", name, e); return False

    async def ensure_deal_property(self, name: str, label: str, field_type: str, prop_type: str) -> bool:
        payload = {"name": name, "label": label, "type": prop_type, "fieldType": field_type, "groupName": "cli_market_intelligence"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.post(f"{self.BASE_URL}/crm/v3/properties/deals", headers=self._headers(), json=payload)
                if r.status_code == 409: return True
                r.raise_for_status(); return True
        except Exception as e:
            logger.error("Error creating deal property %s: %s", name, e); return False

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                return (await c.get(f"{self.BASE_URL}/account-info/v3/details", headers=self._headers())).status_code == 200
        except Exception:
            return False
