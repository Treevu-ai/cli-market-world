"""Tests for secret-token validation on the Telegram webhook.

Without validation, POST /v1/integrations/telegram/webhook accepts any JSON
body claiming to be a Telegram update. An unauthenticated attacker can POST an
arbitrary chat_id/text to trigger a paid LLM call (/v1/intel/ask), spam an
attacker-chosen chat_id via sendMessage, and pollute messenger_sessions rows
keyed by attacker-controlled chat_id. These tests assert Telegram's optional
X-Telegram-Bot-Api-Secret-Token header is required and verified before any of
that logic runs.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized

from market_server import app
import routers.integrations.telegram as telegram

ensure_db_initialized()
client = TestClient(app)

WEBHOOK_PATH = "/v1/integrations/telegram/webhook"
_TEST_TOKEN = "test-telegram-bot-token"
_TEST_SECRET = "test-webhook-secret"

_UPDATE_BODY = {
    "message": {
        "chat": {"id": 123456, "first_name": "Attacker"},
        "text": "hola",
    }
}


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", "")
def test_unconfigured_secret_fails_closed():
    """If TELEGRAM_WEBHOOK_SECRET was never deployed, every request must be
    rejected — not silently accepted because there's nothing to compare against."""
    r = client.post(
        WEBHOOK_PATH,
        json=_UPDATE_BODY,
        headers={"X-Telegram-Bot-Api-Secret-Token": "anything"},
    )
    assert r.status_code == 403


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
def test_missing_secret_header_rejected():
    r = client.post(WEBHOOK_PATH, json=_UPDATE_BODY)
    assert r.status_code == 403


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
def test_wrong_secret_header_rejected():
    r = client.post(
        WEBHOOK_PATH,
        json=_UPDATE_BODY,
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert r.status_code == 403


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_no_downstream_calls_without_valid_secret(mock_send):
    """Regression pin: an unauthenticated update must never reach
    _send_telegram (or the /v1/intel/ask bridge) before the secret check."""
    r = client.post(
        WEBHOOK_PATH,
        json=_UPDATE_BODY,
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert r.status_code == 403
    mock_send.assert_not_called()


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_valid_secret_accepted(mock_send):
    mock_send.return_value = True
    r = client.post(
        WEBHOOK_PATH,
        json=_UPDATE_BODY,
        headers={"X-Telegram-Bot-Api-Secret-Token": _TEST_SECRET},
    )
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
    mock_send.assert_called_once()
