"""P1 interaction controls for the CLI Market Telegram bot."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from market_core import ensure_db_initialized

from market_server import app
import routers.integrations.telegram as telegram
from server_deps import update_messenger_session


ensure_db_initialized()
client = TestClient(app)

WEBHOOK_PATH = "/v1/integrations/telegram/webhook"
_TOKEN = "telegram-test-token"
_SECRET = "telegram-test-secret"
_HEADERS = {"X-Telegram-Bot-Api-Secret-Token": _SECRET}


@patch.object(telegram, "TELEGRAM_TOKEN", _TOKEN)
@patch.object(telegram, "TELEGRAM_PUBLIC_MODE", True)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _SECRET)
@patch.object(telegram, "_process_incoming_message", new_callable=AsyncMock)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_group_messages_are_rejected_before_intelligence(mock_send, mock_process):
    body = {
        "update_id": 880001,
        "message": {
            "chat": {"id": -100123, "type": "group"},
            "from": {"id": 44, "first_name": "Usuario"},
            "text": "cotiza leche",
        },
    }

    response = client.post(WEBHOOK_PATH, json=body, headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "private_chat_required"
    mock_process.assert_not_called()
    assert "chat privado" in mock_send.call_args.args[1]


@patch.object(telegram, "TELEGRAM_TOKEN", _TOKEN)
@patch.object(telegram, "TELEGRAM_WEBHOOK_SECRET", _SECRET)
@patch.object(telegram, "TELEGRAM_PUBLIC_MODE", False)
@patch.object(telegram, "TELEGRAM_ALLOWED_CHAT_IDS", set())
@patch.object(telegram, "_process_incoming_message", new_callable=AsyncMock)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_empty_allowlist_keeps_private_pilot_closed(mock_send, mock_process):
    body = {
        "update_id": 880002,
        "message": {
            "chat": {"id": 45, "type": "private"},
            "from": {"id": 45, "first_name": "Usuario"},
            "text": "cotiza leche",
        },
    }

    response = client.post(WEBHOOK_PATH, json=body, headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "denied"
    mock_process.assert_not_called()
    assert "no está autorizado" in mock_send.call_args.args[1]


@patch.object(telegram, "TELEGRAM_TOKEN", _TOKEN)
@patch.object(telegram, "_telegram_api", new_callable=AsyncMock)
def test_registers_private_spanish_command_menu(mock_api):
    mock_api.return_value = None

    asyncio.run(telegram.register_telegram_commands())

    method, payload = mock_api.call_args.args
    assert method == "setMyCommands"
    assert payload["scope"] == {"type": "all_private_chats"}
    assert payload["language_code"] == "es"
    assert {item["command"] for item in payload["commands"]} == {"cotizar", "buscar", "ayuda"}


def _ensure_messenger_sessions_table() -> None:
    from market_core import get_db

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


@patch.object(telegram, "_search_catalog", new_callable=AsyncMock)
@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_buscar_uses_structured_catalog_results_not_intel(mock_send, mock_search):
    _ensure_messenger_sessions_table()
    mock_search.return_value = [{
        "id": "p-1", "name": "Café Altomayo clásico 180 g", "brand": "Altomayo",
        "price": 15.9, "currency": "PEN", "store_name": "Wong", "stock": True,
        "confidence": 0.91, "canonical_product_id": "upid-cafe-180g",
        "queried_at": "2026-08-01 10:00:00",
    }]

    asyncio.run(telegram._process_message("801", "801", None, "/buscar café Altomayo clásico 180 g", "Ana"))

    assert mock_search.await_count == 1
    answer = mock_send.call_args.args[1]
    keyboard = mock_send.call_args.args[2]
    assert "Resultados para" in answer
    assert keyboard["inline_keyboard"][0][0]["callback_data"] == "pick:0"


@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
def test_selected_catalog_candidate_is_shown_as_observed_offer(mock_send):
    _ensure_messenger_sessions_table()
    context = json.dumps({
        "type": "catalog_candidates",
        "query": "café Altomayo 180 g",
        "country": "PE",
        "candidates": [{
            "id": "p-1", "name": "Café Altomayo clásico 180 g", "brand": "Altomayo",
            "price": 15.9, "currency": "PEN", "store_name": "Wong", "stock": True,
            "confidence": 0.91, "canonical_product_id": "upid-cafe-180g",
            "observed_at": "2026-08-01 10:00:00",
        }],
    })
    update_messenger_session("telegram:802", context=context)

    asyncio.run(telegram._process_callback("802", "802", "40", "pick:0"))

    answer = mock_send.call_args.args[1]
    assert "Oferta observada" in answer
    assert "S/ 15.9" in answer
    assert "Identidad canónica: registrada" in answer
    assert "Última observación: 2026-08-01 10:00:00" in answer
    assert "más barata" not in answer


def test_long_telegram_text_is_split_under_limit_without_format_tags():
    text = "<b>" + ("producto observado " * 300) + "</b>"

    chunks = telegram._split_telegram_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 3900 for chunk in chunks)
    assert all("<b>" not in chunk and "</b>" not in chunk for chunk in chunks)


@patch.object(telegram, "_compare_basket", new_callable=AsyncMock)
def test_incomplete_basket_blocks_total_and_recommendation(mock_compare):
    _ensure_messenger_sessions_table()
    mock_compare.return_value = ({"items_searched": 2, "items_found": 1, "stores": []}, 200)

    answer, keyboard = asyncio.run(
        telegram._process_basket_input("810", "telegram:810", "2 x leche Gloria 390 g\n1 arroz extra 5 kg", "token")
    )

    assert "1 de 2" in answer
    assert "No mostraré total" in answer
    assert keyboard["force_reply"] is True


@patch.object(telegram, "_send_telegram", new_callable=AsyncMock)
@patch.object(telegram, "_compare_basket", new_callable=AsyncMock)
def test_complete_basket_requires_store_review_before_observed_total(mock_compare, mock_send):
    _ensure_messenger_sessions_table()
    mock_compare.return_value = ({
        "items_searched": 2,
        "items_found": 2,
        "stores": [{
            "store": "wong", "store_name": "Wong", "currency": "PEN", "total": 28.4,
            "items_found": 2, "data_freshness": "ok", "data_age_hours": 2.5,
            "breakdown": [
                {"item": "leche Gloria 390 g", "resolved_name": "Leche Gloria 390 g", "brand": "Gloria", "qty": 2, "unit_price": 4.2, "canonical_product_id": "upid-leche-390g", "observed_at": "2026-08-01 10:00:00", "match_confidence": "high"},
                {"item": "arroz extra 5 kg", "resolved_name": "Arroz extra 5 kg", "brand": "Costeño", "qty": 1, "unit_price": 20.0, "canonical_product_id": "upid-arroz-5kg", "observed_at": "2026-08-01 10:00:00", "match_confidence": "high"},
            ],
        }],
    }, 200)

    answer, keyboard = asyncio.run(
        telegram._process_basket_input("811", "telegram:811", "2 x leche Gloria 390 g\n1 arroz extra 5 kg", "token")
    )

    assert "cobertura completa" in answer
    assert "Total observado" not in answer
    assert keyboard["inline_keyboard"][0][0]["callback_data"] == "basket:0"

    asyncio.run(telegram._process_callback("811", "811", "41", "basket:0"))
    detail = mock_send.call_args.args[1]
    assert "Total observado" in detail
    assert "Identidad canónica: registrada" in detail
    assert "Coincidencia: high" in detail
    assert "recomendación de compra" in detail


@patch.object(telegram, "_compare_basket", new_callable=AsyncMock)
def test_complete_basket_without_high_identity_confidence_stays_blocked(mock_compare):
    _ensure_messenger_sessions_table()
    mock_compare.return_value = ({
        "items_searched": 2,
        "items_found": 2,
        "stores": [{
            "store": "wong", "store_name": "Wong", "currency": "PEN", "total": 28.4,
            "items_found": 2,
            "breakdown": [
                {"item": "leche", "resolved_name": "Leche Gloria 390 g", "qty": 1, "canonical_product_id": "upid-leche", "match_confidence": "medium"},
                {"item": "arroz", "resolved_name": "Arroz extra 5 kg", "qty": 1, "canonical_product_id": "upid-arroz", "match_confidence": "high"},
            ],
        }],
    }, 200)

    answer, keyboard = asyncio.run(
        telegram._process_basket_input("812", "telegram:812", "leche\narroz", "token")
    )

    assert "no puedo verificar" in answer
    assert "No mostraré total" in answer
    assert keyboard["force_reply"] is True
