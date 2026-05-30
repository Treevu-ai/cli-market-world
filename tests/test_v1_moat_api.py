"""Tests for Phase 3 endpoints 3.3–3.6."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    import market_core

    data_dir = tmp_path / "market_data"
    data_dir.mkdir()
    db_file = data_dir / "market.db"
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setattr(market_core, "DATA_DIR", data_dir)
    monkeypatch.setattr(market_core, "DB_FILE", db_file)
    monkeypatch.setattr(market_core, "USE_PG", False)
    monkeypatch.setattr(market_core, "_db_initialized", False)
    return market_core


def _snap(db, *, product_id: str, store: str, name: str, price: float = 10.0, list_price=None, line="supermercados"):
    db.execute(
        """
        INSERT INTO price_snapshots (
            product_id, name, store, store_name, price, list_price,
            currency, line, line_name, queried_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'PEN', ?, 'Supermercados', datetime('now'))
        """,
        (product_id, name, store, store.title(), price, list_price, line),
    )


def test_v1_basket_snapshot_source_and_min_items(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app
    from market_spread import CANASTA_ITEMS

    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()

    for i, prod in enumerate(CANASTA_ITEMS[:3]):
        _snap(db, product_id=f"c{i}", store=store, name=f"Leche {prod} 1L" if prod == "leche" else f"{prod} producto 1kg")
    _snap(db, product_id="only2a", store=store, name="leche entera 1L")
    _snap(db, product_id="only2b", store=store, name="arroz premium 1kg")
    db.commit()
    db.close()

    with TestClient(app) as client:
        r = client.get("/v1/basket?min_items=3")
        dash = client.get("/dashboard/data").json()

    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "snapshot"
    assert body["partial_threshold"] == 6
    assert len(body["stores"]) >= 1
    assert body["stores"][0]["items_found"] >= 3

    view_stores = dash["dashboard_view"]["blocks"]["canasta"]["stores"]
    if view_stores:
        api_store = body["stores"][0]
        view_match = next(s for s in view_stores if s["store_name"] == api_store["store_name"])
        assert view_match["items_found"] == api_store["items_found"]


def test_v1_prices_clean_excludes_high_discount(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()
    _snap(db, product_id="bad", store=store, name="item bad", price=1.0, list_price=100.0)
    _snap(db, product_id="good", store=store, name="item good", price=50.0, list_price=100.0)
    db.commit()
    db.close()

    with TestClient(app) as client:
        r = client.get("/v1/prices?clean=1&store=" + store)
    assert r.status_code == 200
    body = r.json()
    assert body["clean"] is True
    names = {i["name"] for i in body["items"]}
    assert "item good" in names
    assert "item bad" not in names


def test_v1_dispersion_clean_excludes_crit(isolated_db):
    from quality_dispersion import build_dispersion

    market_core = isolated_db
    market_core.ensure_db_initialized()
    db = market_core.get_db()
    store = market_core.DEFAULT_STORES[0]
    for i, price in enumerate([10, 12, 14, 16, 18, 200]):
        _snap(db, product_id=f"d{i}", store=store, name=f"aceite común {i} 1L", price=float(price))
    db.commit()

    clean = build_dispersion(db, clean=True)
    raw = build_dispersion(db, clean=False)
    db.close()

    assert all(i.get("status") != "crit" for i in clean["items"])
    assert len(raw["items"]) >= len(clean["items"])


def test_v1_coverage_matrix_gaps(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()
    _snap(db, product_id="m1", store=store, name="x", line="supermercados")
    db.commit()
    db.close()

    with TestClient(app) as client:
        api = client.get("/v1/coverage/matrix").json()
        dash = client.get("/dashboard/data").json()

    assert api["cells"]
    assert api["cells"] == dash["line_country_matrix"]


def test_portada_acceso_v12(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    with TestClient(app) as client:
        dash = client.get("/dashboard/data").json()

    view = dash["dashboard_view"]
    assert view["spec_version"] == "1.2"
    acceso = view["blocks"]["portada"]["acceso"]
    assert len(acceso) >= 6
    assert all("source_field" in a for a in acceso)
    cmds = " ".join(a["cmd"] for a in acceso)
    assert "/v1/sources/health" in cmds
    assert "/v1/basket" in cmds
