"""Public API key registration."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from market_core import db_validate_api_key, ensure_db_initialized
from market_server import app

ensure_db_initialized()
client = TestClient(app)


def test_register_creates_valid_api_key():
    r = client.post("/auth/register")
    assert r.status_code == 200
    data = r.json()
    assert data["api_key"].startswith("sk-")
    assert data["username"].startswith("user-")
    key_data = db_validate_api_key(data["api_key"])
    assert key_data is not None
    assert key_data["username"] == data["username"]
