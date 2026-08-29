"""collect_full_catalog_pg must log (not silently swallow) a failed insert.

Before this fix, a product that failed `pg_insert` (constraint, bad type,
whatever) vanished from that store's catalog for the cycle with zero
diagnosable trace — `except Exception: pass`, unlike the store-level fetch
exceptions two lines up which already use logger.warning
(cli-market-core PRD 2026-08-28, backlog Epic C / C1).
"""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock, patch

import collect_prices as cp

_STORE = "__test_catalog_insert_store__"


class _FakeConnector:
    async def fetch_all_products(self, cfg, max_pages=20):
        return [{"id": "1"}, {"id": "2"}]

    def normalize(self, raw, store, cfg):
        return {"product_id": raw["id"], "price": 10.0, "name": f"Product {raw['id']}"}


class _FakePoolConn:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, *exc):
        return False


class _FakePool:
    def acquire(self):
        return _FakePoolConn()


def test_failed_insert_is_logged_not_swallowed(caplog):
    async def _pg_insert(conn, prod):
        if prod["product_id"] == "1":
            raise ValueError("boom")
        return None

    with patch("store_credentials.resolve_store_config", return_value={"platform": "vtex", "line": "hogar"}), \
         patch("market_connectors.get_connector", return_value=_FakeConnector()), \
         patch("collect_prices.pg_insert", new=AsyncMock(side_effect=_pg_insert), create=True), \
         patch("collect_prices.max_allowed_price", return_value=999_999.0), \
         caplog.at_level(logging.WARNING):
        collected = asyncio.run(cp.collect_full_catalog_pg(_FakePool(), _STORE))

    # The second product (id=2) still gets inserted despite the first failing.
    assert collected == 1
    warnings = [r for r in caplog.records if "catalog insert failed" in r.getMessage()]
    assert len(warnings) == 1
    assert _STORE in warnings[0].getMessage()
    assert "1" in warnings[0].getMessage()
