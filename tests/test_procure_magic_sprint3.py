"""Sprint 3 unit tests — Procure magic link onboarding."""

import os
import time

import pytest

from market_core import db_save_user, ensure_db_initialized
from procure_magic import (
    build_procure_magic_url,
    create_procure_magic_token,
    exchange_procure_magic_token,
    procure_magic_enabled,
    provision_procure_api_key,
)


@pytest.fixture(autouse=True)
def _magic_secret(monkeypatch):
    monkeypatch.setenv("PROCURE_MAGIC_SECRET", "test-secret-for-sprint3-unit-tests")
    monkeypatch.setenv("PROCURE_APP_URL", "https://procure.example/dashboard")
    ensure_db_initialized()


def test_procure_magic_enabled():
    assert procure_magic_enabled() is True


def test_create_and_exchange_token():
    db_save_user("magic-user", "hash", "sess")
    api_key = provision_procure_api_key("magic-user")
    token = create_procure_magic_token(
        username="magic-user",
        api_key=api_key,
        tier="procure_pro",
    )
    url = build_procure_magic_url(token)
    assert "token=" in url
    assert url.startswith("https://procure.example/dashboard")
    body = token.rsplit(".", 1)[0]
    import base64
    import json

    pad = "=" * (-len(body) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(body + pad))
    assert "key" not in decoded
    assert "sub" not in decoded
    assert "jti" in decoded
    assert api_key not in token

    result = exchange_procure_magic_token(token)
    assert result["username"] == "magic-user"
    assert result["api_key"] == api_key
    assert result["tier"] == "procure_pro"
    assert "email" in result

    with pytest.raises(ValueError, match="already used"):
        exchange_procure_magic_token(token)


def test_expired_token(monkeypatch):
    db_save_user("exp-user", "hash", "sess")
    api_key = provision_procure_api_key("exp-user")
    monkeypatch.setenv("PROCURE_MAGIC_TTL_SECONDS", "1")
    token = create_procure_magic_token(
        username="exp-user",
        api_key=api_key,
        tier="procure_starter",
    )
    time.sleep(2)
    with pytest.raises(ValueError, match="expired"):
        exchange_procure_magic_token(token)


def test_invalid_signature():
    db_save_user("bad-user", "hash", "sess")
    api_key = provision_procure_api_key("bad-user")
    token = create_procure_magic_token(
        username="bad-user",
        api_key=api_key,
        tier="procure_builder",
    )
    tampered = token[:-4] + "XXXX"
    with pytest.raises(ValueError):
        exchange_procure_magic_token(tampered)
