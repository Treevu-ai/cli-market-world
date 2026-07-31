"""
CLI Market API Client
Cliente async alineado a los endpoints reales de producción (cli-market-api.fly.dev).
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Endpoints canónicos (OpenAPI prod, 2026-07-31)
PATH_SEARCH = "/products/search"
PATH_COMPARE = "/products/compare"
PATH_BASKET = "/v1/basket/compare"
PATH_PRICE_HISTORY = "/analytics/price-history"
PATH_HEALTH = "/health/stats"


class CLIMarketClient:
    """Cliente para la API de CLI Market (auth Bearer sk-… / API key)."""

    def __init__(self) -> None:
        self.api_url = os.getenv("CLI_MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")
        self.api_key = os.getenv("CLI_MARKET_API_KEY") or os.getenv("MARKET_API_TOKEN") or ""
        self.timeout = float(os.getenv("CLI_MARKET_TIMEOUT", "30"))
        if not self.api_key:
            logger.warning("CLI_MARKET_API_KEY no está configurada")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search_product(self, query: str, country: str = "PE", limit: int = 10) -> dict[str, Any]:
        """POST /products/search — discovery de un producto."""
        payload = {"query": query, "country": country, "limit": limit, "live": False}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}{PATH_SEARCH}",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                raw = response.json()
                return self._normalize_search(raw, query)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error en search: %s %s", e.response.status_code, e.request.url)
            return {"error": f"search_http_{e.response.status_code}", "products": [], "query": query}
        except Exception as e:
            logger.error("Error en search: %s", e)
            return {"error": str(e), "products": [], "query": query}

    async def compare_prices(self, product: str, country: str = "PE", limit: int = 20) -> dict[str, Any]:
        """POST /products/compare — un producto, ranking por tienda."""
        payload = {"query": product, "country": country, "limit": limit, "live": False}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}{PATH_COMPARE}",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                raw = response.json()
                return self._normalize_compare(raw, product)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error en compare: %s", e)
            return {"error": f"compare_http_{e.response.status_code}", "comparisons": []}
        except Exception as e:
            logger.error("Error en compare: %s", e)
            return {"error": str(e), "comparisons": []}

    async def optimize_basket(self, products: list[str], country: str = "PE") -> dict[str, Any]:
        """POST /v1/basket/compare — canasta multi-item (tier Pro+ en prod)."""
        # Contrato real: items = lista de strings o {query, qty}
        payload: dict[str, Any] = {
            "items": [{"query": p, "qty": 1} for p in products if p and str(p).strip()],
            "country": country,
            "live": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}{PATH_BASKET}",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                raw = response.json()
                return self._normalize_basket(raw)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error en basket: %s body=%s", e, getattr(e.response, "text", "")[:200])
            return {"error": f"basket_http_{e.response.status_code}", "recommendations": []}
        except Exception as e:
            logger.error("Error en basket: %s", e)
            return {"error": str(e), "recommendations": []}

    async def get_price_history(
        self,
        product: str,
        days: int = 30,
        country: str = "PE",
        product_id: str | None = None,
    ) -> dict[str, Any]:
        """GET /analytics/price-history — snapshots (mejor con product_id)."""
        params: dict[str, Any] = {"country": country, "limit": max(days, 10)}
        if product_id:
            params["product_id"] = product_id
        # Sin product_id la API filtra por line/store; hacemos search y tomamos el primero
        try:
            if not product_id:
                search = await self.search_product(product, country=country, limit=1)
                products = search.get("products") or []
                if not products:
                    return {"error": "no_product_for_history", "history": []}
                product_id = products[0].get("product_id") or products[0].get("id")
                if product_id:
                    params["product_id"] = product_id
                store = products[0].get("store_id") or products[0].get("store")
                if store:
                    params["store"] = store

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}{PATH_PRICE_HISTORY}",
                    headers=self._headers(),
                    params=params,
                )
                response.raise_for_status()
                raw = response.json()
                return self._normalize_history(raw)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error en price_history: %s", e)
            return {"error": f"history_http_{e.response.status_code}", "history": []}
        except Exception as e:
            logger.error("Error en price_history: %s", e)
            return {"error": str(e), "history": []}

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}{PATH_HEALTH}")
                return response.status_code == 200
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False

    # ── normalizers: API prod → shape que espera whatsapp_formatter ─────────

    @staticmethod
    def _normalize_search(raw: dict[str, Any], query: str) -> dict[str, Any]:
        results = raw.get("results") or raw.get("products") or raw.get("items") or []
        products = []
        for item in results:
            products.append(
                {
                    "name": item.get("name") or item.get("title") or query,
                    "price": item.get("price") or item.get("current_price") or item.get("price_pen"),
                    "store": item.get("store_name") or item.get("store") or item.get("retailer"),
                    "store_id": item.get("store_id") or item.get("store"),
                    "product_id": item.get("product_id") or item.get("id"),
                    "url": item.get("url") or item.get("product_url"),
                    "last_updated": item.get("last_updated") or item.get("captured_at") or item.get("ts"),
                    "currency": item.get("currency") or "PEN",
                }
            )
        return {
            "query": raw.get("query", query),
            "products": products,
            "total": raw.get("total", len(products)),
            "raw_keys": list(raw.keys()),
        }

    @staticmethod
    def _normalize_compare(raw: dict[str, Any], product: str) -> dict[str, Any]:
        # compare suele devolver results por tienda o un ranking similar a search
        results = raw.get("results") or raw.get("comparisons") or raw.get("stores") or []
        comparisons: list[dict[str, Any]] = []
        for item in results:
            price = item.get("price") or item.get("current_price")
            comparisons.append(
                {
                    "store": item.get("store_name") or item.get("store") or item.get("retailer"),
                    "price": price if price is not None else 0,
                    "name": item.get("name") or product,
                    "url": item.get("url") or item.get("product_url"),
                }
            )
        comparisons = [c for c in comparisons if c.get("price") is not None]
        comparisons.sort(key=lambda x: float(x.get("price") or 0))
        best = comparisons[0] if comparisons else None
        return {
            "product": product,
            "comparisons": comparisons,
            "best_price": best,
        }

    @staticmethod
    def _normalize_basket(raw: dict[str, Any]) -> dict[str, Any]:
        best_store = raw.get("best_store") or raw.get("recommended_store")
        best_total = raw.get("best_total") or raw.get("total")
        breakdown = raw.get("breakdown") or raw.get("items") or raw.get("leader_items") or []
        recommendations = []
        for row in breakdown:
            if isinstance(row, dict):
                recommendations.append(
                    {
                        "product": row.get("query") or row.get("name") or row.get("item") or "item",
                        "optimized_price": row.get("price") or row.get("unit_price") or 0,
                        "original_price": row.get("list_price") or row.get("price") or 0,
                        "savings": row.get("savings") or 0,
                        "store": row.get("store_name") or row.get("store") or best_store,
                    }
                )
        return {
            "recommendations": recommendations,
            "recommended_store": best_store,
            "total_savings": raw.get("savings") or raw.get("total_savings"),
            "best_total": best_total,
            "incomplete": raw.get("incomplete") or raw.get("items_missing"),
        }

    @staticmethod
    def _normalize_history(raw: dict[str, Any]) -> dict[str, Any]:
        rows = raw.get("history") or raw.get("snapshots") or raw.get("data") or raw.get("results") or []
        if isinstance(raw, list):
            rows = raw
        history = []
        for entry in rows:
            if not isinstance(entry, dict):
                continue
            history.append(
                {
                    "date": entry.get("date")
                    or entry.get("captured_at")
                    or entry.get("ts")
                    or entry.get("created_at"),
                    "price": entry.get("price") or entry.get("current_price"),
                    "store": entry.get("store_name") or entry.get("store"),
                }
            )
        return {"history": history}
