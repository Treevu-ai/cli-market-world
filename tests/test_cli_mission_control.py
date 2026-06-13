"""CLI tests for Mission Control shell + market mcp center."""

import argparse
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli
import market_ui


SAMPLE_OBSERVATORY = {
    "maa": 30,
    "maa_proxy": 5,
    "display_maa": 30,
    "display_label": "maa",
}

SAMPLE_TOOLS = [
    {"name": "market_search", "description": "Search products"},
    {"name": "market_compare", "description": "Compare prices"},
]

SAMPLE_CHECKS = [
    ("API health", "200 OK", "ok"),
    ("Auth", "demo", "ok"),
    ("Tier", "starter", "ok"),
    ("market-mcp", "/usr/bin/market-mcp", "ok"),
]


@pytest.fixture(autouse=True)
def _missions_on(monkeypatch):
    monkeypatch.setenv("MARKET_MISSIONS", "1")
    monkeypatch.setattr(market_cli.ui, "fetch_tier", lambda: "starter")
    monkeypatch.setattr(
        market_cli.ui,
        "fetch_session_context",
        lambda: {"username": "demo", "tier": "starter", "valid": True},
    )


def test_fetch_observatory_public_maa_threshold(monkeypatch):
    class FakeResp:
        status_code = 200

        @staticmethod
        def json():
            return {"maa": 30, "maa_proxy": 5}

    monkeypatch.setattr(market_ui.httpx, "get", lambda *a, **k: FakeResp())
    data = market_ui.fetch_observatory_public()
    assert data is not None
    assert data["display_maa"] == 30
    assert data["display_label"] == "maa"


def test_fetch_observatory_public_proxy_fallback(monkeypatch):
    class FakeResp:
        status_code = 200

        @staticmethod
        def json():
            return {"maa": 3, "maa_proxy": 42}

    monkeypatch.setattr(market_ui.httpx, "get", lambda *a, **k: FakeResp())
    data = market_ui.fetch_observatory_public()
    assert data["display_maa"] == 42
    assert data["display_label"] == "maa_proxy"


def test_print_mission_control_smoke():
    console = Console(file=StringIO(), force_terminal=True, width=100)
    market_ui.print_mission_control(
        console,
        tier="starter",
        observatory=SAMPLE_OBSERVATORY,
        username="demo",
    )
    out = console.file.getvalue()
    assert "CLI MARKET OS" in out
    assert "MISSIONS" in out or "MISIONES" in out
    assert "investigate" in out


def test_cmd_mcp_json(monkeypatch):
    monkeypatch.setattr(market_cli, "_collect_doctor_checks", lambda: (SAMPLE_CHECKS, True))
    monkeypatch.setattr(
        "market_core.market_mcp_registry.list_tools",
        lambda profile: SAMPLE_TOOLS,
    )
    emitted: list[dict] = []
    monkeypatch.setattr(
        market_cli.ui,
        "emit_json",
        lambda payload, console=None: emitted.append(payload),
    )
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_mcp(argparse.Namespace(profile="default", json=True))
    assert exc.value.code == 0
    assert emitted[0]["ok"] is True
    assert emitted[0]["data"]["total"] == 2
    assert emitted[0]["data"]["readiness_pct"] >= 0


def test_cmd_mcp_rich(monkeypatch):
    monkeypatch.setattr(market_cli, "_collect_doctor_checks", lambda: (SAMPLE_CHECKS, True))
    monkeypatch.setattr(
        "market_core.market_mcp_registry.list_tools",
        lambda profile: SAMPLE_TOOLS,
    )
    mock_center = MagicMock()
    monkeypatch.setattr(market_cli.ui, "print_mcp_center", mock_center)
    market_cli.cmd_mcp(argparse.Namespace(profile="default", json=False))
    mock_center.assert_called_once()


def test_shell_mission_control_startup(monkeypatch):
    monkeypatch.setattr(market_cli.ui, "fetch_observatory_public", lambda **k: SAMPLE_OBSERVATORY)
    mock_mc = MagicMock()
    monkeypatch.setattr(market_cli.ui, "print_mission_control", mock_mc)
    monkeypatch.setattr(market_cli.console, "input", lambda *a, **k: "")
    market_cli.cmd_shell(argparse.Namespace(json=False))
    mock_mc.assert_called_once()


def test_shell_legacy_when_missions_disabled(monkeypatch):
    monkeypatch.setenv("MARKET_MISSIONS", "0")
    mock_bar = MagicMock()
    monkeypatch.setattr(market_cli.ui, "print_context_bar", mock_bar)
    monkeypatch.setattr(market_cli.console, "input", lambda *a, **k: "")
    market_cli.cmd_shell(argparse.Namespace(json=False))
    mock_bar.assert_called_once()


def test_shell_parse_investigate_flags():
    ns = market_cli._shell_parse_investigate(
        ["arroz", "--country", "PE", "--no-intel", "--days", "14"]
    )
    assert ns.query == "arroz"
    assert ns.country == "PE"
    assert ns.no_intel is True
    assert ns.days == 14
