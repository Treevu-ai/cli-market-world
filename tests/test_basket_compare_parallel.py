"""Regression for world#363: POST /v1/basket/compare (live-fetch fallback,
no include_tco/include_action_links) used to fetch every item across every
store fully sequentially — O(stores * items) awaited calls, one after
another — which timed out at 60s in production for a 3-item PE basket.
It must fetch items in parallel instead.

No pytest-asyncio in this repo's CI — drive the coroutine with asyncio.run()
from a plain sync test, matching the rest of this test suite's convention.
"""

from __future__ import annotations

import asyncio

import pytest

import routers.search as search_mod


@pytest.fixture
def two_test_stores(monkeypatch):
    stores = {
        "store_a": {"name": "Store A", "currency": "PEN", "country": "PE", "line": "supermercados"},
        "store_b": {"name": "Store B", "currency": "PEN", "country": "PE", "line": "supermercados"},
    }
    monkeypatch.setattr(search_mod, "STORES", stores)
    monkeypatch.setattr(search_mod, "require_api_key", lambda auth: "test-user")
    return stores


def test_basket_compare_fetches_items_concurrently_not_sequentially(two_test_stores, monkeypatch):
    """Two items, each fetch takes 0.2s. Sequential (old behavior) would take
    ~2 * stores * 0.2s = 0.8s; parallel (gather across items) should take
    close to a single _parallel_fetch_stores round (~0.2s)."""
    call_log: list[str] = []

    async def fake_parallel_fetch_stores(stores, query, page, limit):
        call_log.append(query)
        await asyncio.sleep(0.2)
        raw = {
            s: [{"id": f"{s}-{query}", "name": f"Leche Gloria 1L ({s})", "price": 3.5 if s == "store_a" else 3.0}]
            for s in stores
        }
        return raw, []

    monkeypatch.setattr(search_mod, "_parallel_fetch_stores", fake_parallel_fetch_stores)
    monkeypatch.setattr(search_mod, "product_from_json", lambda p, store: p)
    monkeypatch.setattr(search_mod, "_query_tokens", lambda q: [])
    monkeypatch.setattr(search_mod, "infer_category", lambda name: None)

    body = search_mod.BasketRequest(
        items=[{"name": "leche gloria"}, {"name": "arroz costeño"}],
        stores=["store_a", "store_b"],
    )

    async def _run():
        start = asyncio.get_event_loop().time()
        result = await search_mod.basket_compare(body, authorization="Bearer test")
        elapsed = asyncio.get_event_loop().time() - start
        return result, elapsed

    result, elapsed = asyncio.run(_run())

    assert len(call_log) == 2  # one _parallel_fetch_stores call per item
    assert elapsed < 0.35, f"basket_compare took {elapsed:.2f}s — items were not fetched in parallel"
    assert result["stores_compared"] == 2
    assert result["best_store"] == "store_b"  # cheaper per-item price
    assert result["comparison"]["store_a"]["items_found"] == 2
    assert result["comparison"]["store_b"]["total"] == pytest.approx(6.0)
