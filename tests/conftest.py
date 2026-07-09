"""Shared pytest configuration — single SQLite test DB for all unit tests."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# pytest_configure fires before pytest inserts rootdir onto sys.path (that
# happens during collection), so a plain `import server_deps` here is only
# reliable when pytest is invoked from a cwd that happens to already have
# the repo root on sys.path (true locally, not guaranteed in CI). Add it
# explicitly so the import below is robust regardless of invocation cwd.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Must run before test modules import market_core (conftest loads first).
_TEST_DATA_DIR = tempfile.mkdtemp(prefix="market_test_")
os.environ["MARKET_DATA_DIR"] = _TEST_DATA_DIR
os.environ["DATABASE_URL"] = ""
os.environ.setdefault("MARKET_LEGACY_CHECKOUT", "1")
# Tests use username ``admin`` with tier fixtures — do not enable prod ops bypass.
os.environ.pop("MARKET_API_TOKEN", None)
os.environ.pop("MARKET_ADMIN_USERS", None)
os.environ.pop("MARKET_ADMIN_API_KEYS", None)

# Many test modules share one "admin" identity against this one session-wide
# DB (see module docstring above) — dozens of requests across the whole
# suite, all counted against the same daily/per-minute quota. That's fine
# against the old free tier's generous 1_000/day, but production tightened
# it to 15/day to drive plan upgrades (a business decision, not a test
# concern) — tests that explicitly downgrade "admin" to free tier
# (e.g. test_intel.py::test_refresh_requires_pro) exist to exercise the
# *tier gate* (expect 403), not the *rate limiter* (would incorrectly get
# 429 first once "admin"'s shared quota is exhausted by earlier tests).
# db_set_subscription()/db_get_subscription() (market_billing.py) both read
# TIERS["free"]["req_day"/"req_min"] directly — server_deps.TIER_LIMITS is
# only a fallback for the rare case of a DB row with a null limit, so it
# has to be patched here too but isn't the one actually driving this.
# Give the test session's free tier a budget large enough that no single
# pytest run can plausibly exhaust it, without touching the real value
# TIERS["free"] resolves to in production.
def pytest_configure(config):
    from market_billing import TIERS
    from server_deps import TIER_LIMITS

    TIERS["free"]["req_day"] = 100_000
    TIERS["free"]["req_min"] = 6_000
    TIER_LIMITS["free"] = (100_000, 6_000)


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
