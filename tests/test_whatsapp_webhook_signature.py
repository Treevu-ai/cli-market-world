"""Tests for Twilio signature validation on the WhatsApp webhook.

Without signature validation, POST /v1/integrations/whatsapp/webhook trusts the
"From" form field unconditionally. Since routers/integrations/whatsapp.py grants
the admin-scoped MARKET_API_TOKEN to senders in WHATSAPP_ADMIN_NUMBERS, an
unauthenticated attacker could spoof "From" to impersonate an admin number and
gain admin-token-backed access to the internal API. These tests assert Twilio's
X-Twilio-Signature header is required and verified before any of that logic runs.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized
from twilio.request_validator import RequestValidator

from market_server import app
import routers.integrations.whatsapp as whatsapp

ensure_db_initialized()
client = TestClient(app)

WEBHOOK_PATH = "/v1/integrations/whatsapp/webhook"
WEBHOOK_URL = f"http://testserver{WEBHOOK_PATH}"
_TEST_AUTH_TOKEN = "test-twilio-auth-token"


def _valid_signature(params: dict) -> str:
    return RequestValidator(_TEST_AUTH_TOKEN).compute_signature(WEBHOOK_URL, params)


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
def test_missing_signature_header_rejected():
    r = client.post(WEBHOOK_PATH, data={"From": "whatsapp:+15550001111", "Body": "hola"})
    assert r.status_code == 403


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
def test_invalid_signature_rejected():
    r = client.post(
        WEBHOOK_PATH,
        data={"From": "whatsapp:+15550001111", "Body": "hola"},
        headers={"X-Twilio-Signature": "not-a-real-signature"},
    )
    assert r.status_code == 403


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
def test_spoofed_admin_number_rejected_without_valid_signature():
    """An attacker cannot claim an admin number without a matching signature."""
    with patch.object(whatsapp, "WHATSAPP_ADMIN_NUMBERS", {"whatsapp:+15551234567"}):
        r = client.post(
            WEBHOOK_PATH,
            data={"From": "whatsapp:+15551234567", "Body": "hola"},
            headers={"X-Twilio-Signature": "forged"},
        )
        assert r.status_code == 403


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "transcribe_whatsapp_audio")
def test_audio_transcription_never_runs_without_valid_signature(mock_transcribe):
    """Regression pin for the SSRF/credential-leak path: an unsigned request
    carrying an attacker-controlled MediaUrl0 must be rejected before the
    audio branch ever fires transcribe_whatsapp_audio (which sends the real
    Twilio Account SID/Auth Token to that URL)."""
    r = client.post(
        WEBHOOK_PATH,
        data={
            "From": "whatsapp:+15550001111",
            "MediaContentType": "audio/ogg",
            "MediaUrl0": "https://attacker.example.com/exfil",
        },
        headers={"X-Twilio-Signature": "forged"},
    )
    assert r.status_code == 403
    mock_transcribe.assert_not_called()


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch("routers.integrations.whatsapp.Client")
def test_valid_signature_accepted(mock_twilio_client_cls):
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    params = {"From": "whatsapp:+15550001111", "Body": "hola"}
    r = client.post(
        WEBHOOK_PATH,
        data=params,
        headers={"X-Twilio-Signature": _valid_signature(params)},
    )
    assert r.status_code == 200
    mock_twilio_client_cls.return_value.messages.create.assert_called_once()
