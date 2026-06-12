"""Tests for market doctor readiness checks."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli


def _mock_response(status_code: int, payload: dict | None = None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload or {}
    return resp


@patch("shutil.which", return_value="/usr/bin/market-mcp")
@patch("market_cli.get_token", return_value=None)
@patch("httpx.get")
def test_collect_doctor_checks_prod_ok(mock_get, _token, _which):
    def side_effect(url, timeout=10):
        if url.endswith("/health/db"):
            return _mock_response(200, {"snapshots": 50_000})
        if url.endswith("/v1/sources/health"):
            return _mock_response(200, {"summary": {"ok": 38, "partial": 0, "dead": 0}})
        if url.endswith("/health/stats"):
            return _mock_response(200, {"golden_linkage_pct": 86.0})
        raise AssertionError(f"unexpected url {url}")

    mock_get.side_effect = side_effect
    checks, ok = market_cli._collect_doctor_checks()
    names = {n: (d, s) for n, d, s in checks}
    assert ok is True
    assert names["API health"][1] == "ok"
    assert names["Sources health"][1] == "ok"
    assert "86.0%" in names["Golden linkage"][0]
    assert names["Golden linkage"][1] == "ok"


@patch("shutil.which", return_value=None)
@patch("market_cli.get_token", return_value=None)
@patch("httpx.get")
def test_collect_doctor_checks_linkage_warn(mock_get, _token, _which):
    def side_effect(url, timeout=10):
        if url.endswith("/health/db"):
            return _mock_response(200, {"snapshots": 10_000})
        if url.endswith("/v1/sources/health"):
            return _mock_response(200, {"summary": {"ok": 30, "partial": 2, "dead": 1}})
        if url.endswith("/health/stats"):
            return _mock_response(200, {"golden_linkage_pct": 42.0})
        raise AssertionError(f"unexpected url {url}")

    mock_get.side_effect = side_effect
    checks, ok = market_cli._collect_doctor_checks()
    names = {n: (d, s) for n, d, s in checks}
    assert ok is True
    assert names["Sources health"][1] == "warn"
    assert names["Golden linkage"][1] == "warn"


@patch("shutil.which", return_value=None)
@patch("market_cli.get_token", return_value=None)
@patch("httpx.get")
def test_collect_doctor_checks_api_fail(mock_get, _token, _which):
    mock_get.side_effect = lambda url, timeout=10: _mock_response(503, {})
    checks, ok = market_cli._collect_doctor_checks()
    assert ok is False
    assert any(name == "API health" and status == "fail" for name, _, status in checks)


def test_doctor_prod_gate_script():
    from ops.doctor_prod_gate import run_gate

    with patch("ops.doctor_prod_gate.httpx.Client") as mock_client_cls:
        client = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = client

        def get(url):
            if url.endswith("/health/db"):
                return _mock_response(200, {"snapshots": 40_000})
            if url.endswith("/v1/sources/health"):
                return _mock_response(200, {"summary": {"ok": 38, "dead": 0}})
            if url.endswith("/health/stats"):
                return _mock_response(200, {"golden_linkage_pct": 86.0})
            raise AssertionError(url)

        client.get.side_effect = get
        assert run_gate() == []
