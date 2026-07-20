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
os.environ.setdefault("PAYPAL_SANDBOX", "true")
# Tests use username ``admin`` with tier fixtures — do not enable prod ops bypass.
# Empty string, not pop(): a *missing* key is exactly what load_repo_env()
# (patched to a no-op below, but kept here as defense in depth) treats as
# "not yet set" and would happily fill in from the repo .env's real secrets.
os.environ["MARKET_API_TOKEN"] = ""
os.environ["MARKET_ADMIN_USERS"] = ""
os.environ["MARKET_ADMIN_API_KEYS"] = ""
# CLI_MARKET_API_KEY is the *other* key market_core.get_token() checks (after
# MARKET_API_TOKEN) before falling back to the local session file. Unlike the
# .env-sourced leaks above, this one isn't test- or repo-related at all: it's
# a real, persisted Windows user-level env var (a developer's actual `market`
# CLI login key) present in every fresh shell on a machine where `market
# login` was ever run — nothing in this repo sets it. Any test asserting on
# get_token()/session-based auth (test_cli_session.py) would silently pick up
# a real personal API key instead of its own test fixture value.
os.environ["CLI_MARKET_API_KEY"] = ""
# Same leak class as CLI_MARKET_API_KEY above, but for Slack: SLACK_BOT_TOKEN
# is a real, persisted dev-shell env var on machines set up to run ops/*.py
# Slack scripts by hand — nothing in this repo sets it either. Every ops/*.py
# Slack-sender (billing_slack.py's _subscription_slack_ready()/
# _funnel_slack_ready(), slack_notify.py, etc.) gates on this one token being
# present. Unmocked tests that exercise a billing/subscription code path
# (tests/test_server.py's /billing/pro-checkout tests) call straight into
# that gate — without this scrub, they silently posted real fake-data
# "$49 pago pendiente" messages to the live production #revenue Slack channel
# on every local test run. Scrub the webhook fallbacks too, not just the token.
os.environ["SLACK_BOT_TOKEN"] = ""
os.environ["SLACK_WEBHOOK_CLI_MARKET_PRO"] = ""
os.environ["SLACK_WEBHOOK_FUNNEL"] = ""

# Several ops/*.py scripts (e.g. activate_pro.py, imported by
# run_activate_pro_cli() below and by test_pro_display_name.py/test_server.py)
# call load_env.load_repo_env() at *module import time*, which reads the repo's
# real .env (production DATABASE_URL, PAYPAL_SANDBOX=false, a real
# MARKET_API_TOKEN, ...) and does `os.environ[key] = value` for any key not
# already present — a plain assignment with no teardown, unlike
# monkeypatch.setenv. The first test that imports one of those ops modules
# permanently pollutes the shared process environment for the rest of the
# pytest session: is_production_deploy() starts returning True (real secrets
# leak into TestClient/lifespan startup checks), cascading into
# "Production deploy detected but running on SQLite" RuntimeErrors and
# downstream tempfile/fixture teardown failures for every test that runs
# afterward — reproducible only via the full suite, never in isolation, which
# is what made this hard to spot. Neutralize the loader itself instead of
# chasing every individual key it might inject.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ops"))
import load_env as _load_env  # noqa: E402

_load_env.load_repo_env = lambda: None

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
