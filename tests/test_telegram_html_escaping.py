"""Regression test: Telegram messages must escape user/LLM-controlled text
before interpolating it into an HTML-parse-mode message.

_send_telegram() sets parse_mode: "HTML" unconditionally. first_name (from
the Telegram update, user-controlled — a display name can legally contain
"&", "<", ">") and answer (LLM-generated via /v1/intel/ask, also not under
our control) were interpolated raw into HTML-formatted strings. Telegram's
HTML parser then either mangles the message or rejects it outright with a
400, which _send_telegram's bare `except Exception: return False` swallows
silently — the bot goes mute for that user with no visible error anywhere.
procure-telegram-bot hit and fixed this exact bug class already (see
src/lib/format.ts's esc()); it was never ported to this bot.
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
_AUTH_HEADERS = {"X-Telegram-Bot-Api-Secret-Token": _TEST_SECRET}


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
@patch.object(telegram, "_edit_telegram", new_callable=AsyncMock)
def test_first_name_with_html_special_chars_is_escaped_in_welcome_message(mock_edit, mock_send):
    # The webhook sends a "🔍 Buscando..." placeholder via _send_telegram,
    # then the background task edits it in place via _edit_telegram with the
    # real (escaped) welcome text — assert against the edit, not the send.
    mock_send.return_value = "1"
    mock_edit.return_value = True
    body = {
        "message": {
            "chat": {"id": 999, "first_name": "R&D <Team>"},
            "text": "hola",
        }
    }
    r = client.post(WEBHOOK_PATH, json=body, headers=_AUTH_HEADERS)

    assert r.status_code == 200
    mock_edit.assert_called_once()
    sent_text = mock_edit.call_args.args[2]
    assert "R&amp;D &lt;Team&gt;" in sent_text
    # No raw, unescaped user input leaked into the HTML-parsed message.
    assert "R&D <Team>" not in sent_text


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
@patch.object(telegram, "_edit_telegram", new_callable=AsyncMock)
@patch("httpx.AsyncClient.post")
def test_llm_answer_with_html_special_chars_is_escaped(mock_post, mock_edit, mock_send):
    mock_send.return_value = "1"
    mock_edit.return_value = True
    mock_post.return_value.status_code = 200
    mock_post.return_value.json = lambda: {
        "answer": "El precio subió 5% & bajó <b>ayer</b> (fake tag)"
    }
    body = {
        "message": {
            "chat": {"id": 998, "first_name": "Ana"},
            "text": "cuanto cuesta el arroz",
        }
    }
    r = client.post(WEBHOOK_PATH, json=body, headers=_AUTH_HEADERS)

    assert r.status_code == 200
    mock_edit.assert_called_once()
    sent_text = mock_edit.call_args.args[2]
    assert "5% &amp; bajó &lt;b&gt;ayer&lt;/b&gt;" in sent_text
    assert "<b>ayer</b>" not in sent_text


@patch.object(telegram, "TELEGRAM_TOKEN", _TEST_TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _TEST_SECRET)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
@patch.object(telegram, "_edit_telegram", new_callable=AsyncMock)
@patch("httpx.AsyncClient.post")
def test_llm_answer_markdown_bold_is_rendered_as_html_bold(mock_post, mock_edit, mock_send):
    """ask_intel answers are written in Markdown (**bold**); sent with
    parse_mode: "HTML" they must become <b>...</b>, not show literal
    asterisks (reported live 2026-07-20)."""
    mock_send.return_value = "1"
    mock_edit.return_value = True
    mock_post.return_value.status_code = 200
    mock_post.return_value.json = lambda: {
        "answer": "**Leche Evaporada Gloria**: 4.20 PEN en Wong"
    }
    body = {
        "message": {
            "chat": {"id": 997, "first_name": "Ana"},
            "text": "leche evaporada en peru",
        }
    }
    r = client.post(WEBHOOK_PATH, json=body, headers=_AUTH_HEADERS)

    assert r.status_code == 200
    mock_edit.assert_called_once()
    sent_text = mock_edit.call_args.args[2]
    assert "<b>Leche Evaporada Gloria</b>" in sent_text
    assert "**" not in sent_text
