"""Guided first-search activation after register/init."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli
import market_core


@pytest.fixture(autouse=True)
def clear_activation_flag():
    flag = market_core.SESSION_FILE.parent / "activation_search_done"
    if flag.is_file():
        flag.unlink()
    yield
    if flag.is_file():
        flag.unlink()


def test_activation_query_by_country():
    assert market_cli._activation_query("PE") == "leche"
    assert market_cli._activation_query("US") == "milk"


def test_run_activation_search_once(monkeypatch):
    calls: list[dict] = []

    def fake_api(method, path, body=None):
        calls.append({"method": method, "path": path, "body": body})
        return {
            "total": 2,
            "results": [
                {
                    "name": "Leche entera",
                    "store": "wong",
                    "store_name": "Wong",
                    "price": 4.2,
                    "currency": "PEN",
                }
            ],
        }

    monkeypatch.setattr(market_cli, "api", fake_api)
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-test")
    monkeypatch.setattr(market_cli.ui, "get_default_country", lambda: "PE")
    monkeypatch.setattr(market_cli.console, "print", MagicMock())

    assert market_cli._run_activation_search() is True
    assert market_cli._run_activation_search() is False
    assert len(calls) == 1
    assert calls[0]["path"] == "/products/search"
    assert calls[0]["body"]["query"] == "leche"
    assert market_cli._activation_search_done() is True


def test_register_runs_activation_search(monkeypatch):
    monkeypatch.setattr(
        market_cli,
        "api",
        lambda method, path, body=None: (
            {"username": "user-x", "api_key": "sk-x"}
            if path == "/auth/register"
            else {"total": 1, "results": [{"name": "Leche", "store": "wong", "price": 1, "currency": "PEN"}]}
        ),
    )
    monkeypatch.setattr(market_cli, "get_token", lambda: "sk-x")
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: True)
    monkeypatch.setattr(market_cli.ui, "get_default_country", lambda: "PE")
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    panel = MagicMock()
    panel.fit = MagicMock(return_value="panel")
    monkeypatch.setattr(market_cli, "Panel", panel)

    import argparse

    market_cli.cmd_register(argparse.Namespace(json=False, skip_search=False))
    assert market_cli._activation_search_done() is True


def test_register_passes_ref_code(monkeypatch):
    calls: list[dict] = []

    def fake_api(method, path, body=None):
        calls.append({"method": method, "path": path, "body": body})
        return {"username": "user-x", "api_key": "sk-x"}

    monkeypatch.setattr(market_cli, "api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    panel = MagicMock()
    panel.fit = MagicMock(return_value="panel")
    monkeypatch.setattr(market_cli, "Panel", panel)

    import argparse

    market_cli.cmd_register(argparse.Namespace(json=False, skip_search=True, ref="ref-abc123"))
    assert calls == [{"method": "POST", "path": "/auth/register", "body": {"ref_code": "ref-abc123"}}]


def test_register_without_ref_sends_no_body(monkeypatch):
    calls: list[dict] = []

    def fake_api(method, path, body=None):
        calls.append({"method": method, "path": path, "body": body})
        return {"username": "user-x", "api_key": "sk-x"}

    monkeypatch.setattr(market_cli, "api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    panel = MagicMock()
    panel.fit = MagicMock(return_value="panel")
    monkeypatch.setattr(market_cli, "Panel", panel)

    import argparse

    market_cli.cmd_register(argparse.Namespace(json=False, skip_search=True, ref=None))
    assert calls == [{"method": "POST", "path": "/auth/register", "body": None}]


class _FakeStatus:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_cmd_inflation_renders_api_shape(monkeypatch):
    """Regression: inflation items use line/avg_* fields, not product/first_price."""
    mock_data = {
        "items": [
            {
                "line": "Supermercados",
                "line_key": "supermercados",
                "currency": "PEN",
                "avg_now": 12.0,
                "avg_before": 10.0,
                "delta_pct": 20.0,
                "n_products": 3,
            }
        ],
        "avg_inflation_pct": 20.0,
    }
    printed: list = []

    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: mock_data)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _FakeStatus())
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a))
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)

    import argparse

    market_cli.cmd_inflation(argparse.Namespace(country="PE", line=None, days=7, json=False))
    assert printed


def test_cmd_alerts_list_uses_get(monkeypatch):
    calls: list[tuple] = []

    def fake_api(method, path, body=None):
        calls.append((method, path, body))
        return {"alerts": [{"id": "ALT-1", "product_query": "leche", "condition": "price_drop", "threshold_pct": 5.0}]}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: None)
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)

    import argparse

    market_cli.cmd_alerts(argparse.Namespace(action="list", product=None, threshold=5.0, condition="price_drop", email=None))
    assert calls == [("GET", "/v1/alerts", None)]