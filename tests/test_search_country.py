"""Country filter for search/compare store resolution."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from routers.search import SearchRequest, _resolve_search_stores


@pytest.fixture(autouse=True)
def _mock_store_exists(monkeypatch):
    monkeypatch.setattr("routers.search._STORE_CREDENTIALS_AVAILABLE", False)


def test_resolve_search_stores_filters_by_country():
    body = SearchRequest(query="leche", country="PE")
    stores = _resolve_search_stores(body)
    assert stores
    assert all(
        __import__("market_core").STORES[s]["country"] == "PE"
        for s in stores
    )


def test_resolve_search_stores_single_store_ignores_country_mismatch():
    from market_core import STORES

    pe_store = next(s for s, meta in STORES.items() if meta["country"] == "PE")
    body = SearchRequest(query="leche", store=pe_store, country="AR")
    stores = _resolve_search_stores(body)
    assert stores == []


def test_compare_parallel_fetch(monkeypatch):
    import asyncio

    from routers import search as search_mod

    async def fake_fetch(store: str, query: str, page: int, limit: int):
        return [{"name": f"{store}-{query}", "price": 1.0, "brand": "x"}]

    monkeypatch.setattr(search_mod, "fetch_store", fake_fetch)

    stores = ["wong_pe", "metro_pe"]
    all_raw, errors = asyncio.run(
        search_mod._parallel_fetch_stores(stores, "leche", 1, 5)
    )
    assert errors == []
    assert set(all_raw.keys()) == set(stores)
