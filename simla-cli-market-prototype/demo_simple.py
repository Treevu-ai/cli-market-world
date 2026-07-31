"""
Demo simplificada del prototipo Simla.com + CLI Market (solo CLI Market + intent).
No envía WhatsApp real.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from src.cli_market_client import CLIMarketClient
from src.intent_detector import intent_detector
from src.whatsapp_formatter import whatsapp_formatter


async def demo_simple() -> None:
    print("Demo Simla.com + CLI Market (search only)")
    print("=" * 50)

    cli_market = CLIMarketClient()
    healthy = await cli_market.health_check()
    print(f"CLI Market API: {'OK' if healthy else 'DOWN'}")
    if not healthy:
        print("No se puede continuar sin /health/stats")
        return

    message = "¿Cuánto cuesta la leche?"
    print(f"\nMensaje: {message}")
    intent = intent_detector.detect_intent(message)
    if not intent:
        print("Sin intención de precios")
        return

    print(f"Intent: {intent.intent_type.value} product={intent.product!r} conf={intent.confidence:.2f}")
    result = await cli_market.search_product(intent.product)
    if result.get("error"):
        print(f"API error: {result['error']}")
    print(f"Hits: {len(result.get('products') or [])}")
    print("\nRespuesta WhatsApp:\n")
    print(whatsapp_formatter.format_search_result(result))


if __name__ == "__main__":
    asyncio.run(demo_simple())
