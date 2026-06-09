"""P0 market tutorial command."""

import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import market_cli
import market_core


@pytest.fixture(autouse=True)
def clear_tutorial_artifacts():
    export_path = market_core.SESSION_FILE.parent / "precios-tutorial.json"
    if export_path.is_file():
        export_path.unlink()
    yield
    if export_path.is_file():
        export_path.unlink()


def test_tutorial_demo_emits_event(monkeypatch, capsys):
    events: list[dict] = []

    def fake_report(event, *, meta=None, dedupe=True):
        events.append({"event": event, "meta": meta or {}, "dedupe": dedupe})

    monkeypatch.setattr(market_cli, "_report_onboarding_event", fake_report)
    market_cli.cmd_tutorial(argparse_ns(country="PE", demo=True))

    out = capsys.readouterr().out
    assert "Tutorial completo" in out
    assert "mcp-setup" in out
    assert "utm_campaign=tutorial" in out
    assert len(events) == 1
    assert events[0]["event"] == "tutorial_completed"
    assert events[0]["meta"]["demo"] is True


def test_tutorial_writes_export_file(monkeypatch):
    monkeypatch.setattr(market_cli, "_report_onboarding_event", lambda *a, **k: None)
    market_cli.cmd_tutorial(argparse_ns(country="PE", demo=True))

    export_path = market_core.SESSION_FILE.parent / "precios-tutorial.json"
    assert export_path.is_file()
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["tutorial"] is True
    assert payload["country"] == "PE"


def argparse_ns(**kwargs):
    import argparse

    return argparse.Namespace(**kwargs)