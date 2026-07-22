"""GET /stores must include dynamically-approved retailers (store_credentials),
not just the static built-in catalog, and must badge the Growth flag."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db
from market_server import app

from backend_interface import invalidate_credential_cache

ensure_db_initialized()
client = TestClient(app)

_CUSTOM_STORE = "test_catalog_custom_store"


@pytest.fixture
def custom_store_fixture():
    db = get_db()
    db.execute("DELETE FROM store_credentials WHERE store_id = ?", (_CUSTOM_STORE,))
    db.execute(
        "INSERT INTO store_credentials "
        "(store_id, platform, store_name, country, currency, line, active, "
        "wc_consumer_key, wc_consumer_secret, is_growth) "
        "VALUES (?, 'woocommerce', 'Test Catalog Store', 'PE', 'PEN', 'electro', 1, "
        "'ck_x', 'cs_x', 1)",
        (_CUSTOM_STORE,),
    )
    db.commit()
    db.close()
    invalidate_credential_cache()
    yield
    db = get_db()
    db.execute("DELETE FROM store_credentials WHERE store_id = ?", (_CUSTOM_STORE,))
    db.commit()
    db.close()
    invalidate_credential_cache()


def test_custom_store_appears_in_public_catalog(custom_store_fixture):
    r = client.get("/stores")
    assert r.status_code == 200
    stores = r.json()["stores"]
    assert _CUSTOM_STORE in stores, "dynamically-approved retailer missing from /stores"
    assert stores[_CUSTOM_STORE]["is_growth"] is True


def test_custom_store_country_filter(custom_store_fixture):
    r = client.get("/stores?country=PE")
    assert r.status_code == 200
    assert _CUSTOM_STORE in r.json()["stores"]

    r2 = client.get("/stores?country=AR")
    assert _CUSTOM_STORE not in r2.json()["stores"]


def test_non_growth_store_flag_is_false():
    r = client.get("/stores")
    stores = r.json()["stores"]
    static_store = next(iter(stores.values()))
    assert static_store["is_growth"] is False
