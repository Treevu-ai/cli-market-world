"""CLI post-install funnel telemetry."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli
import market_cli_telemetry
import market_core


@pytest.fixture(autouse=True)
def clear_install_artifacts():
    for name in ("funnel_install", "funnel_session"):
        path = market_core.SESSION_FILE.parent / name
        if path.is_file():
            path.unlink()
    yield
    for name in ("funnel_install", "funnel_session"):
        path = market_core.SESSION_FILE.parent / name
        if path.is_file():
            path.unlink()


def test_report_install_event_once(monkeypatch):
    calls: list[dict] = []

    def fake_api(method, path, body=None):
        calls.append(body or {})
        return {"ok": True}

    monkeypatch.setattr(market_cli_telemetry, "api", fake_api)

    assert market_cli._report_install_event(source="hello") is True
    assert market_cli._report_install_event(source="hello") is False
    assert len(calls) == 1
    assert calls[0]["event"] == "install"
    assert calls[0]["meta"]["source"] == "hello"
    assert calls[0]["session_id"]


def test_install_session_id_is_stable(monkeypatch):
    monkeypatch.setattr(market_cli_telemetry, "api", lambda *a, **k: {"ok": True})
    market_cli._report_install_event(source="cli")
    sid1 = market_cli_telemetry._install_session_id()
    sid2 = market_cli_telemetry._install_session_id()
    assert sid1 == sid2