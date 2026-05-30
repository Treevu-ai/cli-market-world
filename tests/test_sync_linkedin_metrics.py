"""Tests for LinkedIn metrics sync pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ops"))

from content_paths import content_root, template_dir  # noqa: E402
from sync_linkedin_metrics import metrics_from_dashboard  # noqa: E402


def test_content_root_falls_back_to_template(monkeypatch, tmp_path):
    monkeypatch.delenv("CLI_MARKET_CONTENT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    root = content_root()
    assert root == template_dir().resolve()
    assert (root / "linkedin" / "data-gate.md").is_file()


def test_metrics_from_dashboard_extracts_kpis():
    data = {
        "kpis": {
            "total_indexed": 43415,
            "snapshots_24h": 37731,
            "stores_indexed": 35,
            "stores_fresh_24h": 35,
            "coverage_7d_pct": 97.2,
        },
        "collector": {"stores_ok": 30, "stores_total": 36, "prices_upserted": 1812},
        "moat_summary": {"stale": False},
        "by_country": [{"country": "PE"}, {"country": "AR"}],
    }
    m = metrics_from_dashboard(data)
    assert m["indexed"] == "43,415"
    assert m["snap24"] == "37,731"
    assert m["stores"] == "35"
    assert m["coverage"] == "97.2"
    assert m["indexed_k"] == "43K+"
    assert m["snap_k"] == "37K+"
    assert m["moat_stale"] == "false"
    assert m["week"].startswith("20")
