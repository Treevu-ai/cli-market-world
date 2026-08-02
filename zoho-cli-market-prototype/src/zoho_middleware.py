"""
Zoho CRM + CLI Market Middleware — FastAPI.

Endpoints:
  POST /webhook/zoho                      Webhook principal de Zoho CRM
  POST /api/enrich-lead/{id}              Enriquecimiento manual de lead
  POST /api/enrich-deal/{id}              Enriquecimiento manual de deal
  POST /api/optimize-inventory/{id}       Optimización manual de inventario
  GET  /api/market-intelligence           Resumen de inteligencia (libres)
  GET  /api/market-intelligence/pro       Señales Pro (procurement + price-risk)
  GET  /api/basket-optimize               Optimización de canasta
  GET  /health                            Health check
  GET  /                                  Root info
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

from src.cli_market_intel_client import CLIMarketIntelClient
from src.zoho_client import ZohoCRMClient
from src.enrichment import (
    build_lead_market_fields,
    build_deal_market_fields,
    build_product_market_fields,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zoho CRM + CLI Market Integration",
    version="1.0.0",
    description="Middleware: enriquece Leads, Deals y Products de Zoho con inteligencia de góndola de CLI Market",
)

cli_market = CLIMarketIntelClient()
zoho = ZohoCRMClient()

WEBHOOK_SECRET = os.getenv("ZOHO_WEBHOOK_SECRET", "")


# ── Webhook auth ──────────────────────────────────────────────────────────────

def _check_webhook_auth(request: Request) -> None:
    if not WEBHOOK_SECRET:
        return
    sig = request.headers.get("X-Zoho-Webhook-Token") or request.headers.get("X-Webhook-Secret") or ""
    if sig != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook token")


# ── Models ────────────────────────────────────────────────────────────────────

class ZohoWebhookPayload(BaseModel):
    module: str
    record_id: str
    operation: str          # create | update | delete
    trigger: str | None = None


# ── Core enrichment tasks ─────────────────────────────────────────────────────

async def enrich_lead(lead_id: str) -> dict[str, Any]:
    logger.info("Enriching lead %s", lead_id)

    lead_data, market_summary = await asyncio.gather(
        zoho.get_record("Leads", lead_id),
        cli_market.get_market_summary(),
        return_exceptions=True,
    )

    if isinstance(lead_data, Exception):
        logger.error("Error fetching lead %s: %s", lead_id, lead_data)
        lead_data = {}
    if isinstance(market_summary, Exception):
        logger.error("Error fetching market summary: %s", market_summary)
        market_summary = {}

    fields = build_lead_market_fields(market_summary, lead_data)
    result = await zoho.update_record("Leads", lead_id, fields)
    logger.info(
        "Lead %s enriched — market_score=%.2f",
        lead_id, fields.get("Market_Score", 0),
    )
    return {"lead_id": lead_id, "fields_written": list(fields.keys()), "zoho_result": result}


async def enrich_deal(deal_id: str) -> dict[str, Any]:
    logger.info("Enriching deal %s", deal_id)

    deal_data, procurement, price_risk = await asyncio.gather(
        zoho.get_record("Deals", deal_id),
        cli_market.get_procurement_signal(),
        cli_market.get_price_risk(),
        return_exceptions=True,
    )

    if isinstance(deal_data, Exception):
        deal_data = {}
    if isinstance(procurement, Exception):
        procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception):
        price_risk = {"error": str(price_risk)}

    fields = build_deal_market_fields(procurement, price_risk)
    result = await zoho.update_record("Deals", deal_id, fields)
    logger.info(
        "Deal %s enriched — signal=%s risk=%s",
        deal_id, fields.get("Procurement_Signal"), fields.get("Price_Risk_Level"),
    )
    return {"deal_id": deal_id, "fields_written": list(fields.keys()), "zoho_result": result}


async def optimize_inventory(product_id: str) -> dict[str, Any]:
    logger.info("Optimizing inventory for product %s", product_id)

    product_data, procurement, price_risk = await asyncio.gather(
        zoho.get_record("Products", product_id),
        cli_market.get_procurement_signal(),
        cli_market.get_price_risk(),
        return_exceptions=True,
    )

    if isinstance(product_data, Exception):
        product_data = {}
    if isinstance(procurement, Exception):
        procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception):
        price_risk = {"error": str(price_risk)}

    fields = build_product_market_fields(procurement, price_risk, product_data)
    result = await zoho.update_record("Products", product_id, fields)
    logger.info(
        "Product %s optimized — signal=%s recommended_stock=%s",
        product_id, fields.get("Procurement_Signal"), fields.get("Recommended_Stock"),
    )
    return {"product_id": product_id, "fields_written": list(fields.keys()), "zoho_result": result}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "Zoho CRM + CLI Market Integration",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health_check():
    cli_ok, zoho_ok = await asyncio.gather(
        cli_market.health_check(),
        zoho.health_check(),
        return_exceptions=False,
    )
    return {
        "status": "healthy" if (cli_ok and zoho_ok) else "degraded",
        "cli_market_api": cli_ok,
        "zoho_api": zoho_ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/webhook/zoho")
async def zoho_webhook(
    payload: ZohoWebhookPayload,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """
    Webhook principal. Zoho envía un objeto por evento (no array).
    Triggers configurar en: Zoho CRM > Setup > Automation > Workflow Rules > Webhooks
    """
    _check_webhook_auth(request)

    module = payload.module
    op = payload.operation.lower()
    rid = payload.record_id

    if module == "Leads" and op in ("create", "update"):
        background_tasks.add_task(enrich_lead, rid)
        return {"status": "lead_enrichment_scheduled", "record_id": rid}

    if module == "Deals" and op in ("create", "update"):
        background_tasks.add_task(enrich_deal, rid)
        return {"status": "deal_enrichment_scheduled", "record_id": rid}

    if module == "Products" and op in ("create", "update"):
        background_tasks.add_task(optimize_inventory, rid)
        return {"status": "inventory_optimization_scheduled", "record_id": rid}

    return {"status": "no_action_required", "module": module, "operation": op}


@app.post("/api/enrich-lead/{lead_id}")
async def manual_enrich_lead(lead_id: str):
    result = await enrich_lead(lead_id)
    return {"status": "enriched", **result}


@app.post("/api/enrich-deal/{deal_id}")
async def manual_enrich_deal(deal_id: str):
    result = await enrich_deal(deal_id)
    return {"status": "enriched", **result}


@app.post("/api/optimize-inventory/{product_id}")
async def manual_optimize_inventory(product_id: str):
    result = await optimize_inventory(product_id)
    return {"status": "optimized", **result}


@app.get("/api/market-intelligence")
async def market_intelligence(country: str = "PE"):
    """Resumen: brief + scores + inflation + macro (todos tier libre)."""
    summary, macro = await asyncio.gather(
        cli_market.get_market_summary(country=country),
        cli_market.get_macro(country=country),
    )
    return {
        "country": country,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **summary,
        "macro": macro,
    }


@app.get("/api/market-intelligence/pro")
async def market_intelligence_pro(country: str = "PE"):
    """Señales Pro: procurement_signal + price_risk. Requiere CLI Market Pro."""
    procurement, price_risk = await asyncio.gather(
        cli_market.get_procurement_signal(country=country),
        cli_market.get_price_risk(country=country),
    )
    return {
        "country": country,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "procurement_signal": procurement,
        "price_risk": price_risk,
    }


@app.get("/api/basket-optimize")
async def basket_optimize(products: str, country: str = "PE"):
    """
    Optimización de canasta. products = lista separada por coma.
    Ej: /api/basket-optimize?products=leche,arroz,aceite
    """
    product_list = [p.strip() for p in products.split(",") if p.strip()]
    if not product_list:
        raise HTTPException(status_code=400, detail="Enviar al menos un producto")
    result = await cli_market.optimize_basket(product_list, country=country)
    return {"products": product_list, "country": country, "result": result}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    uvicorn.run("src.zoho_middleware:app", host=host, port=port, reload=True)
