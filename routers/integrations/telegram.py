import os
import secrets
import httpx
import uuid
from fastapi import APIRouter, Request, Response
from market_core import check_rate_limit_sqlite
from server_deps import get_messenger_session, update_messenger_session

router = APIRouter(prefix="/v1/integrations/telegram", tags=["integrations"])

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Must match the secret_token passed to Telegram's setWebhook call. Telegram
# echoes it back on every webhook POST as X-Telegram-Bot-Api-Secret-Token;
# without checking it, anyone can POST a forged update body.
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

# Per-chat cap so a single (secret-token-authenticated) chat can't run up
# paid LLM costs by hammering the webhook.
TELEGRAM_RATE_LIMIT_MIN = int(os.getenv("TELEGRAM_RATE_LIMIT_MIN", "20"))
TELEGRAM_RATE_LIMIT_WINDOW = int(os.getenv("TELEGRAM_RATE_LIMIT_WINDOW", "60"))
TELEGRAM_RATE_LIMIT_DAY = int(os.getenv("TELEGRAM_RATE_LIMIT_DAY", "300"))


def _is_valid_telegram_secret(request: Request) -> bool:
    if not TELEGRAM_WEBHOOK_SECRET:
        return False
    return secrets.compare_digest(
        request.headers.get("x-telegram-bot-api-secret-token", ""),
        TELEGRAM_WEBHOOK_SECRET,
    )

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

    if not _is_valid_telegram_secret(request):
        print("❌ Telegram webhook: invalid or missing secret token")
        return Response(content="invalid secret token", status_code=403)

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

    check_rate_limit_sqlite(
        f"telegram:{chat_id}",
        window_secs=TELEGRAM_RATE_LIMIT_WINDOW,
        max_req=TELEGRAM_RATE_LIMIT_MIN,
        daily_max=TELEGRAM_RATE_LIMIT_DAY,
    )

    # 1. Recover session memory
    session = get_messenger_session(chat_id)
    context = session.get("last_context")

    effective_query = incoming_msg
    if context:
        effective_query = f"Context: {context}\nUser: {incoming_msg}"

    # NLP Bridge to market_ask
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    token = os.getenv("MARKET_BOT_API_TOKEN", os.getenv("MARKET_API_TOKEN"))
    
    answer = "No pude consultar los precios ahora. Probá de nuevo en un ratito."

    if incoming_msg.lower() in ("/start", "hola", "hi", "hello"):
        answer = (
            f"Hola <b>{first_name}</b> \U0001f44b\n\n"
            "Soy el bot de <b>CLI Market</b>.\n\n"
            "Preguntame lo que quieras sobre precios de productos en tiendas de América Latina.\n"
            "Por ejemplo: <i>¿Cuánto cuesta el café en Perú?</i> o <i>Busco leche evaporada</i>."
        )
    else:
        async with httpx.AsyncClient() as client_http:
            try:
                response = await client_http.post(
                    f"{market_api_url}/v1/intel/ask",
                    json={"question": effective_query},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", answer)
                else:
                    print(f"❌ /v1/intel/ask returned {response.status_code}: {response.text[:200]}")
            except Exception as e:
                print(f"❌ Error API (Telegram Bridge): {e}")

    # 2. Save memory
    update_messenger_session(chat_id, context=f"Query: {incoming_msg} | Answer: {answer[:100]}...")

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
