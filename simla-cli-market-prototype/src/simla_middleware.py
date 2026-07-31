"""
Simla.com Middleware — FastAPI bridge between WhatsApp (Simla) and CLI Market.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

load_dotenv()

from src.cli_market_client import CLIMarketClient
from src.intent_detector import PriceIntent, PriceIntentType, intent_detector
from src.simla_client import SimlaClient
from src.whatsapp_formatter import whatsapp_formatter

# Ensure logs dir exists before FileHandler
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/simla_integration.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simla CLI Market Integration",
    version="1.0.0",
    description="Prototype middleware: Simla.com WhatsApp ↔ CLI Market price intelligence",
)

cli_market = CLIMarketClient()
simla = SimlaClient()

WEBHOOK_SECRET = os.getenv("SIMLA_WEBHOOK_SECRET", "")


def validate_whatsapp_message(data: dict[str, Any]) -> dict[str, Any]:
    required_fields = ["phone_number", "message", "conversation_id"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    return data


def _check_webhook_auth(request: Request) -> None:
    """Optional shared-secret gate. If SIMLA_WEBHOOK_SECRET is set, require it."""
    if not WEBHOOK_SECRET:
        return
    header = request.headers.get("X-Webhook-Secret") or request.headers.get("X-Simla-Secret")
    if header != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


async def process_price_query(intent: PriceIntent, phone_number: str, conversation_id: str) -> str:
    try:
        logger.info(
            "Processing price query: %s for %s (chat=%s phone=%s)",
            intent.intent_type.value,
            intent.product,
            conversation_id,
            phone_number[-4:] if phone_number else "?",
        )

        if intent.intent_type == PriceIntentType.SEARCH:
            result = await cli_market.search_product(intent.product)
            return whatsapp_formatter.format_search_result(result)

        if intent.intent_type == PriceIntentType.COMPARE:
            result = await cli_market.compare_prices(intent.product)
            return whatsapp_formatter.format_compare_result(result)

        if intent.intent_type == PriceIntentType.OPTIMIZE:
            if intent.products_list:
                result = await cli_market.optimize_basket(intent.products_list)
                return whatsapp_formatter.format_optimize_result(result)
            return whatsapp_formatter.format_error(
                "No pude identificar los productos para optimizar. Intenta especificarlos mejor."
            )

        if intent.intent_type == PriceIntentType.HISTORY:
            result = await cli_market.get_price_history(intent.product)
            return whatsapp_formatter.format_history_result(result)

        if intent.intent_type == PriceIntentType.ALERT:
            result = await cli_market.search_product(intent.product)
            if result.get("products"):
                threshold = intent.threshold or 5.0
                return whatsapp_formatter.format_alert_confirmation(intent.product, threshold)
            return whatsapp_formatter.format_error(
                "No encontré ese producto para configurar la alerta."
            )

        return whatsapp_formatter.format_error("No pude procesar tu consulta de precios.")
    except Exception as e:
        logger.error("Error processing price query: %s", e)
        return whatsapp_formatter.format_error(
            "Hubo un error al procesar tu consulta. Intenta nuevamente."
        )


async def send_whatsapp_response(phone_number: str, message: str, conversation_id: str) -> None:
    try:
        logger.info(
            "Sending WhatsApp response to ***%s (conversation: %s)",
            phone_number[-4:] if phone_number else "????",
            conversation_id,
        )
        result = await simla.send_whatsapp_message(phone_number, message, conversation_id)
        if result.get("status") == "failed":
            logger.error("Failed to send WhatsApp message: %s", result.get("error"))
        else:
            logger.info("WhatsApp response sent successfully")
    except Exception as e:
        logger.error("Error sending WhatsApp response: %s", e)


@app.get("/")
async def root():
    return {
        "service": "Simla CLI Market Integration",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health_check():
    cli_market_healthy = await cli_market.health_check()
    simla_healthy = await simla.health_check()
    return {
        "status": "healthy" if cli_market_healthy else "degraded",
        "cli_market_api": cli_market_healthy,
        "simla_api": simla_healthy,
        "note": "simla_api may report false if Simla health path differs by tenant",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    message: dict[str, Any],
    background_tasks: BackgroundTasks,
    request: Request,
):
    _check_webhook_auth(request)
    try:
        validated = validate_whatsapp_message(message)
        logger.info(
            "Received WhatsApp message from ***%s: %s…",
            validated["phone_number"][-4:],
            validated["message"][:50],
        )

        intent = intent_detector.detect_intent(validated["message"])
        if intent and intent.confidence > 0.5:
            response_message = await process_price_query(
                intent,
                validated["phone_number"],
                validated["conversation_id"],
            )
            background_tasks.add_task(
                send_whatsapp_response,
                validated["phone_number"],
                response_message,
                validated["conversation_id"],
            )
            return {
                "status": "processed",
                "intent": intent.intent_type.value,
                "confidence": intent.confidence,
                "response_type": "price_intelligence",
            }

        return {
            "status": "no_price_intent",
            "message": "No se detectó intención de precios",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing webhook: %s", e)
        raise HTTPException(status_code=500, detail="webhook_processing_error") from e


@app.post("/api/test-intent")
async def test_intent_detection(payload: dict[str, Any]):
    message = payload.get("message") or payload.get("text") or ""
    intent = intent_detector.detect_intent(message)
    if not intent:
        return {"detected": False, "message": "No se detectó intención de precios"}
    return {
        "detected": True,
        "intent_type": intent.intent_type.value,
        "product": intent.product,
        "confidence": intent.confidence,
        "products_list": intent.products_list or None,
        "threshold": intent.threshold,
    }


@app.get("/api/test-search")
async def test_search(query: str, country: str = "PE"):
    result = await cli_market.search_product(query, country)
    return {
        "raw_result": result,
        "formatted_response": whatsapp_formatter.format_search_result(result),
    }


@app.get("/api/test-compare")
async def test_compare(product: str, country: str = "PE"):
    result = await cli_market.compare_prices(product, country)
    return {
        "raw_result": result,
        "formatted_response": whatsapp_formatter.format_compare_result(result),
    }


@app.get("/api/test-optimize")
async def test_optimize(products: str, country: str = "PE"):
    products_list = [p.strip() for p in products.split(",") if p.strip()]
    result = await cli_market.optimize_basket(products_list, country)
    return {
        "raw_result": result,
        "formatted_response": whatsapp_formatter.format_optimize_result(result),
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    uvicorn.run("src.simla_middleware:app", host=host, port=port, reload=True)
