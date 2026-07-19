import os
import httpx
import uuid
from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/v1/integrations/telegram", tags=["integrations"])

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

async def _send_telegram(chat_id: str, text: str) -> bool:
    if not TELEGRAM_TOKEN:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            return r.status_code == 200
    except Exception:
        return False

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Refactored Telegram webhook using market_ask NLP logic."""
    if not TELEGRAM_TOKEN:
        return {"status": "disabled", "hint": "Set TELEGRAM_BOT_TOKEN env var"}
    
    try:
        body = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    message = body.get("message", {})
    chat = message.get("chat", {})
    incoming_msg = (message.get("text") or "").strip()
    chat_id = str(chat.get("id", ""))
    first_name = chat.get("first_name", "")

    if not incoming_msg or not chat_id:
        return {"status": "no_message"}

    # NLP Bridge to market_ask
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    token = os.getenv("MARKET_API_TOKEN")
    
    answer = "Lo siento, tuve un problema consultando los precios en el Data Moat."

    if incoming_msg.lower() in ("/start", "hola", "hi", "hello"):
        answer = (
            f"Hola <b>{first_name}</b> \U0001f44b\n\n"
            "Soy el bot de <b>CLI Market Intelligence</b>.\n\n"
            "Pregúntame lo que quieras sobre precios, retailers o productos en LATAM.\n"
            "Ejemplo: <i>¿Cuál es el precio del café en Perú?</i> o <i>Busca leche evaporada</i>."
        )
    else:
        async with httpx.AsyncClient() as client_http:
            try:
                response = await client_http.post(
                    f"{market_api_url}/v1/shop/ask",
                    json={"query": incoming_msg, "country": "PE"},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", answer)
            except Exception as e:
                print(f"❌ Error API (Telegram Bridge): {e}")

    await _send_telegram(chat_id, answer)
    return {"status": "ok"}

async def register_telegram_commands() -> bool:
    """Register the native Telegram command menu."""
    if not TELEGRAM_TOKEN:
        return False
    commands = [
        {"command": "start", "description": "Comenzar"},
        {"command": "help", "description": "Ayuda"},
    ]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands",
                json={"commands": commands},
            )
            return r.status_code == 200
    except Exception:
        return False
