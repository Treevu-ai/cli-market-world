"""Tests for GET /v1/quality/flagged."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dashboard_quality import count_flagged_discounts
from quality_flagged import build_flagged_quality, fetch_flagged_discounts


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


def _insert_snapshot(db, *, product_id: str, store: str, price: float, list_price: float | None = None):
    db.execute(
        """
        INSERT INTO price_snapshots (
            product_id, name, store, store_name, price, list_price,
            currency, line, line_name, queried_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'PEN', 'supermercados', 'Supermercados', datetime('now'))
        """,
        (product_id, f"Product {product_id}", store, store.title(), price, list_price),
    )


def test_flagged_discount_excludes_sane_discount(isolated_db):
    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()

    _insert_snapshot(db, product_id="bad99", store=store, price=1.0, list_price=100.0)
    _insert_snapshot(db, product_id="ok50", store=store, price=50.0, list_price=100.0)
    db.commit()

    payload = build_flagged_quality(db, reason="discount", limit=50, offset=0)
    db.close()

    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["discount_pct"] >= 90
    assert payload["items"][0]["reason"] == "discount>=90%"
    names = {i["name"] for i in payload["items"]}
    assert "Product bad99" in names
    assert "Product ok50" not in names


def test_flagged_limit_one_returns_full_total(isolated_db):
    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()

    for i in range(3):
        _insert_snapshot(db, product_id=f"sus{i}", store=store, price=1.0, list_price=100.0)
    db.commit()

    payload = build_flagged_quality(db, reason="discount", limit=1, offset=0)
    db.close()

    assert payload["total"] == 3
    assert len(payload["items"]) == 1


def test_flagged_endpoint_coherent_with_dashboard(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()
    _insert_snapshot(db, product_id="dash1", store=store, price=2.0, list_price=200.0)
    _insert_snapshot(db, product_id="dash2", store=store, price=3.0, list_price=300.0)
    db.commit()
    db.close()

    with TestClient(app) as client:
        flagged = client.get("/v1/quality/flagged?reason=discount").json()
        dash = client.get("/dashboard/data").json()

    assert flagged["total"] >= len(dash.get("suspect_discounts") or [])
    assert flagged["total"] == count_flagged_discounts(market_core.get_db())
    market_core.get_db().close()


def test_flagged_pagination_stable(isolated_db):
    market_core = isolated_db
    market_core.ensure_db_initialized()
    store = market_core.DEFAULT_STORES[0]
    db = market_core.get_db()

    for i in range(5):
        _insert_snapshot(db, product_id=f"p{i}", store=store, price=1.0, list_price=100 + i)
    db.commit()

    page0 = fetch_flagged_discounts(db, offset=0, limit=2)
    page1 = fetch_flagged_discounts(db, offset=2, limit=2)
    all_items = fetch_flagged_discounts(db, offset=0, limit=10)
    db.close()

    assert page0[0]["discount_pct"] >= page0[1]["discount_pct"]
    ids_merged = [i["name"] for i in page0 + page1]
    ids_all = [i["name"] for i in all_items[:4]]
    assert ids_merged == ids_all


def test_flagged_filters_applied(isolated_db):
    from fastapi.testclient import TestClient
    from market_server import app

    with TestClient(app) as client:
        r = client.get("/v1/quality/flagged?limit=5")
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 5
    assert "discount>=90%" in body["filters_applied"]
    assert "spread>10x" in body["filters_applied"]
