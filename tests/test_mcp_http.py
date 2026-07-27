"""Tests for routers/mcp_http.py — JSON-RPC tool dispatch → internal REST routes.

No test file existed for this dispatch table before, which is exactly how the
market_procurement_signal -> /v1/intel/basket-stress mismatch (a route that
never existed, verified 404 in production) shipped silently.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from market_server import app

import server_deps

ensure_db_initialized()
client = TestClient(app)

_ADMIN_TOKEN = "test-token-123"
_AUTH = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}


@pytest.fixture(autouse=True)
def patch_token(monkeypatch):
    monkeypatch.setattr(server_deps, "DEFAULT_TOKEN", _ADMIN_TOKEN)


def _rpc_call(tool_name: str, arguments: dict | None = None) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments or {}},
    }


def test_market_procurement_signal_hits_procurement_signal_route():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"data": {"signal": "buy_now"}}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_procurement_signal", {"country": "PE"}), headers=_AUTH)

    assert r.status_code == 200
    called_url = mock_get.call_args.args[0]
    assert called_url == "https://cli-market-api.fly.dev/v1/intel/procurement-signal"
    assert "basket-stress" not in called_url


def test_market_macro_hits_intel_macro_route():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {
        "tipo_cambio": {"venta": {"price": 3.412}, "compra": {"price": 3.405}},
        "ipc_lima": {"price": 120.292167},
        "source": "bcrp_pe",
    }

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_macro"), headers=_AUTH)

    assert r.status_code == 200
    called_url = mock_get.call_args.args[0]
    assert called_url == "https://cli-market-api.fly.dev/v1/intel/macro"


@pytest.mark.parametrize(
    "tool_name,expected_path",
    [
        ("market_receipts", "/v1/receipts"),
        ("market_quality_scores", "/v1/quality/scores"),
        ("market_quality_flagged", "/v1/quality/flagged"),
        ("market_dispersion", "/v1/dispersion"),
        ("market_coverage_matrix", "/v1/coverage/matrix"),
    ],
)
def test_wave5_quality_tools_hit_correct_route(tool_name, expected_path):
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call(tool_name), headers=_AUTH)

    assert r.status_code == 200
    called_url = mock_get.call_args.args[0]
    assert called_url == f"https://cli-market-api.fly.dev{expected_path}"


def test_wave5_quality_tools_listed_and_gated_pro():
    from routers.mcp_http import _PRO_TOOLS, _TOOLS

    wave5 = {
        "market_receipts",
        "market_quality_scores",
        "market_quality_flagged",
        "market_dispersion",
        "market_coverage_matrix",
    }
    names = {t["name"] for t in _TOOLS}
    assert wave5 <= names
    assert wave5 <= _PRO_TOOLS
