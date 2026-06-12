"""Shared pytest configuration — single SQLite test DB for all unit tests."""

from __future__ import annotations

import os
import tempfile

import pytest

# Must run before test modules import market_core (conftest loads first).
_TEST_DATA_DIR = tempfile.mkdtemp(prefix="market_test_")
os.environ["MARKET_DATA_DIR"] = _TEST_DATA_DIR
os.environ["DATABASE_URL"] = ""
os.environ.setdefault("MARKET_LEGACY_CHECKOUT", "1")


def activate_pro_subprocess_env() -> dict:
    """Env for ops/activate_pro.py — match in-process market_core SQLite paths."""
    import market_core as mc

    env = os.environ.copy()
    env["MARKET_DATA_DIR"] = str(mc.DATA_DIR)
    env["DATABASE_URL"] = ""
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_PASS"):
        env[key] = ""
    env["GMAIL_DRAFTS_ENABLED"] = "0"
    try:
        db = mc.get_db()
        db.commit()
        db.close()
    except Exception:
        pass
    return env


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    """SQLite test DB with market_core state reset (package + implementation module)."""
    import market_core
    import market_core.market_core as mc

    data_dir = tmp_path / "market_data"
    data_dir.mkdir()
    db_file = data_dir / "market.db"
    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", "")

    for mod in (mc, market_core):
        monkeypatch.setattr(mod, "DATA_DIR", data_dir, raising=False)
        monkeypatch.setattr(mod, "DB_FILE", db_file, raising=False)
        monkeypatch.setattr(mod, "USE_PG", False, raising=False)
        monkeypatch.setattr(mod, "_db_initialized", False, raising=False)

    return market_core
