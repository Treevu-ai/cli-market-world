"""CLI tests for market investigate (mocked mission dispatch)."""

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli


SAMPLE_REPORT = {
    "mission": "investigate",
    "query": "arroz",
    "country": "PE",
    "status": "complete",
    "sections": {
        "search": {"status": "ok", "data": {"total": 42}},
        "compare": {"status": "ok", "data": {}},
        "inflation": {"status": "ok", "data": {}},
    },
    "insights": {
        "retailers_scanned": 12,
        "skus_matched": 847,
        "leader": {"store_name": "Metro", "price": 4.89, "currency": "PEN"},
        "laggard": {"store_name": "Wong", "pct_vs_mean": 18},
        "spread_pct_max": 22.0,
        "inflation_line": {"line": "arroz", "delta_pct": 5.2, "days": 30},
    },
    "recommendations": [
        {"rule": "baseline_leader", "text": "Prefer Metro for basket baseline."},
    ],
}


@pytest.fixture(autouse=True)
def _starter_tier(monkeypatch):
    monkeypatch.setattr(market_cli.ui, "fetch_tier", lambda: "starter")
    monkeypatch.setenv("MARKET_MISSIONS", "1")


def test_investigate_requires_query(monkeypatch):
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_investigate(argparse.Namespace(
            query="", country="PE", line=None, no_intel=False, days=30, json=False,
        ))
    assert exc.value.code == 1


def test_investigate_requires_query_hint_uses_requested_country(monkeypatch):
    """Regression for cli-market-world#466 (S5): the missing-query hint
    hardcoded --country PE regardless of the country the user requested."""
    emitted: list[dict] = []
    monkeypatch.setattr(
        market_cli.ui,
        "emit_json",
        lambda payload, console=None: emitted.append(payload),
    )
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_investigate(argparse.Namespace(
            query="", country="AR", line=None, no_intel=False, days=30, json=True,
        ))
    assert exc.value.code == 1
    assert all("PE" not in c for c in emitted[0]["next_commands"])
    assert any("AR" in c for c in emitted[0]["next_commands"])


def test_investigate_json_envelope(monkeypatch):
    monkeypatch.setattr(market_cli, "_dispatch_investigate", lambda *a, **k: SAMPLE_REPORT)
    emitted: list[dict] = []
    monkeypatch.setattr(
        market_cli.ui,
        "emit_json",
        lambda payload, console=None: emitted.append(payload),
    )
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_investigate(argparse.Namespace(
            query="arroz", country="PE", line=None, no_intel=False, days=30, json=True,
        ))
    assert exc.value.code == 0
    assert emitted[0]["ok"] is True
    assert emitted[0]["data"]["mission"] == "investigate"
    assert emitted[0]["data"]["insights"]["leader"]["store_name"] == "Metro"


def test_investigate_tier_gate_free(monkeypatch):
    monkeypatch.setattr(market_cli.ui, "fetch_tier", lambda: "free")
    monkeypatch.setattr(market_cli.ui, "tier_gate", lambda *a, **k: sys.exit(1))
    with pytest.raises(SystemExit):
        market_cli.cmd_investigate(argparse.Namespace(
            query="arroz", country="PE", line=None, no_intel=False, days=30, json=False,
        ))


def test_investigate_rich_report(monkeypatch):
    monkeypatch.setattr(market_cli, "_dispatch_investigate", lambda *a, **k: SAMPLE_REPORT)
    mock_report = MagicMock()
    monkeypatch.setattr(market_cli.ui, "print_investigate_report", mock_report)
    status = MagicMock()
    status.__enter__ = MagicMock(return_value=None)
    status.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr(market_cli.console, "status", MagicMock(return_value=status))

    market_cli.cmd_investigate(argparse.Namespace(
        query="arroz", country="PE", line=None, no_intel=False, days=30, json=False,
    ))
    mock_report.assert_called_once()


def test_investigate_disabled_by_env(monkeypatch):
    monkeypatch.setenv("MARKET_MISSIONS", "0")
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    with pytest.raises(SystemExit) as exc:
        market_cli.cmd_investigate(argparse.Namespace(
            query="arroz", country="PE", line=None, no_intel=False, days=30, json=False,
        ))
    assert exc.value.code == 1


def test_print_investigate_report_smoke():
    import os

    from market_ui import print_investigate_report
    from rich.console import Console

    console = Console(file=open(os.devnull, "w", encoding="utf-8"), force_terminal=True, width=100)
    print_investigate_report(console, SAMPLE_REPORT)
