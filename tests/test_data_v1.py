"""Smoke tests for Intelligence API /v1/* (phase 6)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from market_core import db_create_api_key, db_save_user, ensure_db_initialized
from market_server import app, hash_password

ensure_db_initialized()


@pytest.fixture
def v1_client(isolated_db):
    db_save_user("intel-user", hash_password("market"), "intel@test.com")
    key = db_create_api_key("intel-user", "read", "data-v1-smoke")["key"]
    headers = {"Authorization": f"Bearer {key}"}
    with TestClient(app) as client:
        yield client, headers


def test_v1_quality_flagged_shape(v1_client):
    client, headers = v1_client
    r = client.get("/v1/quality/flagged?limit=5", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "total" in body
    assert "items" in body
    assert isinstance(body["items"], list)


def test_v1_prices_shape(v1_client):
    client, headers = v1_client
    r = client.get("/v1/prices?clean=1&country=PE&limit=5", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["clean"] is True
    assert "total" in body
    assert "items" in body


def test_v1_dispersion_shape(v1_client):
    client, headers = v1_client
    r = client.get("/v1/dispersion?clean=1&limit=5", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body


def test_v1_basket_shape(v1_client):
    client, headers = v1_client
    r = client.get("/v1/basket", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "source" in body


def test_v1_coverage_matrix_shape(v1_client):
    client, headers = v1_client
    r = client.get("/v1/coverage/matrix", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "gaps" in body or "matrix" in body or "countries" in body


def test_v1_requires_api_key(isolated_db):
    with TestClient(app) as client:
        r = client.get("/v1/prices?limit=1")
    assert r.status_code == 401
