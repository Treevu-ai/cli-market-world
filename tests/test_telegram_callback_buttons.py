"""Tests for Telegram inline-keyboard button handling (callback_query updates).

Buttons attached to a search answer ("🔄 Comparar tiendas", "📈 ¿Va a subir?",
"🔔 Avisarme si baja") dispatch directly against the session's last_query/
last_country instead of asking the LLM to reinterpret free text — the fix for
the tool-selection ambiguity that caused real product queries ("café",
"nescafe en Wong") to come back as fabricated or "no encontré resultados"
despite the underlying data being correct and queryable.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized, get_db

from market_server import app
import routers.integrations.telegram as telegram
from server_deps import update_messenger_session

ensure_db_initialized()


def _ensure_messenger_sessions_table() -> None:
    """TestClient(app) without a `with` block never runs market_server's
    lifespan, so messenger_sessions (created there) doesn't exist yet —
    mirror that migration here so tests can call update_messenger_session
    directly."""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS messenger_sessions (
            platform_id TEXT PRIMARY KEY,
            username TEXT,
            last_context TEXT,
            last_query TEXT,
            last_country TEXT,
            user_tier TEXT DEFAULT 'starter',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    db.commit()
    db.close()


client = TestClient(app)

WEBHOOK_PATH = "/v1/integrations/telegram/webhook"
_TEST_TOKEN = "test-telegram-bot-token"
_TEST_SECRET = "test-webhook-secret"
_AUTH_HEADERS = {"X-Telegram-Bot-Api-Secret-Token": _TEST_SECRET}


def _callback_body(chat_id: int, message_id: int, action: str, callback_id: str = "cbq1") -> dict:
    return {
        "callback_query": {
            "id": callback_id,
            "data": action,
            "message": {"message_id": message_id, "chat": {"id": chat_id}},
        }
    }


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_telegram_api", new_callable=AsyncMock)
def test_callback_query_answers_immediately(mock_api):
    """Telegram leaves a perpetual loading spinner on the button until
    answerCallbackQuery is called — must happen regardless of downstream
    success/failure."""
    mock_api.return_value = None
    body = _callback_body(70001, 5001, "cmp")

    r = client.post(WEBHOOK_PATH, json=body, headers=_AUTH_HEADERS)

    assert r.status_code == 200
    methods_called = [call.args[0] for call in mock_api.call_args_list]
    assert "answerCallbackQuery" in methods_called


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_answer_callback_query", new_callable=AsyncMock)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
@patch("httpx.AsyncClient.post")
def test_callback_query_reuses_last_query_without_retyping(mock_post, mock_send, mock_answer):
    """A button press must re-run the last search using session context
    (last_query/last_country), not require the user to type the product
    name again. The result must be a NEW message (_send_telegram), not an
    edit of the original — editing in place meant a second button press
    silently erased the first button's answer (reported live 2026-07-20)."""
    _ensure_messenger_sessions_table()
    update_messenger_session(
        "70002", context="prior turn", last_query="nescafe", last_country="PE"
    )
    mock_post.return_value.status_code = 200
    mock_post.return_value.json = lambda: {"answer": "S/16.00 en Wong"}

    body = _callback_body(70002, 5002, "cmp")
    r = client.post(WEBHOOK_PATH, json=body, headers=_AUTH_HEADERS)

    assert r.status_code == 200
    mock_send.assert_called_once()
    sent_question = mock_post.call_args.kwargs["json"]["question"]
    assert "nescafe" in sent_question
    assert "PE" in sent_question
    assert "S/16.00 en Wong" in mock_send.call_args.args[1]


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_answer_callback_query", new_callable=AsyncMock)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_callback_query_without_prior_session_asks_to_retype(mock_send, mock_answer):
    body = _callback_body(70003, 5003, "trend")
    r = client.post(WEBHOOK_PATH, json=body, headers=_AUTH_HEADERS)

    assert r.status_code == 200
    mock_send.assert_called_once()
    assert "expiró" in mock_send.call_args.args[1]


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
def test_callback_query_rejected_without_valid_secret():
    body = _callback_body(70004, 5004, "cmp")
    r = client.post(
        WEBHOOK_PATH, json=body, headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"}
    )
    assert r.status_code == 403
