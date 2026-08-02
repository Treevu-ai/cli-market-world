"""
CLI Market Intelligence Client — HubSpot integration.

Wraps the intel endpoints de la API real de CLI Market:
  - GET /v1/intel/brief           (libre con auth)
  - GET /v1/intel/scores          (libre con auth)
  - GET /v1/intel/inflation       (libre con auth)
  - GET /v1/intel/macro           (libre con auth)
  - GET /v1/intel/procurement-signal  (Pro)
  - GET /v1/intel/price-risk          (Pro)

Los endpoints Pro devuelven 403 si el tier no alcanza; el cliente
los maneja gracefully y devuelve {"error": "tier_insufficient"}.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Paths canónicos (routers/intel.py + server_deps.py, 2026-07-31)
PATH_BRIEF = "/v1/intel/brief"
PATH_SCORES = "/v1/intel/scores"
PATH_INFLATION = "/v1/intel/inflation"
PATH_MACRO = "/v1/intel/macro"
PATH_PROCUREMENT_SIGNAL = "/v1/intel/procurement-signal"  # Pro
PATH_PRICE_RISK = "/v1/intel/price-risk"                  # Pro
PATH_HEALTH = "/health/stats"


class CLIMarketIntelClient:
    """Cliente async para los endpoints de inteligencia de CLI Market."""

    def __init__(self) -> None:
        self.api_url = os.getenv("CLI_MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")
        self.api_key = os.getenv("CLI_MARKET_API_KEY") or os.getenv("MARKET_API_TOKEN") or ""
        self.timeout = float(os.getenv("CLI_MARKET_TIMEOUT", "30"))
        if not self.api_key:
            logger.warning("CLI_MARKET_API_KEY no configurada — las llamadas fallarán con 401")

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET genérico con manejo de errores estándar."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(f"{self.api_url}{path}", headers=self._headers(), params=params or {})
                if r.status_code in (401, 403):
                    logger.warning("Auth/tier error en %s: %s", path, r.status_code)
                    return {"error": "tier_insufficient" if r.status_code == 403 else "unauthorized", "status_code": r.status_code}
                r.raise_for_status()
                return r.json() if r.content else {}
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error en %s: %s", path, e)
            return {"error": f"http_{e.response.status_code}", "path": path}
        except httpx.TimeoutException:
            logger.error("Timeout en %s", path)
            return {"error": "timeout", "path": path}
        except Exception as e:
            logger.error("Error en %s: %s", path, e)
            return {"error": str(e), "path": path}

    async def get_intel_brief(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        """Brief de inteligencia narrativa — shelf signal, headline, alertas."""
        return await self._get(PATH_BRIEF, {"country": country, "line": line})

    async def get_scores(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        """Scores compuestos: retail_aggression, price_fairness, basket_stress, etc."""
        return await self._get(PATH_SCORES, {"country": country, "line": line})

    async def get_inflation(self, country: str = "PE", line: str = "supermercados", days: int = 7) -> dict[str, Any]:
        """Variación de precios en N días, por línea y moneda."""
        return await self._get(PATH_INFLATION, {"country": country, "line": line, "days": days})

    async def get_macro(self, country: str = "PE") -> dict[str, Any]:
        """Tipo de cambio + IPC oficial Lima (BCRP). Sin tier requerido."""
        return await self._get(PATH_MACRO, {"country": country})

    async def get_procurement_signal(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        """Señal de procurement (buy_now / monitor / wait). Requiere Pro."""
        return await self._get(PATH_PROCUREMENT_SIGNAL, {"country": country, "line": line})

    async def get_price_risk(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        """Análisis de riesgo de precios. Requiere Pro."""
        return await self._get(PATH_PRICE_RISK, {"country": country, "line": line})

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self.api_url}{PATH_HEALTH}", headers=self._headers())
                return r.status_code == 200
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False

    async def get_market_summary(self, country: str = "PE") -> dict[str, Any]:
        """Fetch en paralelo de brief + scores + inflation para el enrichment de contactos."""
        import asyncio
        brief, scores, inflation = await asyncio.gather(
            self.get_intel_brief(country=country),
            self.get_scores(country=country),
            self.get_inflation(country=country),
            return_exceptions=False,
        )
        return {
            "country": country,
            "brief": brief if not isinstance(brief, Exception) else {"error": str(brief)},
            "scores": scores if not isinstance(scores, Exception) else {"error": str(scores)},
            "inflation": inflation if not isinstance(inflation, Exception) else {"error": str(inflation)},
        }
