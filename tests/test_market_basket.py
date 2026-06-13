"""Tests for market_core.market_basket — canasta snapshot and aggregation."""

from __future__ import annotations

import pytest
from market_core.market_basket import (
    CANASTA_PARTIAL_THRESHOLD,
    CANASTA_TOTAL_ITEMS,
    _canasta_name_sql,
    build_canasta_basica,
    build_canasta_snapshot,
)
from market_core.market_spread import CANASTA_SQL_LIKE, matches_canasta_item


# ── SQL pattern helpers ───────────────────────────────────────────────────────

def test_single_pattern_no_or():
    sql, params = _canasta_name_sql("leche")
    assert "OR" not in sql
    assert "LOWER(name) LIKE LOWER(?)" in sql
    assert len(params) == 1


def test_multi_pattern_has_or():
    sql, params = _canasta_name_sql("azucar")
    assert "OR" in sql
    assert "%azúcar%" in params


def test_huevos_includes_singular():
    _, params = _canasta_name_sql("huevos")
    assert any("huevo" in p for p in params)


def test_accent_variants_present():
    assert "%azúcar%" in CANASTA_SQL_LIKE["azucar"]
    assert "%café%" in CANASTA_SQL_LIKE["cafe"]
    assert "%jabón%" in CANASTA_SQL_LIKE["jabon"]


def test_matches_canasta_item_huevo_singular():
    row = {"line": "supermercados", "name": "Huevo Blanco 18 Piezas"}
    assert matches_canasta_item(row, "huevos")


def test_matches_canasta_item_wrong_line_is_false():
    row = {"line": "farmacia", "name": "Leche Entera 1L"}
    assert not matches_canasta_item(row, "leche")


# ── Fixtures (helpers) ───────────────────────────────────────────────────────

def _insert_snapshot(db, *, product_id, store, store_name, name, price, currency="PEN", line="supermercados", queried_at="2026-06-13 08:00:00"):
    db.execute(
        """INSERT OR IGNORE INTO price_snapshots
           (product_id, store, store_name, name, price, currency, line, line_name, queried_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Supermercados', ?)""",
        (product_id, store, store_name, name, price, currency, line, queried_at),
    )


# ── build_canasta_basica ──────────────────────────────────────────────────────

def test_build_canasta_basica_empty_db(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    result = build_canasta_basica(db)
    db.close()
    assert result == []


def test_build_canasta_basica_below_min_items_excluded(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    # Insert only 2 canasta items (< default min_items=3)
    _insert_snapshot(db, product_id="l1", store="wong", store_name="Wong", name="Leche Gloria 1L", price=3.5)
    _insert_snapshot(db, product_id="a1", store="wong", store_name="Wong", name="Arroz Costeño 1kg", price=4.0)
    db.commit()
    result = build_canasta_basica(db, min_items=3)
    db.close()
    assert result == []


def test_build_canasta_basica_returns_sorted_by_total(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    # Store A: 3 items, higher total
    _insert_snapshot(db, product_id="l1", store="plaza_vea", store_name="Plaza Vea", name="Leche Gloria 1L", price=10.0)
    _insert_snapshot(db, product_id="a1", store="plaza_vea", store_name="Plaza Vea", name="Arroz Costeño 1kg", price=10.0)
    _insert_snapshot(db, product_id="ac1", store="plaza_vea", store_name="Plaza Vea", name="Aceite Vegetal 1L", price=10.0)
    # Store B: 3 items, lower total
    _insert_snapshot(db, product_id="l2", store="wong", store_name="Wong", name="Leche Gloria 1L", price=3.0)
    _insert_snapshot(db, product_id="a2", store="wong", store_name="Wong", name="Arroz Costeño 1kg", price=3.0)
    _insert_snapshot(db, product_id="ac2", store="wong", store_name="Wong", name="Aceite Vegetal 1L", price=3.0)
    db.commit()
    result = build_canasta_basica(db, min_items=3)
    db.close()
    assert len(result) == 2
    # sorted ascending by total — Wong (9.0) before Plaza Vea (30.0)
    assert result[0]["store_name"] == "Wong"
    assert result[1]["store_name"] == "Plaza Vea"


def test_build_canasta_basica_at_most_ten_stores(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    for i in range(12):
        for _j, (name, prod_prefix) in enumerate([
            ("Leche Gloria 1L", "l"),
            ("Arroz Costeño 1kg", "a"),
            ("Aceite Vegetal 1L", "ac"),
        ]):
            _insert_snapshot(
                db,
                product_id=f"{prod_prefix}{i}",
                store=f"store_{i}",
                store_name=f"Store {i}",
                name=name,
                price=float(i + 1),
            )
    db.commit()
    result = build_canasta_basica(db, min_items=3)
    db.close()
    assert len(result) <= 10


# ── build_canasta_snapshot ────────────────────────────────────────────────────

def test_build_canasta_snapshot_structure_keys(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    snap = build_canasta_snapshot(db)
    db.close()
    assert "source" in snap
    assert "snapshot_at" in snap
    assert "items_total" in snap
    assert "partial_threshold" in snap
    assert "stores" in snap


def test_build_canasta_snapshot_constants(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    snap = build_canasta_snapshot(db)
    db.close()
    assert snap["items_total"] == CANASTA_TOTAL_ITEMS
    assert snap["partial_threshold"] == CANASTA_PARTIAL_THRESHOLD
    assert snap["source"] == "snapshot"


def test_build_canasta_snapshot_empty_db_no_stores(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    snap = build_canasta_snapshot(db)
    db.close()
    assert snap["stores"] == []
    assert snap["snapshot_at"] is None


def test_build_canasta_snapshot_completeness_pct(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    # 3 canasta items → completeness_pct = 30
    _insert_snapshot(db, product_id="l1", store="metro", store_name="Metro", name="Leche Gloria 1L", price=3.5)
    _insert_snapshot(db, product_id="a1", store="metro", store_name="Metro", name="Arroz Costeño 1kg", price=4.0)
    _insert_snapshot(db, product_id="ac1", store="metro", store_name="Metro", name="Aceite Vegetal 1L", price=7.0)
    db.commit()
    snap = build_canasta_snapshot(db, min_items=1)
    db.close()
    store = snap["stores"][0]
    assert store["completeness_pct"] == store["items_found"] * 10


def test_build_canasta_snapshot_comparable_flag(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    # Insert CANASTA_PARTIAL_THRESHOLD items for one store and fewer for another
    items = [
        ("Leche Gloria 1L", "l"), ("Arroz Costeño 1kg", "a"), ("Aceite Vegetal 1L", "ac"),
        ("Azúcar Rubia 1kg", "az"), ("Huevo Blanco 18 Piezas", "h"), ("Pan Integral", "p"),
    ]
    for _pid, (name, prefix) in enumerate(items):
        _insert_snapshot(db, product_id=f"{prefix}1", store="full_store", store_name="Full Store", name=name, price=5.0)
    # partial store: only 2 items
    _insert_snapshot(db, product_id="l2", store="partial_store", store_name="Partial Store", name="Leche Gloria 1L", price=3.5)
    _insert_snapshot(db, product_id="a2", store="partial_store", store_name="Partial Store", name="Arroz Costeño 1kg", price=4.0)
    db.commit()
    snap = build_canasta_snapshot(db, min_items=1)
    db.close()
    by_name = {s["store_name"]: s for s in snap["stores"]}
    assert by_name["Full Store"]["comparable"] is True
    assert by_name["Partial Store"]["comparable"] is False


def test_build_canasta_snapshot_store_filter(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    _insert_snapshot(db, product_id="l1", store="wong", store_name="Wong", name="Leche Gloria 1L", price=3.5)
    _insert_snapshot(db, product_id="a1", store="wong", store_name="Wong", name="Arroz Costeño 1kg", price=4.0)
    _insert_snapshot(db, product_id="l2", store="metro", store_name="Metro", name="Leche Gloria 1L", price=3.5)
    _insert_snapshot(db, product_id="a2", store="metro", store_name="Metro", name="Arroz Costeño 1kg", price=4.0)
    db.commit()
    snap = build_canasta_snapshot(db, min_items=1, store_filter={"wong"})
    db.close()
    store_names = [s["store_name"] for s in snap["stores"]]
    assert "Wong" in store_names
    assert "Metro" not in store_names


def test_build_canasta_snapshot_at_reflects_latest(isolated_db):
    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    _insert_snapshot(db, product_id="l1", store="metro", store_name="Metro", name="Leche Gloria 1L", price=3.5, queried_at="2026-06-10 08:00:00")
    _insert_snapshot(db, product_id="a1", store="metro", store_name="Metro", name="Arroz Costeño 1kg", price=4.0, queried_at="2026-06-13 08:00:00")
    db.commit()
    snap = build_canasta_snapshot(db, min_items=1)
    db.close()
    assert snap["snapshot_at"] == "2026-06-13 08:00:00"
