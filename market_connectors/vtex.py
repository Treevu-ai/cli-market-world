"""
market_connectors/vtex.py — VTEX connector.

Implements BaseConnector for VTEX public catalog API.
Supports standard (/api/) and VTEX IO (/io/api/) path auto-detection.
"""

import asyncio

import httpx
from .base import BaseConnector, parse_price, clean_name

PAGE_SIZE = 20
CATALOG_PAGE_SIZE = 50


def _vtex_headers(store_config: dict) -> dict[str, str]:
    key = store_config.get("vtex_app_key", "")
    token = store_config.get("vtex_app_token", "")
    if key and token:
        return {
            "X-VTEX-API-AppKey": key,
            "X-VTEX-API-AppToken": token,
        }
    return {}


class VtexConnector(BaseConnector):
    platform = "vtex"

    async def _detect_io(self, store_config: dict) -> str:
        base = store_config["base"]
        async with httpx.AsyncClient(timeout=8.0) as c:
            headers = _vtex_headers(store_config)
            try:
                r = await c.get(f"{base}/api/catalog_system/pub/category/tree/10", headers=headers)
                ct = r.headers.get("content-type", "")
                if r.status_code == 200 and "json" in ct:
                    store_config["_io_path"] = ""
                    return ""
            except Exception:
                pass
            try:
                r = await c.get(f"{base}/io/api/catalog_system/pub/category/tree/10", headers=headers)
                ct = r.headers.get("content-type", "")
                if r.status_code == 200 and "json" in ct:
                    store_config["_io_path"] = "/io"
                    return "/io"
            except Exception:
                pass
        store_config["_io_path"] = ""
        return ""

    def _api_url(self, store_config: dict, path: str) -> str:
        base = store_config["base"]
        io = store_config.get("_io_path")
        return f"{base}{io or ''}/api/{path}"

    async def search(self, store_config: dict, term: str,
                     page: int = 1, limit: int = PAGE_SIZE) -> list[dict]:
        if store_config.get("_io_path") is None:
            await self._detect_io(store_config)
        url = f"{self._api_url(store_config, 'catalog_system/pub/products/search')}/{term}"
        _from = (page - 1) * PAGE_SIZE
        _to = min(_from + limit - 1, _from + PAGE_SIZE - 1)
        headers = _vtex_headers(store_config)
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, params={"_from": str(_from), "_to": str(_to)}, headers=headers)
            if resp.status_code == 429:
                await asyncio.sleep(2.0)
                resp = await client.get(url, params={"_from": str(_from), "_to": str(_to)}, headers=headers)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            if "json" not in ct:
                return []
            data = resp.json()
            return data if isinstance(data, list) else []

    async def fetch_all_products(self, store_config: dict,
                                  max_pages: int = 10) -> list[dict]:
        if store_config.get("_io_path") is None:
            await self._detect_io(store_config)
        url = self._api_url(store_config, "catalog_system/pub/products/search")
        all_products = []
        headers = _vtex_headers(store_config)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for page in range(1, max_pages + 1):
                _from = (page - 1) * CATALOG_PAGE_SIZE
                _to = page * CATALOG_PAGE_SIZE - 1
                resp = await client.get(url, params={
                    "_from": str(_from), "_to": str(_to),
                    "O": "OrderByTopSaleDESC",
                }, headers=headers)
                if resp.status_code in (200, 206):
                    data = resp.json()
                    all_products.extend(data)
                    if len(data) < CATALOG_PAGE_SIZE:
                        break
                else:
                    break
        return all_products

    def normalize(self, raw: dict, store_key: str, store_config: dict) -> dict:
        items = raw.get("items", [])
        item = items[0] if items else {}
        sellers = item.get("sellers", [])
        seller = sellers[0] if sellers else {}
        offer = seller.get("commertialOffer", {})
        price = parse_price(offer.get("Price"))
        list_price = parse_price(offer.get("ListPrice"))
        discount = round((1 - price / list_price) * 100) if list_price > price > 0 else None
        return {
            "id": raw.get("productReference", raw.get("productId", "")),
            "product_id": raw.get("productReference", raw.get("productId", "")),
            "name": clean_name(raw.get("productName", "")),
            "brand": raw.get("brand") or "—",
            "category": raw.get("categoryId", ""),
            "price": price,
            "list_price": list_price,
            "discount": discount,
            "stock": offer.get("AvailableQuantity", 0),
            "store": store_key,
            "store_name": store_config["name"],
            "currency": store_config["currency"],
            "url": f"{store_config.get('link_base', store_config['base'])}/{raw.get('linkText', '')}/p",
        }

    async def categories(self, store_config: dict) -> list[dict]:
        if store_config.get("_io_path") is None:
            await self._detect_io(store_config)
        url = self._api_url(store_config, "catalog_system/pub/category/tree/10")
        headers = _vtex_headers(store_config)
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
