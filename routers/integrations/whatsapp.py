import os
import httpx
from fastapi import APIRouter, Request, Response
from twilio.rest import Client
from server_deps import get_messenger_session, update_messenger_session

router = APIRouter(prefix="/v1/integrations/whatsapp", tags=["integrations"])

# Configuración Twilio (Cargar desde variables de entorno)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    # Twilio envía los datos como Form Data (application/x-www-form-urlencoded)
    form_data = await request.form()
    incoming_msg = form_data.get("Body", "").lower()
    sender = form_data.get("From", "")

    if not incoming_msg or not TWILIO_AUTH_TOKEN:
        return Response(content="ignored", status_code=200)

    # 1. Recover session memory
    session = get_messenger_session(sender)
    context = session.get("last_context")
    user_tier = session.get("user_tier", "starter")
    
    # If we have context, we can use it to refine the query
    effective_query = incoming_msg
    if context:
        effective_query = f"Context: {context}\nUser: {incoming_msg}"

    # Puente hacia la lógica de market_ask
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    token = os.getenv("MARKET_API_TOKEN")
    
    answer = "Lo siento, tuve un problema consultando los precios."
    
    async with httpx.AsyncClient() as client_http:
        try:
            response = await client_http.post(
                f"{market_api_url}/v1/shop/ask",
                json={"query": effective_query, "country": "PE"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            if response.status_code == 200:
                answer = response.json().get("answer", answer)
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
