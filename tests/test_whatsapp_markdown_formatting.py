"""Regression test: ask_intel answers use standard Markdown (**bold**), but
WhatsApp's own formatting uses a single asterisk (*bold*) — sent through
unmodified, users saw literal double asterisks instead of bold text (same
bug class reported live on Telegram 2026-07-20; WhatsApp shares the same
/v1/intel/ask answer and had never converted it either).
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

WEBHOOK_PATH = "/v1/integrations/whatsapp/webhook"
WEBHOOK_URL = f"http://testserver{WEBHOOK_PATH}"
_TEST_AUTH_TOKEN = "test-twilio-auth-token"


def _signed_post(params: dict, **kwargs):
    signature = RequestValidator(_TEST_AUTH_TOKEN).compute_signature(WEBHOOK_URL, params)
    return client.post(WEBHOOK_PATH, data=params, headers={"X-Twilio-Signature": signature}, **kwargs)


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch("routers.integrations.whatsapp.Client")
@patch("httpx.AsyncClient.post")
def test_llm_answer_markdown_bold_is_rendered_as_whatsapp_bold(mock_post, mock_twilio_client_cls):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json = lambda: {
        "answer": "**Leche Evaporada Gloria**: 4.20 PEN en Wong"
    }

    r = _signed_post({"From": "whatsapp:+15559990010", "Body": "leche evaporada en peru"})

    assert r.status_code == 200
    mock_twilio_client_cls.return_value.messages.create.assert_called_once()
    _, kwargs = mock_twilio_client_cls.return_value.messages.create.call_args
    assert "*Leche Evaporada Gloria*" in kwargs["body"]
    assert "**" not in kwargs["body"]
