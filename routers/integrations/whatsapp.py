import os
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from market_core import check_rate_limit_sqlite
from server_deps import get_messenger_session, update_messenger_session
from openai import OpenAI

router = APIRouter(prefix="/v1/integrations/whatsapp", tags=["integrations"])

# Configuración Twilio (Cargar desde variables de entorno)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Empty TwiML — Twilio's Messaging webhook expects valid TwiML (or an empty
# body). Returning plain text like "queued" is parsed as TwiML, fails with
# error 12100 (Document parse failure), and the WhatsApp *Sandbox* then
# falls back to its canned "You said :X. Configure your Inbound URL..."
# message even when our BackgroundTask later sends the real answer via REST.
_EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

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
    print(f"📱 WhatsApp processing from {sender}: {incoming_msg[:80]!r}")
    if not incoming_msg and audio_url:
        print(f"🎙️ Audio message from {sender}, transcribing...")
        incoming_msg = await transcribe_whatsapp_audio(audio_url)
        if incoming_msg:
            incoming_msg = incoming_msg.lower()

    if not incoming_msg:
        print(f"⚠️ WhatsApp empty body after transcription for {sender}")
        return

    # 1. Recover session memory
    session = get_messenger_session(sender)
    context = session.get("last_context")

    # If we have context, we can use it to refine the query
    effective_query = incoming_msg
    if context:
        effective_query = f"Context: {context}\nUser: {incoming_msg}"

    # Puente hacia la lógica de la API
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    is_admin_sender = _normalize_whatsapp_number(sender) in WHATSAPP_ADMIN_NUMBERS
    token = (
        os.getenv("MARKET_API_TOKEN") if is_admin_sender
        else os.getenv("MARKET_BOT_API_TOKEN", os.getenv("MARKET_API_TOKEN"))
    )
    if not token:
        print(f"❌ WhatsApp: no MARKET_BOT_API_TOKEN/MARKET_API_TOKEN for {sender}")

    answer = "No pude consultar los precios ahora. Probá de nuevo en un ratito."

    # Simple interactive menu if the user asks for help or is new
    if incoming_msg in ("hola", "hi", "hello", "ayuda", "help", "menu"):
        answer = (
            "¡Hola! Soy el bot de *CLI Market* 🚀\n\n"
            "Te ayudo a saber cuánto cuestan las cosas en los supermercados de América Latina.\n\n"
            "¿Qué querés hacer?\n"
            "1️⃣ *Ver un precio*: '¿Cuánto cuesta el café en Perú?'\n"
            "2️⃣ *Comparar tiendas*: 'Compara leche evaporada en Lima'\n"
            "3️⃣ *Ver si va a subir*: '¿Va a subir el precio del arroz?'"
        )
    else:
        async with httpx.AsyncClient() as client_http:
            try:
                response = await client_http.post(
                    f"{market_api_url}/v1/intel/ask",
                    json={"question": effective_query},
                    headers={"Authorization": f"Bearer {token}"} if token else {},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", answer)
                    print(f"✅ /v1/intel/ask ok for {sender} ({len(answer)} chars)")
                else:
                    print(f"❌ /v1/intel/ask returned {response.status_code}: {response.text[:200]}")
            except Exception as e:
                print(f"❌ Error API: {e}")

    # 2. Save memory
    update_messenger_session(sender, context=f"Query: {incoming_msg} | Answer: {answer[:100]}...")

    # Responder vía Twilio SDK
    try:
        _send_twilio_text(sender, answer)
    except Exception as e:
        print(f"❌ Error Twilio: {e}")


async def _reply_denied(sender: str) -> None:
    """Short denial for numbers not on WHATSAPP_ALLOWED_NUMBERS — no LLM cost."""
    try:
        _send_twilio_text(sender, _DENIED_BODY)
    except Exception as e:
        print(f"❌ Error Twilio (denied): {e}")


@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    # Twilio envía los datos como Form Data (application/x-www-form-urlencoded)
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
        # Never return 429 to Twilio — Sandbox treats non-2xx / invalid TwiML
        # as webhook failure and replies with the canned sandbox message.
        if exc.status_code == 429:
            print(f"⚠️ WhatsApp rate limit hit for {sender}")
            return _empty_twiml()
        raise

    if (not incoming_msg and not audio_url) or not TWILIO_AUTH_TOKEN:
        return _empty_twiml()

    # Ack Twilio immediately with empty TwiML — everything slow (transcription,
    # LLM lookup, the actual Twilio send) runs after this response is sent.
    background_tasks.add_task(_process_and_reply, incoming_msg, sender, audio_url)
    return _empty_twiml()

def send_whatsapp_proactive(to: str, body: str):
    """Envía un mensaje de WhatsApp fuera del flujo de webhook (Outbound)."""
    try:
        sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        if not token or not sid:
            print("❌ send_whatsapp_proactive: TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN no configurado.")
            return False

        client = Client(sid, token)
        message = client.messages.create(
            from_=from_number,
            body=body,
            to=to
        )
        print(f"✅ WhatsApp enviado a {to}. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error enviando WhatsApp proactivo: {e}")
        return False

@router.get("/webhook")
async def whatsapp_verify(request: Request):
    return Response(content="ok", status_code=200)
