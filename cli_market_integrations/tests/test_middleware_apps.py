"""
Integration tests for HubSpot, Zoho and Kommo FastAPI apps.
No real network calls — all CRM and CLI Market clients are mocked.
"""
from __future__ import annotations
import os
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# ── HubSpot ───────────────────────────────────────────────────────────────────

from cli_market_integrations.adapters.hubspot.app import app as hs_app

hs = TestClient(hs_app)

MOCK_SUMMARY = {
    "country": "PE",
    "brief": {"shelf_signal": "neutral"},
    "scores": {"scores": {"retail_aggression": 60.0, "price_fairness": 75.0, "basket_stress": 0.2}},
    "inflation": {},
}
MOCK_PROCUREMENT = {"signal": "buy_now"}
MOCK_RISK = {"risk_level": "moderate"}


class TestHubSpotApp:
    def test_root(self):
        r = hs.get("/")
        assert r.status_code == 200
        assert r.json()["service"] == "HubSpot + CLI Market"

    def test_health_degraded(self):
        with patch("cli_market_integrations.adapters.hubspot.app.cli_market") as m_cli, \
             patch("cli_market_integrations.adapters.hubspot.app.hubspot") as m_hs:
            m_cli.health_check = AsyncMock(return_value=False)
            m_hs.health_check = AsyncMock(return_value=False)
            r = hs.get("/health")
        assert r.json()["status"] == "degraded"

    def test_webhook_contact_creation(self):
        payload = [{"subscriptionType": "contact.creation", "objectId": "100", "occurredAt": 0, "attemptNumber": 1}]
        with patch("cli_market_integrations.adapters.hubspot.app.enrich_contact", new_callable=AsyncMock):
            r = hs.post("/webhook/hubspot", json=payload)
        assert r.status_code == 200
        assert r.json()["count"] == 1

    def test_webhook_skips_market_prop_change(self):
        payload = [{"subscriptionType": "contact.propertyChange", "objectId": "100", "propertyName": "market_basket_stress", "occurredAt": 0, "attemptNumber": 1}]
        r = hs.post("/webhook/hubspot", json=payload)
        assert r.json()["count"] == 0

    def test_webhook_empty(self):
        r = hs.post("/webhook/hubspot", json=[])
        assert r.json()["count"] == 0

    def test_manual_enrich_contact(self):
        with patch("cli_market_integrations.adapters.hubspot.app.cli_market") as m_cli, \
             patch("cli_market_integrations.adapters.hubspot.app.hubspot") as m_hs:
            m_cli.get_market_summary = AsyncMock(return_value=MOCK_SUMMARY)
            m_hs.get_contact = AsyncMock(return_value={"properties": {"region": "PE"}})
            m_hs.update_contact_properties = AsyncMock(return_value={"status": "updated"})
            r = hs.post("/api/enrich-contact/100")
        assert r.status_code == 200
        assert r.json()["status"] == "enriched"

    def test_manual_enrich_deal(self):
        with patch("cli_market_integrations.adapters.hubspot.app.cli_market") as m_cli, \
             patch("cli_market_integrations.adapters.hubspot.app.hubspot") as m_hs:
            m_cli.get_procurement_signal = AsyncMock(return_value=MOCK_PROCUREMENT)
            m_cli.get_price_risk = AsyncMock(return_value=MOCK_RISK)
            m_hs.get_deal = AsyncMock(return_value={})
            m_hs.update_deal_properties = AsyncMock(return_value={})
            r = hs.post("/api/enrich-deal/200")
        assert r.status_code == 200
        assert r.json()["status"] == "enriched"


class TestHubSpotRecentDeals:
    """GET /api/crm/deals/recent — private endpoint, X-CRM-Api-Key required."""

    def test_missing_api_key_401(self):
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", "secret-123"):
            r = hs.get("/api/crm/deals/recent")
        assert r.status_code == 401

    def test_wrong_api_key_401(self):
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", "secret-123"):
            r = hs.get("/api/crm/deals/recent", headers={"X-CRM-Api-Key": "wrong"})
        assert r.status_code == 401

    def test_unconfigured_key_is_401_not_open(self):
        # CRM_API_KEY unset on the server must still reject, never fall open.
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", ""):
            r = hs.get("/api/crm/deals/recent", headers={"X-CRM-Api-Key": "anything"})
        assert r.status_code == 401

    def test_missing_hubspot_token_503(self):
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", "secret-123"), \
             patch("cli_market_integrations.adapters.hubspot.app.hubspot") as m_hs:
            m_hs.access_token = ""
            r = hs.get("/api/crm/deals/recent", headers={"X-CRM-Api-Key": "secret-123"})
        assert r.status_code == 503
        assert "HUBSPOT_ACCESS_TOKEN" in r.json()["detail"]

    def test_hubspot_error_503_no_token_leak(self):
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", "secret-123"), \
             patch("cli_market_integrations.adapters.hubspot.app.hubspot") as m_hs:
            m_hs.access_token = "sk-real-hubspot-token"
            m_hs.search_deals = AsyncMock(return_value={"error": "http_500"})
            r = hs.get("/api/crm/deals/recent", headers={"X-CRM-Api-Key": "secret-123"})
        assert r.status_code == 503
        assert "sk-real-hubspot-token" not in r.text

    def test_happy_path(self):
        raw = {
            "results": [
                {
                    "id": "42",
                    "properties": {
                        "dealname": "Canasta PYME Lima", "amount": "1500", "dealstage": "closedwon",
                        "pipeline": "default", "createdate": "2026-08-09T10:00:00Z", "closedate": "2026-08-10T10:00:00Z",
                    },
                }
            ]
        }
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", "secret-123"), \
             patch("cli_market_integrations.adapters.hubspot.app.HUBSPOT_PORTAL_ID", "12345"), \
             patch("cli_market_integrations.adapters.hubspot.app.hubspot") as m_hs:
            m_hs.access_token = "sk-real-hubspot-token"
            m_hs.search_deals = AsyncMock(return_value=raw)
            r = hs.get("/api/crm/deals/recent?limit=5&days=3", headers={"X-CRM-Api-Key": "secret-123"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] == 1
        deal = body["deals"][0]
        assert deal["deal_id"] == "42"
        assert deal["dealname"] == "Canasta PYME Lima"
        assert deal["hubspot_url"] == "https://app.hubspot.com/contacts/12345/deal/42"
        assert "sk-real-hubspot-token" not in r.text

    def test_limit_out_of_range_422(self):
        with patch("cli_market_integrations.adapters.hubspot.app.CRM_API_KEY", "secret-123"):
            r = hs.get("/api/crm/deals/recent?limit=101", headers={"X-CRM-Api-Key": "secret-123"})
        assert r.status_code == 422


# ── Zoho ──────────────────────────────────────────────────────────────────────

from cli_market_integrations.adapters.zoho.app import app as zoho_app

zo = TestClient(zoho_app)


class TestZohoApp:
    def test_root(self):
        r = zo.get("/")
        assert r.json()["service"] == "Zoho CRM + CLI Market"

    def test_webhook_lead_create(self):
        payload = {"module": "Leads", "record_id": "lead-1", "operation": "create"}
        with patch("cli_market_integrations.adapters.zoho.app.enrich_lead", new_callable=AsyncMock):
            r = zo.post("/webhook/zoho", json=payload)
        assert r.json()["status"] == "lead_enrichment_scheduled"

    def test_webhook_product_update(self):
        payload = {"module": "Products", "record_id": "prod-1", "operation": "update"}
        with patch("cli_market_integrations.adapters.zoho.app.optimize_inventory", new_callable=AsyncMock):
            r = zo.post("/webhook/zoho", json=payload)
        assert r.json()["status"] == "inventory_optimization_scheduled"

    def test_webhook_delete_no_action(self):
        r = zo.post("/webhook/zoho", json={"module": "Leads", "record_id": "x", "operation": "delete"})
        assert r.json()["status"] == "no_action_required"

    def test_basket_optimize_empty_400(self):
        r = zo.get("/api/basket-optimize?products=")
        assert r.status_code == 400

    def test_basket_optimize_valid(self):
        with patch("cli_market_integrations.adapters.zoho.app.cli_market") as m:
            m.optimize_basket = AsyncMock(return_value={"recommendations": []})
            r = zo.get("/api/basket-optimize?products=leche,arroz")
        assert r.status_code == 200
        assert r.json()["products"] == ["leche", "arroz"]


# ── Kommo ─────────────────────────────────────────────────────────────────────

from cli_market_integrations.adapters.kommo.app import app as kommo_app

km = TestClient(kommo_app)


class TestKommoApp:
    def test_root(self):
        r = km.get("/")
        assert r.json()["service"] == "Kommo CRM + CLI Market"

    def test_health_degraded(self):
        with patch("cli_market_integrations.adapters.kommo.app.cli_market") as m_cli, \
             patch("cli_market_integrations.adapters.kommo.app.kommo") as m_kommo:
            m_cli.health_check = AsyncMock(return_value=False)
            m_kommo.health_check = AsyncMock(return_value=False)
            r = km.get("/health")
        assert r.json()["status"] == "degraded"

    def test_webhook_form_encoded_lead_add(self):
        body = b"leads%5Badd%5D%5B0%5D%5Bid%5D=12345&leads%5Badd%5D%5B0%5D%5Bname%5D=Test"
        with patch("cli_market_integrations.adapters.kommo.app.enrich_lead", new_callable=AsyncMock), \
             patch("cli_market_integrations.adapters.kommo.app.enrich_lead_pro", new_callable=AsyncMock):
            r = km.post(
                "/webhook/kommo",
                content=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "accepted"
        assert data["scheduled"] == 1

    def test_webhook_empty_body_no_error(self):
        r = km.post("/webhook/kommo", content=b"", headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert r.status_code == 200
        assert r.json()["scheduled"] == 0

    def test_manual_enrich_lead(self):
        env = {
            "KOMMO_FIELD_BASKET_STRESS": "1001", "KOMMO_FIELD_INFLATION_SIGNAL": "1002",
            "KOMMO_FIELD_PRICE_FAIRNESS": "1003", "KOMMO_FIELD_RETAIL_AGGRESSION": "1004",
            "KOMMO_FIELD_MARKET_SCORE": "1005", "KOMMO_FIELD_PROCUREMENT": "1006",
            "KOMMO_FIELD_PRICE_RISK": "1007", "KOMMO_FIELD_DATA_UPDATED": "1008",
        }
        with patch("cli_market_integrations.adapters.kommo.app.cli_market") as m_cli, \
             patch("cli_market_integrations.adapters.kommo.app.kommo") as m_kommo, \
             patch.dict(os.environ, env):
            m_cli.get_market_summary = AsyncMock(return_value=MOCK_SUMMARY)
            m_kommo.get_lead = AsyncMock(return_value={})
            m_kommo.update_lead = AsyncMock(return_value={})
            r = km.post("/api/enrich-lead/12345")
        assert r.status_code == 200
        assert r.json()["status"] == "enriched"

    def test_market_intelligence(self):
        with patch("cli_market_integrations.adapters.kommo.app.cli_market") as m:
            m.get_market_summary = AsyncMock(return_value=MOCK_SUMMARY)
            m.get_macro = AsyncMock(return_value={"usd_pen": 3.75})
            r = km.get("/api/market-intelligence")
        assert r.status_code == 200
        assert "brief" in r.json()
