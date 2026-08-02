"""HubSpot adapter — FastAPI app. Imports from package instead of prototype."""
from __future__ import annotations
import asyncio, logging, os
from datetime import datetime, timezone
from typing import Any
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

from cli_market_integrations.shared.intel_client import CLIMarketIntelClient
from cli_market_integrations.adapters.hubspot.hubspot_client import HubSpotClient
from cli_market_integrations.adapters.hubspot.enrichment import (
    build_contact_market_properties, build_deal_market_properties, compute_lead_score_delta
)

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="HubSpot + CLI Market", version="0.1.0", description="Enrich HubSpot contacts and deals with CLI Market price intelligence")

cli_market = CLIMarketIntelClient()
hubspot = HubSpotClient()
WEBHOOK_SECRET = os.getenv("HUBSPOT_WEBHOOK_SECRET", "")


def _check_auth(request: Request) -> None:
    if not WEBHOOK_SECRET: return
    if (request.headers.get("X-HubSpot-Signature") or "") != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


class HubSpotWebhookEvent(BaseModel):
    subscriptionType: str
    eventId: str | int | None = None
    objectId: str | int
    changeSource: str | None = None
    occurredAt: int | None = None
    attemptNumber: int | None = None
    propertyName: str | None = None
    propertyValue: str | None = None


async def enrich_contact(contact_id: str) -> dict[str, Any]:
    contact_id = str(contact_id)
    contact_data, market_summary = await asyncio.gather(
        hubspot.get_contact(contact_id, properties=["region","income_level","family_size","country"]),
        cli_market.get_market_summary(),
        return_exceptions=True,
    )
    if isinstance(contact_data, Exception): contact_data = {}
    if isinstance(market_summary, Exception): market_summary = {}
    props = build_contact_market_properties(market_summary, contact_data)
    score_delta = compute_lead_score_delta(props)
    result = await hubspot.update_contact_properties(contact_id, props)
    return {"contact_id": contact_id, "properties_written": list(props.keys()), "score_delta": score_delta, "hubspot_result": result}


async def enrich_deal(deal_id: str) -> dict[str, Any]:
    deal_id = str(deal_id)
    deal_data, procurement, price_risk = await asyncio.gather(
        hubspot.get_deal(deal_id, properties=["dealname","products","amount","region"]),
        cli_market.get_procurement_signal(), cli_market.get_price_risk(),
        return_exceptions=True,
    )
    if isinstance(deal_data, Exception): deal_data = {}
    if isinstance(procurement, Exception): procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception): price_risk = {"error": str(price_risk)}
    props = build_deal_market_properties(procurement, price_risk)
    result = await hubspot.update_deal_properties(deal_id, props)
    return {"deal_id": deal_id, "properties_written": list(props.keys()), "hubspot_result": result}


@app.get("/")
async def root():
    return {"service": "HubSpot + CLI Market", "version": "0.1.0", "status": "running", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health")
async def health():
    cli_ok, hs_ok = await asyncio.gather(cli_market.health_check(), hubspot.health_check())
    return {"status": "healthy" if (cli_ok and hs_ok) else "degraded", "cli_market_api": cli_ok, "hubspot_api": hs_ok, "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/webhook/hubspot")
async def webhook(events: list[HubSpotWebhookEvent], background_tasks: BackgroundTasks, request: Request):
    _check_auth(request)
    scheduled = []
    for event in events:
        etype, oid = event.subscriptionType.lower(), str(event.objectId)
        if "contact" in etype:
            if event.propertyName and event.propertyName.startswith("market_"): continue
            background_tasks.add_task(enrich_contact, oid); scheduled.append({"type": "contact_enrichment", "object_id": oid})
        elif "deal" in etype:
            if event.propertyName and event.propertyName in ("price_risk_level", "procurement_signal"): continue
            background_tasks.add_task(enrich_deal, oid); scheduled.append({"type": "deal_enrichment", "object_id": oid})
    return {"status": "accepted", "scheduled": scheduled, "count": len(scheduled)}

@app.post("/api/enrich-contact/{contact_id}")
async def manual_enrich_contact(contact_id: str):
    return {"status": "enriched", **(await enrich_contact(contact_id))}

@app.post("/api/enrich-deal/{deal_id}")
async def manual_enrich_deal(deal_id: str):
    return {"status": "enriched", **(await enrich_deal(deal_id))}

@app.get("/api/market-intelligence")
async def market_intelligence(country: str = "PE"):
    summary, macro = await asyncio.gather(cli_market.get_market_summary(country=country), cli_market.get_macro(country=country))
    return {"country": country, "timestamp": datetime.now(timezone.utc).isoformat(), **summary, "macro": macro}

@app.get("/api/market-intelligence/pro-signals")
async def pro_signals(country: str = "PE"):
    procurement, price_risk = await asyncio.gather(cli_market.get_procurement_signal(country=country), cli_market.get_price_risk(country=country))
    return {"country": country, "timestamp": datetime.now(timezone.utc).isoformat(), "procurement_signal": procurement, "price_risk": price_risk}

@app.get("/api/setup-properties")
async def setup_properties():
    contact_defs = [("market_basket_stress","Market Basket Stress","number","number"),("market_inflation_signal","Market Inflation Signal","text","string"),("market_price_fairness","Market Price Fairness","number","number"),("market_retail_aggression","Market Retail Aggression","number","number"),("market_data_updated","Market Data Updated","text","string")]
    deal_defs = [("price_risk_level","Price Risk Level","text","string"),("procurement_signal","Procurement Signal","text","string"),("market_recommended_action","Market Recommended Action","text","string"),("price_intelligence_updated","Price Intelligence Updated","text","string")]
    results: dict[str, Any] = {"contacts": {}, "deals": {}}
    for name, label, ft, pt in contact_defs: results["contacts"][name] = "ok" if await hubspot.ensure_contact_property(name, label, ft, pt) else "error"
    for name, label, ft, pt in deal_defs: results["deals"][name] = "ok" if await hubspot.ensure_deal_property(name, label, ft, pt) else "error"
    return {"status": "setup_complete", "properties": results}
