import os
import httpx
from fastapi import APIRouter, Request, Response
from twilio.rest import Client

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

    if not incoming_msg or not TWILIO_AUTH_TOKEN or not TWILIO_ACCOUNT_SID:
        return Response(content="ignored", status_code=200)

    print(f"📱 WhatsApp de {sender}: {incoming_msg}")

    # Puente hacia la lógica de market_ask
    market_api_url = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
    token = os.getenv("MARKET_API_TOKEN")

    answer = "Lo siento, tuve un problema consultando los precios."

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
            print(f"❌ Error API: {e}")

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

@router.get("/webhook")
async def whatsapp_verify(request: Request):
    # Opcional: Para verificación si usaras Meta directamente
    return Response(content="ok", status_code=200)
