"""Subcategory enrichment + tier-2 public sources (mocked HTTP)."""

import sys
from datetime import datetime, timedelta, timezone
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
    for pid, store, name, price in [
        ("sku1", "wong", "Leche Gloria entera 1L", 4.5),
        ("sku2", "metro", "Arroz Costeño 1kg", 3.8),
        ("sku3", "wong", "Aceite Primor 1L", 9.2),
    ]:
        db.execute(
            """
            INSERT INTO price_snapshots
                (product_id, name, brand, price, list_price, discount, store, store_name,
                 currency, line, line_name, category, stock, url, queried_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))
            ON CONFLICT(product_id, store) DO UPDATE SET
                price=excluded.price, name=excluded.name
            """,
            (
                pid, name, "Brand", price, price, 0,
                store, store.title(), "PEN", "supermercados", "Super", "Alimentos", 1, "",
            ),
        )
    db.commit()
    db.close()
    yield


def test_canasta_subcategories_count():
    from market_enrich_subcategory import ENRICH_SUBCATEGORIES

    assert len(ENRICH_SUBCATEGORIES) == 10


def test_subcat_min_price(seeded_snapshots):
    from market_enrich_subcategory import compute_subcat_min_price

    db = get_db()
    leche = compute_subcat_min_price(db, "PE", "leche")
    arroz = compute_subcat_min_price(db, "PE", "arroz")
    db.close()
    assert leche == 4.5
    assert arroz == 3.8


def test_refresh_subcategory_mock(seeded_snapshots, monkeypatch):
    from market_enrich_subcategory import refresh_subcategory_enrichment
    from market_indicators import _upsert_indicator_value, seed_indicator_definitions

    monkeypatch.setattr(
        "market_enrich_subcategory.fetch_subcat_wiki_momentum",
        lambda cc, sub: 1.12,
    )
    monkeypatch.setattr(
        "market_enrich_subcategory.compute_subcat_price_momentum",
        lambda db, cc, sub, days=7: 2.5 if sub == "leche" else 0.5,
    )

    db = get_db()
    seed_indicator_definitions(db)
    n = refresh_subcategory_enrichment(db, "PE", _upsert_indicator_value)
    db.commit()
    count = db.execute(
        "SELECT COUNT(*) AS c FROM indicator_values WHERE scope LIKE 'PE:subcat:%'"
    ).fetchone()["c"]
    db.close()
    assert n >= 10
    assert count >= 10


def test_tier2_fetchers_mock(monkeypatch):
    import market_enrich_sources as mes

    monkeypatch.setattr(mes, "_imf_indicator_table", lambda ind: {"PER": 2.4, "BRA": 4.4, "ITA": 1.1} if ind == "PCPIPCH" else {"PER": 3.5, "BRA": 3.4})
    monkeypatch.setattr(mes, "fetch_eurostat_food_hicp_yoy", lambda cc: 2.4 if cc == "IT" else None)
    monkeypatch.setattr(mes, "fetch_bcb_food_inflation_mom", lambda cc: 1.34 if cc == "BR" else None)
    monkeypatch.setattr(mes, "fetch_wb_unemployment_rate", lambda cc: 5.8)

    assert mes.fetch_imf_inflation_yoy("PE") == 2.4
    assert mes.fetch_imf_gdp_growth_yoy("PE") == 3.5
    assert mes.fetch_eurostat_food_hicp_yoy("IT") == 2.4
    assert mes.fetch_eurostat_food_hicp_yoy("PE") is None
    assert mes.fetch_bcb_food_inflation_mom("BR") == 1.34
    assert mes.fetch_wb_unemployment_rate("PE") == 5.8


def test_refresh_tier2_mock(seeded_snapshots, monkeypatch):
    from market_indicators import refresh_enrichment_indicators, seed_indicator_definitions

    monkeypatch.setattr("market_indicators._indicator_is_stale", lambda *a, **k: True)
    monkeypatch.setattr("market_enrich_sources.sample_off_coverage", lambda *a, **k: {"sampled": 0})
    monkeypatch.setattr("market_enrich_sources.fetch_wiki_demand_momentum", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_wiki_staple_momentum", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_weather_logistics_stress", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_food_cpi_yoy", lambda cc: None)
    monkeypatch.setattr("market_enrich_subcategory.refresh_subcategory_enrichment", lambda *a, **k: 0)
    monkeypatch.setattr("market_enrich_sources.fetch_imf_inflation_yoy", lambda cc: 2.4)
    monkeypatch.setattr("market_enrich_sources.fetch_eurostat_food_hicp_yoy", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_bcb_food_inflation_mom", lambda cc: None)
    monkeypatch.setattr("market_enrich_sources.fetch_wb_unemployment_rate", lambda cc: 6.1)

    db = get_db()
    seed_indicator_definitions(db)
    db.execute(
        """
        INSERT INTO indicator_values (indicator_key, scope, country, value, recorded_at)
        VALUES ('cpi_official_yoy', 'PE:macro', 'PE', 3.2, datetime('now'))
        """
    )
    db.commit()
    n = refresh_enrichment_indicators(db, "PE")
    db.commit()
    keys = {
        r["indicator_key"]
        for r in db.execute(
            "SELECT indicator_key FROM indicator_values WHERE country='PE' AND scope='PE:enrichment'"
        ).fetchall()
    }
    db.close()
    assert n >= 2
    assert "imf_inflation_yoy" in keys
    assert "macro_unemployment_rate" in keys


def test_intel_subcategories_endpoint(seeded_snapshots):
    from market_indicators import _upsert_indicator_value, seed_indicator_definitions

    db = get_db()
    seed_indicator_definitions(db)
    _upsert_indicator_value(
        db,
        indicator_key="subcat_min_price",
        scope="PE:subcat:leche",
        value=4.5,
        country="PE",
        metadata={"subcategory": "leche"},
    )
    db.commit()
    db.close()

    r = client.get("/v1/intel/enrichment/subcategories?country=PE")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    assert "leche" in body["subcategories"]
    leche = next(i for i in body["items"] if i["subcategory"] == "leche")
    assert leche["signals"]["subcat_min_price"]["value"] == 4.5
