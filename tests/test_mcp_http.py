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


@pytest.fixture(autouse=True)
def ensure_admin_pro_tier():
    """market_receipts/quality_scores/quality_flagged/dispersion/
    coverage_matrix/prices/basket_snapshot/procurement_bulk are pre-checked
    for tier in _pre_check_tier() before the (mocked) httpx call ever fires —
    the "admin" test identity only bypasses that check when MARKET_API_TOKEN
    is a real env var (production), not in tests. Set it explicitly (to
    enterprise, a superset of pro, since procurement_bulk needs enterprise
    specifically) so these dispatch-route tests reach their mocked httpx
    call as before."""
    import market_billing

    market_billing.db_set_subscription("admin", "enterprise")


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


# ── Full dispatch-table regression coverage ────────────────────────────────
#
# Only 7/59 tools had a dispatch test before this batch — exactly the class
# of gap that let market_discover/market_price_risk/market_price_alerts ship
# broken silently (see file docstring). Covers every remaining GET-based tool
# with a single parametrized test; POST/PUT/DELETE and tools with non-trivial
# dispatch logic (payload shaping, path params, multi-request composition)
# get their own dedicated test below.

_SIMPLE_GET_TOOLS = [
    ("market_stores", {}, "/stores"),
    ("market_trending", {}, "/analytics/trending"),
    ("market_inflation", {"country": "PE"}, "/v1/intel/inflation"),
    ("market_scores", {"country": "PE"}, "/v1/intel/scores"),
    ("market_intel_brief", {}, "/v1/intel/brief"),
    ("market_stats", {}, "/analytics/stats"),
    ("market_whoami", {}, "/auth/whoami"),
    ("market_price_risk", {"country": "PE"}, "/v1/intel/price-risk"),
    ("market_informal_signal", {"country": "PE"}, "/v1/intel/informal-signal"),
    ("market_promo_detector", {"product": "leche"}, "/v1/intel/promo-detector"),
    ("market_retailer_scorecard", {"store": "wong_pe"}, "/v1/intel/retailer-scorecard"),
    ("market_price_alerts", {"product": "leche"}, "/v1/intel/alerts"),
    ("market_orders", {}, "/orders"),
    ("market_price_history", {}, "/analytics/price-history"),
    ("market_brands", {}, "/analytics/brands"),
    ("market_indicators", {}, "/analytics/indicators"),
    ("market_moat_confidence", {}, "/v1/moat/confidence"),
    ("market_subscription", {}, "/auth/subscription"),
    ("market_preferences", {}, "/agent/preferences"),
    ("market_household_get", {}, "/v1/household"),
    ("market_ecosystem_radar", {}, "/v1/ecosystem/launches"),
    ("market_enrich", {"query": "leche"}, "/products/enrich"),
    ("market_cart", {}, "/cart"),
    ("market_prices", {"country": "PE"}, "/v1/prices"),
    ("market_basket_snapshot", {}, "/v1/basket"),
    ("market_brand_monitor", {"brand": "Gloria"}, "/v1/brand-monitor"),
    ("market_brand_monitor_promos", {"brand": "Gloria"}, "/v1/brand-monitor/promos"),
    ("market_brand_monitor_alerts", {"brand": "gloria"}, "/v1/brand-monitor/alerts"),
    # Added with cli-market-core 1.11.92 — had no dispatch case at all before
    # (fell to "Unknown tool"), on top of cli-market-core never having
    # implemented the backing route (see docs/reports/p0-glo-basket-pe-enterprise-blockers.md).
    ("market_basket_stress", {"country": "PE"}, "/v1/intel/basket-stress"),
    ("market_commerce_pulse", {"country": "PE"}, "/v1/intel/pulse"),
    ("market_price_forecast", {"product": "leche"}, "/v1/intel/forecast"),
    ("market_arbitrage", {"product": "leche", "countries": "PE,MX"}, "/v1/intel/arbitrage"),
]


@pytest.mark.parametrize("tool_name,args,expected_path", _SIMPLE_GET_TOOLS)
def test_simple_get_tools_hit_correct_route(tool_name, args, expected_path):
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call(tool_name, args), headers=_AUTH)

    assert r.status_code == 200
    called_url = mock_get.call_args.args[0]
    assert called_url == f"https://cli-market-api.fly.dev{expected_path}"


_GET_TOOLS_WITH_PATH_PARAM = [
    ("market_barcode", {"code": "7501234567890"}, "/products/barcode/7501234567890"),
    ("market_stock", {"product_id": "sku-1", "store": "wong_pe"}, "/products/stock/sku-1"),
    ("market_delivery", {"product_id": "sku-1", "zipcode": "15000"}, "/products/delivery/sku-1"),
    ("market_categories", {"store": "wong_pe"}, "/categories/wong_pe"),
]


@pytest.mark.parametrize("tool_name,args,expected_path", _GET_TOOLS_WITH_PATH_PARAM)
def test_get_tools_with_path_param_hit_correct_route(tool_name, args, expected_path):
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call(tool_name, args), headers=_AUTH)

    assert r.status_code == 200
    called_url = mock_get.call_args.args[0]
    assert called_url == f"https://cli-market-api.fly.dev{expected_path}"


_SIMPLE_POST_TOOLS = [
    ("market_search", {"query": "leche"}, "/products/search"),
    ("market_compare", {"query": "leche"}, "/products/compare"),
    ("market_optimize_purchase", {"items": [{"name": "leche", "qty": 1}]}, "/v1/missions/optimize-purchase"),
    ("market_favorites", {"action": "list"}, "/favorites"),
    ("market_export", {}, "/v1/data/export"),
    ("market_ask", {"prompt": "buy milk"}, "/agent/ask"),
    ("market_add", {"product_id": "sku-1", "name": "leche", "price": 4.5, "store": "wong_pe"}, "/cart/add"),
    ("market_checkout", {"payment_method": "yape"}, "/checkout"),
    ("market_alert_create", {"product": "leche"}, "/v1/alerts"),
    ("market_procurement_bulk", {"lines": [{"sku_query": "arroz"}]}, "/v1/intel/procurement-bulk"),
    ("market_brand_monitor_config", {"brand_slug": "gloria"}, "/v1/brand-monitor/config"),
]


@pytest.mark.parametrize("tool_name,args,expected_path", _SIMPLE_POST_TOOLS)
def test_simple_post_tools_hit_correct_route(tool_name, args, expected_path):
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post("/mcp", json=_rpc_call(tool_name, args), headers=_AUTH)

    assert r.status_code == 200
    called_url = mock_post.call_args.args[0]
    assert called_url == f"https://cli-market-api.fly.dev{expected_path}"


def test_market_basket_defaults_include_tco_true():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post("/mcp", json=_rpc_call("market_basket", {"items": [{"name": "leche", "qty": 1}]}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_post.call_args.args[0] == "https://cli-market-api.fly.dev/v1/basket/compare"
    assert mock_post.call_args.kwargs["json"]["include_tco"] is True


def test_market_exchange_maps_from_currency_to_currency_fields():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post(
            "/mcp",
            json=_rpc_call("market_exchange", {"amount": 10, "from_currency": "PEN", "to_currency": "USD"}),
            headers=_AUTH,
        )

    assert r.status_code == 200
    assert mock_post.call_args.args[0] == "https://cli-market-api.fly.dev/v1/utils/exchange"
    body = mock_post.call_args.kwargs["json"]
    assert body == {"amount": 10, "from": "PEN", "to": "USD"}


def test_market_voice_hits_transcribe_url_route():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post("/mcp", json=_rpc_call("market_voice", {"url": "https://example.com/a.ogg"}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_post.call_args.args[0] == "https://cli-market-api.fly.dev/v1/voice/transcribe-url"
    assert mock_post.call_args.kwargs["json"] == {"url": "https://example.com/a.ogg"}


def test_market_ticket_hits_scan_url_route_without_crowd_submit():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"scan": "ok"}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post("/mcp", json=_rpc_call("market_ticket", {"url": "https://example.com/t.jpg"}), headers=_AUTH)

    assert r.status_code == 200
    mock_post.assert_called_once()
    assert mock_post.call_args.args[0] == "https://cli-market-api.fly.dev/v1/ticket/scan-url"


def test_market_cart_update_puts_product_id_and_quantity():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_put = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.put", mock_put):
        r = client.post("/mcp", json=_rpc_call("market_cart_update", {"product_id": "sku-1", "quantity": 2}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_put.call_args.args[0] == "https://cli-market-api.fly.dev/cart/update"
    assert mock_put.call_args.kwargs["json"] == {"product_id": "sku-1", "quantity": 2}


def test_market_household_update_defaults_to_put():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_put = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.put", mock_put):
        r = client.post("/mcp", json=_rpc_call("market_household_update", {"payload": {"size": 2}}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_put.call_args.args[0] == "https://cli-market-api.fly.dev/v1/household"


def test_market_household_update_uses_patch_when_requested():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_patch = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.patch", mock_patch):
        r = client.post(
            "/mcp",
            json=_rpc_call("market_household_update", {"payload": {"size": 2}, "patch": True}),
            headers=_AUTH,
        )

    assert r.status_code == 200
    assert mock_patch.call_args.args[0] == "https://cli-market-api.fly.dev/v1/household"


def test_market_alert_delete_hits_delete_route_with_alert_id():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_delete = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.delete", mock_delete):
        r = client.post("/mcp", json=_rpc_call("market_alert_delete", {"alert_id": "al-1"}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_delete.call_args.args[0] == "https://cli-market-api.fly.dev/v1/alerts/al-1"


def test_market_dashboard_defaults_to_slim_true():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_dashboard", {}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_get.call_args.args[0] == "https://cli-market-api.fly.dev/dashboard/data"
    assert mock_get.call_args.kwargs["params"] == {"slim": "true"}


def test_market_dashboard_full_omits_slim_param():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_dashboard", {"full": True}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_get.call_args.kwargs["params"] == {}


def test_market_discover_composes_lines_stores_countries():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"data": []}

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_discover", {"country": "PE"}), headers=_AUTH)

    assert r.status_code == 200
    called_urls = {call.args[0] for call in mock_get.call_args_list}
    assert called_urls == {
        "https://cli-market-api.fly.dev/lines",
        "https://cli-market-api.fly.dev/stores",
        "https://cli-market-api.fly.dev/countries",
    }


# ── Admin tools ─────────────────────────────────────────────────────────────

def test_market_scan_hits_admin_scan_stores_route():
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post("/mcp", json=_rpc_call("market_scan", {}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_post.call_args.args[0] == "https://cli-market-api.fly.dev/v1/admin/scan-stores"


@pytest.mark.parametrize(
    "tool_name,expected_path",
    [
        ("market_intel_refresh", "/v1/intel/refresh"),
        ("market_enrichment_refresh", "/v1/intel/enrichment/refresh"),
    ],
)
def test_admin_refresh_tools_hit_correct_route(tool_name, expected_path):
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post("/mcp", json=_rpc_call(tool_name, {}), headers=_AUTH)

    assert r.status_code == 200
    assert mock_post.call_args.args[0] == f"https://cli-market-api.fly.dev{expected_path}"


# ── Tier-gating consistency ──────────────────────────────────────────────────

def test_admin_tools_excluded_from_all_paid_tier_sets():
    """Admin tools are gated via MARKET_API_TOKEN, not billing tier — a 401
    here means wrong audience, not "pay more". They must not be in any of
    the three paid-tier upgrade-prompt sets."""
    from routers.mcp_http import _ENTERPRISE_TOOLS, _PRO_TOOLS, _STARTER_TOOLS

    admin_tools = {"market_scan", "market_intel_refresh", "market_enrichment_refresh"}
    assert not (admin_tools & _PRO_TOOLS)
    assert not (admin_tools & _STARTER_TOOLS)
    assert not (admin_tools & _ENTERPRISE_TOOLS)


def test_procurement_bulk_gated_enterprise_not_pro():
    from routers.mcp_http import _ENTERPRISE_TOOLS, _PRO_TOOLS

    assert "market_procurement_bulk" in _ENTERPRISE_TOOLS
    assert "market_procurement_bulk" not in _PRO_TOOLS


def test_household_get_gated_starter_returns_friendly_message_on_403():
    from routers.mcp_http import _STARTER_TOOLS

    assert "market_household_get" in _STARTER_TOOLS

    fake_resp = MagicMock()
    fake_resp.status_code = 403
    fake_resp.text = "forbidden"

    mock_get = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_household_get", {}), headers=_AUTH)

    assert r.status_code == 200
    result = r.json()["result"]
    assert result["isError"] is True
    assert "Starter" in result["content"][0]["text"]


def test_procurement_bulk_returns_enterprise_message_on_403():
    fake_resp = MagicMock()
    fake_resp.status_code = 403
    fake_resp.text = "forbidden"

    mock_post = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post(
            "/mcp",
            json=_rpc_call("market_procurement_bulk", {"lines": [{"sku_query": "arroz"}]}),
            headers=_AUTH,
        )

    assert r.status_code == 200
    result = r.json()["result"]
    assert result["isError"] is True
    assert "Enterprise" in result["content"][0]["text"]


def _patch_starter_tier(monkeypatch):
    """Simulate a real (non-admin) Starter-tier caller for _pre_check_tier —
    is_platform_admin("admin") always bypasses tier checks in tests (see
    ensure_admin_pro_tier fixture note), so verifying real rejection needs a
    non-admin identity. Two separate auth_user bindings need patching: the
    request first passes require_api_key() (server_deps.py, own module-level
    auth_user reference) before _call_tool()'s _pre_check_tier (mcp_http.py,
    imported its own auth_user reference at module-import time) runs."""
    import market_billing
    import routers.mcp_http as mcp_http_mod

    fake_sub = {"tier": "starter", "req_limit_min": -1, "req_limit_day": -1}
    fake_auth_user = lambda token: "starter-test-user"
    monkeypatch.setattr(server_deps, "auth_user", fake_auth_user)
    monkeypatch.setattr(mcp_http_mod, "auth_user", fake_auth_user)
    monkeypatch.setattr(server_deps, "db_get_subscription", lambda username: fake_sub)
    monkeypatch.setattr(market_billing, "db_get_subscription", lambda username: fake_sub)


@pytest.mark.parametrize(
    "tool_name,args",
    [
        ("market_receipts", {}),
        ("market_quality_scores", {}),
        ("market_quality_flagged", {}),
        ("market_dispersion", {}),
        ("market_coverage_matrix", {}),
        ("market_prices", {}),
        ("market_basket_snapshot", {}),
        ("market_basket_stress", {}),
        ("market_commerce_pulse", {}),
        ("market_price_forecast", {"product": "leche"}),
        ("market_arbitrage", {"product": "leche", "countries": "PE,MX"}),
    ],
)
def test_pre_check_tier_rejects_starter_for_pro_tools_before_hitting_backend(monkeypatch, tool_name, args):
    _patch_starter_tier(monkeypatch)
    mock_get = AsyncMock()
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call(tool_name, args), headers={"Authorization": "Bearer sk-fake-starter"})

    assert r.status_code == 200
    result = r.json()["result"]
    assert result["isError"] is True
    assert "Pro" in result["content"][0]["text"]
    mock_get.assert_not_called()


def test_pre_check_tier_rejects_starter_for_procurement_bulk_with_enterprise_message(monkeypatch):
    _patch_starter_tier(monkeypatch)
    mock_post = AsyncMock()
    with patch("httpx.AsyncClient.post", mock_post):
        r = client.post(
            "/mcp",
            json=_rpc_call("market_procurement_bulk", {"lines": [{"sku_query": "arroz"}]}),
            headers={"Authorization": "Bearer sk-fake-starter"},
        )

    assert r.status_code == 200
    result = r.json()["result"]
    assert result["isError"] is True
    assert "Enterprise" in result["content"][0]["text"]
    mock_post.assert_not_called()


def test_wave6_and_brand_monitor_tools_listed_and_gated_pro():
    from routers.mcp_http import _PRO_TOOLS, _TOOLS

    new_tools = {
        "market_prices",
        "market_basket_snapshot",
        "market_brand_monitor",
        "market_brand_monitor_promos",
        "market_brand_monitor_config",
        "market_brand_monitor_alerts",
    }
    names = {t["name"] for t in _TOOLS}
    assert new_tools <= names
    assert new_tools <= _PRO_TOOLS


# ── Full tier-gating audit fix (2026-07-27) ──────────────────────────────────
#
# A full audit of all 65 tools found 16 labeled [Pro]/[Starter] whose backend
# endpoint didn't actually enforce it (aspirational label only). 9 are backed
# by cli-market-core (fixed via _PRE_CHECK_TIER, same as wave 5/6); 7 are
# world-native (fixed at the source with require_pro in their own router).

@pytest.mark.parametrize(
    "tool_name,args",
    [
        ("market_optimize_purchase", {"items": [{"name": "leche", "qty": 1}]}),
        ("market_procurement_signal", {}),
        ("market_price_risk", {}),
        ("market_informal_signal", {"country": "PE"}),
        ("market_promo_detector", {"product": "leche"}),
        ("market_retailer_scorecard", {"store": "wong_pe"}),
        ("market_ecosystem_radar", {}),
        ("market_household_update", {"payload": {"size": 1}}),
    ],
)
def test_audit_fix_pre_check_rejects_starter_for_pro_tools(monkeypatch, tool_name, args):
    _patch_starter_tier(monkeypatch)
    mock = AsyncMock()
    with patch("httpx.AsyncClient.get", mock), patch("httpx.AsyncClient.post", mock):
        r = client.post("/mcp", json=_rpc_call(tool_name, args), headers={"Authorization": "Bearer sk-fake-starter"})

    assert r.status_code == 200
    result = r.json()["result"]
    assert result["isError"] is True
    assert "Pro" in result["content"][0]["text"]
    mock.assert_not_called()


def test_audit_fix_household_get_accepts_starter_rejects_free(monkeypatch):
    import market_billing
    import routers.mcp_http as mcp_http_mod

    fake_auth_user = lambda token: "starter-test-user"
    monkeypatch.setattr(server_deps, "auth_user", fake_auth_user)
    monkeypatch.setattr(mcp_http_mod, "auth_user", fake_auth_user)

    # Free tier -> rejected
    monkeypatch.setattr(server_deps, "db_get_subscription", lambda u: {"tier": "free", "req_limit_min": -1, "req_limit_day": -1})
    monkeypatch.setattr(market_billing, "db_get_subscription", lambda u: {"tier": "free", "req_limit_min": -1, "req_limit_day": -1})
    mock_get = AsyncMock()
    with patch("httpx.AsyncClient.get", mock_get):
        r = client.post("/mcp", json=_rpc_call("market_household_get", {}), headers={"Authorization": "Bearer sk-fake"})
    result = r.json()["result"]
    assert result["isError"] is True
    assert "Starter" in result["content"][0]["text"]
    mock_get.assert_not_called()

    # Starter tier -> allowed through to the (mocked) backend call
    monkeypatch.setattr(server_deps, "db_get_subscription", lambda u: {"tier": "starter", "req_limit_min": -1, "req_limit_day": -1})
    monkeypatch.setattr(market_billing, "db_get_subscription", lambda u: {"tier": "starter", "req_limit_min": -1, "req_limit_day": -1})
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"ok": True}
    mock_get2 = AsyncMock(return_value=fake_resp)
    with patch("httpx.AsyncClient.get", mock_get2):
        r = client.post("/mcp", json=_rpc_call("market_household_get", {}), headers={"Authorization": "Bearer sk-fake"})
    result = r.json()["result"]
    assert "isError" not in result
    mock_get2.assert_called_once()


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("post", "/agent/ask", {"prompt": "buy milk"}),
        ("post", "/cart/add", {"product_id": "x", "name": "x", "price": 1, "store": "wong_pe", "quantity": 1}),
        ("get", "/cart", None),
        ("put", "/cart/update", {"product_id": "x", "quantity": 1}),
        ("post", "/favorites", {"action": "list"}),
        ("get", "/orders", None),
        ("post", "/v1/basket/compare", {"items": [{"name": "leche", "qty": 1}]}),
    ],
)
def test_audit_fix_world_native_endpoints_now_require_pro(monkeypatch, method, path, body):
    """These 7 endpoints are cli-market-world's own routers, fixed directly
    at the source (require_pro) rather than via _pre_check_tier -- test them
    directly (not through /mcp, which just proxies bytes to production over
    the network regardless of local code changes) to verify the real
    dependency injection now rejects a genuine Starter-tier account."""
    import market_billing

    market_billing.db_set_subscription("starter-world-native-user", "starter")
    monkeypatch.setattr(server_deps, "auth_user", lambda token: "starter-world-native-user")

    kwargs = {"headers": {"Authorization": "Bearer sk-fake-starter-world-native"}}
    if body is not None:
        kwargs["json"] = body
    r = getattr(client, method)(path, **kwargs)
    assert r.status_code == 403


def test_all_tools_have_dispatch_and_all_dispatch_branches_are_registered():
    """Every _TOOLS entry must resolve in _call_tool (no 'Unknown tool'), and
    every dispatch branch must correspond to a registered tool — catches
    drift between the schema list and the dispatch table in either direction."""
    import inspect

    from routers.mcp_http import _TOOLS, _call_tool

    tool_names = {t["name"] for t in _TOOLS}
    src = inspect.getsource(_call_tool)
    dispatch_names = set(__import__("re").findall(r'name == "(\w+)"', src))

    assert tool_names == dispatch_names, (
        f"In _TOOLS but not dispatched: {tool_names - dispatch_names}; "
        f"Dispatched but not in _TOOLS: {dispatch_names - tool_names}"
    )
