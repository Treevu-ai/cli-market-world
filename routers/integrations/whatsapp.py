import os
import re
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from market_core import check_rate_limit_sqlite
from openai import OpenAI

# Importar extensiones HORECA
try:
    from .whatsapp_horeca import process_horeca_message
    HORECA_AVAILABLE = True
except ImportError:
    HORECA_AVAILABLE = False
    print("⚠️ HORECA extension not available - using standard WhatsApp flow")

router = APIRouter(prefix="/v1/integrations/whatsapp", tags=["integrations"])
# Compatibility alias: Twilio Console sometimes still points at the shorter
# historical path. Live traffic was observed as POST /whatsapp/webhook → 404
# while the canonical route is /v1/integrations/whatsapp/webhook (2026-08-05).
legacy_router = APIRouter(prefix="/whatsapp", tags=["integrations"])

# Configuración Twilio (Cargar desde variables de entorno)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Configuración HORECA
HORECA_ENABLED = os.getenv("HORECA_ENABLED", "false").lower() == "true"

# Empty TwiML — Twilio's Messaging webhook expects valid TwiML (or an empty
# body). Returning plain text like "queued" is parsed as TwiML, fails with
# error 12100 (Document parse failure), and the WhatsApp *Sandbox* then
# falls back to its canned "You said :X. Configure your Inbound URL..."
# message even when our BackgroundTask later sends the real answer via REST.
_EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _markdown_bold_to_whatsapp(text: str) -> str:
    """ask_intel answers are written in standard Markdown (**bold**), but
    WhatsApp's own formatting uses a single asterisk (*bold*) — sent as-is,
    users see literal double asterisks instead of bold text (same bug class
    reported live on Telegram 2026-07-20; WhatsApp uses the same LLM answer
    and was never converted either)."""
    return _MD_BOLD_RE.sub(r"*\1*", text)

# Per-sender cap so a single (correctly-signed) number can't run up paid
# Whisper transcription / LLM costs by hammering the webhook.
WHATSAPP_RATE_LIMIT_MIN = int(os.getenv("WHATSAPP_RATE_LIMIT_MIN", "20"))
WHATSAPP_RATE_LIMIT_WINDOW = int(os.getenv("WHATSAPP_RATE_LIMIT_WINDOW", "60"))
WHATSAPP_RATE_LIMIT_DAY = int(os.getenv("WHATSAPP_RATE_LIMIT_DAY", "300"))

# Access allowlist: only these Twilio From numbers may use the bot. When
# empty, any sandbox-joined sender is accepted (legacy open mode). When set,
# everyone else gets a short denial and no LLM/API call. Comma-separated;
# accepts "whatsapp:+51…" or bare "+51…".
# Admin numbers (token tier) are separate — they must also be on this list
# if the allowlist is non-empty.
def _normalize_whatsapp_number(number: str) -> str:
    n = (number or "").strip()
    if not n:
        return ""
    if n.startswith("whatsapp:"):
        return n
    if not n.startswith("+"):
        n = f"+{n}"
    return f"whatsapp:{n}"


def _parse_number_set(raw: str) -> set[str]:
    return {
        _normalize_whatsapp_number(part)
        for part in (raw or "").split(",")
        if part.strip()
    }


WHATSAPP_ALLOWED_NUMBERS = _parse_number_set(os.getenv("WHATSAPP_ALLOWED_NUMBERS", ""))

# Numbers that get the plenipotentiary/admin token instead of the shared bot
# token. Without this, MARKET_API_TOKEN — which server_deps.auth_user resolves
# to the platform "admin" account — would grant every WhatsApp sender unlimited
# backend access, not just the operator.
WHATSAPP_ADMIN_NUMBERS = _parse_number_set(os.getenv("WHATSAPP_ADMIN_NUMBERS", ""))

_DENIED_BODY = (
    "Este número no está autorizado para usar el bot de CLI Market. "
    "Si necesitás acceso, pedilo al administrador."
)


def _empty_twiml() -> Response:
    """Ack Twilio without auto-replying; the real reply goes out via REST API."""
    return Response(content=_EMPTY_TWIML, media_type="application/xml", status_code=200)


def _is_sender_allowed(sender: str) -> bool:
    """True if sender may use the bot. Empty allowlist = open (no restriction)."""
    if not WHATSAPP_ALLOWED_NUMBERS:
        return True
    return _normalize_whatsapp_number(sender) in WHATSAPP_ALLOWED_NUMBERS


def _bot_token_for_sender(sender: str) -> str | None:
    """Resolve API token for a WhatsApp sender.

    Public bot traffic must use MARKET_BOT_API_TOKEN only — never the platform
    admin MARKET_API_TOKEN, which bypasses tier/rate limits on /v1/intel/ask.
    """
    if _normalize_whatsapp_number(sender) in WHATSAPP_ADMIN_NUMBERS:
        return os.getenv("MARKET_API_TOKEN") or os.getenv("MARKET_BOT_API_TOKEN")
    return os.getenv("MARKET_BOT_API_TOKEN") or None


def _send_twilio_text(to: str, body: str) -> None:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    msg = twilio_client.messages.create(
        from_=TWILIO_NUMBER,
        body=body,
        to=to,
    )
    print(f"✅ WhatsApp reply to {to}. SID: {msg.sid}")

async def transcribe_whatsapp_audio(audio_url: str) -> str:
    """Downloads audio from Twilio and transcribes it using OpenAI Whisper."""
    try:
        client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Download audio from Twilio (requires Auth)
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        async with httpx.AsyncClient() as client_http:
            resp = await client_http.get(audio_url, auth=auth)
            if resp.status_code != 200:
                return ""
            audio_data = resp.content
        
        # Whisper needs a file-like object
        import io
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.ogg" # Whisper needs a filename to guess the format
        
        transcript = client_openai.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        print(f"❌ transcribe_whatsapp_audio error: {e}")
        return ""

def _twilio_request_url(request: Request) -> str:
    """Reconstruct the public HTTPS URL Twilio signed, since uvicorn behind
    Fly.io's proxy sees a plain-HTTP request unless X-Forwarded-* is honored."""
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc))
    url = f"{proto}://{host}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"
    return url


def _is_valid_twilio_signature(request: Request, params: dict) -> bool:
    if not TWILIO_AUTH_TOKEN:
        return False
    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        return False
    # Twilio never repeats a form key (MediaUrl0, MediaUrl1, ... instead of
    # duplicates), so flattening the multidict with dict() is safe here.
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(_twilio_request_url(request), params, signature)


async def _process_and_reply(incoming_msg: str, sender: str, audio_url: str | None) -> None:
    """The slow work: audio transcription, LLM lookup, and the actual Twilio
    send. Runs as a FastAPI BackgroundTask — Starlette/uvicorn send the
    webhook's HTTP response to Twilio BEFORE this executes, so a slow LLM
    call here can no longer cause Twilio's Sandbox to time out and fall back
    to its own "You said :X. Configure your Inbound URL" message while our
    real answer arrives late as a separate message (the exact bug reported
    2026-07-19 — the earlier synchronous version awaited /v1/intel/ask,
    which has a 30s timeout, before ever returning any HTTP response).

    The webhook itself must also return *valid empty TwiML* (not plain text);
    otherwise Twilio logs error 12100 and the Sandbox still shows that same
    canned fallback even when this task succeeds via the REST API."""
    
    # Intentar usar lógica HORECA si está habilitada
    if HORECA_ENABLED and HORECA_AVAILABLE:
        market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
        
        try:
            horeca_processed = await process_horeca_message(
                incoming_msg, 
                sender, 
                audio_url,
                _send_twilio_text,
                market_api_url,
                _bot_token_for_sender
            )
            
            if horeca_processed:
                # La lógica HORECA manejó el mensaje, no continuar con lógica estándar
                return
        except Exception as e:
            print(f"⚠️ HORECA processing failed, falling back to standard: {e}")
    
    # Lógica estándar: funnel conversacional (clarify → candidatos → detalle / intel)
    print(f"📱 WhatsApp processing from {sender}: {incoming_msg[:80]!r}")
    if not incoming_msg and audio_url:
        print(f"🎙️ Audio message from {sender}, transcribing...")
        incoming_msg = await transcribe_whatsapp_audio(audio_url)
        if incoming_msg:
            incoming_msg = incoming_msg.lower()

    if not incoming_msg:
        print(f"⚠️ WhatsApp empty body after transcription for {sender}")
        return

    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    token = _bot_token_for_sender(sender)
    if not token:
        print(f"❌ WhatsApp: no MARKET_BOT_API_TOKEN for {sender}")

    try:
        from .whatsapp_conversation import handle_standard_turn

        answer = await handle_standard_turn(
            sender,
            incoming_msg,
            token=token,
            market_api_url=market_api_url,
        )
    except Exception as e:
        print(f"❌ WhatsApp standard flow error: {e}")
        answer = "No pude consultar los precios ahora. Probá de nuevo en un ratito."

    try:
        _send_twilio_text(sender, _markdown_bold_to_whatsapp(answer))
    except Exception as e:
        print(f"❌ Error Twilio: {e}")


async def _reply_denied(sender: str) -> None:
    """Short denial for numbers not on WHATSAPP_ALLOWED_NUMBERS — no LLM cost."""
    try:
        _send_twilio_text(sender, _DENIED_BODY)
    except Exception as e:
        print(f"❌ Error Twilio (denied): {e}")


@router.post("/webhook")
@legacy_router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook Twilio WhatsApp — ack fast with empty TwiML; slow work in background."""
    form_data = await request.form()
    params = {k: str(v) for k, v in form_data.items()}

    if not _is_valid_twilio_signature(request, params):
        print("❌ WhatsApp webhook: invalid or missing Twilio signature")
        return Response(content="invalid signature", status_code=403)

    # Body can be missing on pure-media messages; MediaContentType0 is the
    # real Twilio form key (MediaContentType without index is not sent).
    incoming_msg = str(form_data.get("Body") or "").strip().lower()
    sender = str(form_data.get("From") or "")
    media_type = str(
        form_data.get("MediaContentType0") or form_data.get("MediaContentType") or ""
    )
    is_audio = media_type.startswith("audio/")
    audio_url = str(form_data.get("MediaUrl0") or "") if is_audio else None

    print(f"📥 WhatsApp webhook ok from {sender!r} body={(incoming_msg or '')[:40]!r}")

    # Access control before rate limit / LLM — anyone who joined the Twilio
    # Sandbox can hit this webhook; the allowlist is the real gate.
    if not _is_sender_allowed(sender):
        print(f"🚫 WhatsApp denied (not on allowlist): {sender}")
        if TWILIO_AUTH_TOKEN:
            background_tasks.add_task(_reply_denied, sender)
        return _empty_twiml()

    try:
        check_rate_limit_sqlite(
            f"whatsapp:{sender}",
            window_secs=WHATSAPP_RATE_LIMIT_WINDOW,
            max_req=WHATSAPP_RATE_LIMIT_MIN,
            daily_max=WHATSAPP_RATE_LIMIT_DAY,
        )
    except HTTPException as exc:
        # Never return 429 to Twilio — Sandbox treats non-2xx as webhook failure.
        if exc.status_code == 429:
            print(f"⚠️ WhatsApp rate limit hit for {sender}")
            return _empty_twiml()
        raise

    if (not incoming_msg and not audio_url) or not TWILIO_AUTH_TOKEN:
        return _empty_twiml()

    # IMPORTANT: pass callable + args (not a pre-created coroutine).
    background_tasks.add_task(_process_and_reply, incoming_msg, sender, audio_url)
    return _empty_twiml()


@router.get("/health")
@legacy_router.get("/health")
async def whatsapp_health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "twilio_configured": bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN),
        "twilio_number_set": bool(TWILIO_NUMBER),
        "bot_token_set": bool(os.getenv("MARKET_BOT_API_TOKEN")),
        "allowlist_size": len(WHATSAPP_ALLOWED_NUMBERS),
        "admin_list_size": len(WHATSAPP_ADMIN_NUMBERS),
        "horeca_enabled": HORECA_ENABLED,
        "horeca_available": HORECA_AVAILABLE,
        "webhook_path": "/v1/integrations/whatsapp/webhook",
        "webhook_path_legacy": "/whatsapp/webhook",
    }


@router.get("/webhook")
@legacy_router.get("/webhook")
async def whatsapp_verify(request: Request):
    return Response(content="ok", status_code=200)