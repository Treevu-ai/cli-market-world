"""Tests for indicator schema, computations, and intel API endpoints."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from market_core import ensure_db_initialized, get_db
from market_server import app


ensure_db_initialized()
client = TestClient(app)


@pytest.fixture
def seeded_snapshots():
    db = get_db()
    for pid, store, price, disc in [
        ("sku1", "wong", 4.5, 10),
        ("sku2", "metro", 4.2, 0),
    ]:
        db.execute(
            """
            INSERT INTO price_snapshots
                (product_id, name, brand, price, list_price, discount, store, store_name,
                 currency, line, line_name, category, stock, url, queried_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))
            ON CONFLICT(product_id, store) DO UPDATE SET
                price=excluded.price, list_price=excluded.list_price, discount=excluded.discount
            """,
            (
                pid,
                "Leche Gloria 1L",
                "Gloria",
                price,
                price + 0.5 if disc else price,
                disc,
                store,
                store.title(),
                "PEN",
                "supermercados",
                "Super",
                "Lácteos",
                1,
                "",
            ),
        )
    db.commit()
    db.close()
    yield


def test_indicator_tables_exist():
    db = get_db()
    tables = {r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    db.close()
    assert "indicator_definitions" in tables
    assert "indicator_values" in tables
    assert "price_history" in tables


def test_indicator_definitions_seeded():
    db = get_db()
    n = db.execute("SELECT COUNT(*) AS c FROM indicator_definitions").fetchone()["c"]
    db.close()
    assert n >= 34


def test_promo_intensity_computation(seeded_snapshots):
    from market_indicators import compute_promo_intensity

    db = get_db()
    val = compute_promo_intensity(db, country="PE", line="supermercados")
    db.close()
    assert val is not None
    assert 0 <= val <= 100


def test_price_history_on_snapshot_save(seeded_snapshots):
    import market_core

    market_core.save_price_snapshot({
        "id": "sku1",
        "name": "Leche Gloria 1L",
        "price": 4.8,
        "list_price": 5.0,
        "discount": 4,
        "store": "wong",
        "store_name": "Wong",
    })
    db = get_db()
    rows = db.execute(
        "SELECT COUNT(*) AS c FROM price_history WHERE product_id = 'sku1' AND store = 'wong'"
    ).fetchone()["c"]
    db.close()
    assert rows >= 1


def test_intel_indicators_catalog_endpoint():
    r = client.get("/v1/intel/indicators")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 34
    keys = {i["key"] for i in data["indicators"]}
    assert "promo_intensity" in keys
    assert "fx_usd_local" in keys


def test_intel_scores_endpoint():
    r = client.get("/v1/intel/scores?country=PE")
    assert r.status_code == 200
    body = r.json()
    assert "scores" in body
    assert "disclaimer" in body


def test_intel_basket_stress_endpoint():
    r = client.get("/v1/intel/basket-stress?country=PE")
    assert r.status_code == 200
    assert "basket_stress_index" in r.json()


def test_intel_inflation_unchanged_contract():
    r = client.get("/v1/intel/inflation?country=PE&days=30&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "avg_inflation_pct" in data
    assert "items" in data
    assert "disclaimer" in data


def test_analytics_indicators_endpoint():
    r = client.get("/analytics/indicators?country=PE&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "indicators" in data
    assert "catalog_size" in data
    assert data["catalog_size"] >= 34


def test_refresh_internal_indicators(seeded_snapshots):
    from market_indicators import refresh_indicators

    result = refresh_indicators(country="PE", line="supermercados")
    assert result["internal_written"] >= 1

    db = get_db()
    n = db.execute(
        "SELECT COUNT(*) AS c FROM indicator_values WHERE country IN ('PE', '')"
    ).fetchone()["c"]
    db.close()
    assert n >= 1


def test_refresh_after_collection_skipped_when_disabled(monkeypatch):
    monkeypatch.setenv("INDICATOR_AUTO_REFRESH", "0")
    from market_indicators import refresh_after_collection

    result = refresh_after_collection(["PE"])
    assert result.get("skipped") is True
