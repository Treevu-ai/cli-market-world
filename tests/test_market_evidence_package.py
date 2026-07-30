"""Unit tests for Market Evidence Package (PIT thin integration)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ops"))

from market_evidence_package import (  # noqa: E402
    SCHEMA_VERSION,
    build_package,
    ficha_to_markdown,
    load_mock_ficha_stub,
    load_mock_package,
    main,
    merge_ficha,
    price_summary,
    validate_package,
)

MOCKS = Path(__file__).resolve().parents[1] / "ops" / "pit_integration" / "mocks"


def test_price_summary_empty():
    s = price_summary([])
    assert s["n"] == 0
    assert s["min"] is None
    assert s["median"] is None


def test_price_summary_basic():
    rows = [
        {"price": 10, "currency": "PEN"},
        {"price": 20, "currency": "PEN"},
        {"price": 30, "currency": "PEN"},
    ]
    s = price_summary(rows)
    assert s["n"] == 3
    assert s["min"] == 10
    assert s["max"] == 30
    assert s["median"] == 20
    assert s["currency"] == "PEN"


def test_build_package_mvp_valid():
    pkg = build_package(
        query="arandanos",
        country="pe",
        pit_run_id="run-1",
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
                "observed_at": None,
            }
        ],
        tools_used=["mock"],
        layer="mock",
    )
    assert pkg["schema_version"] == SCHEMA_VERSION
    assert pkg["request"]["country"] == "PE"
    assert pkg["consumer_ref"]["pit_run_id"] == "run-1"
    assert pkg["price_summary"]["n"] == 1
    assert validate_package(pkg) == []


def test_validate_package_catches_missing_fields():
    errors = validate_package({"schema_version": "0.0"})
    assert any("missing top-level" in e for e in errors)
    assert any("schema_version" in e for e in errors)


def test_mock_fixture_file_validates():
    path = MOCKS / "market_evidence_package.example.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_package(data)
    assert errors == [], errors


def test_load_mock_package_overrides():
    pkg = load_mock_package(query="cafe", country="co", pit_run_id="x")
    assert pkg["request"]["query"] == "cafe"
    assert pkg["request"]["country"] == "CO"
    assert pkg["consumer_ref"]["pit_run_id"] == "x"


def test_merge_ficha_attaches_market_block():
    stub = load_mock_ficha_stub("run-merge")
    pkg = build_package(
        query="arandanos",
        country="PE",
        pit_run_id="run-merge",
        assortment=[
            {
                "product_id": "1",
                "name": "A",
                "brand": None,
                "store": "wong",
                "country": "PE",
                "price": 10.0,
                "currency": "PEN",
                "unit": None,
                "url": None,
                "observed_at": None,
            }
        ],
        tools_used=["mock"],
    )
    merged = merge_ficha(stub, pkg)
    assert merged["market_evidence_package_id"] == pkg["package_id"]
    assert "market_evidence" in merged
    assert merged["market_evidence"]["price_summary"]["n"] == 1
    assert "Góndola PE" in merged["market_headline"]
    md = ficha_to_markdown(merged)
    assert "Evidencia de mercado" in md
    assert "Arándanos" in md or "A" in md


def test_merge_ficha_empty_assortment_headline():
    stub = {"pit_run_id": "r", "segment": "s", "stage": "concepto"}
    pkg = build_package(query="xyz", country="PE", assortment=[], tools_used=["mock"])
    merged = merge_ficha(stub, pkg)
    assert "Sin cobertura" in merged["market_headline"]


def test_cli_mock_merge(tmp_path: Path):
    code = main(
        [
            "--mode",
            "mock",
            "--merge-ficha",
            "--out-dir",
            str(tmp_path),
            "--pit-run-id",
            "cli-test",
        ]
    )
    assert code == 0
    pkg_path = tmp_path / "last-market-evidence-package.json"
    ficha_path = tmp_path / "last-ficha-merged.json"
    md_path = tmp_path / "last-ficha-merged.md"
    assert pkg_path.is_file()
    assert ficha_path.is_file()
    assert md_path.is_file()
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert validate_package(pkg) == []
    ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
    assert ficha["pit_run_id"] == "cli-test"
    assert "market_evidence" in ficha


def test_ficha_merged_example_shape():
    path = MOCKS / "ficha_merged.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "market_evidence" in data
    assert data["market_evidence"]["schema_version"] == SCHEMA_VERSION
