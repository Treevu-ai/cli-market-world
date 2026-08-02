"""
HubSpot API Client — wrapper sobre hubspot-api-client SDK.

Usa Private App Access Token (HUBSPOT_ACCESS_TOKEN), que es el
método recomendado por HubSpot (API Keys están deprecados).

Operaciones:
  - Leer contactos y deals por ID
  - Actualizar propiedades custom (market intelligence)
  - Crear propiedades custom (setup inicial)
  - Asociaciones contact → deal
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Las custom properties que el middleware escribe en HubSpot
CONTACT_MARKET_PROPS = [
    "market_basket_stress",
    "market_inflation_signal",
    "market_price_fairness",
    "market_retail_aggression",
    "market_data_updated",
]

DEAL_MARKET_PROPS = [
    "price_risk_level",
    "procurement_signal",
    "market_recommended_action",
    "price_intelligence_updated",
]


class HubSpotClient:
    """
    Cliente REST directo a la HubSpot API v3 (sin SDK de terceros para
    evitar dependencias pesadas en el prototipo; usa httpx async igual
    que el resto del stack).

    Para producción se puede migrar a hubspot-api-client si se necesita
    el SDK completo (objetos, paginación, batch updates, etc.).
    """

    BASE_URL = "https://api.hubapi.com"

    def __init__(self) -> None:
        self.access_token = (
            os.getenv("HUBSPOT_ACCESS_TOKEN")
            or os.getenv("HUBSPOT_API_KEY")  # fallback legacy
            or ""
        )
        self.timeout = float(os.getenv("HUBSPOT_TIMEOUT", "30"))
        if not self.access_token:
            logger.warning("HUBSPOT_ACCESS_TOKEN no configurado — operaciones HubSpot fallarán")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ── Contactos ─────────────────────────────────────────────────────────────

    async def get_contact(self, contact_id: str, properties: list[str] | None = None) -> dict[str, Any]:
        """GET /crm/v3/objects/contacts/{id}"""
        params: dict[str, str] = {}
        if properties:
            params["properties"] = ",".join(properties)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(
                    f"{self.BASE_URL}/crm/v3/objects/contacts/{contact_id}",
                    headers=self._headers(),
                    params=params,
                )
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            logger.error("Error get_contact %s: %s", contact_id, e)
            return {"error": f"http_{e.response.status_code}", "contact_id": contact_id}
        except Exception as e:
            logger.error("Error get_contact %s: %s", contact_id, e)
            return {"error": str(e)}

    async def update_contact_properties(
        self, contact_id: str, properties: dict[str, str]
    ) -> dict[str, Any]:
        """PATCH /crm/v3/objects/contacts/{id}"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.patch(
                    f"{self.BASE_URL}/crm/v3/objects/contacts/{contact_id}",
                    headers=self._headers(),
                    json={"properties": properties},
                )
                r.raise_for_status()
                return r.json() if r.content else {"status": "updated"}
        except httpx.HTTPStatusError as e:
            logger.error("Error update_contact %s: %s", contact_id, e)
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            logger.error("Error update_contact %s: %s", contact_id, e)
            return {"error": str(e)}

    # ── Deals ─────────────────────────────────────────────────────────────────

    async def get_deal(self, deal_id: str, properties: list[str] | None = None) -> dict[str, Any]:
        """GET /crm/v3/objects/deals/{id}"""
        params: dict[str, str] = {}
        if properties:
            params["properties"] = ",".join(properties)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(
                    f"{self.BASE_URL}/crm/v3/objects/deals/{deal_id}",
                    headers=self._headers(),
                    params=params,
                )
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            logger.error("Error get_deal %s: %s", deal_id, e)
            return {"error": f"http_{e.response.status_code}", "deal_id": deal_id}
        except Exception as e:
            logger.error("Error get_deal %s: %s", deal_id, e)
            return {"error": str(e)}

    async def update_deal_properties(
        self, deal_id: str, properties: dict[str, str]
    ) -> dict[str, Any]:
        """PATCH /crm/v3/objects/deals/{id}"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.patch(
                    f"{self.BASE_URL}/crm/v3/objects/deals/{deal_id}",
                    headers=self._headers(),
                    json={"properties": properties},
                )
                r.raise_for_status()
                return r.json() if r.content else {"status": "updated"}
        except httpx.HTTPStatusError as e:
            logger.error("Error update_deal %s: %s", deal_id, e)
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            logger.error("Error update_deal %s: %s", deal_id, e)
            return {"error": str(e)}

    # ── Propiedades custom (setup) ─────────────────────────────────────────────

    async def ensure_contact_property(self, name: str, label: str, field_type: str, prop_type: str) -> bool:
        """
        Crea una propiedad custom de contacto si no existe.
        field_type: 'text' | 'number' | 'date' | 'select'
        prop_type:  'string' | 'number' | 'datetime' | 'enumeration'
        """
        payload = {
            "name": name,
            "label": label,
            "type": prop_type,
            "fieldType": field_type,
            "groupName": "cli_market_intelligence",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(
                    f"{self.BASE_URL}/crm/v3/properties/contacts",
                    headers=self._headers(),
                    json=payload,
                )
                if r.status_code == 409:
                    # Ya existe — OK
                    return True
                r.raise_for_status()
                logger.info("Propiedad creada en HubSpot: contacts.%s", name)
                return True
        except Exception as e:
            logger.error("Error creando propiedad %s: %s", name, e)
            return False

    async def ensure_deal_property(self, name: str, label: str, field_type: str, prop_type: str) -> bool:
        """Crea una propiedad custom de deal si no existe."""
        payload = {
            "name": name,
            "label": label,
            "type": prop_type,
            "fieldType": field_type,
            "groupName": "cli_market_intelligence",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(
                    f"{self.BASE_URL}/crm/v3/properties/deals",
                    headers=self._headers(),
                    json=payload,
                )
                if r.status_code == 409:
                    return True
                r.raise_for_status()
                logger.info("Propiedad creada en HubSpot: deals.%s", name)
                return True
        except Exception as e:
            logger.error("Error creando propiedad deal %s: %s", name, e)
            return False

    async def health_check(self) -> bool:
        """Verifica conectividad con HubSpot usando el endpoint de account info."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self.BASE_URL}/account-info/v3/details",
                    headers=self._headers(),
                )
                return r.status_code == 200
        except Exception as e:
            logger.error("HubSpot health check failed: %s", e)
            return False
