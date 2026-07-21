"""Tests for WHATSAPP_ALLOWED_NUMBERS access control on the WhatsApp webhook.

Anyone who joins the Twilio Sandbox can hit the webhook. The allowlist is the
gate: only listed numbers may use the bot / spend LLM quota.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi import BackgroundTasks
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
_ALLOWED = "whatsapp:+51903176598"
_OTHER = "whatsapp:+51999999999"


def _signed_post(params: dict, **kwargs):
    signature = RequestValidator(_TEST_AUTH_TOKEN).compute_signature(WEBHOOK_URL, params)
    return client.post(
        WEBHOOK_PATH,
        data=params,
        headers={"X-Twilio-Signature": signature},
        **kwargs,
    )


def test_normalize_accepts_bare_e164():
    assert whatsapp._normalize_whatsapp_number("+51903176598") == "whatsapp:+51903176598"
    assert whatsapp._normalize_whatsapp_number("whatsapp:+51903176598") == "whatsapp:+51903176598"
    assert whatsapp._normalize_whatsapp_number("51903176598") == "whatsapp:+51903176598"


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_ALLOWED_NUMBERS", {_ALLOWED})
@patch("routers.integrations.whatsapp.Client")
def test_allowed_sender_is_processed(mock_twilio_client_cls):
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    r = _signed_post({"From": _ALLOWED, "Body": "hola"})
    assert r.status_code == 200
    assert "<Response></Response>" in r.text
    mock_twilio_client_cls.return_value.messages.create.assert_called_once()
    _, kwargs = mock_twilio_client_cls.return_value.messages.create.call_args
    assert "CLI Market" in kwargs["body"]


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_ALLOWED_NUMBERS", {_ALLOWED})
@patch("routers.integrations.whatsapp.Client")
def test_unknown_sender_is_denied_without_llm(mock_twilio_client_cls):
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    with patch.object(BackgroundTasks, "add_task", autospec=True) as mock_add_task:
        r = _signed_post({"From": _OTHER, "Body": "precio de leche"})

    assert r.status_code == 200
    assert "<Response></Response>" in r.text
    # Denial is scheduled; price processing is not.
    mock_add_task.assert_called_once()
    args = mock_add_task.call_args[0]
    assert args[1] is whatsapp._reply_denied
    assert args[2] == _OTHER


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_ALLOWED_NUMBERS", {_ALLOWED})
@patch("routers.integrations.whatsapp.Client")
def test_denied_sender_gets_plain_language_message(mock_twilio_client_cls):
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    r = _signed_post({"From": _OTHER, "Body": "hola"})
    assert r.status_code == 200
    mock_twilio_client_cls.return_value.messages.create.assert_called_once()
    _, kwargs = mock_twilio_client_cls.return_value.messages.create.call_args
    assert "no está autorizado" in kwargs["body"]


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch.object(whatsapp, "WHATSAPP_ALLOWED_NUMBERS", set())
@patch("routers.integrations.whatsapp.Client")
def test_empty_allowlist_allows_any_sender(mock_twilio_client_cls):
    """Empty allowlist keeps legacy open mode (any sandbox joiner)."""
    mock_twilio_client_cls.return_value.messages.create = MagicMock()
    r = _signed_post({"From": _OTHER, "Body": "hola"})
    assert r.status_code == 200
    mock_twilio_client_cls.return_value.messages.create.assert_called_once()
    _, kwargs = mock_twilio_client_cls.return_value.messages.create.call_args
    assert "CLI Market" in kwargs["body"]
