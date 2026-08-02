"""
CLIMarketIntelClient — shared by HubSpot and Zoho adapters.

Endpoints:
  Libre (solo auth):
    GET /v1/intel/brief
    GET /v1/intel/scores
    GET /v1/intel/inflation
    GET /v1/intel/macro
  Pro-gated:
    GET /v1/intel/procurement-signal
    GET /v1/intel/price-risk
  Pro+ (basket):
    POST /v1/basket/compare
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

PATH_BRIEF              = "/v1/intel/brief"
PATH_SCORES             = "/v1/intel/scores"
PATH_INFLATION          = "/v1/intel/inflation"
PATH_MACRO              = "/v1/intel/macro"
PATH_PROCUREMENT_SIGNAL = "/v1/intel/procurement-signal"  # Pro
PATH_PRICE_RISK         = "/v1/intel/price-risk"          # Pro
PATH_BASKET             = "/v1/basket/compare"
PATH_HEALTH             = "/health/stats"


class CLIMarketIntelClient:
    """
    Async client for CLI Market intelligence endpoints.
    Used by HubSpot and Zoho adapters.
    Simla uses CLIMarketProductClient (product search/compare/basket) instead.
    """

    def __init__(self) -> None:
        self.api_url = os.getenv("CLI_MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")
        self.api_key = os.getenv("CLI_MARKET_API_KEY") or os.getenv("MARKET_API_TOKEN") or ""
        self.timeout = float(os.getenv("CLI_MARKET_TIMEOUT", "30"))
        if not self.api_key:
            logger.warning("CLI_MARKET_API_KEY not set — requests will fail with 401")

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(
                    f"{self.api_url}{path}", headers=self._headers(), params=params or {}
                )
                if r.status_code in (401, 403):
                    return {
                        "error": "tier_insufficient" if r.status_code == 403 else "unauthorized",
                        "status_code": r.status_code,
                    }
                r.raise_for_status()
                return r.json() if r.content else {}
        except httpx.TimeoutException:
            logger.error("Timeout on %s", path)
            return {"error": "timeout", "path": path}
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error on %s: %s", path, e)
            return {"error": f"http_{e.response.status_code}", "path": path}
        except Exception as e:
            logger.error("Error on %s: %s", path, e)
            return {"error": str(e), "path": path}

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(
                    f"{self.api_url}{path}",
                    headers={**self._headers(), "Content-Type": "application/json"},
                    json=payload,
                )
                if r.status_code in (401, 403):
                    return {
                        "error": "tier_insufficient" if r.status_code == 403 else "unauthorized",
                        "status_code": r.status_code,
                    }
                r.raise_for_status()
                return r.json() if r.content else {}
        except Exception as e:
            logger.error("Error POST %s: %s", path, e)
            return {"error": str(e), "path": path}

    # ── Free endpoints ────────────────────────────────────────────────────────

    async def get_intel_brief(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        return await self._get(PATH_BRIEF, {"country": country, "line": line})

    async def get_scores(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        return await self._get(PATH_SCORES, {"country": country, "line": line})

    async def get_inflation(self, country: str = "PE", line: str = "supermercados", days: int = 7) -> dict[str, Any]:
        return await self._get(PATH_INFLATION, {"country": country, "line": line, "days": days})

    async def get_macro(self, country: str = "PE") -> dict[str, Any]:
        return await self._get(PATH_MACRO, {"country": country})

    # ── Pro endpoints ─────────────────────────────────────────────────────────

    async def get_procurement_signal(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        """Requires Pro tier. Returns {"error": "tier_insufficient"} if not enough."""
        return await self._get(PATH_PROCUREMENT_SIGNAL, {"country": country, "line": line})

    async def get_price_risk(self, country: str = "PE", line: str = "supermercados") -> dict[str, Any]:
        """Requires Pro tier."""
        return await self._get(PATH_PRICE_RISK, {"country": country, "line": line})

    # ── Basket (Pro+) ─────────────────────────────────────────────────────────

    async def optimize_basket(self, products: list[str], country: str = "PE") -> dict[str, Any]:
        """POST /v1/basket/compare — Pro+ in prod. NOTE: /v1/optimize does not exist."""
        payload = {
            "items": [{"query": p, "qty": 1} for p in products if p and str(p).strip()],
            "country": country,
            "live": False,
        }
        return await self._post(PATH_BASKET, payload)

    # ── Convenience ───────────────────────────────────────────────────────────

    async def get_market_summary(self, country: str = "PE") -> dict[str, Any]:
        """brief + scores + inflation in parallel (all free tier)."""
        brief, scores, inflation = await asyncio.gather(
            self.get_intel_brief(country=country),
            self.get_scores(country=country),
            self.get_inflation(country=country),
        )
        return {"country": country, "brief": brief, "scores": scores, "inflation": inflation}

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self.api_url}{PATH_HEALTH}", headers=self._headers())
                return r.status_code == 200
        except Exception:
            return False
