"""Tests for enrichment sources (mocked HTTP — no live API calls in CI)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from market_core import ensure_db_initialized, get_db


ensure_db_initialized()


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
                pid, "Leche Gloria 1L", "Gloria", price, price + 0.5 if disc else price, disc,
                store, store.title(), "PEN", "supermercados", "Super", "Lácteos", 1, "",
            ),
        )
    db.commit()
    db.close()
    yield


def test_enrichment_cache_table_exists():
    db = get_db()
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    db.close()
    assert "enrichment_cache" in tables


def test_off_normalize_and_cache(seeded_snapshots, monkeypatch):
    from market_enrich_sources import cache_get, cache_set, fetch_off_by_search, resolve_off_for_product

    fake = {
        "product_name": "Leche entera",
        "brands": "Gloria",
        "nutriscore_grade": "b",
        "nova_group": 2,
        "categories": "dairies",
        "code": "1234567890123",
    }

    monkeypatch.setattr(
        "market_enrich_sources.fetch_off_by_search",
        lambda q: {
            "code": fake["code"],
            "name": fake["product_name"],
            "brand": fake["brands"],
            "nutriscore": "B",
            "nova_group": 2,
            "categories": fake["categories"],
        },
    )

    db = get_db()
    result = resolve_off_for_product(db, "not-ean-id", "Leche Gloria entera 1L")
    db.commit()
    assert result is not None
    assert result["nutriscore"] == "B"
    cached = cache_get(db, "off:search:leche gloria entera")
    db.close()
    assert cached is not None


def test_sample_off_coverage_mock(seeded_snapshots, monkeypatch):
    from market_enrich_sources import sample_off_coverage

    monkeypatch.setattr(
        "market_enrich_sources.resolve_off_for_product",
        lambda db, pid, name: {
            "code": "1",
            "name": name,
            "nutriscore": "A",
            "nova_group": 1,
        },
    )

    db = get_db()
    off = sample_off_coverage(db, "PE", limit=2)
    db.close()
    assert off["sampled"] >= 1
    assert off["match_rate_pct"] == 100.0


def test_refresh_enrichment_mock(seeded_snapshots, monkeypatch):
    from market_indicators import refresh_enrichment_indicators

    monkeypatch.setattr("market_indicators._indicator_is_stale", lambda *a, **k: True)
    monkeypatch.setattr(
        "market_enrich_sources.sample_off_coverage",
        lambda db, cc, limit=None: {
            "sampled": 5,
            "matched": 3,
            "match_rate_pct": 60.0,
            "nutriscore_ab_pct": 66.7,
            "nova_avg": 2.3,
            "ultra_processed_pct": 33.3,
            "ecoscore_avg": 3.8,
            "samples": [],
        },
    )
    monkeypatch.setattr("market_enrich_sources.fetch_wiki_demand_momentum", lambda cc: 1.15)
    monkeypatch.setattr("market_enrich_sources.fetch_wiki_staple_momentum", lambda cc: 1.08)
    monkeypatch.setattr("market_enrich_sources.fetch_weather_logistics_stress", lambda cc: 22.5)
    monkeypatch.setattr("market_enrich_sources.fetch_food_cpi_yoy", lambda cc: 8.2)
    monkeypatch.setattr("market_indicators.compute_staple_price_momentum", lambda db, cc, days=7: 2.4)
    monkeypatch.setattr("market_enrich_subcategory.refresh_subcategory_enrichment", lambda *a, **k: 0)
    monkeypatch.setattr("market_enrich_sources.fetch_imf_inflation_yoy", lambda cc: 2.1)
    monkeypatch.setattr("market_enrich_sources.fetch_eurostat_food_hicp_yoy", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_bcb_food_inflation_mom", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_wb_unemployment_rate", lambda cc: 5.5)

    db = get_db()
    n = refresh_enrichment_indicators(db, "PE")
    db.commit()
    count = db.execute(
        """
        SELECT COUNT(*) AS c FROM indicator_values
        WHERE country = 'PE' AND indicator_key IN (
            'off_match_rate', 'off_nutriscore_ab_pct', 'off_nova_avg', 'off_ultra_processed_pct',
            'off_ecoscore_avg', 'wiki_demand_momentum', 'wiki_staple_momentum',
            'weather_logistics_stress', 'food_cpi_yoy', 'food_inflation_spread', 'staple_price_momentum'
        )
        """
    ).fetchone()["c"]
    db.close()
    assert n >= 6
    assert count >= 6


def test_staple_price_momentum(seeded_snapshots):
    from datetime import datetime, timedelta, timezone
    from market_indicators import compute_staple_price_momentum

    db = get_db()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    for pid, store, prices in [
        ("sku1", "wong", [(week_ago, 4.0), (now, 4.4)]),
        ("sku2", "metro", [(week_ago, 3.0), (now, 3.0)]),
    ]:
        for ts, price in prices:
            db.execute(
                """
                INSERT INTO price_history (product_id, store, price, list_price, discount, recorded_at)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (pid, store, price, price, ts),
            )
    db.commit()
    mom = compute_staple_price_momentum(db, "PE", days=7)
    db.close()
    assert mom is not None
    assert mom > 0


def test_ultra_processed_in_off_sample(seeded_snapshots, monkeypatch):
    from market_enrich_sources import sample_off_coverage

    monkeypatch.setattr(
        "market_enrich_sources.resolve_off_for_product",
        lambda db, pid, name: {
            "code": "1",
            "name": name,
            "nutriscore": "C",
            "nova_group": 4 if pid == "sku1" else 2,
        },
    )

    db = get_db()
    off = sample_off_coverage(db, "PE", limit=2)
    db.close()
    assert off["ultra_processed_pct"] == 50.0


def test_intel_enrichment_refresh_endpoint(seeded_snapshots, monkeypatch):
    from fastapi.testclient import TestClient
    from market_server import app

    monkeypatch.setattr("market_indicators._indicator_is_stale", lambda *a, **k: True)
    monkeypatch.setattr(
        "market_enrich_sources.sample_off_coverage",
        lambda db, cc, limit=None: {
            "sampled": 3,
            "matched": 2,
            "match_rate_pct": 66.7,
            "nutriscore_ab_pct": 50.0,
            "nova_avg": 3.0,
            "ultra_processed_pct": 50.0,
            "ecoscore_avg": 3.5,
            "samples": [],
        },
    )
    monkeypatch.setattr("market_enrich_sources.fetch_wiki_demand_momentum", lambda cc: 1.0)
    monkeypatch.setattr("market_enrich_sources.fetch_wiki_staple_momentum", lambda cc: 1.05)
    monkeypatch.setattr("market_enrich_sources.fetch_weather_logistics_stress", lambda cc: 10.0)
    monkeypatch.setattr("market_enrich_sources.fetch_food_cpi_yoy", lambda cc: 9.5)
    monkeypatch.setattr("market_indicators.compute_staple_price_momentum", lambda db, cc, days=7: 1.2)
    monkeypatch.setattr("market_enrich_subcategory.refresh_subcategory_enrichment", lambda *a, **k: 0)
    monkeypatch.setattr("market_enrich_sources.fetch_imf_inflation_yoy", lambda cc: 2.0)
    monkeypatch.setattr("market_enrich_sources.fetch_wb_unemployment_rate", lambda cc: 5.0)

    client = TestClient(app)
    r = client.post("/v1/intel/enrichment/refresh?country=PE")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body.get("enrichment_written", 0) >= 1


def test_intel_enrichment_endpoint(seeded_snapshots):
    from fastapi.testclient import TestClient
    from market_server import app

    client = TestClient(app)
    r = client.get("/v1/intel/enrichment?country=PE")
    assert r.status_code == 200
    body = r.json()
    assert "indicators" in body
    assert "openfoodfacts" in body["sources"]
