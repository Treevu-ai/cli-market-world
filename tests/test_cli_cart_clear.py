"""Regression test for market_cli.cmd_cart_clear.

cmd_cart_clear used to call DELETE /cart (a bulk-clear endpoint that was
never implemented in cli-market-backend/routers/cart.py — only
DELETE /cart/{product_id} exists). Every invocation 404'd, so the command
was unconditionally broken. Fixed by looping DELETE /cart/{cart_id} over
each cart row, matching the only endpoint the backend actually exposes.
"""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


def test_cart_clear_deletes_each_item_individually(monkeypatch):
    calls = []

    def fake_api(method, path, body=None):
        calls.append((method, path))
        if method == "GET" and path == "/cart":
            return {
                "cart": [
                    {"cart_id": "1", "product_id": "p1", "name": "Arroz", "price": 4.2, "quantity": 1},
                    {"cart_id": "2", "product_id": "p2", "name": "Aceite", "price": 9.8, "quantity": 2},
                ]
            }
        if method == "DELETE":
            return {"message": "Producto eliminado del carrito"}
        return {}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli, "input", lambda *_a: "s", raising=False)

    market_cli.cmd_cart_clear(argparse.Namespace())

    delete_calls = [path for method, path in calls if method == "DELETE"]
    assert delete_calls == ["/cart/1", "/cart/2"]
    assert ("DELETE", "/cart") not in calls


def test_cart_clear_noop_when_empty(monkeypatch):
    monkeypatch.setattr(market_cli, "cli_api", lambda method, path, body=None: {"cart": []})
    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    market_cli.cmd_cart_clear(argparse.Namespace())

    assert any("vacío" in str(p) for p in printed)


def test_cart_clear_cancelled_makes_no_delete_calls(monkeypatch):
    calls = []

    def fake_api(method, path, body=None):
        calls.append((method, path))
        return {"cart": [{"cart_id": "1", "product_id": "p1", "name": "Arroz", "price": 4.2, "quantity": 1}]}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli, "input", lambda *_a: "n", raising=False)

    market_cli.cmd_cart_clear(argparse.Namespace())

    assert all(method != "DELETE" for method, _ in calls)
