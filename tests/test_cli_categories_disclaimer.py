"""Regression test for cli-market-backend#127/#135 (O4/O5): /categories/{store}
changed shape from a bare list to {"store", "categories", "disclaimer"} —
cmd_categories must handle both without breaking."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


def test_cmd_categories_handles_new_dict_shape(monkeypatch):
    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda *a, **k: {
            "store": "olimpica",
            "categories": [{"name": "Juguetería", "children": []}],
            "disclaimer": "Árbol de categorías en vivo de la tienda...",
        },
    )
    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(str(a)))
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli, "STORES", {"olimpica": {"name": "Olímpica"}})

    market_cli.cmd_categories(argparse.Namespace(store="olimpica", json=False))

    assert any("Juguetería" in p for p in printed)
    assert any("Árbol de categorías" in p for p in printed)


def test_cmd_categories_handles_legacy_list_shape(monkeypatch):
    """Backward-compat with an older pinned backend still returning a bare list."""
    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda *a, **k: [{"name": "Almacén", "children": []}],
    )
    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(str(a)))
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli, "STORES", {"carrefour": {"name": "Carrefour"}})

    market_cli.cmd_categories(argparse.Namespace(store="carrefour", json=False))

    assert any("Almacén" in p for p in printed)
