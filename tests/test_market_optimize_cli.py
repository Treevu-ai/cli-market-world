"""Tests for market optimize command helpers."""

from __future__ import annotations

from market_cli import _parse_basket_items, _unwrap_v1


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
