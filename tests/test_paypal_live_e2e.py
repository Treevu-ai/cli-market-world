"""Unit tests for PayPal live E2E gate (GO-LIVE §5)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ops"))

import paypal_live_e2e as gate  # noqa: E402


def test_gate_status_not_started(tmp_path: Path):
    state = tmp_path / "state.json"
    passed = tmp_path / "pass.json"
    status = gate.gate_status(state_path=state, pass_path=passed)
    assert status["status"] == "not_started"
    assert status["passed"] is False


def test_gate_status_awaiting_approval(tmp_path: Path):
    state = tmp_path / "state.json"
    passed = tmp_path / "pass.json"
    state.write_text(
        json.dumps({"phase": "awaiting_paypal_approval", "approve_url": "https://paypal.test"}),
        encoding="utf-8",
    )
    status = gate.gate_status(state_path=state, pass_path=passed)
    assert status["status"] == "awaiting_approval"
    assert status["passed"] is False


def test_gate_status_passed(tmp_path: Path):
    state = tmp_path / "state.json"
    passed = tmp_path / "pass.json"
    passed.write_text(
        json.dumps({"ok": True, "verified_at": "2026-06-12T00:00:00Z", "username": "u1"}),
        encoding="utf-8",
    )
    status = gate.gate_status(state_path=state, pass_path=passed)
    assert status["status"] == "passed"
    assert status["passed"] is True


def test_prepare_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state = tmp_path / "state.json"
    monkeypatch.setattr(gate, "STATE_PATH", state)

    def fake_register(_base: str):
        return "user-test", "sk-test-key"

    calls: list[tuple] = []

    def fake_http(base, method, path, *, token="", body=None, **kwargs):
        calls.append((method, path, token))
        if path == "/v1/data/export":
            return 403, {}, 1.0
        if path == "/billing/paypal":
            return 200, {"ok": True, "approve_url": "https://paypal.test/approve", "subscription_id": "I-1"}, 2.0
        raise AssertionError(f"unexpected {method} {path}")

    with patch.object(gate, "register_user", fake_register), patch.object(gate, "http_json", fake_http):
        prep = gate.prepare(write_state=True)

    assert prep["username"] == "user-test"
    assert prep["free_export_status"] == 403
    assert prep["approve_url"].startswith("https://")
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert saved["api_key"] == "sk-test-key"


def test_prepare_fails_when_export_not_403():
    with patch.object(gate, "register_user", lambda _b: ("u", "sk")), patch.object(
        gate, "export_status", lambda _b, _k: 200
    ):
        with pytest.raises(SystemExit, match="403"):
            gate.prepare(write_state=False)


def test_verify_writes_pass_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state = tmp_path / "state.json"
    passed = tmp_path / "pass.json"
    state.write_text(json.dumps({"username": "user-verify"}), encoding="utf-8")
    monkeypatch.setattr(gate, "STATE_PATH", state)

    with patch.object(gate, "subscription_tier", lambda _b, _k: "pro"), patch.object(
        gate, "export_status", lambda _b, _k: 200
    ):
        result = gate.verify("sk-live-test", pass_path=passed)

    assert result["ok"] is True
    evidence = json.loads(passed.read_text(encoding="utf-8"))
    assert evidence["ok"] is True
    assert evidence["tier"] == "pro"
    assert evidence["export_status"] == 200
    assert evidence["api_key_suffix"] == "e-test"


def test_verify_fails_without_pass_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state = tmp_path / "state.json"
    passed = tmp_path / "pass.json"
    monkeypatch.setattr(gate, "STATE_PATH", state)

    with patch.object(gate, "subscription_tier", lambda _b, _k: "free"), patch.object(
        gate, "export_status", lambda _b, _k: 403
    ):
        result = gate.verify("sk-x", pass_path=passed, write_pass=True)

    assert result["ok"] is False
    assert not passed.exists()
