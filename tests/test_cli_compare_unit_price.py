"""Regression test for `market compare`'s per-unit price display (T3,
cli-market-backend#127 search/compare/enrich findings): the CLI never
rendered prices_per_unit even after the backend started computing it."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


def test_cmd_compare_renders_per_unit_price_in_cell(monkeypatch):
    captured_rows: list[list[str]] = []

    class _FakeTable:
        def __init__(self, *a, **k):
            pass

        def add_column(self, *a, **k):
            pass

        def add_row(self, *row):
            captured_rows.append(list(row))

    monkeypatch.setattr(market_cli, "Table", _FakeTable)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)

    comparison = [
        {
            "name": "Leche entera La Serenísima",
            "brand": "La Serenisima",
            "prices": {"carrefour_ar": 500.0, "vea_ar": 480.0},
            "prices_per_unit": {
                "carrefour_ar": {"basis": "L", "pack_qty": 0.2, "price_per": 2500.0},
                "vea_ar": {"basis": "L", "pack_qty": 0.2, "price_per": 2400.0},
            },
            "best_store": "vea_ar",
            "best_price": 480.0,
        }
    ]
    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda *a, **k: {"comparison": comparison, "query": "leche entera"},
    )
    monkeypatch.setattr(market_cli, "STORES", {
        "carrefour_ar": {"name": "Carrefour", "currency": "ARS"},
        "vea_ar": {"name": "Vea", "currency": "ARS"},
    })

    market_cli.cmd_compare(argparse.Namespace(
        query="leche entera", store=None, line=None, country="AR", limit=10, json=False,
    ))

    # Product row is the last one added (after header setup calls, if any).
    product_row = captured_rows[-1]
    joined = " ".join(product_row)
    assert "/L" in joined, f"expected a per-unit price suffix in the row, got: {product_row}"
