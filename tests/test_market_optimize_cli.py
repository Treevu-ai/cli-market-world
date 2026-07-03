"""Tests for market optimize command helpers and core v1 route mount."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from market_cli import (
    _parse_basket_items,
    _unwrap_v1,
    _normalize_basket_store_rows,
    _country_supermarket_stores,
    _format_basket_item_label,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_unwrap_v1_envelope():
    payload = {"data": {"status": "ok", "mission": "optimize_purchase"}, "meta": {}, "trace": {}}
    assert _unwrap_v1(payload)["status"] == "ok"
    assert _unwrap_v1({"status": "ok"})["status"] == "ok"


def test_parse_basket_items():
    items = _parse_basket_items(["leche:2", "arroz", "aceite:3"])
    assert items == [
        {"name": "leche", "qty": 2},
        {"name": "arroz", "qty": 1},
        {"name": "aceite", "qty": 3},
    ]


def test_normalize_basket_store_rows_legacy_comparison():
    data = {
        "source": "live",
        "comparison": {
            "metro": {
                "store_name": "Metro",
                "currency": "PEN",
                "total": 5.8,
                "items": [{"name": "Leche Gloria", "brand": "Gloria", "qty": 1, "price": 2.9}],
            }
        },
    }
    rows = _normalize_basket_store_rows(data)
    assert len(rows) == 1
    assert rows[0]["store_name"] == "Metro"
    assert rows[0]["total"] == 5.8
    assert rows[0]["breakdown"][0]["brand"] == "Gloria"


def test_normalize_basket_store_rows_legacy_comparison_brand_missing():
    data = {
        "comparison": {
            "wong": {
                "store_name": "Wong",
                "currency": "PEN",
                "total": 3.0,
                "items": [{"name": "Leche Evaporada", "qty": 1, "price": 3.0}],
            }
        },
    }
    rows = _normalize_basket_store_rows(data)
    assert rows[0]["breakdown"][0]["brand"] is None


def test_format_basket_item_label_with_brand():
    label = _format_basket_item_label({"item": "leche", "resolved_name": "Leche Entera 1L", "brand": "Gloria", "qty": 2})
    assert label == "2x Gloria — Leche Entera 1L"


def test_format_basket_item_label_placeholder_brand_omitted():
    label = _format_basket_item_label({"item": "Papel Higiénico Jumbo", "brand": "—", "qty": 1})
    assert label == "1x Papel Higiénico Jumbo"
    assert "—" not in label.replace("Papel Higiénico Jumbo", "")


def test_format_basket_item_label_brand_already_in_name_not_duplicated():
    label = _format_basket_item_label({"item": "Leche Gloria 1L", "brand": "Gloria", "qty": 1})
    assert label == "1x Leche Gloria 1L"


def test_format_basket_item_label_uses_resolved_name_over_raw_query():
    label = _format_basket_item_label({"item": "papel higienico", "resolved_name": "Papel Higiénico Elite", "brand": None, "qty": 3})
    assert label == "3x Papel Higiénico Elite"


def test_format_basket_item_label_missing_name_falls_back_to_placeholder():
    label = _format_basket_item_label({"qty": 1})
    assert label == "1x ?"


def test_country_supermarket_stores_pe():
    stores = _country_supermarket_stores("PE")
    assert "wong" in stores
    assert "metro" in stores
    assert "ripley_pe" not in stores


def test_market_server_mounts_core_v1_router():
    text = (REPO_ROOT / "market_server.py").read_text(encoding="utf-8")
    assert "from market_core.api_routes import router as core_v1_router" in text
    assert "core_api_routes._auth_fn = require_api_key" in text
    assert 'app.include_router(core_v1_router, prefix="/v1")' in text


def _load_server_app():
    try:
        from market_core import ensure_db_initialized
        from market_server import app

        ensure_db_initialized()
        return app
    except ModuleNotFoundError as exc:
        pytest.skip(f"world server runtime deps missing: {exc}")


def test_optimize_purchase_route_mounted():
    client = TestClient(_load_server_app())
    response = client.post(
        "/v1/missions/optimize-purchase",
        json={"items": [{"name": "leche", "qty": 1}], "country": "PE"},
    )
    assert response.status_code != 404
    assert response.status_code in (401, 200, 402)


def test_affordability_route_mounted():
    client = TestClient(_load_server_app())
    response = client.get("/v1/intel/affordability", params={"country": "PE"})
    assert response.status_code != 404
    assert response.status_code in (401, 200)
