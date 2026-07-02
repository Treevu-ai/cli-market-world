"""Regression test for market_cli.cmd_ask.

/agent/ask (cli-market-backend routers/agent.py) has two response shapes:
  - LLM agent (ANTHROPIC_API_KEY set): {"answer", "tools_used", "model", "rounds"}
  - regex fallback (no key configured): {"action", "query", "quantity", "message"}

cmd_ask used to only understand the regex-fallback shape. When the LLM path
answered instead, the missing "action"/"query" keys made it default to
action="search" with an empty query, which matched none of the action
branches and silently printed only "→ search" with no answer at all.
"""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import market_cli


def _args(prompt="necesito armar una canasta basica para una familia de 5 personas"):
    return argparse.Namespace(prompt=prompt, json=False)


def test_ask_renders_llm_agent_answer(monkeypatch):
    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda method, path, body=None: {
            "answer": "Canasta básica (PE): arroz S/4.20 en Wong, aceite S/9.80 en Plaza Vea.",
            "tools_used": ["search_products", "compare_basket"],
            "model": "claude-haiku-4-5-20251001",
            "rounds": 2,
        },
    )
    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    market_cli.cmd_ask(_args())

    rendered = "\n".join(str(p) for p in printed)
    assert "search_products" in rendered
    assert "compare_basket" in rendered
    assert any(
        isinstance(p, market_cli.Panel) and "Canasta básica" in str(p.renderable)
        for p in printed
    )


def test_ask_renders_empty_llm_answer_without_crashing(monkeypatch):
    monkeypatch.setattr(
        market_cli,
        "cli_api",
        lambda method, path, body=None: {"answer": "", "tools_used": [], "model": "x", "rounds": 1},
    )
    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    market_cli.cmd_ask(_args())

    rendered = "\n".join(str(p) for p in printed)
    assert "Sin respuesta del agente" in rendered


def test_ask_regex_fallback_search_still_works(monkeypatch):
    calls = []

    def fake_api(method, path, body=None):
        calls.append(path)
        if path == "/agent/ask":
            return {"action": "search", "query": "leche", "quantity": 1, "message": "Buscando 'leche'..."}
        if path == "/products/search":
            return {
                "results": [
                    {"name": "Leche Gloria 1L", "price": 4.5, "currency": "PEN", "store": "wong", "store_name": "Wong"},
                ]
            }
        return {}

    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    monkeypatch.setattr(market_cli, "input", lambda *_a: "n", raising=False)

    market_cli.cmd_ask(_args("compra leche"))

    assert "/products/search" in calls


def test_ask_surfaces_error(monkeypatch):
    monkeypatch.setattr(
        market_cli, "cli_api", lambda method, path, body=None: {"error": "DATA_GATE_STALE"}
    )
    printed = []
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    market_cli.cmd_ask(_args())

    assert any("DATA_GATE_STALE" in str(p) for p in printed)
