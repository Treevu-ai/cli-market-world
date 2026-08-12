"""Tests for routers/search.py — product search, stock, delivery, barcode, enrich."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db
from market_server import app

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


def _as_timestamp_str(value):
    """queried_at is TIMESTAMPTZ on Postgres -- psycopg2 auto-deserializes it
    to a datetime, unlike SQLite's plain TEXT column (found 2026-08-05, test-pg
    triage). Normalize either form to the same 'YYYY-MM-DD HH:MM:SS' string."""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


# ── POST /products/search ─────────────────────────────────────────────────────

def test_search_requires_auth():
    r = client.post("/products/search", json={"query": "leche"})
    assert r.status_code == 401


def test_search_empty_query_returns_422():
    r = client.post("/products/search", json={"query": ""}, headers=_AUTH)
    assert r.status_code == 422


def test_search_returns_query_and_results_keys():
    # live=true exercises the mocked per-store scrape path — the default
    # path reads price_snapshots directly and ignores this mock, so
    # asserting total==0 against it is only meaningful for the live path
    # (and otherwise flakes on real "leche"-matching rows other tests seed
    # into the shared DB).
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post("/products/search", json={"query": "leche", "live": True}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "query" in data
    assert "results" in data
    assert "total" in data
    assert data["query"] == "leche"
    assert data["total"] == 0


def test_search_with_store_filter():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post(
            "/products/search",
            json={"query": "arroz", "store": "wong", "country": "PE"},
            headers=_AUTH,
        )
    assert r.status_code == 200


def test_search_errors_in_partial_response():
    # live=true exercises the per-store scrape path (_parallel_fetch_stores);
    # the default path now reads price_snapshots and has no per-store errors.
    errors = [{"store": "somestore", "error": "timeout"}]
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, errors))):
        r = client.post("/products/search", json={"query": "aceite", "live": True}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data.get("partial") is True
    assert len(data["errors"]) >= 1


def test_search_query_sanitizes_special_chars():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post(
            "/products/search",
            json={"query": "<script>alert(1)</script>leche"},
            headers=_AUTH,
        )
    assert r.status_code == 200
    assert "<script>" not in r.json()["query"]


# ── POST /products/compare ────────────────────────────────────────────────────

def test_compare_no_auth_returns_401():
    r = client.post("/products/compare", json={"query": "leche"})
    assert r.status_code == 401


def test_compare_returns_comparison_structure():
    with patch("routers.search._parallel_fetch_stores", new=AsyncMock(return_value=({}, []))):
        r = client.post("/products/compare", json={"query": "arroz"}, headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "comparison" in data
    assert "stores_compared" in data
    assert "stores_resolved" in data


def test_compare_stores_resolved_zero_for_unknown_country():
    """Reproduces a real diagnosed ambiguity: market_compare returning an
    empty comparison looked identical whether zero stores matched the
    filters or products existed but didn't match -- stores_resolved makes
    the two distinguishable without needing to re-run market_search with
    the same args to compare."""
    r = client.post(
        "/products/compare",
        json={"query": "arroz", "country": "ZZ"},
        headers=_AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["comparison"] == []
    assert data["stores_resolved"] == 0


def test_search_stores_resolved_zero_for_unknown_country():
    r = client.post(
        "/products/search",
        json={"query": "arroz", "country": "ZZ"},
        headers=_AUTH,
    )
    assert r.status_code == 200
    assert r.json()["stores_resolved"] == 0


def test_fuzzy_compare_ranks_full_token_match_over_cheaper_partial_match():
    """Regression: "aceite vegetal primor" OR-matched (require_all=False,
    the /products/compare default) any product containing just "aceite" +
    "vegetal", so a cheap tuna-in-oil can outranked the actual Primor oil
    bottle on price alone and buried it past the CLI's top-5 cutoff.
    Matching more query tokens should now win the tiebreak before price."""
    from routers.search import _fuzzy_compare, _query_tokens

    all_products = {
        "storeA": [
            {"name": "Filete de Atún CAMPOMAR en Aceite Vegetal Lata 150g", "brand": "CAMPOMAR", "price": 4.9},
            {"name": "Aceite Vegetal PRIMOR Botella 900ml", "brand": "PRIMOR", "price": 6.9},
        ],
    }
    q_tokens = _query_tokens("aceite vegetal primor")

    comparison = _fuzzy_compare(all_products, ["storeA"], q_tokens=q_tokens)

    assert comparison[0]["name"] == "Aceite Vegetal PRIMOR Botella 900ml"


def test_fuzzy_compare_without_q_tokens_still_sorts_by_price():
    """No regression for callers that don't pass q_tokens (e.g. future
    callers) -- falls back to pure price sort."""
    from routers.search import _fuzzy_compare

    all_products = {
        "storeA": [
            {"name": "Producto caro", "brand": "", "price": 9.9},
            {"name": "Producto barato", "brand": "", "price": 1.5},
        ],
    }

    comparison = _fuzzy_compare(all_products, ["storeA"])

    assert comparison[0]["name"] == "Producto barato"


def test_search_exposes_snapshot_identity_and_observation_when_available():
    import routers.search as search_mod
    from price_snapshots_schema import ensure_canonical_product_id_column
    from routers.search import SearchRequest, _search_products_db

    store = "telegram_identity_store"
    product_id = "telegram-identity-1"
    db = get_db()
    ensure_canonical_product_id_column(db)
    db.execute("DELETE FROM price_snapshots WHERE product_id = ?", (product_id,))
    db.execute(
        "INSERT INTO price_snapshots "
        "(product_id, store, store_name, name, brand, price, currency, line, queried_at, canonical_product_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            product_id, store, "Tienda de prueba", "Cafe Identidad 180 g", "Marca Prueba", 12.5,
            "PEN", "supermercados", "2026-08-01 10:00:00", "upid-cafe-180g",
        ),
    )
    db.commit()
    db.close()
    try:
        with patch.object(search_mod, "_resolve_search_stores", return_value=[store]):
            result = _search_products_db(SearchRequest(query="cafe identidad 180 g", require_all=True))
        row = result["results"][0]
        assert row["canonical_product_id"] == "upid-cafe-180g"
        assert _as_timestamp_str(row["queried_at"]) == "2026-08-01 10:00:00"
    finally:
        db = get_db()
        db.execute("DELETE FROM price_snapshots WHERE product_id = ?", (product_id,))
        db.commit()
        db.close()


def test_basket_identity_enrichment_adds_snapshot_evidence():
    import routers.search as search_mod
    from price_snapshots_schema import ensure_canonical_product_id_column

    store = "telegram_basket_identity_store"
    product_id = "telegram-basket-identity-1"
    db = get_db()
    ensure_canonical_product_id_column(db)
    db.execute("DELETE FROM price_snapshots WHERE product_id = ?", (product_id,))
    db.execute(
        "INSERT INTO price_snapshots "
        "(product_id, store, store_name, name, price, currency, line, queried_at, stock, canonical_product_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            product_id, store, "Tienda de prueba", "Leche Identidad 390 g", 4.2,
            "PEN", "supermercados", "2026-08-01 10:00:00", 8, "upid-leche-390g",
        ),
    )
    db.commit()
    try:
        result = {"stores": [{"store": store, "breakdown": [{"product_id": product_id}]}]}
        enriched = search_mod._enrich_basket_identity(result, db)
        row = enriched["stores"][0]["breakdown"][0]
        assert row["canonical_product_id"] == "upid-leche-390g"
        assert _as_timestamp_str(row["observed_at"]) == "2026-08-01 10:00:00"
        assert row["stock"] == 8
    finally:
        db.execute("DELETE FROM price_snapshots WHERE product_id = ?", (product_id,))
        db.commit()
        db.close()


def test_basket_identity_enrichment_supports_response_envelope():
    import routers.search as search_mod
    from price_snapshots_schema import ensure_canonical_product_id_column

    store = "telegram_basket_envelope_store"
    product_id = "telegram-basket-envelope-1"
    db = get_db()
    ensure_canonical_product_id_column(db)
    db.execute("DELETE FROM price_snapshots WHERE product_id = ?", (product_id,))
    db.execute(
        "INSERT INTO price_snapshots "
        "(product_id, store, store_name, name, price, currency, line, queried_at, canonical_product_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            product_id, store, "Tienda de prueba", "Arroz Identidad 5 kg", 20.0,
            "PEN", "supermercados", "2026-08-01 10:00:00", "upid-arroz-5kg",
        ),
    )
    db.commit()
    try:
        result = {"data": [{"store": store, "breakdown": [{"product_id": product_id}]}]}
        enriched = search_mod._enrich_basket_identity(result, db)
        assert enriched["data"][0]["breakdown"][0]["canonical_product_id"] == "upid-arroz-5kg"
    finally:
        db.execute("DELETE FROM price_snapshots WHERE product_id = ?", (product_id,))
        db.commit()
        db.close()


# ── Growth-tier priority tiebreak ────────────────────────────────────────────
# growth stores win exact price ties only — never outrank a genuinely
# cheaper competitor, so "cheapest first" stays honest regardless of who paid.

_GT_QUERY = "testgrowthproduct unique9x"
_GT_STORE_A = "test_gt_store_a"  # non-growth
_GT_STORE_B = "test_gt_store_b"  # growth


@pytest.fixture
def growth_tiebreak_snapshots():
    import routers.search as search_mod

    db = get_db()
    for sid in (_GT_STORE_A, _GT_STORE_B):
        db.execute("DELETE FROM store_credentials WHERE store_id = ?", (sid,))
        db.execute(
            "INSERT INTO store_credentials (store_id, platform, store_name, active) "
            "VALUES (?, 'woocommerce', ?, 1)",
            (sid, sid),
        )
    db.execute("DELETE FROM price_snapshots WHERE store IN (?, ?)", (_GT_STORE_A, _GT_STORE_B))
    for sid in (_GT_STORE_A, _GT_STORE_B):
        db.execute(
            "INSERT INTO price_snapshots (product_id, store, name, price, currency, queried_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (f"prod-{sid}", sid, "Testgrowthproduct Unique9x", 25.0, "PEN"),
        )
    db.execute(
        "UPDATE store_credentials SET is_growth = 1 WHERE store_id = ?", (_GT_STORE_B,)
    )
    db.commit()
    db.close()
    search_mod._growth_cache = (0.0, frozenset())  # bust the TTL cache
    yield
    db = get_db()
    db.execute("DELETE FROM price_snapshots WHERE store IN (?, ?)", (_GT_STORE_A, _GT_STORE_B))
    db.execute("DELETE FROM store_credentials WHERE store_id IN (?, ?)", (_GT_STORE_A, _GT_STORE_B))
    db.commit()
    db.close()
    search_mod._growth_cache = (0.0, frozenset())


def test_search_boosts_growth_store_on_exact_price_tie(growth_tiebreak_snapshots):
    import routers.search as search_mod
    from routers.search import SearchRequest, _search_products_db

    with patch.object(
        search_mod, "_resolve_search_stores", return_value=[_GT_STORE_A, _GT_STORE_B]
    ):
        body = SearchRequest(query=_GT_QUERY, require_all=True, limit=10)
        result = _search_products_db(body)

    stores_in_order = [r["store"] for r in result["results"]]
    assert stores_in_order[0] == _GT_STORE_B, (
        f"growth store {_GT_STORE_B} should win the exact price tie, got order {stores_in_order}"
    )


def test_compare_boosts_growth_store_on_exact_price_tie(growth_tiebreak_snapshots):
    import routers.search as search_mod
    from routers.search import SearchRequest, _compare_products_db

    with patch.object(
        search_mod, "_resolve_search_stores", return_value=[_GT_STORE_A, _GT_STORE_B]
    ):
        body = SearchRequest(query=_GT_QUERY, require_all=True, limit=10)
        result = _compare_products_db(body)

    assert result["comparison"], "expected at least one matched product"
    assert result["comparison"][0]["best_store"] == _GT_STORE_B


# ── GET /products/stock/{product_id} ─────────────────────────────────────────

def test_stock_requires_auth():
    r = client.get("/products/stock/prod-123?store=wong")
    assert r.status_code == 401


def test_stock_not_found_returns_no_data():
    r = client.get("/products/stock/no-such-product?store=wong", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["stock"] is None
    assert "message" in data


def test_stock_found_returns_stock_info():
    db = get_db()
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, stock, queried_at)
           VALUES ('test-prod-1', 'wong', 'Wong', 'Leche Gloria 1L', 3.5, 'PEN', 'supermercados', 'Supermercados', 12, datetime('now'))"""
    )
    db.commit()
    db.close()

    r = client.get("/products/stock/test-prod-1?store=wong", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["product_id"] == "test-prod-1"
    assert data["store"] == "wong"
    assert data["stock"] == 12
    assert data["name"] == "Leche Gloria 1L"


# ── GET /products/delivery/{product_id} ──────────────────────────────────────

def test_delivery_no_auth_required():
    r = client.get("/products/delivery/prod-123?store=wong")
    assert r.status_code == 200


def test_delivery_returns_expected_fields():
    r = client.get("/products/delivery/prod-abc?store=plaza_vea")
    assert r.status_code == 200
    data = r.json()
    assert data["product_id"] == "prod-abc"
    assert data["store"] == "plaza_vea"
    assert "delivery_available" in data
    assert "estimated_days" in data


def test_delivery_unknown_store_still_returns_200():
    r = client.get("/products/delivery/prod-xyz?store=unknown_store_xyz")
    assert r.status_code == 200
    data = r.json()
    assert data["store"] == "unknown_store_xyz"


# ── GET /products/barcode/{code} ──────────────────────────────────────────────

def test_barcode_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "product": {
            "product_name": "Leche Entera",
            "brands": "Gloria",
            "nutriscore_grade": "b",
            "categories": "Dairy",
        }
    }
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/barcode/7501234567890")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Leche Entera"
    assert data["brand"] == "Gloria"
    assert data["nutriscore"] == "B"
    assert data["code"] == "7501234567890"


def test_barcode_not_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/barcode/0000000000000")
    assert r.status_code == 200
    assert "error" in r.json()


# ── GET /products/enrich ──────────────────────────────────────────────────────

def test_enrich_returns_results():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "products": [
            {"product_name": "Arroz", "brands": "Costeño", "nutriscore_grade": "a", "code": "123"},
        ],
        "count": 1,
    }
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/enrich?query=arroz&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["results"][0]["name"] == "Arroz"


def test_enrich_upstream_failure_returns_empty():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("routers.search.httpx.get", return_value=mock_resp):
        r = client.get("/products/enrich?query=xyz")
    assert r.status_code == 200
    assert r.json()["results"] == []
    assert r.json()["total"] == 0


# ── GET /categories/{store} ───────────────────────────────────────────────────

def test_categories_unknown_store_returns_404():
    r = client.get("/categories/no_such_store_xyz")
    assert r.status_code == 404
