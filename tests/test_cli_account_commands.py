"""Tests for the account-related CLI commands mirroring previously
MCP-only tools: market subscription, household, ticket."""

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
        captured["payload"] = a[0] if a else k.get("json_data")
        return response

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)
    return captured


def test_cmd_subscription_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "username": "user-abc", "api_keys": 1,
        "subscription": {"tier": "free", "req_limit_day": 1000, "req_limit_min": 60,
                          "alerts": 0, "export": False, "history_days": 7, "expires_at": None},
    })
    args = argparse.Namespace(json=False)
    market_cli.cmd_subscription(args)
    assert captured["method"] == "GET"
    assert captured["path"] == "/auth/subscription"


def test_cmd_household_get_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {
        "data": {"size": 1, "country": "PE", "currency": "PEN", "budget_monthly": None,
                 "default_line": "supermercados", "default_stores": [], "staple_list": []},
        "meta": {},
    })
    args = argparse.Namespace(action="get", json=False)
    market_cli.cmd_household(args)
    assert captured["method"] == "GET"
    assert captured["path"] == "/v1/household"


def test_cmd_household_update_uses_put_by_default(monkeypatch):
    captured = _patch_common(monkeypatch, {"data": {}, "meta": {}})
    args = argparse.Namespace(
        action="update", size=None, country=None, budget=500.0, default_line=None,
        patch=False, json=False,
    )
    market_cli.cmd_household(args)
    assert captured["method"] == "PUT"
    assert captured["path"] == "/v1/household"
    assert captured["payload"] == {"budget_monthly": 500.0}


def test_cmd_household_update_uses_patch_when_flag_set(monkeypatch):
    captured = _patch_common(monkeypatch, {"data": {}, "meta": {}})
    args = argparse.Namespace(
        action="update", size=4, country="PE", budget=None, default_line=None,
        patch=True, json=False,
    )
    market_cli.cmd_household(args)
    assert captured["method"] == "PATCH"
    assert captured["payload"] == {"size": 4, "country": "PE"}


def test_cmd_household_update_with_no_flags_does_not_call_api(monkeypatch):
    called = {"count": 0}

    def _fake_cli_api(*a, **k):
        called["count"] += 1
        return {}

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(
        action="update", size=None, country=None, budget=None, default_line=None,
        patch=False, json=False,
    )
    market_cli.cmd_household(args)
    assert called["count"] == 0


def test_cmd_ticket_calls_correct_endpoint(monkeypatch):
    captured = _patch_common(monkeypatch, {"receipt": {}, "matches": []})
    args = argparse.Namespace(
        url="https://example.com/receipt.jpg", country="PE", submit_to_crowd=False, json=False,
    )
    market_cli.cmd_ticket(args)
    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/ticket/scan-url"
    assert captured["payload"] == {"url": "https://example.com/receipt.jpg", "country": "PE"}


def test_cmd_ticket_submits_to_crowd_when_flag_set(monkeypatch):
    calls = []

    def _fake_cli_api(method, path, payload=None, *a, **k):
        calls.append((method, path, payload))
        if path == "/v1/ticket/scan-url":
            return {"receipt": {}, "matches": []}
        return {"submitted": True}

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(
        url="https://example.com/receipt.jpg", country="PE", submit_to_crowd=True, json=False,
    )
    market_cli.cmd_ticket(args)

    assert len(calls) == 2
    assert calls[1][1] == "/v1/receipts/submit"


def test_cmd_ticket_skips_crowd_submit_on_scan_error(monkeypatch):
    calls = []

    def _fake_cli_api(method, path, payload=None, *a, **k):
        calls.append(path)
        return {"error": "scan failed", "status": 502}

    monkeypatch.setattr(market_cli, "cli_api", _fake_cli_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: False)

    args = argparse.Namespace(
        url="https://example.com/bad.jpg", country="PE", submit_to_crowd=True, json=False,
    )
    market_cli.cmd_ticket(args)

    assert calls == ["/v1/ticket/scan-url"]  # crowd submit skipped after error


def test_cmd_subscription_json_mode_prints_raw_payload(monkeypatch):
    response = {"username": "user-abc", "subscription": {"tier": "free"}}
    monkeypatch.setattr(market_cli, "cli_api", lambda *a, **k: response)
    monkeypatch.setattr(market_cli.console, "status", lambda *a, **k: _status_mock())

    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    args = argparse.Namespace(json=True)
    market_cli.cmd_subscription(args)

    assert len(printed) == 1
    assert json.loads(printed[0]) == response
