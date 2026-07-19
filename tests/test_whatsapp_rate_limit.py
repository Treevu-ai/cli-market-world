"""Tests for per-sender rate limiting on the WhatsApp webhook.

Without a limit, an authenticated (correctly-signed) sender can still hammer
the webhook to run up paid Whisper transcription / LLM costs. These tests
assert the webhook enforces a per-minute cap per sender via the existing
SQLite rate limiter (market_core.check_rate_limit_sqlite).
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
_SENDER = "whatsapp:+15557778888"


def _signed_post(params: dict, **kwargs):
    signature = RequestValidator(_TEST_AUTH_TOKEN).compute_signature(WEBHOOK_URL, params)
    return client.post(WEBHOOK_PATH, data=params, headers={"X-Twilio-Signature": signature}, **kwargs)


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_RATE_LIMIT_MIN", 2)
@patch.object(whatsapp, "WHATSAPP_RATE_LIMIT_DAY", 1000)
@patch("routers.integrations.whatsapp.Client")
def test_sender_is_rate_limited_after_threshold(mock_twilio_client_cls):
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    params = {"From": _SENDER, "Body": "hola"}

    r1 = _signed_post(params)
    r2 = _signed_post(params)
    r3 = _signed_post(params)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429
    # Only the first two requests should have reached the Twilio send step.
    assert mock_twilio_client_cls.return_value.messages.create.call_count == 2


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_RATE_LIMIT_MIN", 1)
@patch.object(whatsapp, "WHATSAPP_RATE_LIMIT_DAY", 1000)
@patch.object(whatsapp, "transcribe_whatsapp_audio")
@patch("routers.integrations.whatsapp.Client")
def test_rate_limit_blocks_before_audio_transcription(mock_twilio_client_cls, mock_transcribe):
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    other_sender = "whatsapp:+15557778889"
    params_text = {"From": other_sender, "Body": "hola"}
    _signed_post(params_text)  # consumes the single allowed request

    params_audio = {"From": other_sender, "MediaContentType": "audio/ogg", "MediaUrl0": "https://api.twilio.com/media"}
    r = _signed_post(params_audio)

    assert r.status_code == 429
    mock_transcribe.assert_not_called()
