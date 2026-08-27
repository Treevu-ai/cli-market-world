"""Tests for the `market affordability` CLI command."""

from __future__ import annotations

import argparse
import json
from unittest.mock import MagicMock

import market_cli

FAKE_RESPONSE = {
    "data": {
        "question": "How affordable is daily life this month?",
        "country": "PE",
        "line": "supermercados",
        "days": 30,
        "affordability_score": 97,
        "affordability_band": "comfortable",
        "affordability_band_es": "cómodo",
        "score_data_quality": "low",
        "headline_es": "Canasta mínima observada ~65 PEN en PE",
        "components": {
            "canasta_min": 65.1,
            "canasta_average": 91.05,
            "canasta_worst": 149.72,
            "canasta_currency": "PEN",
            "minimum_wage_local": 1130.0,
            "canastas_per_minimum_wage": 17.36,
            "vs_official_cpi_gap_pp": 1.11,
            "staple_momentum_7d_pct": 5.98,
        },
        "signals": {"price_dispersion_pct": 21.35, "promo_intensity_pct": 37.41},
        "disclaimer_es": "Precios observados en tiendas online indexadas.",
    },
    "meta": {"confidence": "moderate"},
}


def test_cmd_affordability_calls_correct_endpoint(monkeypatch):
    captured = {}

    def _fake_cli_api(method, path, *a, **k):
        captured["method"] = method
        captured["path"] = path
        return FAKE_RESPONSE

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False))
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(country="PE", line=None, days=30, json=False)
    market_cli.cmd_affordability(args)

    assert captured["method"] == "GET"
    assert captured["path"] == "/v1/intel/affordability?country=PE&line=supermercados&days=30"


def test_cmd_affordability_defaults_country_to_pe(monkeypatch):
    captured = {}

    def _fake_cli_api(method, path, *a, **k):
        captured["path"] = path
        return FAKE_RESPONSE

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False))
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(country=None, line=None, days=None, json=False)
    market_cli.cmd_affordability(args)

    assert "country=PE" in captured["path"]
    assert "line=supermercados" in captured["path"]
    assert "days=30" in captured["path"]


class _FakeTable:
    """Records add_row calls instead of rendering, so tests can assert on
    the actual table content rather than just that console.print ran."""

    def __init__(self, *a, **k):
        self.rows: list[tuple] = []

    def add_column(self, *a, **k):
        pass

    def add_row(self, *a, **k):
        self.rows.append(a)


def test_cmd_affordability_shows_best_worst_case_band(monkeypatch):
    """K2 (docs/backlog/2026-08-27-transparencia-metricas-ambiguas-backlog.md):
    canastas_per_minimum_wage is a midpoint, not an absolute figure -- the
    best/worst band the API already returns (components.
    canastas_per_minimum_wage_best/_worst) must be visible in the table, not
    just the average."""
    response = json.loads(json.dumps(FAKE_RESPONSE))  # deep copy
    response["data"]["components"]["canastas_per_minimum_wage_best"] = 19.58
    response["data"]["components"]["canastas_per_minimum_wage_worst"] = 13.68

    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: response)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False))
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    tables: list[_FakeTable] = []
    monkeypatch.setattr(market_cli, "Table", lambda *a, **k: tables.append(_FakeTable()) or tables[-1])

    args = argparse.Namespace(country="PE", line=None, days=30, json=False)
    market_cli.cmd_affordability(args)

    assert len(tables) == 1
    values_by_label = {label: value for label, value in tables[0].rows}
    assert "19.58" in next(v for k, v in values_by_label.items() if "mejor caso" in k)
    assert "13.68" in next(v for k, v in values_by_label.items() if "peor caso" in k)


def test_cmd_affordability_json_mode_prints_raw_payload(monkeypatch, capsys):
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: FAKE_RESPONSE)
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False))

    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(country="PE", line=None, days=30, json=True)
    market_cli.cmd_affordability(args)

    assert len(printed) == 1
    parsed = json.loads(printed[0])
    assert parsed == FAKE_RESPONSE
