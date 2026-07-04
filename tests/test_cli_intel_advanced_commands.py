"""Tests for the final "advanced intel/B2B" batch CLI commands mirroring
previously MCP-only tools: market inflation-report, procurement-signal,
moat-confidence, export, procurement-bulk."""

from __future__ import annotations

import argparse
import json
from unittest.mock import MagicMock

import market_cli


def _status_mock():
    return MagicMock(__enter__=lambda s: s, __exit__=lambda *a: False)


def _patch_common(monkeypatch, response):
    captured = {}

    def _fake_cli_api(method, path, *a, **k):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = a[0] if a else None
        return response

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)
    return captured


def test_cmd_inflation_report_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {"pressure": "rising", "signals": {"staple_momentum_pct": 5.98}}, "meta": {},
    })
    args = argparse.Namespace(country="PE", line=None, days=30, json=False)
    market_cli.cmd_inflation_report(args)
    assert captured["path"] == "/v1/intel/inflation-report?country=PE&line=&days=30"


def test_cmd_procurement_signal_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {"signal": "wait", "signal_reason": "staples rising"}, "meta": {},
    })
    args = argparse.Namespace(country="PE", line=None, json=False)
    market_cli.cmd_procurement_signal(args)
    assert captured["path"] == "/v1/intel/procurement-signal?country=PE&line="


def test_cmd_moat_confidence_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {"confidence_tier": "unverified", "crowd_confirmations_7d": 0,
                 "crowd_conflicts_7d": 0, "verified_threshold": 5},
        "meta": {},
    })
    args = argparse.Namespace(product_id="543365", store="metro", name=None, json=False)
    market_cli.cmd_moat_confidence(args)
    assert captured["path"] == "/v1/moat/confidence?product_id=543365&store=metro&name="


def test_cmd_moat_confidence_escapes_name(monkeypatch):
    captured = _patch_common(monkeypatch, {"data": {}, "meta": {}})
    args = argparse.Namespace(product_id=None, store=None, name="leche & queso", json=False)
    market_cli.cmd_moat_confidence(args)
    assert "name=leche%20%26%20queso" in captured["path"]


def test_cmd_export_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {"format": "json", "data": [{"id": 1}], "total": 1})
    args = argparse.Namespace(country="PE", line="supermercados", format="json", limit=100, output=None, json=False)
    market_cli.cmd_export(args)
    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/data/export"
    assert captured["payload"] == {"country": "PE", "line": "supermercados", "format": "json", "limit": 100}


def test_cmd_export_writes_json_to_output_file(monkeypatch, tmp_path):
    _patch_common(monkeypatch, {"format": "json", "data": [{"id": 1}], "total": 1})
    out_file = tmp_path / "export.json"
    args = argparse.Namespace(country="PE", line=None, format="json", limit=100, output=str(out_file), json=False)
    market_cli.cmd_export(args)
    assert out_file.exists()
    assert json.loads(out_file.read_text())["total"] == 1


def test_cmd_export_writes_csv_string_to_output_file(monkeypatch, tmp_path):
    _patch_common(monkeypatch, {"format": "csv", "data": "id,name\r\n1,Leche\r\n", "total": 1})
    out_file = tmp_path / "export.csv"
    args = argparse.Namespace(country="PE", line=None, format="csv", limit=100, output=str(out_file), json=False)
    market_cli.cmd_export(args)
    assert out_file.exists()
    assert out_file.read_text().startswith("id,name")


def test_cmd_export_refuses_to_write_json_as_csv(monkeypatch, tmp_path):
    """Regression (code-reviewer finding): if --format csv is requested but the
    API returns a non-string data.data (broken contract), the CLI must refuse
    to silently write a JSON envelope into a .csv-named file."""
    _patch_common(monkeypatch, {"format": "csv", "data": [{"id": 1}], "total": 1})
    out_file = tmp_path / "export.csv"
    args = argparse.Namespace(country="PE", line=None, format="csv", limit=100, output=str(out_file), json=False)
    market_cli.cmd_export(args)
    assert not out_file.exists()


def test_cmd_export_handles_error_response(monkeypatch):
    _patch_common(monkeypatch, {"error": "starter tier required", "status": 403})
    args = argparse.Namespace(country="PE", line=None, format="json", limit=100, output=None, json=False)
    market_cli.cmd_export(args)  # should not raise


def test_cmd_procurement_bulk_parses_sku_qty_unit(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {"lines": [], "summary": {"buy_now": 0, "monitor": 0, "wait": 0}}, "meta": {},
    })
    args = argparse.Namespace(
        items=["arroz:10:kg", "aceite:5"], country="PE", organization_id=None,
        no_substitutes=False, output_format="json", json=False,
    )
    market_cli.cmd_procurement_bulk(args)

    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/intel/procurement-bulk"
    lines = captured["payload"]["lines"]
    assert lines[0] == {"sku_query": "arroz", "qty": 10, "unit": "kg"}
    assert lines[1] == {"sku_query": "aceite", "qty": 5, "unit": "unit"}


def test_cmd_procurement_bulk_parses_decimal_quantity(monkeypatch):
    """Regression (code-reviewer finding): int() on '2.5' raised ValueError and
    silently fell back to qty=1 — weight-based purchases (kg, L) commonly use
    decimal quantities."""
    captured = _patch_common(monkeypatch, {"data": {"lines": [], "summary": {}}, "meta": {}})
    args = argparse.Namespace(
        items=["arroz:2.5:kg"], country="PE", organization_id=None,
        no_substitutes=False, output_format="json", json=False,
    )
    market_cli.cmd_procurement_bulk(args)
    assert captured["payload"]["lines"][0] == {"sku_query": "arroz", "qty": 2.5, "unit": "kg"}


def test_cmd_procurement_bulk_sku_query_with_colon_not_mangled(monkeypatch):
    """Regression (code-reviewer finding): a sku_query containing ':' used to
    be split from the left, corrupting sku_query/qty/unit. rsplit from the
    right fixes this."""
    captured = _patch_common(monkeypatch, {"data": {"lines": [], "summary": {}}, "meta": {}})
    args = argparse.Namespace(
        items=["arroz:premium:10:kg"], country="PE", organization_id=None,
        no_substitutes=False, output_format="json", json=False,
    )
    market_cli.cmd_procurement_bulk(args)
    assert captured["payload"]["lines"][0] == {"sku_query": "arroz:premium", "qty": 10, "unit": "kg"}


def test_cmd_procurement_bulk_warns_on_unparseable_quantity(monkeypatch):
    printed = []
    _patch_common(monkeypatch, {"data": {"lines": [], "summary": {}}, "meta": {}})
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(str(a[0]) if a else ""))
    args = argparse.Namespace(
        items=["arroz:abc"], country="PE", organization_id=None,
        no_substitutes=False, output_format="json", json=False,
    )
    market_cli.cmd_procurement_bulk(args)
    assert any("cantidad" in p.lower() or "quantity" in p.lower() for p in printed)


def test_cmd_procurement_bulk_no_items_does_not_call_api(monkeypatch):
    called = {"count": 0}

    def _fake_cli_api(*a, **k):
        called["count"] += 1
        return {}

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(
        items=[], country="PE", organization_id=None, no_substitutes=False,
        output_format="json", json=False,
    )
    market_cli.cmd_procurement_bulk(args)
    assert called["count"] == 0


def test_cmd_procurement_bulk_renders_results(monkeypatch):
    _patch_common(monkeypatch, {
        "data": {
            "lines": [{"sku_query": "arroz", "signal": "wait",
                       "best_match": {"name": "Arroz Superior", "price": 5.8, "currency": "PEN"}}],
            "summary": {"buy_now": 0, "monitor": 0, "wait": 1},
        },
        "meta": {},
    })
    args = argparse.Namespace(
        items=["arroz:10"], country="PE", organization_id=None,
        no_substitutes=True, output_format="json", json=False,
    )
    market_cli.cmd_procurement_bulk(args)  # should not raise


def test_cmd_inflation_report_json_mode_prints_raw_payload(monkeypatch):
    response = {"data": {"pressure": "stable"}, "meta": {}}
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: response)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())

    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(country="PE", line=None, days=30, json=True)
    market_cli.cmd_inflation_report(args)

    assert len(printed) == 1
    assert json.loads(printed[0]) == response
