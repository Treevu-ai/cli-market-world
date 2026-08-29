"""run_full_catalog_pg must call every platform collect_full_catalog_pg supports.

Before this fix, run_full_catalog_pg's per-store filter only allowed
vtex/woocommerce/estacion90, silently excluding shopify/algolia stores from
the periodic full-catalog pull even though collect_full_catalog_pg (the
function it calls) already supported those two platforms
(cli-market-core PRD 2026-08-28, backlog Epic A / A1).
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import collect_prices as cp

_STORE = "__test_shopify_store__"


def _fake_resolve_store_config(store: str) -> dict:
    if store == _STORE:
        return {"platform": "shopify", "line": "moda"}
    return {"platform": "unknown"}


def test_run_full_catalog_pg_calls_shopify_store():
    with patch("store_credentials.resolve_store_config", side_effect=_fake_resolve_store_config), \
         patch("collect_prices.collect_full_catalog_pg", new=AsyncMock(return_value=5)) as mock_collect:
        cp._last_catalog_pull = 0.0
        total = asyncio.run(cp.run_full_catalog_pg(pool=None, stores=[_STORE], force=True))

    mock_collect.assert_awaited_once_with(None, _STORE)
    assert total == 5


def test_run_full_catalog_pg_calls_algolia_store():
    def _resolve(store: str) -> dict:
        return {"platform": "algolia", "line": "farmacias"} if store == _STORE else {"platform": "unknown"}

    with patch("store_credentials.resolve_store_config", side_effect=_resolve), \
         patch("collect_prices.collect_full_catalog_pg", new=AsyncMock(return_value=3)) as mock_collect:
        cp._last_catalog_pull = 0.0
        total = asyncio.run(cp.run_full_catalog_pg(pool=None, stores=[_STORE], force=True))

    mock_collect.assert_awaited_once_with(None, _STORE)
    assert total == 3


def test_run_full_catalog_pg_still_skips_unsupported_platform():
    def _resolve(store: str) -> dict:
        return {"platform": "custom_rest", "line": "hogar"} if store == _STORE else {"platform": "unknown"}

    with patch("store_credentials.resolve_store_config", side_effect=_resolve), \
         patch("collect_prices.collect_full_catalog_pg", new=AsyncMock(return_value=0)) as mock_collect:
        cp._last_catalog_pull = 0.0
        asyncio.run(cp.run_full_catalog_pg(pool=None, stores=[_STORE], force=True))

    mock_collect.assert_not_awaited()
