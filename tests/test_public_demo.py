"""Public demo compare endpoint for landing hero."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from market_core import ensure_db_initialized
from market_server import app

ensure_db_initialized()
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_demo_cache():
    import routers.public_demo as public_demo

    public_demo._cache.clear()
    yield
    public_demo._cache.clear()


def test_public_demo_rejects_unknown_query():
    r = client.get("/public/demo/compare?q=pollo")
    assert r.status_code == 400


def test_public_demo_serves_seed_when_refresh_fails(monkeypatch):
    async def fail_refresh(_query: str):
        raise RuntimeError("collector down")

    monkeypatch.setattr("routers.public_demo._refresh_query", fail_refresh)
    r = client.get("/public/demo/compare?q=arroz")
    assert r.status_code == 200
    data = r.json()
    assert data["demo"] is True
    assert data["seed"] is True
    assert data["comparison"][0]["best_store"] == "plazavea"


def test_public_demo_caches_refresh(monkeypatch):
    calls = {"n": 0}

    async def fake_refresh(query: str):
        calls["n"] += 1
        return {
            "query": query,
            "comparison": [
                {
                    "name": "Arroz test",
                    "brand": "T",
                    "prices": {"plazavea": 2.5},
                    "best_store": "plazavea",
                    "best_price": 2.5,
                }
            ],
            "stores_compared": 5,
        }

    monkeypatch.setattr("routers.public_demo._refresh_query", fake_refresh)
    r1 = client.get("/public/demo/compare?q=leche")
    r2 = client.get("/public/demo/compare?q=leche")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["comparison"][0]["name"] == "Arroz test"
    assert calls["n"] == 1
