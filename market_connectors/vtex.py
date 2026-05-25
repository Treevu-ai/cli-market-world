"""
market_connectors/vtex.py — VTEX connector.

Migrated from market_core.py. Implements BaseConnector for VTEX's public
catalog API (/api/catalog_system/pub/products/search).
"""

import httpx
from .base import BaseConnector, parse_price, clean_name

PAGE_SIZE = 20


class VtexConnector(BaseConnector):
    platform = "vtex"

    async def search(self, store_config: dict, term: str,
                     page: int = 1, limit: int = PAGE_SIZE) -> list[dict]:
        base = store_config["base"]
        url = f"{base}/api/catalog_system/pub/products/search/{term}"
        _from = (page - 1) * PAGE_SIZE
        _to = min(_from + limit - 1, _from + PAGE_SIZE - 1)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params={"_from": str(_from), "_to": str(_to)})
            resp.raise_for_status()
            return resp.json()

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
            "url": f"{store_config['base']}/{raw.get('linkText', '')}/p",
        }

    async def categories(self, store_config: dict) -> list[dict]:
        base = store_config["base"]
        url = f"{base}/api/catalog_system/pub/category/tree/10"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
