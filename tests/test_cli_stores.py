"""Tests for `market stores` CLI command."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


def test_cmd_stores_filters_country(monkeypatch):
    calls: list[str] = []

    def fake_api(method, path, json_data=None):
        calls.append(path)
        return {
            "stores": {
                "wong": {
                    "name": "Wong",
                    "country": "PE",
                    "currency": "PEN",
                    "line": "super",
                    "line_name": "Supermercado",
                }
            },
            "total": 1,
        }

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    market_cli.cmd_stores(argparse.Namespace(country="PE", line=None, json=False))

    assert calls == ["/stores?country=PE"]


def test_cmd_stores_json(monkeypatch):
    emitted: list = []

    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda *a, **k: {"stores": {"metro": {"name": "Metro", "country": "PE"}}, "total": 1},
    )
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: True)
    monkeypatch.setattr(market_cli.ui, "emit_json", lambda payload, _console: emitted.append(payload))

    market_cli.cmd_stores(argparse.Namespace(country=None, line=None, json=True))

    assert emitted
    assert emitted[0]["ok"] is True
    assert emitted[0]["data"]["total"] == 1


def test_cmd_stores_json_next_commands_use_requested_country(monkeypatch):
    """Regression for cli-market-world#466 (S5): next_commands hardcoded
    --country PE regardless of the country actually requested/active."""
    emitted: list = []

    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda *a, **k: {"stores": {"carrefour_ar": {"name": "Carrefour", "country": "AR"}}, "total": 1},
    )
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: True)
    monkeypatch.setattr(market_cli.ui, "emit_json", lambda payload, _console: emitted.append(payload))

    market_cli.cmd_stores(argparse.Namespace(country="AR", line=None, json=True))

    assert emitted
    assert all("PE" not in c for c in emitted[0]["next_commands"])
    assert any("AR" in c for c in emitted[0]["next_commands"])
