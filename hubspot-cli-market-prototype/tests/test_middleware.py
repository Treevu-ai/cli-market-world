"""
Tests de integración del middleware FastAPI — sin red real.
Mockea CLIMarketIntelClient y HubSpotClient.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.hubspot_middleware import app


# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_MARKET_SUMMARY = {
    "country": "PE",
    "brief": {"shelf_signal": "neutral", "headline": "Estable"},
    "scores": {"scores": {"retail_aggression": 60.0, "price_fairness": 75.0, "basket_stress": 0.3}},
    "inflation": {"rpv": 0.5},
}

MOCK_PROCUREMENT = {"signal": "monitor"}
MOCK_PRICE_RISK = {"risk_level": "low"}


@pytest.fixture
def client():
    return TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

def test_root_returns_service_info(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "HubSpot + CLI Market Integration"
    assert data["status"] == "running"


def test_health_both_down_returns_degraded(client):
    with patch("src.hubspot_middleware.cli_market") as mock_cli, \
         patch("src.hubspot_middleware.hubspot") as mock_hs:
        mock_cli.health_check = AsyncMock(return_value=False)
        mock_hs.health_check = AsyncMock(return_value=False)
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "degraded"


# ── Webhook ───────────────────────────────────────────────────────────────────

def test_webhook_contact_creation_scheduled(client):
    payload = [{
        "subscriptionType": "contact.creation",
        "eventId": "evt-001",
        "objectId": "12345",
        "changeSource": "EXTERNAL",
        "occurredAt": 1659263400,
        "attemptNumber": 1,
    }]
    with patch("src.hubspot_middleware.enrich_contact", new_callable=AsyncMock):
        r = client.post("/webhook/hubspot", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["count"] == 1
    assert data["scheduled"][0]["type"] == "contact_enrichment"


def test_webhook_deal_creation_scheduled(client):
    payload = [{
        "subscriptionType": "deal.creation",
        "eventId": "evt-002",
        "objectId": "67890",
        "changeSource": "EXTERNAL",
        "occurredAt": 1659263400,
        "attemptNumber": 1,
    }]
    with patch("src.hubspot_middleware.enrich_deal", new_callable=AsyncMock):
        r = client.post("/webhook/hubspot", json=payload)
    assert r.status_code == 200
    assert r.json()["scheduled"][0]["type"] == "deal_enrichment"


def test_webhook_skips_our_own_property_changes(client):
    """Si HubSpot nos notifica que cambiamos market_basket_stress, no re-encolamos."""
    payload = [{
        "subscriptionType": "contact.propertyChange",
        "eventId": "evt-003",
        "objectId": "12345",
        "propertyName": "market_basket_stress",
        "propertyValue": "0.45",
        "occurredAt": 1659263400,
        "attemptNumber": 1,
    }]
    r = client.post("/webhook/hubspot", json=payload)
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_webhook_empty_array(client):
    r = client.post("/webhook/hubspot", json=[])
    assert r.status_code == 200
    assert r.json()["count"] == 0


# ── Market intelligence endpoint ──────────────────────────────────────────────

def test_market_intelligence_returns_structure(client):
    with patch("src.hubspot_middleware.cli_market") as mock_cli:
        mock_cli.get_market_summary = AsyncMock(return_value=MOCK_MARKET_SUMMARY)
        mock_cli.get_macro = AsyncMock(return_value={"usd_pen": 3.75})
        r = client.get("/api/market-intelligence?country=PE")
    assert r.status_code == 200
    data = r.json()
    assert data["country"] == "PE"
    assert "brief" in data
    assert "scores" in data


# ── Manual enrichment endpoints ───────────────────────────────────────────────

def test_manual_enrich_contact(client):
    with patch("src.hubspot_middleware.cli_market") as mock_cli, \
         patch("src.hubspot_middleware.hubspot") as mock_hs:
        mock_cli.get_market_summary = AsyncMock(return_value=MOCK_MARKET_SUMMARY)
        mock_hs.get_contact = AsyncMock(return_value={"properties": {"region": "PE"}})
        mock_hs.update_contact_properties = AsyncMock(return_value={"status": "updated"})

        r = client.post("/api/enrich-contact/12345")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "enriched"
    assert data["contact_id"] == "12345"
    assert "market_basket_stress" in data["properties_written"]


def test_manual_enrich_deal(client):
    with patch("src.hubspot_middleware.cli_market") as mock_cli, \
         patch("src.hubspot_middleware.hubspot") as mock_hs:
        mock_cli.get_procurement_signal = AsyncMock(return_value=MOCK_PROCUREMENT)
        mock_cli.get_price_risk = AsyncMock(return_value=MOCK_PRICE_RISK)
        mock_hs.get_deal = AsyncMock(return_value={"properties": {"dealname": "Test Deal"}})
        mock_hs.update_deal_properties = AsyncMock(return_value={"status": "updated"})

        r = client.post("/api/enrich-deal/67890")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "enriched"
    assert data["deal_id"] == "67890"
    assert "procurement_signal" in data["properties_written"]
