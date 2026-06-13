"""Tests for ops/sync_linkedin_metrics.py — pure transformation functions."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# ops/ must be on sys.path before importing the module
_OPS = Path(__file__).resolve().parent.parent / "ops"
if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))

from sync_linkedin_metrics import (
    METRIC_DAYS,
    _fmt,
    _iso_week,
    _patch_day_file,
    _replace_block,
    _short_k,
    metrics_from_dashboard,
)


# ── _fmt ─────────────────────────────────────────────────────────────────────

def test_fmt_integer():
    assert _fmt(1000) == "1,000"


def test_fmt_large_integer():
    assert _fmt(53000) == "53,000"


def test_fmt_float_truncates():
    assert _fmt(1234.9) == "1,234"


def test_fmt_small_number():
    assert _fmt(5) == "5"


# ── _short_k ─────────────────────────────────────────────────────────────────

def test_short_k_below_thousand():
    assert _short_k(999) == "999"


def test_short_k_exactly_thousand():
    assert _short_k(1000) == "1K+"


def test_short_k_rounds_down():
    assert _short_k(53456) == "53K+"


def test_short_k_large():
    assert _short_k(100000) == "100K+"


# ── _iso_week ─────────────────────────────────────────────────────────────────

def test_iso_week_format():
    week = _iso_week()
    assert week.startswith("20")
    assert "-W" in week
    parts = week.split("-W")
    assert len(parts) == 2
    assert len(parts[1]) == 2  # zero-padded


def test_iso_week_with_known_date():
    # 2026-06-13 is Saturday — ISO week 24 of 2026
    dt = datetime(2026, 6, 13, tzinfo=timezone.utc)
    assert _iso_week(dt) == "2026-W24"


def test_iso_week_with_another_date():
    dt = datetime(2026, 1, 5, tzinfo=timezone.utc)  # Week 2
    assert _iso_week(dt) == "2026-W02"


# ── metrics_from_dashboard ────────────────────────────────────────────────────

_SAMPLE_DATA = {
    "kpis": {
        "total_indexed": 53000,
        "snapshots_24h": 38000,
        "stores_indexed": 38,
        "stores_fresh_24h": 36,
        "coverage_7d_pct": 97.5,
        "total_stores": 38,
    },
    "collector": {
        "prices_upserted": 1200,
        "stores_ok": 37,
        "stores_total": 38,
    },
    "moat_summary": {"stale": False},
    "by_country": ["PE", "MX", "AR", "CO", "CL", "UY", "EC", "BO"],
}


def test_metrics_from_dashboard_keys():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    for key in ("indexed", "snap24", "stores", "fresh", "coverage", "countries", "week", "run_line"):
        assert key in m, f"Missing key: {key}"


def test_metrics_from_dashboard_indexed():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert m["indexed"] == "53,000"
    assert m["indexed_raw"] == "53000"
    assert m["indexed_k"] == "53K+"


def test_metrics_from_dashboard_snap24():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert m["snap24"] == "38,000"
    assert m["snap_k"] == "38K+"


def test_metrics_from_dashboard_stores():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert m["stores"] == "38"
    assert m["fresh"] == "36"


def test_metrics_from_dashboard_coverage():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert m["coverage"] == "97.5"


def test_metrics_from_dashboard_countries():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert m["countries"] == "8"


def test_metrics_from_dashboard_run_line_with_collector():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert "37/38" in m["run_line"]
    assert "1200" in m["run_line"] or "1,200" in m["run_line"]


def test_metrics_from_dashboard_run_line_no_stores_ok():
    data = {**_SAMPLE_DATA, "collector": {"prices_upserted": 500}}
    m = metrics_from_dashboard(data)
    assert "tiendas indexadas" in m["run_line"] or "collector" in m["run_line"]


def test_metrics_from_dashboard_moat_stale_false():
    m = metrics_from_dashboard(_SAMPLE_DATA)
    assert m["moat_stale"] == "false"


def test_metrics_from_dashboard_moat_stale_true():
    data = {**_SAMPLE_DATA, "moat_summary": {"stale": True}}
    m = metrics_from_dashboard(data)
    assert m["moat_stale"] == "true"


def test_metrics_from_dashboard_empty_kpis():
    m = metrics_from_dashboard({})
    assert m["indexed"] == "0"
    assert m["stores"] == "0"
    assert m["countries"] == "8"  # default fallback


# ── _replace_block ────────────────────────────────────────────────────────────

_BLOCK_TEXT = """\
## Métricas — Semana actual

| Clave | Valor |
| --- | --- |
| Indexed | 19,452 |
| Stores | 30 |

## Otra sección

Texto aquí.
"""


def test_replace_block_replaces_table():
    new_body = "| Clave | Valor |\n| --- | --- |\n| Indexed | 53,000 |\n| Stores | 38 |\n"
    result = _replace_block(_BLOCK_TEXT, "Métricas", new_body)
    assert "53,000" in result
    assert "19,452" not in result


def test_replace_block_preserves_other_sections():
    new_body = "| Clave | Valor |\n| --- | --- |\n| Indexed | 53,000 |\n"
    result = _replace_block(_BLOCK_TEXT, "Métricas", new_body)
    assert "## Otra sección" in result
    assert "Texto aquí." in result


def test_replace_block_no_match_unchanged():
    result = _replace_block(_BLOCK_TEXT, "Inexistente", "| x | y |\n")
    assert result == _BLOCK_TEXT


# ── _patch_day_file ───────────────────────────────────────────────────────────

_METRIC_DAYS_SUBSET = (7, 10, 14)

_DAY_CONTENT = """\
---
status: draft
---

## Intro

Hoy tenemos **19,452** precios indexados de 30 retailers.
La cobertura es del 94.4% con 8K+ snapshots diarios.
"""

_METRICS = {
    "indexed": "53,000",
    "indexed_raw": "53000",
    "indexed_k": "53K+",
    "snap24": "40,000",
    "snap24_raw": "40000",
    "snap_k": "40K+",
    "stores": "38",
    "fresh": "36",
    "coverage": "97.5",
    "countries": "8",
    "week": "2026-W24",
    "run_line": "1,200 precios · 37/38 tiendas",
    "moat_stale": "false",
    "date": "2026-06-13",
}


def test_patch_day_file_dry_run_no_write(tmp_path):
    f = tmp_path / "Day-07.md"
    f.write_text(_DAY_CONTENT, encoding="utf-8")
    _patch_day_file(f, _METRICS, dry_run=True)
    # Content should still be original (dry run — no write)
    assert f.read_text(encoding="utf-8") == _DAY_CONTENT


def test_patch_day_file_patches_indexed(tmp_path):
    f = tmp_path / "Day-07.md"
    f.write_text(_DAY_CONTENT, encoding="utf-8")
    _patch_day_file(f, _METRICS, dry_run=False)
    result = f.read_text(encoding="utf-8")
    assert "53,000" in result
    assert "19,452" not in result


def test_patch_day_file_patches_snap_k(tmp_path):
    f = tmp_path / "Day-07.md"
    content = "Texto con 8K+ snapshots"
    f.write_text(content, encoding="utf-8")
    _patch_day_file(f, _METRICS, dry_run=False)
    result = f.read_text(encoding="utf-8")
    assert "40K+" in result


def test_patch_day_file_missing_file_returns_false(tmp_path):
    missing = tmp_path / "Day-99.md"
    changed = _patch_day_file(missing, _METRICS, dry_run=False)
    assert changed is False


def test_patch_day_file_no_match_returns_false(tmp_path):
    f = tmp_path / "Day-07.md"
    f.write_text("No metrics to patch here.", encoding="utf-8")
    changed = _patch_day_file(f, _METRICS, dry_run=False)
    assert changed is False


# ── METRIC_DAYS constant ──────────────────────────────────────────────────────

def test_metric_days_contains_expected():
    assert 7 in METRIC_DAYS
    assert 14 in METRIC_DAYS
    assert 30 in METRIC_DAYS
