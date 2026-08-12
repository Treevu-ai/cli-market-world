"""Regression tests for /agent/ask basket-intent routing.

"compara la mejor combinacion de canasta basica para peru" used to be
routed to action=compare with the whole sentence as a free-text query for
POST /products/compare (single-SKU fuzzy match). Generic Spanish words in
the sentence ("canasta", "para") then OR-matched unrelated products
("Canastilla de Acero", "CHOCOLATE PARA TAZA"). Basket-shaped queries
should route to action=basket (GET /v1/basket) instead.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import db_create_api_key, db_save_user, ensure_db_initialized
from market_server import app, hash_password


@pytest.fixture
def agent_client(isolated_db):
    ensure_db_initialized()
    import market_billing

    db_save_user("agent-user", hash_password("market"), "agent@test.com")
    market_billing.db_set_subscription("agent-user", "pro")
    key = db_create_api_key("agent-user", "read", "agent-ask-test")["key"]
    headers = {"Authorization": f"Bearer {key}"}
    with TestClient(app) as client:
        yield client, headers


def test_ask_canasta_basica_routes_to_basket_action(agent_client):
    client, headers = agent_client
    r = client.post(
        "/agent/ask",
        json={"prompt": "compara la mejor combinación de canasta basica para peru"},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["action"] == "basket"
    assert body["country"] == "PE"


def test_ask_canasta_basica_without_country(agent_client):
    client, headers = agent_client
    r = client.post(
        "/agent/ask",
        json={"prompt": "compara la canasta basica"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["action"] == "basket"
    assert "country" not in r.json()


def test_ask_single_product_compare_still_works(agent_client):
    client, headers = agent_client
    r = client.post(
        "/agent/ask",
        json={"prompt": "compara leche gloria"},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["action"] == "compare"
    assert body["query"] == "leche gloria"


def test_ask_canasta_de_frutas_is_not_treated_as_basket(agent_client):
    """"canasta" alone (no basica/familiar/combinacion qualifier) is a
    plausible single-SKU product name and should stay on the compare path."""
    client, headers = agent_client
    r = client.post(
        "/agent/ask",
        json={"prompt": "compara canasta de frutas"},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["action"] == "compare"
    assert body["query"] == "canasta de frutas"
