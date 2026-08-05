"""Unit tests for the standard WhatsApp conversation funnel."""

from __future__ import annotations

import json

import pytest

from market_core import ensure_db_initialized, get_db
from routers.integrations import whatsapp_conversation as conv
from server_deps import get_messenger_session, update_messenger_session

ensure_db_initialized()


def _ensure_messenger_sessions_table() -> None:
    """Table is normally created in market_server lifespan; tests may not run it."""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS messenger_sessions (
            platform_id TEXT PRIMARY KEY,
            username TEXT,
            last_context TEXT,
            last_query TEXT,
            last_country TEXT,
            user_tier TEXT DEFAULT 'starter',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


@pytest.fixture
def platform_id():
    _ensure_messenger_sessions_table()
    pid = "whatsapp:+51999000001"
    update_messenger_session(pid, context=json.dumps({"type": conv.FLOW_TYPE, "state": "idle"}))
    return pid


def test_classify_vague_family():
    assert conv.classify_specificity("aceite") == "vague"
    assert conv.classify_specificity("LIMPIEZA") == "vague"
    assert conv.classify_specificity("pollo") == "vague"


def test_classify_medium_and_specific():
    assert conv.classify_specificity("aceite vegetal") == "medium"
    assert conv.classify_specificity("aceite Primor 1L") == "specific"
    assert conv.classify_specificity("leche gloria evaporada 400g") == "specific"


def test_classify_intel_and_pick():
    assert conv.classify_specificity("compara leche evaporada en Lima") == "intel"
    assert conv.classify_specificity("va a subir el arroz") == "intel"
    assert conv.classify_specificity("2") == "pick"
    assert conv.classify_specificity("hola") == "greeting"
    assert conv.classify_specificity("menu") == "help"


@pytest.mark.asyncio
async def test_vague_prompts_clarify_without_search(platform_id):
    async def boom(*_a, **_k):
        raise AssertionError("search must not run on vague turn")

    reply = await conv.handle_standard_turn(
        platform_id,
        "aceite",
        token="tok",
        market_api_url="https://example.test",
        search_fn=boom,
    )
    assert "Vegetal" in reply or "vegetal" in reply.lower()
    assert "1." in reply
    state = json.loads(get_messenger_session(platform_id)["last_context"])
    assert state["state"] == "clarify"
    assert state["family"] == "aceite"


@pytest.mark.asyncio
async def test_clarify_choice_triggers_search(platform_id):
    _ensure_messenger_sessions_table()
    update_messenger_session(
        platform_id,
        context=json.dumps(
            {
                "type": conv.FLOW_TYPE,
                "state": "clarify",
                "family": "aceite",
                "country": "PE",
                "clarify_options": conv._FAMILY_CLARIFY["aceite"],
            },
            ensure_ascii=False,
        ),
    )
    seen = {}

    async def fake_search(query, country, token):
        seen["query"] = query
        seen["country"] = country
        return [
            {
                "id": "1",
                "name": "Aceite Primor 1L",
                "brand": "Primor",
                "price": 12.5,
                "currency": "PEN",
                "store_name": "Wong",
            },
            {
                "id": "2",
                "name": "Aceite Cocinero 900ml",
                "brand": "Cocinero",
                "price": 10.9,
                "currency": "PEN",
                "store_name": "Metro",
            },
        ]

    reply = await conv.handle_standard_turn(
        platform_id,
        "1",
        token="tok",
        market_api_url="https://example.test",
        search_fn=fake_search,
    )
    assert "Primor" in reply
    assert "1." in reply and "2." in reply
    assert "vegetal" in seen["query"].lower() or "soya" in seen["query"].lower()
    state = json.loads(get_messenger_session(platform_id)["last_context"])
    assert state["state"] == "candidates"
    assert len(state["candidates"]) == 2


@pytest.mark.asyncio
async def test_pick_candidate_shows_detail(platform_id):
    _ensure_messenger_sessions_table()
    update_messenger_session(
        platform_id,
        context=json.dumps(
            {
                "type": conv.FLOW_TYPE,
                "state": "candidates",
                "country": "PE",
                "query": "aceite vegetal",
                "candidates": [
                    {
                        "id": "1",
                        "name": "Aceite Primor 1L",
                        "brand": "Primor",
                        "price": 12.5,
                        "currency": "PEN",
                        "store_name": "Wong",
                    }
                ],
            },
            ensure_ascii=False,
        ),
    )

    async def no_search(*_a, **_k):
        raise AssertionError("no search")

    reply = await conv.handle_standard_turn(
        platform_id,
        "1",
        token="tok",
        market_api_url="https://example.test",
        search_fn=no_search,
    )
    assert "Primor" in reply
    assert "Wong" in reply
    assert "S/" in reply


@pytest.mark.asyncio
async def test_medium_query_searches_catalog(platform_id):
    async def fake_search(query, country, token):
        assert query == "aceite vegetal"
        assert country == "PE"
        return [
            {
                "id": "9",
                "name": "Aceite Vegetal 1L",
                "brand": "Cocinero",
                "price": 11,
                "currency": "PEN",
                "store_name": "PlazaVea",
            }
        ]

    reply = await conv.handle_standard_turn(
        platform_id,
        "aceite vegetal",
        token="tok",
        market_api_url="https://example.test",
        search_fn=fake_search,
    )
    assert "PlazaVea" in reply
    assert "1." in reply


@pytest.mark.asyncio
async def test_intel_path_uses_guardrails(platform_id):
    seen = {}

    async def fake_intel(question, token):
        seen["q"] = question
        return "Respuesta de prueba"

    reply = await conv.handle_standard_turn(
        platform_id,
        "compara leche evaporada en Lima",
        token="tok",
        market_api_url="https://example.test",
        intel_fn=fake_intel,
        search_fn=lambda *a, **k: (_ for _ in ()).throw(AssertionError("no search")),
    )
    assert reply == "Respuesta de prueba"
    assert "verificables" in seen["q"].lower() or "verificable" in seen["q"].lower()


@pytest.mark.asyncio
async def test_welcome_on_hola(platform_id):
    reply = await conv.handle_standard_turn(
        platform_id,
        "hola",
        token="tok",
        market_api_url="https://example.test",
    )
    assert "CLI Market" in reply
    assert "Mal:" in reply or "mal" in reply.lower()
    assert "Bien:" in reply or "bien" in reply.lower()
