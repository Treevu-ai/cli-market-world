"""
Simla adapter — FastAPI app entry point.
Imports from this package instead of prototype's src.*
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

load_dotenv()

from cli_market_integrations.adapters.simla.cli_market_client import CLIMarketProductClient
from cli_market_integrations.adapters.simla.intent_detector import PriceIntent, PriceIntentType, intent_detector
from cli_market_integrations.adapters.simla.simla_client import SimlaClient
from cli_market_integrations.adapters.simla.whatsapp_formatter import whatsapp_formatter

_log_handlers: list[logging.Handler] = [logging.StreamHandler()]
if os.getenv("LOG_TO_FILE", "").lower() in ("1", "true", "yes"):
    os.makedirs("logs", exist_ok=True)
    _log_handlers.append(logging.FileHandler("logs/simla_integration.log", encoding="utf-8"))
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=_log_handlers)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simla + CLI Market", version="0.1.0", description="Simla.com WhatsApp ↔ CLI Market price intelligence")

cli_market = CLIMarketProductClient()
simla = SimlaClient()
WEBHOOK_SECRET = os.getenv("SIMLA_WEBHOOK_SECRET", "")


def _check_auth(request: Request) -> None:
    if not WEBHOOK_SECRET: return
    if (request.headers.get("X-Webhook-Secret") or request.headers.get("X-Simla-Secret")) != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


async def _process(intent: PriceIntent, phone: str, conv: str) -> str:
    try:
        if intent.intent_type == PriceIntentType.SEARCH:
            return whatsapp_formatter.format_search_result(await cli_market.search_product(intent.product))
        if intent.intent_type == PriceIntentType.COMPARE:
            return whatsapp_formatter.format_compare_result(await cli_market.compare_prices(intent.product))
        if intent.intent_type == PriceIntentType.OPTIMIZE:
            if intent.products_list:
                return whatsapp_formatter.format_optimize_result(await cli_market.optimize_basket(intent.products_list))
            return whatsapp_formatter.format_error("No pude identificar los productos. Especificalos mejor.")
        if intent.intent_type == PriceIntentType.HISTORY:
            return whatsapp_formatter.format_history_result(await cli_market.get_price_history(intent.product))
        if intent.intent_type == PriceIntentType.ALERT:
            r = await cli_market.search_product(intent.product)
            if r.get("products"):
                return whatsapp_formatter.format_alert_confirmation(intent.product, intent.threshold or 5.0)
            return whatsapp_formatter.format_error("No encontré ese producto para configurar la alerta.")
    except Exception as e:
        logger.error("Error processing intent: %s", e)
    return whatsapp_formatter.format_error("Hubo un error. Intenta nuevamente.")


async def _send(phone: str, message: str, conv: str) -> None:
    result = await simla.send_whatsapp_message(phone, message, conv)
    if result.get("status") == "failed":
        logger.error("Failed to send WhatsApp: %s", result.get("error"))


@app.get("/")
async def root():
    return {"service": "Simla + CLI Market", "version": "0.1.0", "status": "running", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health")
async def health():
    cli_ok = await cli_market.health_check()
    simla_ok, simla_checked = False, False
    if os.getenv("SIMLA_API_KEY"):
        simla_checked = True
        try: simla_ok = await asyncio.wait_for(simla.health_check(), timeout=2.0)
        except Exception: pass
    return {"status": "healthy" if cli_ok else "degraded", "cli_market_api": cli_ok, "simla_api": simla_ok if simla_checked else None, "simla_checked": simla_checked, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/webhook/whatsapp")
async def webhook(message: dict[str, Any], background_tasks: BackgroundTasks, request: Request):
    _check_auth(request)
    for f in ("phone_number", "message", "conversation_id"):
        if f not in message:
            raise HTTPException(status_code=400, detail=f"Missing field: {f}")
    intent = intent_detector.detect_intent(message["message"])
    if intent and intent.confidence > 0.5:
        resp = await _process(intent, message["phone_number"], message["conversation_id"])
        background_tasks.add_task(_send, message["phone_number"], resp, message["conversation_id"])
        return {"status": "processed", "intent": intent.intent_type.value, "confidence": intent.confidence}
    return {"status": "no_price_intent"}


def _intent_resp(msg: str) -> dict[str, Any]:
    intent = intent_detector.detect_intent(msg)
    if not intent: return {"detected": False}
    return {"detected": True, "intent_type": intent.intent_type.value, "product": intent.product, "confidence": intent.confidence, "products_list": intent.products_list or None, "threshold": intent.threshold}


@app.get("/api/test-intent")
async def test_intent_get(message: str): return _intent_resp(message)

@app.post("/api/test-intent")
async def test_intent_post(request: Request):
    try: p = await request.json()
    except: p = {}
    msg = (p or {}).get("message") or ""
    if not msg: raise HTTPException(400, detail='Send {"message": "..."}')
    return _intent_resp(msg)

@app.get("/api/test-search")
async def test_search(query: str, country: str = "PE"):
    r = await cli_market.search_product(query, country)
    return {"raw_result": r, "formatted_response": whatsapp_formatter.format_search_result(r)}

@app.get("/api/test-compare")
async def test_compare(product: str, country: str = "PE"):
    r = await cli_market.compare_prices(product, country)
    return {"raw_result": r, "formatted_response": whatsapp_formatter.format_compare_result(r)}

@app.get("/api/test-optimize")
async def test_optimize(products: str, country: str = "PE"):
    r = await cli_market.optimize_basket([p.strip() for p in products.split(",") if p.strip()], country)
    return {"raw_result": r, "formatted_response": whatsapp_formatter.format_optimize_result(r)}
