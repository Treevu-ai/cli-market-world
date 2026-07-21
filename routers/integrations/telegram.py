import os
import re
import secrets
import httpx
from fastapi import APIRouter, BackgroundTasks, Request, Response
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

_COUNTRY_HINTS = {
    "peru": "PE", "perú": "PE",
    "colombia": "CO",
    "mexico": "MX", "méxico": "MX",
    "argentina": "AR",
    "chile": "CL",
    "brasil": "BR", "brazil": "BR",
}


def _esc(text: str) -> str:
    """Escape text interpolated into an HTML parse_mode Telegram message.
    Telegram's HTML parser only reserves & < > (unlike MarkdownV2's ~20
    punctuation chars) — but first_name (user-controlled) and answer
    (LLM-generated) are never under our control, and an unescaped & < > in
    either breaks the parser (Telegram returns 400, silently swallowed by
    _send_telegram's bare except) or lets the sender/LLM inject fake <b>/<i>
    formatting. Same fix procure-telegram-bot's src/lib/format.ts already
    applied for the same reason — ported here since it never was."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _markdown_bold_to_html(text: str) -> str:
    """ask_intel's answers are written in Markdown (**bold**), but Telegram
    messages are sent with parse_mode: "HTML" — the two don't mix, so users
    were seeing literal asterisks instead of bold text (reported live
    2026-07-20). Must run AFTER _esc() escapes & < > — ** itself isn't
    affected by that escaping, and text captured between markers can't
    contain raw < > to reintroduce after the fact."""
    return _MD_BOLD_RE.sub(r"<b>\1</b>", text)


def _guess_country(text: str) -> str:
    """Best-effort country code from free text, defaulting to PE (primary
    market) — used only to re-run a button-triggered follow-up query, not
    for anything user-facing."""
    lowered = text.lower()
    for name, code in _COUNTRY_HINTS.items():
        if name in lowered:
            return code
    return "PE"


def _is_valid_telegram_secret(request: Request) -> bool:
    if not TELEGRAM_WEBHOOK_SECRET:
        return False
    return secrets.compare_digest(
        request.headers.get("x-telegram-bot-api-secret-token", ""),
        TELEGRAM_WEBHOOK_SECRET,
    )


def _follow_up_keyboard() -> dict:
    """Inline keyboard attached to a real product-search answer. Each button
    carries only the action code — the product/country context is read back
    from messenger_sessions by chat_id, not from callback_data (Telegram
    caps callback_data at 64 bytes, too tight for arbitrary product names)."""
    return {
        "inline_keyboard": [
            [
                {"text": "🔄 Comparar tiendas", "callback_data": "cmp"},
                {"text": "📈 ¿Va a subir?", "callback_data": "trend"},
            ],
            [{"text": "🔔 Avisarme si baja", "callback_data": "alert"}],
        ]
    }


async def _telegram_api(method: str, payload: dict) -> httpx.Response | None:
    if not TELEGRAM_TOKEN:
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            return await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}",
                json=payload,
            )
    except Exception as e:
        print(f"❌ Telegram API error ({method}): {e}")
        return None


async def _send_telegram(chat_id: str, text: str, reply_markup: dict | None = None) -> str | None:
    """Send a message; returns its message_id (for later editing) or None."""
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = await _telegram_api("sendMessage", payload)
    if r is None or r.status_code != 200:
        return None
    try:
        return str(r.json()["result"]["message_id"])
    except Exception:
        return None


async def _edit_telegram(chat_id: str, message_id: str, text: str, reply_markup: dict | None = None) -> bool:
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = await _telegram_api("editMessageText", payload)
    return bool(r and r.status_code == 200)


async def _send_typing(chat_id: str) -> None:
    await _telegram_api("sendChatAction", {"chat_id": chat_id, "action": "typing"})


async def _answer_callback_query(callback_query_id: str, text: str | None = None) -> None:
    """Mandatory: Telegram leaves the button showing a loading spinner on the
    sender's client until this is called, regardless of what else we do."""
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    await _telegram_api("answerCallbackQuery", payload)


async def _ask_intel(question: str, token: str) -> str:
    """Call /v1/intel/ask and return the answer text, or a fallback message."""
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                f"{market_api_url}/v1/intel/ask",
                json={"question": question},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if response.status_code == 200:
                return _markdown_bold_to_html(_esc(response.json().get("answer", "")))
            print(f"❌ /v1/intel/ask returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error API (Telegram Bridge): {e}")
    return "No pude consultar los precios ahora. Probá de nuevo en un ratito."


async def _process_message(chat_id: str, message_id: str | None, incoming_msg: str, first_name: str) -> None:
    """The slow work for a plain-text message: LLM call, session save, and
    editing the placeholder in place (or sending a fresh message if the
    placeholder itself failed to send)."""
    token = os.getenv("MARKET_BOT_API_TOKEN", os.getenv("MARKET_API_TOKEN"))

    if incoming_msg.lower() in ("/start", "hola", "hi", "hello"):
        answer = (
            f"Hola <b>{_esc(first_name)}</b> \U0001f44b\n\n"
            "Soy el bot de <b>CLI Market</b>. Te ayudo a ver precios de productos en "
            "supermercados de Perú y otros países de Latinoamérica.\n\n"
            "<b>Qué puedo hacer:</b>\n"
            "• Buscarte el precio de un producto (ej: <i>¿Cuánto cuesta el café en Perú?</i>)\n"
            "• Comparar precios entre tiendas\n"
            "• Avisarte si el precio de algo baja\n\n"
            "<b>Qué NO puedo hacer:</b>\n"
            "• No hago compras ni pagos, solo te muestro precios\n"
            "• Solo veo las tiendas que ya monitoreamos — puede faltar alguna marca o producto puntual\n"
            "• Los precios se actualizan varias veces al día, no al segundo\n\n"
            "Escribime el producto que buscás."
        )
        keyboard = None
    else:
        session = get_messenger_session(chat_id)
        context = session.get("last_context")
        effective_query = f"Context: {context}\nUser: {incoming_msg}" if context else incoming_msg

        answer = await _ask_intel(effective_query, token)
        keyboard = _follow_up_keyboard()
        update_messenger_session(
            chat_id,
            context=f"Query: {incoming_msg} | Answer: {answer[:100]}...",
            last_query=incoming_msg,
            last_country=_guess_country(incoming_msg),
        )

    if message_id:
        if not await _edit_telegram(chat_id, message_id, answer, reply_markup=keyboard):
            await _send_telegram(chat_id, answer, reply_markup=keyboard)
    else:
        await _send_telegram(chat_id, answer, reply_markup=keyboard)


_BUTTON_QUESTIONS = {
    "cmp": lambda q, c: f"Compara precios de {q} en {c} entre tiendas",
    "trend": lambda q, c: f"¿Va a subir o bajar el precio de {q} en {c}?",
    "alert": lambda q, c: f"Avísame si baja el precio de {q} en {c}",
}
_BUTTON_LABELS = {"cmp": "🔄 Comparando tiendas...", "trend": "📈 Revisando tendencia...", "alert": "🔔 Configurando aviso..."}


async def _process_callback(chat_id: str, message_id: str, action: str) -> None:
    """The slow work for an inline-button press: re-run the last query with
    the button's action folded in, using session context instead of asking
    the user to retype the product — the concrete fix for the tool-selection
    ambiguity that caused free-text follow-ups to fail (2026-07-20 café bug)."""
    session = get_messenger_session(chat_id)
    last_query = session.get("last_query")
    if not last_query:
        await _edit_telegram(chat_id, message_id, "Esa búsqueda ya expiró — escribime de nuevo qué precio querés ver.")
        return

    country = session.get("last_country") or "PE"
    builder = _BUTTON_QUESTIONS.get(action)
    if not builder:
        return
    token = os.getenv("MARKET_BOT_API_TOKEN", os.getenv("MARKET_API_TOKEN"))
    answer = await _ask_intel(builder(last_query, country), token)
    await _edit_telegram(chat_id, message_id, answer, reply_markup=_follow_up_keyboard())


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Telegram webhook — acks fast, does the slow LLM/tool work in the
    background (mirrors routers/integrations/whatsapp.py's pattern), and
    edits its own placeholder message in place instead of leaving the chat
    silent until the real answer is ready."""
    if not TELEGRAM_TOKEN:
        return {"status": "disabled", "hint": "Set TELEGRAM_BOT_TOKEN env var"}

    if not _is_valid_telegram_secret(request):
        print("❌ Telegram webhook: invalid or missing secret token")
        return Response(content="invalid secret token", status_code=403)

    try:
        body = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    callback_query = body.get("callback_query")
    if callback_query:
        chat_id = str(callback_query.get("message", {}).get("chat", {}).get("id", ""))
        message_id = str(callback_query.get("message", {}).get("message_id", ""))
        action = callback_query.get("data", "")
        callback_query_id = callback_query.get("id", "")

        if not chat_id or not message_id:
            return {"status": "no_message"}

        # Mandatory ack first — Telegram shows a perpetual loading spinner on
        # the button otherwise, regardless of what we do afterwards.
        await _answer_callback_query(callback_query_id, _BUTTON_LABELS.get(action))

        check_rate_limit_sqlite(
            f"telegram:{chat_id}",
            window_secs=TELEGRAM_RATE_LIMIT_WINDOW,
            max_req=TELEGRAM_RATE_LIMIT_MIN,
            daily_max=TELEGRAM_RATE_LIMIT_DAY,
        )
        await _send_typing(chat_id)
        background_tasks.add_task(_process_callback, chat_id, message_id, action)
        return {"status": "ok"}

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

    await _send_typing(chat_id)
    message_id = await _send_telegram(chat_id, "🔍 Buscando...")
    background_tasks.add_task(_process_message, chat_id, message_id, incoming_msg, first_name)
    return {"status": "ok"}


async def register_telegram_commands() -> bool:
    """Register the native Telegram command menu."""
    if not TELEGRAM_TOKEN:
        return False
    commands = [
        {"command": "start", "description": "Comenzar"},
        {"command": "help", "description": "Ayuda"},
    ]
    r = await _telegram_api("setMyCommands", {"commands": commands})
    return bool(r and r.status_code == 200)
