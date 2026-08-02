"""
HubSpot + CLI Market Middleware — FastAPI.

Endpoints:
  POST /webhook/hubspot              Webhook principal de HubSpot
  POST /api/enrich-contact/{id}      Enriquecimiento manual de contacto
  POST /api/enrich-deal/{id}         Enriquecimiento manual de deal
  GET  /api/market-intelligence      Resumen de inteligencia de mercado
  GET  /api/setup-properties         Crea custom properties en HubSpot (idempotente)
  GET  /health                       Health check (CLI Market + HubSpot)
  GET  /                             Root info
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import asyncio
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

from src.cli_market_intel_client import CLIMarketIntelClient
from src.hubspot_client import HubSpotClient
from src.enrichment import (
    build_contact_market_properties,
    build_deal_market_properties,
    compute_lead_score_delta,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HubSpot + CLI Market Integration",
    version="1.0.0",
    description="Middleware: enriquece contactos y deals de HubSpot con inteligencia de góndola de CLI Market",
)

cli_market = CLIMarketIntelClient()
hubspot = HubSpotClient()

HUBSPOT_WEBHOOK_SECRET = os.getenv("HUBSPOT_WEBHOOK_SECRET", "")


# ── Webhook auth ──────────────────────────────────────────────────────────────

def _check_webhook_auth(request: Request) -> None:
    """Opcional: exige X-HubSpot-Signature si HUBSPOT_WEBHOOK_SECRET está seteado."""
    if not HUBSPOT_WEBHOOK_SECRET:
        return
    sig = request.headers.get("X-HubSpot-Signature") or ""
    if sig != HUBSPOT_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


# ── Models ─────────────────────────────────────────────────────────────────────

class HubSpotWebhookEvent(BaseModel):
    subscriptionType: str
    eventId: str | int | None = None
    objectId: str | int
    changeSource: str | None = None
    occurredAt: int | None = None
    attemptNumber: int | None = None
    propertyName: str | None = None
    propertyValue: str | None = None


# ── Background tasks ──────────────────────────────────────────────────────────

async def enrich_contact(contact_id: str) -> dict[str, Any]:
    """
    Fetch contact + market summary → compute properties → PATCH HubSpot.
    Usado como background task desde el webhook y como acción directa.
    """
    contact_id = str(contact_id)
    logger.info("Enriching contact %s", contact_id)

    # Fetch en paralelo: datos del contacto + market summary
    contact_props_to_read = ["region", "income_level", "family_size", "country"]
    contact_data, market_summary = await asyncio.gather(
        hubspot.get_contact(contact_id, properties=contact_props_to_read),
        cli_market.get_market_summary(),
        return_exceptions=True,
    )

    if isinstance(contact_data, Exception):
        logger.error("Error fetching contact %s: %s", contact_id, contact_data)
        contact_data = {}
    if isinstance(market_summary, Exception):
        logger.error("Error fetching market summary: %s", market_summary)
        market_summary = {}

    if contact_data.get("error"):
        logger.warning("Contact %s fetch error: %s", contact_id, contact_data["error"])

    props = build_contact_market_properties(market_summary, contact_data)
    score_delta = compute_lead_score_delta(props)

    result = await hubspot.update_contact_properties(contact_id, props)
    logger.info(
        "Contact %s enriched — basket_stress=%s score_delta=%d",
        contact_id, props.get("market_basket_stress"), score_delta,
    )
    return {"contact_id": contact_id, "properties_written": list(props.keys()), "score_delta": score_delta, "hubspot_result": result}


async def enrich_deal(deal_id: str) -> dict[str, Any]:
    """
    Fetch deal + Pro signals → compute properties → PATCH HubSpot.
    Si el tier no es Pro, escribe valores degradados (no lanza excepción).
    """
    deal_id = str(deal_id)
    logger.info("Enriching deal %s", deal_id)

    deal_data, procurement, price_risk = await asyncio.gather(
        hubspot.get_deal(deal_id, properties=["dealname", "products", "amount", "region"]),
        cli_market.get_procurement_signal(),
        cli_market.get_price_risk(),
        return_exceptions=True,
    )

    if isinstance(deal_data, Exception):
        logger.error("Error fetching deal %s: %s", deal_id, deal_data)
        deal_data = {}
    if isinstance(procurement, Exception):
        procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception):
        price_risk = {"error": str(price_risk)}

    props = build_deal_market_properties(procurement, price_risk)
    result = await hubspot.update_deal_properties(deal_id, props)
    logger.info("Deal %s enriched — signal=%s risk=%s", deal_id, props.get("procurement_signal"), props.get("price_risk_level"))
    return {"deal_id": deal_id, "properties_written": list(props.keys()), "hubspot_result": result}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "HubSpot + CLI Market Integration",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health_check():
    cli_ok, hs_ok = await asyncio.gather(
        cli_market.health_check(),
        hubspot.health_check(),
        return_exceptions=False,
    )
    overall = "healthy" if (cli_ok and hs_ok) else "degraded"
    return {
        "status": overall,
        "cli_market_api": cli_ok,
        "hubspot_api": hs_ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/webhook/hubspot")
async def hubspot_webhook(
    events: list[HubSpotWebhookEvent],
    background_tasks: BackgroundTasks,
    request: Request,
):
    """
    HubSpot envía un array de eventos. Procesamos cada uno.
    Suscripciones relevantes:
      contact.creation, contact.propertyChange
      deal.creation, deal.propertyChange
    """
    _check_webhook_auth(request)
    scheduled: list[dict[str, Any]] = []

    for event in events:
        etype = event.subscriptionType.lower()
        oid = str(event.objectId)

        if "contact" in etype:
            # No re-encolar si la propiedad que cambió es una de las que nosotros escribimos
            if event.propertyName and event.propertyName.startswith("market_"):
                continue
            background_tasks.add_task(enrich_contact, oid)
            scheduled.append({"type": "contact_enrichment", "object_id": oid})

        elif "deal" in etype:
            if event.propertyName and event.propertyName in ("price_risk_level", "procurement_signal"):
                continue
            background_tasks.add_task(enrich_deal, oid)
            scheduled.append({"type": "deal_enrichment", "object_id": oid})

    return {
        "status": "accepted",
        "scheduled": scheduled,
        "count": len(scheduled),
    }


@app.post("/api/enrich-contact/{contact_id}")
async def manual_enrich_contact(contact_id: str):
    """Enriquecimiento manual de un contacto. Útil para backfill."""
    result = await enrich_contact(contact_id)
    return {"status": "enriched", **result}


@app.post("/api/enrich-deal/{deal_id}")
async def manual_enrich_deal(deal_id: str):
    """Enriquecimiento manual de un deal."""
    result = await enrich_deal(deal_id)
    return {"status": "enriched", **result}


@app.get("/api/market-intelligence")
async def market_intelligence_summary(country: str = "PE"):
    """
    Resumen de inteligencia de mercado en tiempo real.
    Incluye brief + scores + inflation (tier libre).
    Nota: procurement_signal y price_risk requieren Pro.
    """
    summary, macro = await asyncio.gather(
        cli_market.get_market_summary(country=country),
        cli_market.get_macro(country=country),
        return_exceptions=False,
    )
    return {
        "country": country,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **summary,
        "macro": macro,
    }


@app.get("/api/market-intelligence/pro-signals")
async def pro_signals(country: str = "PE"):
    """Señales Pro: procurement_signal + price_risk. Requiere CLI Market Pro."""
    procurement, price_risk = await asyncio.gather(
        cli_market.get_procurement_signal(country=country),
        cli_market.get_price_risk(country=country),
        return_exceptions=False,
    )
    return {
        "country": country,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "procurement_signal": procurement,
        "price_risk": price_risk,
    }


@app.get("/api/setup-properties")
async def setup_hubspot_properties():
    """
    Crea las custom properties de CLI Market en HubSpot (idempotente).
    Ejecutar una sola vez antes de que empiece el enriquecimiento.
    """
    contact_defs = [
        ("market_basket_stress", "Market Basket Stress", "number", "number"),
        ("market_inflation_signal", "Market Inflation Signal", "text", "string"),
        ("market_price_fairness", "Market Price Fairness", "number", "number"),
        ("market_retail_aggression", "Market Retail Aggression", "number", "number"),
        ("market_data_updated", "Market Data Updated", "text", "string"),
    ]
    deal_defs = [
        ("price_risk_level", "Price Risk Level", "text", "string"),
        ("procurement_signal", "Procurement Signal", "text", "string"),
        ("market_recommended_action", "Market Recommended Action", "text", "string"),
        ("price_intelligence_updated", "Price Intelligence Updated", "text", "string"),
    ]

    results: dict[str, Any] = {"contacts": {}, "deals": {}}

    for name, label, ftype, ptype in contact_defs:
        ok = await hubspot.ensure_contact_property(name, label, ftype, ptype)
        results["contacts"][name] = "ok" if ok else "error"

    for name, label, ftype, ptype in deal_defs:
        ok = await hubspot.ensure_deal_property(name, label, ftype, ptype)
        results["deals"][name] = "ok" if ok else "error"

    return {"status": "setup_complete", "properties": results}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    uvicorn.run("src.hubspot_middleware:app", host=host, port=port, reload=True)
