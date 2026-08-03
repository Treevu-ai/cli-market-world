"""
CLI Market product client for Simla adapter.
Handles product search, compare, basket, price history.
(Simla uses product endpoints, not intel endpoints — see shared/intel_client.py for intel.)
"""
from __future__ import annotations

# Re-export from prototype — same code, lives here for package install
from simla_cli_market_prototype.src.cli_market_client import CLIMarketClient  # noqa: F401

# If installed as package (not from prototype path), inline the class:
import logging, os
from typing import Any
import httpx

logger = logging.getLogger(__name__)

PATH_SEARCH       = "/products/search"
PATH_COMPARE      = "/products/compare"
PATH_BASKET       = "/v1/basket/compare"
PATH_PRICE_HISTORY = "/analytics/price-history"
PATH_HEALTH       = "/health/stats"


class CLIMarketProductClient:
    """Client for CLI Market product/price endpoints (used by Simla adapter)."""

    def __init__(self) -> None:
        self.api_url = os.getenv("CLI_MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")
        self.api_key = os.getenv("CLI_MARKET_API_KEY") or os.getenv("MARKET_API_TOKEN") or ""
        self.timeout = float(os.getenv("CLI_MARKET_TIMEOUT", "30"))
        if not self.api_key:
            logger.warning("CLI_MARKET_API_KEY not set")

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.post(f"{self.api_url}{path}", headers=self._headers(), json=payload)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def search_product(self, query: str, country: str = "PE", limit: int = 10) -> dict[str, Any]:
        raw = await self._post(PATH_SEARCH, {"query": query, "country": country, "limit": limit, "live": False})
        if raw.get("error"):
            return {**raw, "products": [], "query": query}
        results = raw.get("results") or raw.get("products") or raw.get("items") or []
        products = [
            {
                "name": i.get("name") or i.get("title") or query,
                "price": i.get("price") or i.get("current_price") or i.get("price_pen"),
                "store": i.get("store_name") or i.get("store") or i.get("retailer"),
                "store_id": i.get("store_id") or i.get("store"),
                "product_id": i.get("product_id") or i.get("id"),
                "url": i.get("url") or i.get("product_url"),
                "last_updated": i.get("last_updated") or i.get("captured_at") or i.get("ts"),
                "currency": i.get("currency") or "PEN",
            }
            for i in results
        ]
        return {"query": raw.get("query", query), "products": products, "total": raw.get("total", len(products))}

    async def compare_prices(self, product: str, country: str = "PE", limit: int = 20) -> dict[str, Any]:
        raw = await self._post(PATH_COMPARE, {"query": product, "country": country, "limit": limit, "live": False})
        if raw.get("error"):
            return {**raw, "comparisons": []}
        results = raw.get("results") or raw.get("comparisons") or raw.get("stores") or []
        comparisons = sorted(
            [{"store": i.get("store_name") or i.get("store"), "price": i.get("price") or 0, "name": i.get("name") or product, "url": i.get("url")} for i in results if i.get("price") is not None],
            key=lambda x: float(x.get("price") or 0),
        )
        return {"product": product, "comparisons": comparisons, "best_price": comparisons[0] if comparisons else None}

    async def optimize_basket(self, products: list[str], country: str = "PE") -> dict[str, Any]:
        raw = await self._post(PATH_BASKET, {"items": [{"query": p, "qty": 1} for p in products if p], "country": country, "live": False})
        if raw.get("error"):
            return {**raw, "recommendations": []}
        best_store = raw.get("best_store") or raw.get("recommended_store")
        breakdown = raw.get("breakdown") or raw.get("items") or raw.get("leader_items") or []
        recs = [
            {"product": r.get("query") or r.get("name") or "item", "optimized_price": r.get("price") or 0, "original_price": r.get("list_price") or r.get("price") or 0, "savings": r.get("savings") or 0, "store": r.get("store_name") or r.get("store") or best_store}
            for r in breakdown if isinstance(r, dict)
        ]
        return {"recommendations": recs, "recommended_store": best_store, "total_savings": raw.get("savings") or raw.get("total_savings"), "best_total": raw.get("best_total") or raw.get("total")}

    async def get_price_history(self, product: str, days: int = 30, country: str = "PE", product_id: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"country": country, "limit": max(days, 10)}
        if not product_id:
            search = await self.search_product(product, country=country, limit=1)
            prods = search.get("products") or []
            if not prods:
                return {"error": "no_product_for_history", "history": []}
            product_id = prods[0].get("product_id") or prods[0].get("id")
            if product_id:
                params["product_id"] = product_id
            store = prods[0].get("store_id") or prods[0].get("store")
            if store:
                params["store"] = store
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.get(f"{self.api_url}{PATH_PRICE_HISTORY}", headers=self._headers(), params=params)
                r.raise_for_status()
                raw = r.json()
        except Exception as e:
            return {"error": str(e), "history": []}
        rows = raw.get("history") or raw.get("snapshots") or raw.get("data") or raw.get("results") or (raw if isinstance(raw, list) else [])
        return {"history": [{"date": e.get("date") or e.get("captured_at") or e.get("ts"), "price": e.get("price") or e.get("current_price"), "store": e.get("store_name") or e.get("store")} for e in rows if isinstance(e, dict)]}

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                return (await c.get(f"{self.api_url}{PATH_HEALTH}")).status_code == 200
        except Exception:
            return False
