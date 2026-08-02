"""Zoho adapter — FastAPI app. Imports from package instead of prototype."""
from __future__ import annotations
import asyncio, logging, os
from datetime import datetime, timezone
from typing import Any
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

from cli_market_integrations.shared.intel_client import CLIMarketIntelClient
from cli_market_integrations.adapters.zoho.zoho_client import ZohoCRMClient
from cli_market_integrations.adapters.zoho.enrichment import (
    build_lead_market_fields, build_deal_market_fields, build_product_market_fields
)

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Zoho CRM + CLI Market", version="0.1.0", description="Enrich Zoho Leads, Deals and Products with CLI Market price intelligence")

cli_market = CLIMarketIntelClient()
zoho = ZohoCRMClient()
WEBHOOK_SECRET = os.getenv("ZOHO_WEBHOOK_SECRET", "")


def _check_auth(request: Request) -> None:
    if not WEBHOOK_SECRET: return
    sig = request.headers.get("X-Zoho-Webhook-Token") or request.headers.get("X-Webhook-Secret") or ""
    if sig != WEBHOOK_SECRET: raise HTTPException(status_code=401, detail="Invalid webhook token")


class ZohoWebhookPayload(BaseModel):
    module: str
    record_id: str
    operation: str
    trigger: str | None = None


async def enrich_lead(lead_id: str) -> dict[str, Any]:
    lead_data, summary = await asyncio.gather(zoho.get_record("Leads", lead_id), cli_market.get_market_summary(), return_exceptions=True)
    if isinstance(lead_data, Exception): lead_data = {}
    if isinstance(summary, Exception): summary = {}
    fields = build_lead_market_fields(summary, lead_data)
    result = await zoho.update_record("Leads", lead_id, fields)
    return {"lead_id": lead_id, "fields_written": list(fields.keys()), "zoho_result": result}


async def enrich_deal(deal_id: str) -> dict[str, Any]:
    deal_data, procurement, price_risk = await asyncio.gather(zoho.get_record("Deals", deal_id), cli_market.get_procurement_signal(), cli_market.get_price_risk(), return_exceptions=True)
    if isinstance(deal_data, Exception): deal_data = {}
    if isinstance(procurement, Exception): procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception): price_risk = {"error": str(price_risk)}
    fields = build_deal_market_fields(procurement, price_risk)
    result = await zoho.update_record("Deals", deal_id, fields)
    return {"deal_id": deal_id, "fields_written": list(fields.keys()), "zoho_result": result}


async def optimize_inventory(product_id: str) -> dict[str, Any]:
    product_data, procurement, price_risk = await asyncio.gather(zoho.get_record("Products", product_id), cli_market.get_procurement_signal(), cli_market.get_price_risk(), return_exceptions=True)
    if isinstance(product_data, Exception): product_data = {}
    if isinstance(procurement, Exception): procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception): price_risk = {"error": str(price_risk)}
    fields = build_product_market_fields(procurement, price_risk, product_data)
    result = await zoho.update_record("Products", product_id, fields)
    return {"product_id": product_id, "fields_written": list(fields.keys()), "zoho_result": result}


@app.get("/")
async def root():
    return {"service": "Zoho CRM + CLI Market", "version": "0.1.0", "status": "running", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health")
async def health():
    cli_ok, zoho_ok = await asyncio.gather(cli_market.health_check(), zoho.health_check())
    return {"status": "healthy" if (cli_ok and zoho_ok) else "degraded", "cli_market_api": cli_ok, "zoho_api": zoho_ok, "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/webhook/zoho")
async def webhook(payload: ZohoWebhookPayload, background_tasks: BackgroundTasks, request: Request):
    _check_auth(request)
    op, rid = payload.operation.lower(), payload.record_id
    if payload.module == "Leads" and op in ("create","update"):
        background_tasks.add_task(enrich_lead, rid); return {"status": "lead_enrichment_scheduled", "record_id": rid}
    if payload.module == "Deals" and op in ("create","update"):
        background_tasks.add_task(enrich_deal, rid); return {"status": "deal_enrichment_scheduled", "record_id": rid}
    if payload.module == "Products" and op in ("create","update"):
        background_tasks.add_task(optimize_inventory, rid); return {"status": "inventory_optimization_scheduled", "record_id": rid}
    return {"status": "no_action_required", "module": payload.module, "operation": op}

@app.post("/api/enrich-lead/{lead_id}")
async def manual_enrich_lead(lead_id: str): return {"status": "enriched", **(await enrich_lead(lead_id))}

@app.post("/api/enrich-deal/{deal_id}")
async def manual_enrich_deal(deal_id: str): return {"status": "enriched", **(await enrich_deal(deal_id))}

@app.post("/api/optimize-inventory/{product_id}")
async def manual_optimize_inventory(product_id: str): return {"status": "optimized", **(await optimize_inventory(product_id))}

@app.get("/api/market-intelligence")
async def market_intelligence(country: str = "PE"):
    summary, macro = await asyncio.gather(cli_market.get_market_summary(country=country), cli_market.get_macro(country=country))
    return {"country": country, "timestamp": datetime.now(timezone.utc).isoformat(), **summary, "macro": macro}

@app.get("/api/market-intelligence/pro")
async def market_intelligence_pro(country: str = "PE"):
    procurement, price_risk = await asyncio.gather(cli_market.get_procurement_signal(country=country), cli_market.get_price_risk(country=country))
    return {"country": country, "timestamp": datetime.now(timezone.utc).isoformat(), "procurement_signal": procurement, "price_risk": price_risk}

@app.get("/api/basket-optimize")
async def basket_optimize(products: str, country: str = "PE"):
    product_list = [p.strip() for p in products.split(",") if p.strip()]
    if not product_list: raise HTTPException(status_code=400, detail="Enviar al menos un producto")
    return {"products": product_list, "country": country, "result": await cli_market.optimize_basket(product_list, country=country)}
