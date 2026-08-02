"""
Tests de integración del middleware FastAPI de Zoho.
Mockea ZohoCRMClient y CLIMarketIntelClient — sin red.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.zoho_middleware import app

# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_MARKET_SUMMARY = {
    "country": "PE",
    "brief": {"shelf_signal": "neutral"},
    "scores": {"scores": {"retail_aggression": 60.0, "price_fairness": 75.0, "basket_stress": 0.2}},
    "inflation": {"rpv": 0.5},
}

MOCK_LEAD = {"data": [{"Lead_Score": 60, "Region": "PE"}]}
MOCK_DEAL = {"data": [{"Deal_Name": "Test Deal", "Products": "arroz, aceite"}]}
MOCK_PRODUCT = {
    "data": [{
        "Product_Name": "Arroz 1kg",
        "Quantity_In_Stock": 50,
        "Lead_Time": 7,
        "Daily_Demand": 20,
    }]
}
MOCK_PROCUREMENT = {"signal": "buy_now"}
MOCK_PRICE_RISK = {"risk_level": "moderate"}
MOCK_ZOHO_UPDATE = {"data": [{"code": "SUCCESS"}]}


client = TestClient(app)


# ── Root / health ─────────────────────────────────────────────────────────────

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "Zoho CRM + CLI Market Integration"
    assert r.json()["status"] == "running"


def test_health_both_down_returns_degraded():
    with patch("src.zoho_middleware.cli_market") as mock_cli, \
         patch("src.zoho_middleware.zoho") as mock_zoho:
        mock_cli.health_check = AsyncMock(return_value=False)
        mock_zoho.health_check = AsyncMock(return_value=False)
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "degraded"


def test_health_both_up_returns_healthy():
    with patch("src.zoho_middleware.cli_market") as mock_cli, \
         patch("src.zoho_middleware.zoho") as mock_zoho:
        mock_cli.health_check = AsyncMock(return_value=True)
        mock_zoho.health_check = AsyncMock(return_value=True)
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# ── Webhook ───────────────────────────────────────────────────────────────────

def test_webhook_lead_create_schedules_enrichment():
    payload = {"module": "Leads", "record_id": "lead-001", "operation": "create"}
    with patch("src.zoho_middleware.enrich_lead", new_callable=AsyncMock):
        r = client.post("/webhook/zoho", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "lead_enrichment_scheduled"
    assert r.json()["record_id"] == "lead-001"


def test_webhook_deal_create_schedules_enrichment():
    payload = {"module": "Deals", "record_id": "deal-002", "operation": "create"}
    with patch("src.zoho_middleware.enrich_deal", new_callable=AsyncMock):
        r = client.post("/webhook/zoho", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "deal_enrichment_scheduled"


def test_webhook_product_update_schedules_optimization():
    payload = {"module": "Products", "record_id": "prod-003", "operation": "update"}
    with patch("src.zoho_middleware.optimize_inventory", new_callable=AsyncMock):
        r = client.post("/webhook/zoho", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "inventory_optimization_scheduled"


def test_webhook_unknown_module_no_action():
    payload = {"module": "Accounts", "record_id": "acc-999", "operation": "create"}
    r = client.post("/webhook/zoho", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "no_action_required"


def test_webhook_delete_operation_no_action():
    payload = {"module": "Leads", "record_id": "lead-del", "operation": "delete"}
    r = client.post("/webhook/zoho", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "no_action_required"


# ── Manual enrich lead ────────────────────────────────────────────────────────

def test_manual_enrich_lead():
    with patch("src.zoho_middleware.cli_market") as mock_cli, \
         patch("src.zoho_middleware.zoho") as mock_zoho:
        mock_cli.get_market_summary = AsyncMock(return_value=MOCK_MARKET_SUMMARY)
        mock_zoho.get_record = AsyncMock(return_value=MOCK_LEAD)
        mock_zoho.update_record = AsyncMock(return_value=MOCK_ZOHO_UPDATE)
        r = client.post("/api/enrich-lead/lead-001")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "enriched"
    assert data["lead_id"] == "lead-001"
    assert "Market_Score" in data["fields_written"]
    assert "Market_Data_Updated" in data["fields_written"]


# ── Manual enrich deal ────────────────────────────────────────────────────────

def test_manual_enrich_deal():
    with patch("src.zoho_middleware.cli_market") as mock_cli, \
         patch("src.zoho_middleware.zoho") as mock_zoho:
        mock_cli.get_procurement_signal = AsyncMock(return_value=MOCK_PROCUREMENT)
        mock_cli.get_price_risk = AsyncMock(return_value=MOCK_PRICE_RISK)
        mock_zoho.get_record = AsyncMock(return_value=MOCK_DEAL)
        mock_zoho.update_record = AsyncMock(return_value=MOCK_ZOHO_UPDATE)
        r = client.post("/api/enrich-deal/deal-002")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "enriched"
    assert data["deal_id"] == "deal-002"
    assert "Procurement_Signal" in data["fields_written"]
    assert "Price_Risk_Level" in data["fields_written"]


# ── Manual optimize inventory ─────────────────────────────────────────────────

def test_manual_optimize_inventory():
    with patch("src.zoho_middleware.cli_market") as mock_cli, \
         patch("src.zoho_middleware.zoho") as mock_zoho:
        mock_cli.get_procurement_signal = AsyncMock(return_value=MOCK_PROCUREMENT)
        mock_cli.get_price_risk = AsyncMock(return_value=MOCK_PRICE_RISK)
        mock_zoho.get_record = AsyncMock(return_value=MOCK_PRODUCT)
        mock_zoho.update_record = AsyncMock(return_value=MOCK_ZOHO_UPDATE)
        r = client.post("/api/optimize-inventory/prod-003")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "optimized"
    assert data["product_id"] == "prod-003"
    assert "Recommended_Stock" in data["fields_written"]


# ── Market intelligence ───────────────────────────────────────────────────────

def test_market_intelligence_endpoint():
    with patch("src.zoho_middleware.cli_market") as mock_cli:
        mock_cli.get_market_summary = AsyncMock(return_value=MOCK_MARKET_SUMMARY)
        mock_cli.get_macro = AsyncMock(return_value={"usd_pen": 3.75})
        r = client.get("/api/market-intelligence?country=PE")
    assert r.status_code == 200
    data = r.json()
    assert data["country"] == "PE"
    assert "brief" in data
    assert "scores" in data
    assert "macro" in data


def test_market_intelligence_pro_endpoint():
    with patch("src.zoho_middleware.cli_market") as mock_cli:
        mock_cli.get_procurement_signal = AsyncMock(return_value=MOCK_PROCUREMENT)
        mock_cli.get_price_risk = AsyncMock(return_value=MOCK_PRICE_RISK)
        r = client.get("/api/market-intelligence/pro?country=PE")
    assert r.status_code == 200
    data = r.json()
    assert "procurement_signal" in data
    assert "price_risk" in data


# ── Basket optimize ───────────────────────────────────────────────────────────

def test_basket_optimize_valid():
    with patch("src.zoho_middleware.cli_market") as mock_cli:
        mock_cli.optimize_basket = AsyncMock(return_value={"recommendations": []})
        r = client.get("/api/basket-optimize?products=leche,arroz,aceite")
    assert r.status_code == 200
    data = r.json()
    assert data["products"] == ["leche", "arroz", "aceite"]


def test_basket_optimize_empty_returns_400():
    r = client.get("/api/basket-optimize?products=")
    assert r.status_code == 400
