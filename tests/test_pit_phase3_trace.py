"""Phase 3: trace receipt + thin PIT client (mocked HTTP)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

OPS = Path(__file__).resolve().parents[1] / "ops"
sys.path.insert(0, str(OPS))

from market_evidence_package import build_package, main  # noqa: E402
from pit_integration.pit_client import PitClient  # noqa: E402
from pit_integration.run_metadata import (  # noqa: E402
    METADATA_SCHEMA_VERSION,
    build_pit_run_metadata,
    proposed_research_run_create_extension,
    validate_pit_run_metadata,
)
from pit_integration.trace import (  # noqa: E402
    TRACE_SCHEMA_VERSION,
    build_trace_receipt,
    validate_trace_receipt,
)

MOCKS = OPS / "pit_integration" / "mocks"


def _sample_package(**kwargs: Any) -> dict[str, Any]:
    defaults = dict(
        query="arandanos",
        country="PE",
        pit_run_id="run-abc",
        assortment=[
            {
                "product_id": "1",
                "name": "Arándanos 125g",
                "brand": None,
                "store": "wong",
                "country": "PE",
                "price": 9.9,
                "currency": "PEN",
                "unit": "125g",
                "url": None,
                "observed_at": "2026-07-29T12:00:00Z",
            }
        ],
        tools_used=["mock"],
        as_of="2026-07-29T18:00:00Z",
        package_id="mep_test_phase3",
    )
    defaults.update(kwargs)
    return build_package(**defaults)


def test_build_trace_receipt_valid():
    pkg = _sample_package()
    receipt = build_trace_receipt(
        pkg,
        pit_run_id="run-abc",
        pit_api_base="https://cli-market-pit-backend.fly.dev",
        mode="mock",
        artifact_paths={"package": "/tmp/pkg.json"},
    )
    assert receipt["schema_version"] == TRACE_SCHEMA_VERSION
    assert receipt["package_id"] == "mep_test_phase3"
    assert receipt["as_of"] == "2026-07-29T18:00:00Z"
    assert receipt["pit_run_id"] == "run-abc"
    assert "mep_test_phase3" in receipt["audit_statement"]
    assert "run-abc" in receipt["audit_statement"]
    assert validate_trace_receipt(receipt) == []


def test_validate_trace_receipt_errors():
    assert validate_trace_receipt({}) != []


def test_trace_fixture_validates():
    path = MOCKS / "trace_receipt.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert validate_trace_receipt(data) == []


def test_merge_ficha_includes_trace_when_set_by_writer(tmp_path: Path):
    code = main(
        [
            "--mode",
            "mock",
            "--merge-ficha",
            "--write-trace",
            "--pit-run-id",
            "run-cli",
            "--out-dir",
            str(tmp_path),
        ]
    )
    assert code == 0
    ficha = json.loads((tmp_path / "last-ficha-merged.json").read_text(encoding="utf-8"))
    assert ficha["trace"]["pit_run_id"] == "run-cli"
    assert ficha["trace"]["package_id"]
    assert ficha["trace"]["as_of"]
    receipt = json.loads((tmp_path / "last-trace-receipt.json").read_text(encoding="utf-8"))
    assert validate_trace_receipt(receipt) == []
    assert receipt["pit_run_id"] == "run-cli"
    assert receipt["package_id"] == ficha["trace"]["package_id"]
    md = (tmp_path / "last-ficha-merged.md").read_text(encoding="utf-8")
    assert "Trazabilidad" in md


def test_pit_client_extract_run_id():
    assert PitClient.extract_run_id({"body": {"run_id": "r1"}}) == "r1"
    assert PitClient.extract_run_id({"body": {"data": {"id": "r2"}}}) == "r2"
    assert PitClient.extract_run_id({"body": {}}) is None


def test_pit_client_health_mocked():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok", "version": "0.1.0"}
    mock_resp.text = ""

    mock_client = MagicMock()
    mock_client.request.return_value = mock_resp

    pit = PitClient(base_url="https://example.test", token="", client=mock_client)
    out = pit.health()
    assert out["ok"] is True
    assert out["status_code"] == 200
    assert out["body"]["status"] == "ok"
    mock_client.request.assert_called()


def test_pit_client_create_research_run_mocked():
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"run_id": "new-run-9", "status": "queued"}
    mock_resp.text = ""

    mock_client = MagicMock()
    mock_client.request.return_value = mock_resp

    pit = PitClient(base_url="https://example.test", token="tok", client=mock_client)
    out = pit.create_research_run("blueberry", target_market="PE", limit=10)
    assert out["ok"] is True
    assert PitClient.extract_run_id(out) == "new-run-9"
    call_kwargs = mock_client.request.call_args
    assert call_kwargs[0][0] == "POST"
    assert "/v1/research-runs" in call_kwargs[0][1]


def test_build_pit_run_metadata_valid():
    pkg = _sample_package()
    meta = build_pit_run_metadata(pkg, pit_run_id="run-abc", trace_id="trc_1", mode="mock")
    assert meta["schema_version"] == METADATA_SCHEMA_VERSION
    assert meta["kind"] == "cli_market.market_evidence_ref"
    assert meta["package_id"] == "mep_test_phase3"
    assert meta["as_of"] == "2026-07-29T18:00:00Z"
    assert meta["pit_run_id"] == "run-abc"
    assert validate_pit_run_metadata(meta) == []


def test_run_metadata_fixture_validates():
    data = json.loads((MOCKS / "pit_run_metadata.example.json").read_text(encoding="utf-8"))
    assert validate_pit_run_metadata(data) == []


def test_proposed_research_run_create_extension_includes_ref():
    pkg = _sample_package()
    meta = build_pit_run_metadata(pkg, pit_run_id="r1")
    body = proposed_research_run_create_extension(
        "blueberry",
        target_market="PE",
        application="functional foods",
        market_evidence_ref=meta,
    )
    assert body["market_evidence_ref"]["package_id"] == "mep_test_phase3"
    assert body["target_market"] == "PE"


def test_cli_writes_run_metadata(tmp_path: Path):
    code = main(
        [
            "--mode",
            "mock",
            "--merge-ficha",
            "--write-trace",
            "--pit-run-id",
            "run-meta",
            "--out-dir",
            str(tmp_path),
        ]
    )
    assert code == 0
    meta_path = tmp_path / "last-pit-run-metadata.json"
    assert meta_path.is_file()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert validate_pit_run_metadata(meta) == []
    assert meta["pit_run_id"] == "run-meta"
    assert meta["package_id"]


def test_cli_create_pit_run_records_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Even when PIT returns 401, we still write a trace with create status."""

    class FakePit:
        def __init__(self, *a: Any, **k: Any) -> None:
            pass

        def create_research_run(self, *a: Any, **k: Any) -> dict[str, Any]:
            return {"ok": False, "status_code": 401, "body": {"detail": "Not authenticated"}}

        def health(self) -> dict[str, Any]:
            return {"ok": True, "status_code": 200, "body": {"status": "ok"}}

        def agents_status(self) -> dict[str, Any]:
            return {
                "ok": True,
                "status_code": 200,
                "body": {"data": {"ficha_available": False}},
            }

        def get_research_run(self, run_id: str) -> dict[str, Any]:
            return {"ok": False, "status_code": 401, "body": {}}

        @staticmethod
        def extract_run_id(resp: dict[str, Any]) -> str | None:
            return PitClient.extract_run_id(resp)

    monkeypatch.setattr("market_evidence_package.PitClient", FakePit)

    code = main(
        [
            "--mode",
            "mock",
            "--create-pit-run",
            "--merge-ficha",
            "--write-trace",
            "--out-dir",
            str(tmp_path),
            "--query",
            "blueberry functional",
            "--country",
            "PE",
        ]
    )
    assert code == 0
    receipt = json.loads((tmp_path / "last-trace-receipt.json").read_text(encoding="utf-8"))
    assert receipt["pit"]["create"]["status_code"] == 401
    assert receipt["pit"]["create"]["health"]["ok"] is True
