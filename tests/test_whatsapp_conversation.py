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
    assert "Canasta" in reply or "canasta" in reply.lower()


def test_parse_basket_items_multiline_and_semicolon():
    items = conv.parse_basket_items(
        "12 x leche Gloria 390 g\n4 x aceite vegetal 1 L\n2 x arroz extra 5 kg"
    )
    assert items is not None
    assert len(items) == 3
    assert items[0] == {"name": "leche Gloria 390 g", "qty": 12}

    items2 = conv.parse_basket_items("2 x leche Gloria; 1 arroz extra 5 kg")
    assert items2 is not None
    assert len(items2) == 2

    assert conv.parse_basket_items("solo un producto") is None
    assert conv.parse_basket_items("aceite") is None


def test_parse_basket_strips_canasta_prefix():
    items = conv.parse_basket_items("canasta\n2 x leche Gloria\n1 x arroz 5kg")
    assert items is not None
    assert len(items) == 2


@pytest.mark.asyncio
async def test_canasta_command_shows_help(platform_id):
    reply = await conv.handle_standard_turn(
        platform_id,
        "canasta",
        token="tok",
        market_api_url="https://example.test",
    )
    assert "2 y 20" in reply or "2 a 20" in reply.lower() or "entre" in reply.lower()


@pytest.mark.asyncio
async def test_basket_incomplete_blocks_total(platform_id):
    async def fake_basket(items, country, token):
        assert len(items) == 2
        return {"items_searched": 2, "items_found": 1, "stores": []}, 200

    reply = await conv.handle_standard_turn(
        platform_id,
        "2 x leche Gloria 390 g\n1 arroz extra 5 kg",
        token="tok",
        market_api_url="https://example.test",
        basket_fn=fake_basket,
    )
    assert "1" in reply and "2" in reply
    assert "total" in reply.lower() or "Cobertura" in reply


@pytest.mark.asyncio
async def test_basket_complete_lists_stores_and_pick_detail(platform_id):
    async def fake_basket(items, country, token):
        return {
            "items_searched": 2,
            "items_found": 2,
            "stores": [
                {
                    "store": "wong",
                    "store_name": "Wong",
                    "currency": "PEN",
                    "total": 28.4,
                    "items_found": 2,
                    "breakdown": [
                        {
                            "item": "leche Gloria 390 g",
                            "resolved_name": "Leche Gloria 390 g",
                            "brand": "Gloria",
                            "qty": 2,
                            "unit_price": 4.2,
                            "canonical_product_id": "upid-leche",
                            "match_confidence": "high",
                        },
                        {
                            "item": "arroz extra 5 kg",
                            "resolved_name": "Arroz extra 5 kg",
                            "brand": "Costeño",
                            "qty": 1,
                            "unit_price": 20.0,
                            "canonical_product_id": "upid-arroz",
                            "match_confidence": "high",
                        },
                    ],
                }
            ],
        }, 200

    reply = await conv.handle_standard_turn(
        platform_id,
        "2 x leche Gloria 390 g\n1 arroz extra 5 kg",
        token="tok",
        market_api_url="https://example.test",
        basket_fn=fake_basket,
    )
    assert "Wong" in reply
    assert "1." in reply
    assert "cobertura completa" in reply.lower() or "Canasta" in reply

    detail = await conv.handle_standard_turn(
        platform_id,
        "1",
        token="tok",
        market_api_url="https://example.test",
        basket_fn=fake_basket,
    )
    assert "Total observado" in detail
    assert "Gloria" in detail
