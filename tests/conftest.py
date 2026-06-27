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
# Tests use username ``admin`` with tier fixtures — do not enable prod ops bypass.
os.environ.pop("MARKET_API_TOKEN", None)
os.environ.pop("MARKET_ADMIN_USERS", None)
os.environ.pop("MARKET_ADMIN_API_KEYS", None)


def run_activate_pro_cli(*argv: str) -> tuple[int, str, str]:
    """Run activate_pro.main() in-process — same SQLite DB as the test runner."""
    import io
    import sys
    from contextlib import redirect_stderr, redirect_stdout
    from pathlib import Path

    ops_dir = Path(__file__).resolve().parent.parent / "ops"
    root = ops_dir.parent
    for entry in (str(ops_dir), str(root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)

    import activate_pro  # noqa: WPS433 — ops script, not a package

    old_argv = sys.argv
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    try:
        sys.argv = ["activate_pro.py", *argv]
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            code = activate_pro.main()
    finally:
        sys.argv = old_argv
    return code, out_buf.getvalue(), err_buf.getvalue()


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
