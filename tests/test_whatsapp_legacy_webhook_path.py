"""Regression: Twilio Console may still POST to /whatsapp/webhook.

Live incident 2026-08-05: registered numbers sent "hola" and got silence.
Fly logs showed POST /whatsapp/webhook → 404 while the canonical route
/v1/integrations/whatsapp/webhook was healthy. The legacy alias must accept
the same signed Twilio requests.
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from twilio.request_validator import RequestValidator

from market_server import app
import routers.integrations.whatsapp as whatsapp

ensure_db_initialized()
client = TestClient(app)

LEGACY_PATH = "/whatsapp/webhook"
LEGACY_URL = f"http://testserver{LEGACY_PATH}"
CANONICAL_PATH = "/v1/integrations/whatsapp/webhook"
_TEST_AUTH_TOKEN = "test-twilio-auth-token"


def _valid_signature(params: dict, url: str = LEGACY_URL) -> str:
    return RequestValidator(_TEST_AUTH_TOKEN).compute_signature(url, params)


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
def test_legacy_path_rejects_missing_signature():
    r = client.post(LEGACY_PATH, data={"From": "whatsapp:+15550001111", "Body": "hola"})
    assert r.status_code == 403
    assert r.text == "invalid signature"


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_ALLOWED_NUMBERS", {"whatsapp:+15550001111"})
@patch.object(whatsapp, "HORECA_ENABLED", False)
def test_legacy_path_accepts_valid_signature_and_returns_empty_twiml():
    params = {"From": "whatsapp:+15550001111", "Body": "hola", "To": "whatsapp:+14155238886"}
    r = client.post(
        LEGACY_PATH,
        data=params,
        headers={"X-Twilio-Signature": _valid_signature(params)},
    )
    assert r.status_code == 200
    assert "Response" in r.text
    assert r.headers.get("content-type", "").startswith("application/xml")


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
def test_legacy_and_canonical_health_both_ok():
    r1 = client.get("/whatsapp/health")
    r2 = client.get("/v1/integrations/whatsapp/health")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["status"] == "ok"
    assert r2.json()["webhook_path_legacy"] == LEGACY_PATH
    assert r2.json()["webhook_path"] == CANONICAL_PATH
