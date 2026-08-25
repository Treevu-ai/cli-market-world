"""Tests for routers/intel.py — indicators, scores, inflation, alerts, enrichment, refresh."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, db_save_user, db_set_subscription
from market_server import app, hash_password

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    """All /v1/intel/* read endpoints require Pro (routers/intel.py). Default the
    admin token to Pro tier so existing tests keep exercising response shape;
    tier-gating itself is covered separately by test_intel_read_endpoint_requires_pro."""
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "pro")
    yield
    db_set_subscription("admin", "free")


@pytest.fixture()
def pro_user(monkeypatch):
    """Elevate the admin user to Pro tier for pro-gated endpoints."""
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "pro")
    yield
    db_set_subscription("admin", "free")


# ── Tier gating ──────────────────────────────────────────────────────────────

def test_intel_read_endpoint_requires_pro():
    """Intel tools are Pro-only (Starter gets shop tools; Pro adds intel + checkout)."""
    db_set_subscription("admin", "starter")
    try:
        r = client.get("/v1/intel/scores", headers=_AUTH)
        assert r.status_code == 403
        assert "Pro" in r.json()["detail"]
    finally:
        db_set_subscription("admin", "pro")


# ── GET /v1/intel/indicators ──────────────────────────────────────────────────

def test_indicators_requires_auth():
    r = client.get("/v1/intel/indicators")
    assert r.status_code == 401


def test_indicators_returns_catalog():
    r = client.get("/v1/intel/indicators", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "indicators" in data
    assert "total" in data
    assert isinstance(data["indicators"], list)
    assert data["total"] >= 0


# ── GET /v1/intel/indicators/{key} ───────────────────────────────────────────

def test_indicator_detail_requires_auth():
    r = client.get("/v1/intel/indicators/moat_freshness")
    assert r.status_code == 401


def test_indicator_detail_unknown_key_returns_404():
    r = client.get("/v1/intel/indicators/no_such_indicator_xyz", headers=_AUTH)
    assert r.status_code == 404


def test_indicator_detail_returns_structure():
    # Get a valid key from the catalog first
    catalog_r = client.get("/v1/intel/indicators", headers=_AUTH)
    catalog = catalog_r.json()["indicators"]
    if not catalog:
        pytest.skip("Empty catalog — no keys to test")
    key = catalog[0]["key"]
    r = client.get(f"/v1/intel/indicators/{key}", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "indicator" in data
    assert "latest_value" in data


# ── GET /v1/intel/scores ──────────────────────────────────────────────────────

def test_scores_requires_auth():
    r = client.get("/v1/intel/scores")
    assert r.status_code == 401


def test_scores_returns_200():
    r = client.get("/v1/intel/scores", headers=_AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), (dict, list))


# ── GET /v1/intel/inflation ────────────────────────────────────────────────────

def test_inflation_requires_auth():
    r = client.get("/v1/intel/inflation")
    assert r.status_code == 401


def test_inflation_returns_structure():
    r = client.get("/v1/intel/inflation", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "avg_inflation_pct" in data
    assert "avg_rpv_7d_pct" in data
    assert "days" in data
    assert data.get("metric") == "shelf_price_momentum_7d"


def test_inflation_unknown_country_returns_empty():
    r = client.get("/v1/intel/inflation?country=ZZ", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["avg_inflation_pct"] == 0


def test_inflation_excludes_price_outliers_and_out_of_stock():
    """Real example from live validation: a 1.79 ARS 'Leche' row next to
    normal ~1975 ARS milk prices dragged avg_now/delta_pct for the whole
    line. A single placeholder-scrape row shouldn't swing the aggregate."""
    from market_core import get_db

    store = "inflation_outlier_store"
    line = "inflation_outlier_line"
    db = get_db()
    db.execute("DELETE FROM price_snapshots WHERE store = ?", (store,))
    normal_rows = [
        ("infl-out-1", 1900.0, None),
        ("infl-out-2", 1950.0, None),
        ("infl-out-3", 2000.0, None),
        ("infl-out-4", 2050.0, 0),  # would be a normal price but out of stock
    ]
    for pid, price, stock in normal_rows:
        db.execute(
            "INSERT INTO price_snapshots "
            "(product_id, store, name, price, currency, line, stock, queried_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (pid, store, "Producto normal", price, "ARS", line, stock),
        )
    db.execute(
        "INSERT INTO price_snapshots "
        "(product_id, store, name, price, currency, line, stock, queried_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        ("infl-out-placeholder", store, "Producto con precio roto", 1.79, "ARS", line, None),
    )
    db.commit()
    db.close()
    try:
        r = client.get(f"/v1/intel/inflation?line={line}", headers=_AUTH)
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) == 1
        item = data["items"][0]
        # The three normal, in-stock rows (1900, 1950, 2000) should survive —
        # the out-of-stock row (2050, stock=0) and the 1.79 placeholder
        # (>5x below the median) are both excluded from the average.
        assert item["avg_now"] == pytest.approx((1900.0 + 1950.0 + 2000.0) / 3, abs=0.01)
    finally:
        db = get_db()
        db.execute("DELETE FROM price_snapshots WHERE store = ?", (store,))
        db.commit()
        db.close()


# ── GET /v1/intel/alerts ──────────────────────────────────────────────────────

def test_alerts_requires_auth():
    r = client.get("/v1/intel/alerts?product=leche")
    assert r.status_code == 401


def test_alerts_missing_product_returns_422():
    r = client.get("/v1/intel/alerts", headers=_AUTH)
    assert r.status_code == 422


def test_alerts_returns_structure():
    r = client.get("/v1/intel/alerts?product=leche", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "product" in data
    assert "results" in data
    assert data["product"] == "leche"


def test_alerts_with_store_filter():
    r = client.get("/v1/intel/alerts?product=arroz&store=wong", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["store"] == "wong"


# ── GET /v1/intel/brief ────────────────────────────────────────────────────────

def test_brief_requires_auth():
    r = client.get("/v1/intel/brief")
    assert r.status_code == 401


def test_brief_returns_200():
    r = client.get("/v1/intel/brief", headers=_AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


def test_brief_with_params():
    r = client.get("/v1/intel/brief?country=PE&line=supermercados&days=7", headers=_AUTH)
    assert r.status_code == 200


# ── GET /v1/intel/enrichment ──────────────────────────────────────────────────

def test_enrichment_requires_auth():
    r = client.get("/v1/intel/enrichment")
    assert r.status_code == 401


def test_enrichment_returns_structure():
    r = client.get("/v1/intel/enrichment", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "indicators" in data
    assert "total" in data
    assert "sources" in data


# ── GET /v1/intel/enrichment/subcategories ────────────────────────────────────

def test_enrichment_subcategories_requires_auth():
    r = client.get("/v1/intel/enrichment/subcategories")
    assert r.status_code == 401


def test_enrichment_subcategories_returns_structure():
    r = client.get("/v1/intel/enrichment/subcategories", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "subcategories" in data
    assert "total" in data
    assert "country" in data


# ── POST /v1/intel/refresh ────────────────────────────────────────────────────

def test_refresh_requires_pro(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "free")
    r = client.post("/v1/intel/refresh", headers=_AUTH)
    assert r.status_code == 403


def test_refresh_with_pro_returns_ok(pro_user):
    r = client.post("/v1/intel/refresh", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "internal_written" in data


def test_refresh_with_country_scope(pro_user):
    r = client.post("/v1/intel/refresh?country=PE", headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["country"] == "PE"


# ── POST /v1/intel/enrichment/refresh ────────────────────────────────────────

def test_enrichment_refresh_requires_pro(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)
    db_save_user("admin", hash_password("market"), _ADMIN_TOKEN)
    db_set_subscription("admin", "free")
    r = client.post("/v1/intel/enrichment/refresh", headers=_AUTH)
    assert r.status_code == 403


def test_enrichment_refresh_with_pro_returns_ok(pro_user):
    r = client.post("/v1/intel/enrichment/refresh?country=PE", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "enrichment_written" in data


# ── GET /v1/intel/macro ───────────────────────────────────────────────────────

def test_macro_requires_auth():
    r = client.get("/v1/intel/macro")
    assert r.status_code == 401


def test_macro_returns_bcrp_snapshot(monkeypatch):
    fake_snapshot = {
        "tipo_cambio": {
            "venta": {"price": 3.412, "observation_date": "2026-07-08"},
            "compra": {"price": 3.405, "observation_date": "2026-07-08"},
        },
        "ipc_lima": {"price": 120.292167, "observation_date": "2026-06-01"},
        "source": "bcrp_pe",
    }
    monkeypatch.setattr("routers.intel.gov_macro_snapshot", lambda: fake_snapshot)
    r = client.get("/v1/intel/macro", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["source"] == "bcrp_pe"
    assert data["tipo_cambio"]["venta"]["price"] == 3.412
    assert data["ipc_lima"]["price"] == 120.292167


def test_macro_degrades_gracefully_when_no_data_yet(monkeypatch):
    monkeypatch.setattr(
        "routers.intel.gov_macro_snapshot",
        lambda: {"tipo_cambio": None, "ipc_lima": None, "source": "bcrp_pe"},
    )
    r = client.get("/v1/intel/macro", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["tipo_cambio"] is None
    assert data["ipc_lima"] is None


# ── POST /v1/intel/macro/refresh ─────────────────────────────────────────────

def test_macro_refresh_requires_auth():
    r = client.post("/v1/intel/macro/refresh")
    assert r.status_code == 401


def test_macro_refresh_calls_gov_collect_bcrp(monkeypatch):
    async def fake_collect():
        return {"collected": 3, "resolved": 3, "registry_size": 3}

    monkeypatch.setattr("routers.intel.gov_collect_bcrp", fake_collect)
    r = client.post("/v1/intel/macro/refresh", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["collected"] == 3
    assert data["resolved"] == 3


# ── GET /v1/intel/gov-observations ───────────────────────────────────────────

def test_gov_observations_requires_auth():
    r = client.get("/v1/intel/gov-observations")
    assert r.status_code == 401


def test_gov_observations_filters_by_commodity_slug(monkeypatch):
    captured = {}

    def fake_list(commodity_slug="", region="", limit=30):
        captured["args"] = (commodity_slug, region, limit)
        return [{"commodity_slug": commodity_slug, "price": 3.41}]

    monkeypatch.setattr("routers.intel.gov_list_observations", fake_list)
    r = client.get(
        "/v1/intel/gov-observations?commodity_slug=tipo_cambio_usd_pen&limit=5",
        headers=_AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["commodity_slug"] == "tipo_cambio_usd_pen"
    assert data["observations"] == [{"commodity_slug": "tipo_cambio_usd_pen", "price": 3.41}]
    assert captured["args"] == ("tipo_cambio_usd_pen", "", 5)


def test_gov_observations_degrades_gracefully_when_empty(monkeypatch):
    monkeypatch.setattr("routers.intel.gov_list_observations", lambda **kw: [])
    r = client.get("/v1/intel/gov-observations?commodity_slug=ipc_lima", headers=_AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["observations"] == []


# ── POST /v1/intel/gondola-advise ─────────────────────────────────────────────

_GONDOLA_BODY = {
    "country": "PE",
    "category": "leche",
    "line": "supermercados",
    "portfolio": [{"query": "leche gloria 1l", "pvp": 4.0}],
    "competitors": ["Laive"],
}


def test_gondola_advise_requires_auth():
    r = client.post("/v1/intel/gondola-advise", json=_GONDOLA_BODY)
    assert r.status_code == 401


def test_gondola_advise_requires_pro():
    db_set_subscription("admin", "starter")
    try:
        r = client.post("/v1/intel/gondola-advise", json=_GONDOLA_BODY, headers=_AUTH)
        assert r.status_code == 403
        assert "Pro" in r.json()["detail"]
    finally:
        db_set_subscription("admin", "pro")


def test_gondola_advise_requires_country_and_category():
    r = client.post(
        "/v1/intel/gondola-advise",
        json={"portfolio": [{"query": "leche"}]},
        headers=_AUTH,
    )
    assert r.status_code == 422
    assert "country" in r.json()["detail"]


def test_gondola_advise_returns_digital_shelf_payload(monkeypatch):
    from datetime import datetime, timedelta, timezone

    from market_core import get_db

    catalog = {
        "wong": {"name": "Wong", "country": "PE", "line": "supermercados"},
        "metro": {"name": "Metro", "country": "PE", "line": "supermercados"},
        "plaza_vea": {"name": "Plaza Vea", "country": "PE", "line": "supermercados"},
        "exito": {"name": "Éxito", "country": "CO", "line": "supermercados"},
    }
    monkeypatch.setattr("market_core.store_credentials.get_all_stores", lambda: catalog)
    now = datetime.now(timezone.utc)
    db = get_db()
    try:
        db.execute("DELETE FROM price_snapshots WHERE store IN ('wong','metro','plaza_vea','exito')")
        rows = [
            ("g1", "wong", "Leche Gloria Entera 1L", "Gloria", 5.5, None, 0, now.isoformat()),
            ("g2", "metro", "Arroz Costeno 1kg", "Costeno", 5.0, None, 0, now.isoformat()),
            ("g3", "plaza_vea", "Azucar Rubia 1kg", "Cartier", 4.0, None, 0,
             (now - timedelta(hours=72)).isoformat()),
            ("g4", "wong", "Leche Laive Entera 1L", "Laive", 4.0, 5.0, 20, now.isoformat()),
            ("g5", "wong", "Leche Ideal Evaporada 400g", "Ideal", 3.8, None, 0, now.isoformat()),
        ]
        for pid, store, name, brand, price, list_price, discount, ts in rows:
            db.execute(
                """INSERT INTO price_snapshots
                   (product_id, store, store_name, name, brand, price, list_price, discount,
                    line, currency, queried_at, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'supermercados', 'PEN', ?, 'ok')""",
                (pid, store, store.title(), name, brand, price, list_price, discount, ts),
            )
        db.commit()
    finally:
        db.close()

    r = client.post("/v1/intel/gondola-advise", json=_GONDOLA_BODY, headers=_AUTH)
    assert r.status_code == 200, r.text
    body = r.json()
    data = body.get("data", body)
    assert data["schema_version"] == "gondola-advise.v0"
    assert data["scope"] == "digital_shelf_formal"
    assert "planogram" in data["not_included"]
    assert data["run_id"]
    cells = {(c["sku"], c["store"]): c["status"] for c in data["coverage"]["cells"]}
    assert cells[("leche gloria 1l", "wong")] == "listed"
    assert cells[("leche gloria 1l", "metro")] == "missing"
    assert cells[("leche gloria 1l", "plaza_vea")] == "stale"
    assert "exito" not in {c["store"] for c in data["coverage"]["cells"]}
    types = {a["type"] for a in data["actions"]}
    assert "LIST" in types
    assert "PRICE" in types
    assert "PROMO" in types
    rationale_blob = " ".join(str(a.get("rationale") or "") for a in data["actions"]).lower()
    for term in ("facing", "planogram", "planograma", "share of shelf", "espacio lineal"):
        assert term not in rationale_blob
