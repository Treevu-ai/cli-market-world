"""Tests for routers/analytics.py — price history, stats, trending, brands, indicators."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db, db_save_user, db_set_subscription
from market_server import app, hash_password

import server_deps
from market_brand_registry import ensure_known_brands_schema

ensure_db_initialized()
ensure_known_brands_schema()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    # /analytics/indicators and /analytics/trending are Pro-gated (same data
    # tier as their /v1/intel/* equivalents) — default the token to Pro so
    # existing structure/behavior tests keep exercising the real response;
    # tier-gating itself is covered separately below.
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "pro")
    yield
    db_set_subscription("admin", "free")


# ── GET /analytics/price-history ─────────────────────────────────────────────

def test_price_history_requires_auth():
    r = client.get("/analytics/price-history")
    assert r.status_code == 401


def test_price_history_returns_structure():
    r = client.get("/analytics/price-history", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "snapshots" in data
    assert isinstance(data["snapshots"], list)


def test_price_history_with_store_filter():
    r = client.get("/analytics/price-history?store=wong", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "snapshots" in data


def test_price_history_with_product_filter():
    r = client.get("/analytics/price-history?product_id=prod-xyz", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_price_history_returns_inserted_row():
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, queried_at)
           VALUES ('hist-prod-1', 'metro', 'Metro', 'Arroz Costeño', 5.9, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/price-history?product_id=hist-prod-1", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert data["snapshots"][0]["product_id"] == "hist-prod-1"


def test_price_history_limit_param():
    r = client.get("/analytics/price-history?limit=1", headers=_AUTH)
    assert r.status_code == 200
    assert len(r.json()["snapshots"]) <= 1


# ── GET /analytics/stats ──────────────────────────────────────────────────────

def test_stats_requires_auth():
    r = client.get("/analytics/stats")
    assert r.status_code == 401


def test_stats_returns_expected_keys():
    r = client.get("/analytics/stats", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "total_price_snapshots" in data
    assert "total_search_queries" in data
    assert "unique_stores_tracked" in data
    assert "unique_products_tracked" in data
    assert "latest_snapshot_at" in data


def test_stats_counts_are_non_negative():
    r = client.get("/analytics/stats", headers=_AUTH)
    data = r.json()
    assert data["total_price_snapshots"] >= 0
    assert data["unique_stores_tracked"] >= 0


# ── GET /analytics/trending ───────────────────────────────────────────────────

def test_trending_requires_auth():
    r = client.get("/analytics/trending")
    assert r.status_code == 401


def test_trending_requires_pro():
    """Was require_api_key (any Free-tier key) — the same computed values
    /v1/intel/* charges Pro for. Free-tier users could read live trending
    price-velocity data for free."""
    db_set_subscription("admin", "starter")
    try:
        r = client.get("/analytics/trending", headers=_AUTH)
        assert r.status_code == 403
        assert "Pro" in r.json()["detail"]
    finally:
        db_set_subscription("admin", "pro")


def test_trending_returns_structure():
    r = client.get("/analytics/trending", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "trending" in data
    assert "total" in data
    assert isinstance(data["trending"], list)


def test_trending_with_line_filter():
    r = client.get("/analytics/trending?line=supermercados&limit=5", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "trending" in data


# ── GET /analytics/brands ─────────────────────────────────────────────────────

def test_brands_requires_auth():
    r = client.get("/analytics/brands")
    assert r.status_code == 401


def test_brands_returns_structure():
    r = client.get("/analytics/brands", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "brands" in data
    assert "total" in data
    assert isinstance(data["brands"], list)


def test_brands_with_line_filter():
    r = client.get("/analytics/brands?line=supermercados&limit=5", headers=_AUTH)
    assert r.status_code == 200


def test_brands_with_country_filter_excludes_other_countries():
    # wong=PE, carrefour=AR. Previously `country` was accepted but never
    # applied to the query, so both would appear regardless of the filter.
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('brand-filter-pe', 'wong', 'Wong', 'Producto PE', 'MarcaSoloPE', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('brand-filter-ar', 'carrefour', 'Carrefour AR', 'Producto AR', 'MarcaSoloAR', 5.0, 'ARS', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?country=PE&limit=50", headers=_AUTH)
    assert r.status_code == 200
    brands = {b["brand"] for b in r.json()["brands"]}
    assert "MarcaSoloPE" in brands
    assert "MarcaSoloAR" not in brands


def test_brands_merges_casing_variants():
    """"Gloria" and "GLORIA" are the same brand — price_snapshots.brand keeps
    whatever casing each retailer's page used, so a naive GROUP BY brand
    fragments one brand into several rows."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('casing-1', 'wong', 'Wong', 'Producto A', 'CasingBrandX', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('casing-2', 'metro', 'Metro', 'Producto B', 'CASINGBRANDX', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    assert r.status_code == 200
    matches = [b for b in r.json()["brands"] if b["brand"].lower() == "casingbrandx"]
    assert len(matches) == 1
    assert matches[0]["count"] >= 2


def test_brands_merges_accent_and_hyphen_variants():
    """Confirmed live 2026-07-20 across real PE data: "Nescafe"/"NESCAFÉ",
    "Genérico"/"Generico", "Fisher-Price"/"FISHER PRICE" and 5 more pairs all
    fragmented the same brand across accent or hyphenation differences —
    not a one-brand fluke, the same accent-folding normalizer product search
    already uses (_normalize_text) must merge these too, not just casing."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('accent-1', 'wong', 'Wong', 'Producto A', 'AccéntBrandZ', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('accent-2', 'metro', 'Metro', 'Producto B', 'ACCENTBRANDZ', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('hyphen-1', 'plazavea', 'Plaza Vea', 'Producto C', 'Hyphen-BrandZ', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('hyphen-2', 'wong', 'Wong', 'Producto D', 'HYPHEN BRANDZ', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    assert r.status_code == 200
    accent_matches = [b for b in r.json()["brands"] if "accentbrandz" in b["brand"].lower().replace("é", "e")]
    assert len(accent_matches) == 1
    assert accent_matches[0]["count"] >= 2

    hyphen_matches = [b for b in r.json()["brands"] if "brandz" in b["brand"].lower() and "hyphen" in b["brand"].lower()]
    assert len(hyphen_matches) == 1
    assert hyphen_matches[0]["count"] >= 2


def test_brands_merges_spacing_variants():
    """Confirmed live 2026-07-20 on real PE 'arroz' data: "Valle Norte" and
    "VALLENORTE" are the same brand missing a space, not merged by
    casing/accent folding alone since that preserves word boundaries."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('spacing-1', 'wong', 'Wong', 'Producto E', 'Space Brand Q', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('spacing-2', 'metro', 'Metro', 'Producto F', 'SPACEBRANDQ', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    assert r.status_code == 200
    matches = [b for b in r.json()["brands"] if b["brand"].lower().replace(" ", "") == "spacebrandq"]
    assert len(matches) == 1
    assert matches[0]["count"] >= 2


def test_brands_keeps_store_name_as_brand_for_private_label():
    """A store's own name as brand ("Wong") is real private-label ("marca
    blanca") data, not a scraping artifact — must not be filtered out just
    because it matches a store key."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('privatelabel-1', 'wong', 'Wong', 'Producto Marca Blanca', 'Wong', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    assert r.status_code == 200
    brands = {b["brand"] for b in r.json()["brands"]}
    assert "Wong" in brands


def test_brands_filters_placeholder_junk_values():
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('junk-1', 'wong', 'Wong', 'Producto Sin Marca', '—', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    assert r.status_code == 200
    brands = {b["brand"] for b in r.json()["brands"]}
    assert "—" not in brands


def test_brands_flags_new_brand_only_on_first_sighting():
    """First call with a never-seen brand marks is_new=true; the exact same
    call again must report is_new=false — it's already in known_brands now."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('newbrand-1', 'wong', 'Wong', 'Producto Nuevo', 'BrandNeverSeenBefore', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r1 = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    row1 = next(b for b in r1.json()["brands"] if b["brand"] == "BrandNeverSeenBefore")
    assert row1["is_new"] is True

    r2 = client.get("/analytics/brands?country=PE&limit=200", headers=_AUTH)
    row2 = next(b for b in r2.json()["brands"] if b["brand"] == "BrandNeverSeenBefore")
    assert row2["is_new"] is False


def test_brands_is_new_is_null_without_country_filter():
    """"New" is only meaningful scoped to a country — without one, is_new is
    null rather than silently defaulting to a guess."""
    r = client.get("/analytics/brands?limit=5", headers=_AUTH)
    assert r.status_code == 200
    for b in r.json()["brands"]:
        assert b["is_new"] is None


def test_brands_query_scopes_to_matching_products_only():
    """query='cafe' should only count brands whose SKUs actually match
    'cafe' by name (word-boundary), not every brand in the line."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('query-cafe-1', 'wong', 'Wong', 'Cafe Instantaneo QueryBrandCafe 100g', 'QueryBrandCafe', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('query-noncafe-1', 'wong', 'Wong', 'Arroz QueryBrandArroz 1kg', 'QueryBrandArroz', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?query=cafe&limit=200", headers=_AUTH)
    assert r.status_code == 200
    brands = {b["brand"] for b in r.json()["brands"]}
    assert "QueryBrandCafe" in brands
    assert "QueryBrandArroz" not in brands


def test_brands_query_avoids_prefix_false_positive():
    """Word-boundary matching: query='pan' must not match a product whose
    name merely contains 'pan' as a substring ('pantalon')."""
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, currency, line, line_name, queried_at)
           VALUES ('query-prefix-1', 'wong', 'Wong', 'Pantalon QueryBrandPantalon Talla M', 'QueryBrandPantalon', 5.0, 'PEN', 'supermercados', 'Supermercados', datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/analytics/brands?query=pan&limit=200", headers=_AUTH)
    assert r.status_code == 200
    brands = {b["brand"] for b in r.json()["brands"]}
    assert "QueryBrandPantalon" not in brands


# ── GET /analytics/indicators ─────────────────────────────────────────────────

def test_indicators_requires_auth():
    r = client.get("/analytics/indicators")
    assert r.status_code == 401


def test_indicators_requires_pro():
    """Returns live computed indicator VALUES (promo_intensity, moat_freshness,
    price_dispersion, + external World Bank/IMF/Eurostat/BCB sources) — more
    valuable than /v1/intel/indicators' Pro-gated definitions-only catalog.
    Was require_api_key (any Free-tier key), an unintended paywall bypass."""
    db_set_subscription("admin", "starter")
    try:
        r = client.get("/analytics/indicators", headers=_AUTH)
        assert r.status_code == 403
        assert "Pro" in r.json()["detail"]
    finally:
        db_set_subscription("admin", "pro")


def test_indicators_returns_structure():
    r = client.get("/analytics/indicators", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "catalog_size" in data
    assert "indicators" in data
    assert isinstance(data["indicators"], list)


def test_indicators_with_country_filter():
    r = client.get("/analytics/indicators?country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["country"] == "PE"
