"""Tests for per-chat rate limiting on the Telegram webhook.

Without a limit, an authenticated (correct secret-token) chat can still hammer
the webhook to run up paid LLM costs via /v1/intel/ask. These tests assert the
webhook enforces a per-minute cap per chat_id via the existing SQLite rate
limiter (market_core.check_rate_limit_sqlite).
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
_HEADERS = {"X-Telegram-Bot-Api-Secret-Token": _TEST_SECRET}


def _update_body(chat_id: int) -> dict:
    return {"message": {"chat": {"id": chat_id, "first_name": "User"}, "text": "hola"}}


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "TELEGRAM_RATE_LIMIT_MIN", 2)
@patch.object(telegram, "TELEGRAM_RATE_LIMIT_DAY", 1000)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_chat_is_rate_limited_after_threshold(mock_send):
    mock_send.return_value = True
    body = _update_body(90001)

    r1 = client.post(WEBHOOK_PATH, json=body, headers=_HEADERS)
    r2 = client.post(WEBHOOK_PATH, json=body, headers=_HEADERS)
    r3 = client.post(WEBHOOK_PATH, json=body, headers=_HEADERS)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429
    assert mock_send.call_count == 2
