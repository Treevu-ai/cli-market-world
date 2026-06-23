"""Tests for market optimize command helpers and core v1 route mount."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from market_cli import _parse_basket_items, _unwrap_v1

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_unwrap_v1_envelope():
    payload = {"data": {"status": "ok", "mission": "optimize_purchase"}, "meta": {}, "trace": {}}
    assert _unwrap_v1(payload)["status"] == "ok"
    assert _unwrap_v1({"status": "ok"})["status"] == "ok"


def test_parse_basket_items():
    items = _parse_basket_items(["leche:2", "arroz", "aceite:3"])
    assert items == [
        {"name": "leche", "qty": 2},
        {"name": "arroz", "qty": 1},
        {"name": "aceite", "qty": 3},
    ]


def test_market_server_mounts_core_v1_router():
    text = (REPO_ROOT / "market_server.py").read_text(encoding="utf-8")
    assert "from market_core.api_routes import router as core_v1_router" in text
    assert "core_api_routes._auth_fn = require_api_key" in text
    assert 'app.include_router(core_v1_router, prefix="/v1")' in text


def _load_server_app():
    try:
        from market_core import ensure_db_initialized
        from market_server import app

        ensure_db_initialized()
        return app
    except ModuleNotFoundError as exc:
        pytest.skip(f"world server runtime deps missing: {exc}")


def test_optimize_purchase_route_mounted():
    client = TestClient(_load_server_app())
    response = client.post(
        "/v1/missions/optimize-purchase",
        json={"items": [{"name": "leche", "qty": 1}], "country": "PE"},
    )
    assert response.status_code != 404
    assert response.status_code in (401, 200, 402)


def test_affordability_route_mounted():
    client = TestClient(_load_server_app())
    response = client.get("/v1/intel/affordability", params={"country": "PE"})
    assert response.status_code != 404
    assert response.status_code in (401, 200)
