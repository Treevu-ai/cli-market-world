"""Epic T (docs/backlog/2026-08-27-transparencia-cli-wiring-backlog.md):
transparency fields already added API-side in cli-market-core (Epics I/J/N)
must actually render in the CLI, not just exist in the raw JSON."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


class _FakeTable:
    def __init__(self, *a, **k):
        self.rows: list[tuple] = []

    def add_column(self, *a, **k):
        pass

    def add_row(self, *a, **k):
        self.rows.append(a)


def _status_mock():
    return MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False)


def _patch_common(monkeypatch, response):
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: response)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)


def test_cmd_price_risk_shows_basket_stress_baseline_source(monkeypatch):
    _patch_common(monkeypatch, {
        "data": {
            "risk_level": "moderate",
            "risk_reason": "test",
            "signals": {
                "price_dispersion_pct": 8.4,
                "basket_stress_index": 100.0,
                "basket_stress_baseline_source": "current_fallback",
            },
        },
        "meta": {},
    })
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    tables: list[_FakeTable] = []
    monkeypatch.setattr(market_cli, "Table", lambda *a, **k: tables.append(_FakeTable()) or tables[-1])

    args = argparse.Namespace(country="PE", line=None, days=7, json=False)
    market_cli.cmd_price_risk(args)

    assert len(tables) == 1
    # basket_stress_baseline_source is added as the LAST row, after the
    # existing signal_labels loop (see cmd_price_risk).
    baseline_label, baseline_value = tables[0].rows[-1]
    assert "fuente" in baseline_label.lower()
    assert "historial" in baseline_value.lower() or "history" in baseline_value.lower()


def test_cmd_inflation_report_warns_on_low_baseline(monkeypatch):
    printed = []
    _patch_common(monkeypatch, {
        "data": {
            "pressure": "rising",
            "signals": {
                "internal_inflation_pct": 745.8,
                "internal_inflation_low_baseline": True,
            },
        },
        "meta": {},
    })
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(country="PE", line=None, days=30, json=False)
    market_cli.cmd_inflation_report(args)

    assert any("respaldo débil" in str(p) for p in printed)


def test_cmd_inflation_report_no_warning_when_baseline_is_solid(monkeypatch):
    printed = []
    _patch_common(monkeypatch, {
        "data": {
            "pressure": "stable",
            "signals": {
                "internal_inflation_pct": 3.2,
                "internal_inflation_low_baseline": False,
            },
        },
        "meta": {},
    })
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(country="PE", line=None, days=30, json=False)
    market_cli.cmd_inflation_report(args)

    assert not any("respaldo débil" in str(p) for p in printed)


def test_cmd_substitutes_shows_match_quality_column(monkeypatch):
    _patch_common(monkeypatch, {
        "data": {
            "original": {"name": "Big Cola 400ml", "store": "wong", "price": 1.9},
            "substitutes": [
                {"name": "Big Cola 400ml", "store": "metro", "price": 2.0,
                 "price_per_unit": {"price_per": 5.0, "basis": "l"}, "match_quality": "exact"},
                {"name": "Pepsi 355ml", "store": "wong", "price": 1.5,
                 "price_per_unit": {"price_per": 4.2, "basis": "l"}, "match_quality": "canonical"},
            ],
        },
        "meta": {},
    })
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    tables: list[_FakeTable] = []
    monkeypatch.setattr(market_cli, "Table", lambda *a, **k: tables.append(_FakeTable()) or tables[-1])

    args = argparse.Namespace(query="big cola", country="PE", store=None, limit=3, json=False)
    market_cli.cmd_substitutes(args)

    assert len(tables) == 1
    assert len(tables[0].rows) == 2
    last_cells = [row[-1] for row in tables[0].rows]
    assert any("exacto" in cell for cell in last_cells)
    assert any("mismo tipo" in cell for cell in last_cells)


def test_cmd_substitutes_falls_back_to_confidence_when_match_quality_missing(monkeypatch):
    _patch_common(monkeypatch, {
        "data": {
            "original": {"name": "Big Cola 400ml", "store": "wong", "price": 1.9},
            "substitutes": [
                {"name": "Big Cola 400ml", "store": "metro", "price": 2.0,
                 "price_per_unit": {"price_per": 5.0, "basis": "l"}, "confidence": "ok"},
            ],
        },
        "meta": {},
    })
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    tables: list[_FakeTable] = []
    monkeypatch.setattr(market_cli, "Table", lambda *a, **k: tables.append(_FakeTable()) or tables[-1])

    args = argparse.Namespace(query="big cola", country="PE", store=None, limit=3, json=False)
    market_cli.cmd_substitutes(args)

    assert tables[0].rows[0][-1] == "[white]ok[/]"
