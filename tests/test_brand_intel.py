"""Tests for routers/brand_intel.py — brand monitor, promos, config, alerts."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db
from market_server import app

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


def _seed_snapshot(
    product_id: str,
    store: str,
    store_name: str,
    name: str,
    brand: str,
    price: float,
    list_price: float | None = None,
    discount: float | None = None,
    canonical_product_id: str | None = None,
    queried_at: str | None = None,
):
    db = get_db()
    if canonical_product_id is not None:
        try:
            db.execute("ALTER TABLE price_snapshots ADD COLUMN canonical_product_id TEXT")
            db.commit()
        except Exception:
            pass  # already added by a previous test in this session
    queried_at_sql = "?" if queried_at else "datetime('now')"
    extra_cols = ", canonical_product_id" if canonical_product_id is not None else ""
    extra_placeholders = ", ?" if canonical_product_id is not None else ""
    db.execute(
        f"""INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, brand, price, list_price, discount,
            currency, line, line_name, queried_at{extra_cols})
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PEN', 'supermercados', 'Supermercados', {queried_at_sql}{extra_placeholders})""",
        [product_id, store, store_name, name, brand, price, list_price, discount]
        + ([queried_at] if queried_at else [])
        + ([canonical_product_id] if canonical_product_id is not None else []),
    )
    db.commit()
    db.close()


# ── GET /v1/brand-monitor ─────────────────────────────────────────────────────

def test_brand_monitor_requires_auth():
    r = client.get("/v1/brand-monitor?brand=Gloria")
    assert r.status_code == 401


def test_brand_monitor_requires_brand_param():
    r = client.get("/v1/brand-monitor", headers=_AUTH)
    assert r.status_code == 422


def test_brand_monitor_unknown_country_returns_empty_structure():
    r = client.get("/v1/brand-monitor?brand=Gloria&country=ZZ", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["my_skus"] == []
    assert data["competitor_skus"] == []
    assert data["summary"] == {}


def test_brand_monitor_returns_my_skus_and_competitors_with_dispersion_score():
    _seed_snapshot("bi-leche-gloria", "wong", "Wong", "Leche Gloria 400ml", "Gloria", 3.50)
    _seed_snapshot("bi-leche-gloria", "metro", "Metro", "Leche Gloria 400ml", "Gloria", 3.80)
    _seed_snapshot("bi-leche-laive", "wong", "Wong", "Leche Laive 400ml", "Laive", 3.40)

    r = client.get(
        "/v1/brand-monitor?brand=Gloria&competitors=Laive&country=PE",
        headers=_AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    my_pids = {s["product_id"] for s in data["my_skus"]}
    comp_pids = {s["product_id"] for s in data["competitor_skus"]}
    assert "bi-leche-gloria" in my_pids
    assert "bi-leche-laive" in comp_pids

    gloria_rows = [s for s in data["my_skus"] if s["product_id"] == "bi-leche-gloria"]
    assert len(gloria_rows) == 2
    assert all(row["dispersion_score"] is not None for row in gloria_rows)
    assert data["summary"]["brand"] == "Gloria"
    assert data["summary"]["my_skus_count"] == 2


def test_brand_monitor_homologates_brand_casing_across_retailers():
    # Same competitor scraped with three different casings across stores —
    # regression test for the bug where "Laive"/"LAIVE"/"laive" counted as
    # three separate competitors instead of being merged into one.
    _seed_snapshot("bi-casing-mine", "wong", "Wong", "SKU Mine", "CasingBrand", 4.0)
    _seed_snapshot("bi-casing-comp-1", "wong", "Wong", "SKU Comp 1", "CompBrand", 3.0)
    _seed_snapshot("bi-casing-comp-2", "metro", "Metro", "SKU Comp 2", "COMPBRAND", 3.2)
    _seed_snapshot("bi-casing-comp-3", "plazavea", "Plaza Vea", "SKU Comp 3", "compbrand", 3.1)

    r = client.get(
        "/v1/brand-monitor?brand=CasingBrand&competitors=CompBrand&country=PE",
        headers=_AUTH,
    )
    assert r.status_code == 200
    data = r.json()

    comp_brand_names = {s["brand"] for s in data["competitor_skus"]}
    assert comp_brand_names == {"CompBrand"}
    assert data["summary"]["competitors_found"] == ["CompBrand"]


def test_brand_monitor_collapses_duplicate_retailer_skus_via_canonical_product_id():
    # Regression test: a retailer sometimes carries two catalog SKUs
    # (product_id) for what the Golden Record layer already knows is the same
    # product (e.g. an old + a re-listed SKU at a different price) — real
    # example: Metro had product_id "359806" and "42081" both named
    # "Mantequilla con Sal Gloria 180g". Both share canonical_product_id and
    # should collapse to one row, keeping the most recent snapshot.
    _seed_snapshot(
        "canon-old-sku", "wong", "Wong", "Mantequilla Canon Test", "CanonBrand",
        price=11.90, canonical_product_id="canon-golden-1",
        queried_at="2026-07-01 10:00:00",
    )
    _seed_snapshot(
        "canon-new-sku", "wong", "Wong", "Mantequilla Canon Test", "CanonBrand",
        price=10.50, canonical_product_id="canon-golden-1",
        queried_at="2026-07-05 10:00:00",
    )

    r = client.get("/v1/brand-monitor?brand=CanonBrand&country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()

    matching = [s for s in data["my_skus"] if s["name"] == "Mantequilla Canon Test"]
    assert len(matching) == 1
    assert matching[0]["product_id"] == "canon-new-sku"
    assert matching[0]["price"] == 10.50


# ── GET /v1/brand-monitor/promos ──────────────────────────────────────────────

def test_brand_promos_requires_auth():
    r = client.get("/v1/brand-monitor/promos?brand=Gloria")
    assert r.status_code == 401


def test_brand_promos_unknown_country_returns_empty():
    r = client.get("/v1/brand-monitor/promos?brand=Gloria&country=ZZ", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["promo_events"] == []
    assert data["count"] == 0


def test_brand_promos_returns_discount_depth():
    _seed_snapshot(
        "bi-promo-gloria", "wong", "Wong", "Leche Gloria Promo 400ml", "Gloria",
        price=3.00, list_price=4.00, discount=25.0,
    )

    r = client.get("/v1/brand-monitor/promos?brand=Gloria&country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    matching = [e for e in data["promo_events"] if e["product_id"] == "bi-promo-gloria"]
    assert len(matching) >= 1
    assert matching[0]["discount_depth_pct"] == 25.0


# ── POST /v1/brand-monitor/config ─────────────────────────────────────────────

def test_brand_config_requires_auth():
    r = client.post("/v1/brand-monitor/config", json={"brand_slug": "gloria"})
    assert r.status_code == 401


def test_brand_config_upsert_creates_then_updates():
    r1 = client.post(
        "/v1/brand-monitor/config",
        headers=_AUTH,
        json={
            "brand_slug": "gloria-test",
            "competitors": ["Laive"],
            "sku_pvps": {"bi-leche-gloria": 3.60},
        },
    )
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["status"] == "ok"
    assert body1["brand_slug"] == "gloria-test"
    assert body1["sku_pvps_registered"] == 1
    assert body1["competitors_registered"] == 1

    # Calling again with the same brand_slug updates in place (no duplicate row).
    r2 = client.post(
        "/v1/brand-monitor/config",
        headers=_AUTH,
        json={
            "brand_slug": "gloria-test",
            "competitors": ["Laive", "Nestlé"],
            "sku_pvps": {"bi-leche-gloria": 3.60, "bi-leche-gloria-2": 5.00},
        },
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["sku_pvps_registered"] == 2
    assert body2["competitors_registered"] == 2

    db = get_db()
    rows = db.execute(
        "SELECT COUNT(*) AS n FROM brand_intel_config WHERE brand_slug = 'gloria-test'"
    ).fetchall()
    db.close()
    assert dict(rows[0])["n"] == 1


# ── GET /v1/brand-monitor/alerts ──────────────────────────────────────────────

def test_brand_alerts_requires_auth():
    r = client.get("/v1/brand-monitor/alerts?brand=gloria-test")
    assert r.status_code == 401


def test_brand_alerts_no_config_returns_empty_with_message():
    r = client.get("/v1/brand-monitor/alerts?brand=never-registered-brand", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["alerts"] == []
    assert data["count"] == 0
    assert "message" in data


def test_brand_alerts_detects_above_and_below_pvp_deviation():
    client.post(
        "/v1/brand-monitor/config",
        headers=_AUTH,
        json={
            "brand_slug": "alertbrand",
            "sku_pvps": {
                "bi-alert-above": 10.0,   # alert if price > 10.50
                "bi-alert-below": 10.0,   # alert if price < 8.50
                "bi-alert-normal": 10.0,  # within band, no alert
            },
        },
    )

    _seed_snapshot("bi-alert-above", "wong", "Wong", "SKU Above", "AlertBrand", price=10.90)   # +9%
    _seed_snapshot("bi-alert-below", "wong", "Wong", "SKU Below", "AlertBrand", price=8.00)    # -20%
    _seed_snapshot("bi-alert-normal", "wong", "Wong", "SKU Normal", "AlertBrand", price=10.10)  # +1%

    r = client.get("/v1/brand-monitor/alerts?brand=alertbrand&country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()

    alerted_pids = {a["product_id"]: a["pvp_alert"] for a in data["alerts"]}
    assert alerted_pids.get("bi-alert-above") == "above_pvp"
    assert alerted_pids.get("bi-alert-below") == "far_below_pvp"
    assert "bi-alert-normal" not in alerted_pids

    # Sorted by absolute deviation descending: -20% comes before +9%.
    assert data["alerts"][0]["product_id"] == "bi-alert-below"
