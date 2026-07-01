"""Tests for intel CLI country-related UX fixes: positional shorthand and
exit codes on no-coverage responses (cli-market-world#465/#466)."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import pytest

import market_cli


def test_rewrite_positional_country_valid_code():
    argv = ["market", "intel", "brief", "pe"]
    assert market_cli._rewrite_positional_country(argv) == [
        "market", "intel", "brief", "--country", "PE",
    ]


def test_rewrite_positional_country_uppercase_valid_code():
    argv = ["market", "intel", "inflation", "AR", "--days", "14"]
    assert market_cli._rewrite_positional_country(argv) == [
        "market", "intel", "inflation", "--country", "AR", "--days", "14",
    ]


def test_rewrite_positional_country_noop_when_flag_present():
    argv = ["market", "intel", "inflation", "--country", "PE"]
    assert market_cli._rewrite_positional_country(argv) == argv


def test_rewrite_positional_country_noop_for_unknown_code():
    # Not in market_core.COUNTRIES (e.g. a typo or a fully-disabled country
    # like UY, which was excluded upstream in cli-market-core#128).
    argv = ["market", "intel", "brief", "xyz"]
    assert market_cli._rewrite_positional_country(argv) == argv


def test_rewrite_positional_country_noop_when_no_extra_token():
    argv = ["market", "intel", "brief"]
    assert market_cli._rewrite_positional_country(argv) == argv


def test_rewrite_positional_country_noop_for_unrelated_command():
    argv = ["market", "search", "leche"]
    assert market_cli._rewrite_positional_country(argv) == argv


def test_cmd_inflation_exits_2_on_no_coverage(monkeypatch):
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: {"items": []})
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(country="UY", line=None, days=7, json=False)
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_inflation(args)
    assert exc.value.code == 2


def test_cmd_inflation_no_exit_when_items_present(monkeypatch):
    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda *a, **k: {"items": [{"n_products": 3, "delta_pct": 1.0, "line": "supermercados"}]},
    )
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(country="PE", line=None, days=7, json=False)
    market_cli.cmd_inflation(args)  # should not raise


def test_cmd_enrichment_exits_2_on_no_coverage(monkeypatch):
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: {"indicators": []})
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(country="UY", refresh=False, json=False)
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_enrichment(args)
    assert exc.value.code == 2
