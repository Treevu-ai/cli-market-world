"""Revoke leaked API keys (account_service helper)."""

from __future__ import annotations

import pytest

from account_service import revoke_api_key_by_value
from market_core import db_create_api_key, db_save_user, db_validate_api_key
from server_deps import hash_password


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    data_dir = tmp_path / "market_data"
    data_dir.mkdir()
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", "")
    import market_core
    import market_core.market_core as mc

    market_core._db_initialized = False
    mc._db_initialized = False
    mc.ensure_db_initialized()
    yield
    market_core._db_initialized = False
    mc._db_initialized = False


def test_revoke_api_key_by_value(isolated_db):
    db_save_user("revoke-me", hash_password("market"), "revoke@test.com")
    created = db_create_api_key("revoke-me", "read", "incident-test")
    assert db_validate_api_key(created["key"]) is not None

    result = revoke_api_key_by_value(created["key"])
    assert result == {"username": "revoke-me", "key_id": created["id"]}
    assert db_validate_api_key(created["key"]) is None
    assert revoke_api_key_by_value(created["key"]) is None


def test_revoke_api_key_by_value_rejects_non_sk(isolated_db):
    assert revoke_api_key_by_value("not-a-key") is None
