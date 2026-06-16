"""Pro account visibility on default `market` / `hello` entry."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_core
import market_cli
import market_cli_hello
import market_ui as ui


@pytest.fixture(autouse=True)
def clear_session():
    if market_core.SESSION_FILE.exists():
        market_core.SESSION_FILE.unlink()
    yield
    if market_core.SESSION_FILE.exists():
        market_core.SESSION_FILE.unlink()


def test_fetch_session_context_pro(monkeypatch):
    market_core.save_session("acubatruweb", "sess-pro-1")

    def fake_api(method, path, json_data=None):
        if path == "/auth/whoami":
            return {"username": "acubatruweb"}
        if path == "/auth/subscription":
            return {
                "username": "acubatruweb",
                "subscription": {"tier": "pro", "req_limit_day": 10000},
            }
        return {}

    monkeypatch.setattr(ui, "api", fake_api)
    ctx = ui.fetch_session_context()
    assert ctx is not None
    assert ctx["valid"] is True
    assert ctx["username"] == "acubatruweb"
    assert ctx["tier"] == "pro"
    assert ui.is_pro_tier(ctx["tier"])


def test_hello_json_includes_pro_auth(monkeypatch):
    market_core.save_session("acubatruweb", "sess-pro-1")

    def fake_api(method, path, json_data=None):
        if path == "/auth/whoami":
            return {"username": "acubatruweb"}
        if path == "/auth/subscription":
            return {
                "username": "acubatruweb",
                "subscription": {"tier": "pro", "req_limit_day": 10000},
            }
        return {}

    monkeypatch.setattr(ui, "api", fake_api)
    monkeypatch.setattr(market_cli.ui, "api", fake_api)
    data = market_cli_hello._hello_data(is_en=False, ctx=ui.fetch_session_context())
    assert data["auth"]["pro_active"] is True
    assert data["auth"]["username"] == "acubatruweb"
    assert "market account" in data["next_steps"][1]


def test_hello_default_emits_pro_context(monkeypatch, capsys):
    market_core.save_session("acubatruweb", "sess-pro-1")

    def fake_api(method, path, json_data=None):
        if path == "/auth/whoami":
            return {"username": "acubatruweb"}
        if path == "/auth/subscription":
            return {
                "username": "acubatruweb",
                "subscription": {"tier": "pro", "req_limit_day": 10000},
            }
        return {}

    monkeypatch.setattr(ui, "api", fake_api)
    monkeypatch.setattr(market_cli.ui, "api", fake_api)
    monkeypatch.setattr(market_cli_hello, "_report_install_event", lambda **kwargs: None)
    monkeypatch.setattr(market_cli.ui, "maybe_version_notice", lambda *a, **k: None)
    monkeypatch.setattr(market_cli.ui, "mcp_snippet_panel", lambda *a, **k: None)

    market_cli.cmd_hello(argparse_ns(json=False))
    out = capsys.readouterr().out
    assert "acubatruweb" in out
    assert "pro" in out.lower()
    # New splash shows tier in left panel and "Build Pro" in footer
    assert "Build Pro" in out or "pro" in out.lower()


def argparse_ns(**kwargs):
    return type("NS", (), kwargs)()