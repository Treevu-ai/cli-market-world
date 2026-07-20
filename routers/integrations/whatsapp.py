import os
import httpx
from fastapi import APIRouter, Request, Response
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

# Per-sender cap so a single (correctly-signed) number can't run up paid
# Whisper transcription / LLM costs by hammering the webhook.
WHATSAPP_RATE_LIMIT_MIN = int(os.getenv("WHATSAPP_RATE_LIMIT_MIN", "20"))
WHATSAPP_RATE_LIMIT_WINDOW = int(os.getenv("WHATSAPP_RATE_LIMIT_WINDOW", "60"))
WHATSAPP_RATE_LIMIT_DAY = int(os.getenv("WHATSAPP_RATE_LIMIT_DAY", "300"))

# Numbers (Twilio "From" format, e.g. "whatsapp:+51999999999") that get the
# plenipotentiary/admin token instead of the shared bot token below. Without
# this allowlist MARKET_API_TOKEN — which server_deps.auth_user resolves to
# the platform "admin" account — would grant every WhatsApp sender unlimited
# backend access, not just the operator.
WHATSAPP_ADMIN_NUMBERS = {
    n.strip() for n in os.getenv("WHATSAPP_ADMIN_NUMBERS", "").split(",") if n.strip()
}

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


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    # Twilio envía los datos como Form Data (application/x-www-form-urlencoded)
    form_data = await request.form()

    if not _is_valid_twilio_signature(request, dict(form_data)):
        print("❌ WhatsApp webhook: invalid or missing Twilio signature")
        return Response(content="invalid signature", status_code=403)

    incoming_msg = form_data.get("Body", "").lower()
    sender = form_data.get("From", "")

    check_rate_limit_sqlite(
        f"whatsapp:{sender}",
        window_secs=WHATSAPP_RATE_LIMIT_WINDOW,
        max_req=WHATSAPP_RATE_LIMIT_MIN,
        daily_max=WHATSAPP_RATE_LIMIT_DAY,
    )

    # Handle Voice Messages
    if not incoming_msg and form_data.get("MediaContentType", "").startswith("audio/"):
        audio_url = form_data.get("MediaUrl0")
        if audio_url:
            print(f"🎙️ Audio message from {sender}, transcribing...")
            incoming_msg = await transcribe_whatsapp_audio(audio_url)
            if incoming_msg:
                incoming_msg = incoming_msg.lower()

    if not incoming_msg or not TWILIO_AUTH_TOKEN:
        return Response(content="ignored", status_code=200)

    # 1. Recover session memory
    session = get_messenger_session(sender)
    context = session.get("last_context")

    # If we have context, we can use it to refine the query
    effective_query = incoming_msg
    if context:
        effective_query = f"Context: {context}\nUser: {incoming_msg}"

    # Puente hacia la lógica de la API
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    is_admin_sender = sender in WHATSAPP_ADMIN_NUMBERS
    token = (
        os.getenv("MARKET_API_TOKEN") if is_admin_sender
        else os.getenv("MARKET_BOT_API_TOKEN", os.getenv("MARKET_API_TOKEN"))
    )

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
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", answer)
                else:
                    print(f"❌ /v1/intel/ask returned {response.status_code}: {response.text[:200]}")
            except Exception as e:
                print(f"❌ Error API: {e}")

    # 2. Save memory
    update_messenger_session(sender, context=f"Query: {incoming_msg} | Answer: {answer[:100]}...")

    # Responder vía Twilio SDK
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_client.messages.create(
            from_=TWILIO_NUMBER,
            body=answer,
            to=sender
        )
        return Response(content="success", status_code=200)
    except Exception as e:
        print(f"❌ Error Twilio: {e}")
        return Response(content="error", status_code=500)

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
