"""Regression test for _collect_doctor_checks / cmd_init vs /health/db and
/health/stats error branches.

Both endpoints (cli-market-backend routers/health.py) return HTTP 200 even
when the underlying check failed:
  - /health/db failure:    {"backend": "error", "detail": "DB connection failed: ..."}
  - /health/stats failure: {"error": "...", "status": "degraded"}

_collect_doctor_checks (used by `market doctor`, `market init`, `market mcp`)
and cmd_init's own /health/db probe used to treat any HTTP-200 body as
healthy, so a real backend outage was reported as "no data" (health/stats)
or, worse, crashed the "ok" formatting path with `f"{'?':,}"` and surfaced
a Python format error instead of the real DB failure detail.
"""

from __future__ import annotations

import argparse
from types import SimpleNamespace
from unittest.mock import MagicMock

import market_cli


class _FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _fake_httpx_get_factory(db_body, stats_status=200, stats_body=None):
    def fake_get(url, timeout=None):
        if url.endswith("/health/db"):
            return _FakeResponse(200, db_body)
        if url.endswith("/health/stats"):
            return _FakeResponse(stats_status, stats_body or {})
        if url.endswith("/v1/sources/health"):
            return _FakeResponse(200, {"summary": {"ok": 1, "partial": 0, "dead": 0}})
        raise AssertionError(f"unexpected URL: {url}")
    return fake_get


def test_doctor_surfaces_health_db_error_body_instead_of_format_crash(monkeypatch):
    monkeypatch.setattr(
        "httpx.get",
        _fake_httpx_get_factory({"backend": "error", "detail": "DB connection failed: timeout"}),
    )
    monkeypatch.setattr(market_cli, "get_token", lambda: None)

    checks, ok = market_cli._collect_doctor_checks()

    api_health = next(c for c in checks if c[0] == "API health")
    assert api_health[2] == "fail"
    assert "DB connection failed" in api_health[1]
    assert ok is False


def test_doctor_health_db_ok_still_renders_snapshot_count(monkeypatch):
    monkeypatch.setattr("httpx.get", _fake_httpx_get_factory({"backend": "sqlite", "snapshots": 66725}))
    monkeypatch.setattr(market_cli, "get_token", lambda: None)

    checks, ok = market_cli._collect_doctor_checks()

    api_health = next(c for c in checks if c[0] == "API health")
    assert api_health[2] == "ok"
    assert "66,725" in api_health[1]
    assert ok is True


def test_doctor_surfaces_health_stats_error_instead_of_no_data(monkeypatch):
    monkeypatch.setattr(
        "httpx.get",
        _fake_httpx_get_factory(
            {"backend": "sqlite", "snapshots": 1},
            stats_body={"error": "DB connection failed: pool exhausted", "status": "degraded"},
        ),
    )
    monkeypatch.setattr(market_cli, "get_token", lambda: None)

    checks, _ok = market_cli._collect_doctor_checks()

    linkage = next(c for c in checks if c[0] == "Golden linkage")
    assert "DB connection failed" in linkage[1]
    assert linkage[1] != "no data"


def test_init_treats_health_db_error_body_as_failure(monkeypatch):
    monkeypatch.setattr(
        "httpx.get",
        _fake_httpx_get_factory({"backend": "error", "detail": "DB connection failed: timeout"}),
    )
    monkeypatch.setattr(market_cli.ui, "is_json_mode", lambda: False)
    monkeypatch.setattr(market_cli.ui, "is_en", lambda: True)
    monkeypatch.setattr(market_cli.console, "print", MagicMock())
    errors = []
    monkeypatch.setattr(market_cli.ui, "print_actionable_error", lambda c, msg, **k: errors.append(msg))

    try:
        market_cli.cmd_init(argparse.Namespace(json=False))
    except SystemExit:
        pass

    assert any("DB connection failed" in e for e in errors)
