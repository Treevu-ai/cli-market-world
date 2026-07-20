"""Regression test: the WhatsApp webhook must ack Twilio immediately instead
of blocking on the LLM call (up to 30s, see /v1/intel/ask's httpx timeout).

Real-world symptom this pins: a user texted "1", got Twilio Sandbox's own
"You said :1. Configure your WhatsApp Sandbox's Inbound URL..." fallback
message, and THEN got the real bot answer seconds later as a separate
message. Twilio's webhook has its own response timeout; when our handler
blocks synchronously on an LLM call before returning any HTTP response,
Twilio gives up waiting and falls back to its canned Sandbox message —
while our handler keeps running and sends the real answer late, out of
band, via the Twilio REST API. The fix: return the webhook's HTTP response
immediately (fast checks only — signature, rate limit, has-a-body), and
defer the slow work (LLM call, audio transcription, Twilio send) to a
FastAPI BackgroundTask, which Starlette/uvicorn only run *after* the
response has already been sent to Twilio.
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


def _signed_post(params: dict, **kwargs):
    signature = RequestValidator(_TEST_AUTH_TOKEN).compute_signature(WEBHOOK_URL, params)
    return client.post(WEBHOOK_PATH, data=params, headers={"X-Twilio-Signature": signature}, **kwargs)


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch("routers.integrations.whatsapp.Client")
def test_message_processing_is_deferred_to_a_background_task(mock_twilio_client_cls):
    """The slow work (LLM call + Twilio send) must be scheduled via
    BackgroundTasks.add_task, not awaited inline before the response is
    built — that's what lets uvicorn send the ack to Twilio before this
    work even starts running."""
    mock_twilio_client_cls.return_value.messages.create = MagicMock()

    with patch.object(BackgroundTasks, "add_task", autospec=True) as mock_add_task:
        r = _signed_post({"From": "whatsapp:+15559990000", "Body": "hola"})

    assert r.status_code == 200
    mock_add_task.assert_called_once()
    # The Twilio send must NOT have happened synchronously within the request —
    # only the (mocked-away) background task would have triggered it.
    mock_twilio_client_cls.return_value.messages.create.assert_not_called()


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
@patch("routers.integrations.whatsapp.Client")
def test_end_to_end_reply_still_sent_once_background_task_runs(mock_twilio_client_cls):
    """Without mocking away BackgroundTasks (TestClient runs them before
    returning), the real answer must still reach Twilio's REST API exactly
    once — the fix changes *when* this happens relative to the HTTP
    response, not *whether* it happens."""
    mock_twilio_client_cls.return_value.messages.create = MagicMock()

    r = _signed_post({"From": "whatsapp:+15559990001", "Body": "hola"})

    assert r.status_code == 200
    mock_twilio_client_cls.return_value.messages.create.assert_called_once()
    _, kwargs = mock_twilio_client_cls.return_value.messages.create.call_args
    assert "CLI Market" in kwargs["body"]


@patch.object(whatsapp, "TWILIO_AUTH_TOKEN", _TEST_AUTH_TOKEN)
def test_empty_body_and_no_media_returns_fast_without_queuing_background_work():
    """Nothing to process — must not even schedule a background task."""
    with patch.object(BackgroundTasks, "add_task", autospec=True) as mock_add_task:
        r = _signed_post({"From": "whatsapp:+15559990002", "Body": ""})

    assert r.status_code == 200
    mock_add_task.assert_not_called()
