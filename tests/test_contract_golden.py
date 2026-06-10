"""P1-E golden-file contract tests for public API shapes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_ROOT = REPO_ROOT.parent / "cli-market-core"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "contract_golden"

if CORE_ROOT.is_dir():
    sys.path.insert(0, str(CORE_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from market_core import ensure_db_initialized
from market_observatory import ensure_observatory_schema
from market_server import app

ensure_db_initialized()
ensure_observatory_schema()
client = TestClient(app)


def _load_json(name: str) -> dict | list:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _assert_subset(golden: dict, actual: dict, *, path: str = "") -> None:
    for key, expected in golden.items():
        full = f"{path}.{key}" if path else key
        assert key in actual, f"missing key {full}"
        value = actual[key]
        if isinstance(expected, dict):
            assert isinstance(value, dict), f"{full} should be object"
            _assert_subset(expected, value, path=full)
        elif isinstance(expected, list) and expected and isinstance(expected[0], str):
            assert isinstance(value, list), f"{full} should be array"
            assert set(value) >= set(expected), f"{full} missing items: {set(expected) - set(value)}"
        else:
            assert value == expected, f"{full}: {value!r} != {expected!r}"


def test_golden_capabilities():
    golden = _load_json("capabilities.json")
    r = client.get("/v1/capabilities")
    assert r.status_code == 200
    _assert_subset(golden, r.json())


def test_golden_sources_health_shape():
    keys = _load_json("sources_health_keys.json")
    r = client.get("/v1/sources/health")
    assert r.status_code == 200
    data = r.json()
    if "error" in data:
        pytest.skip("source_health module not available in this install")
    for key in keys["root"]:
        assert key in data, f"missing root key {key}"
    for key in keys["summary"]:
        assert key in data["summary"], f"missing summary.{key}"
    assert isinstance(data["stores"], list)
    if data["stores"]:
        sample = data["stores"][0]
        for key in keys["store_item"]:
            assert key in sample, f"missing stores[].{key}"


def test_golden_observatory_keys():
    required = _load_json("observatory_keys.json")
    r = client.get("/analytics/observatory?days=30")
    assert r.status_code == 200
    data = r.json()
    for key in required:
        assert key in data, f"missing observatory key {key}"
    assert isinstance(data["top_tools"], list)
    assert data["telemetry_maturity"] in ("early", "established")
    assert isinstance(data["maa_public_threshold"], int)
