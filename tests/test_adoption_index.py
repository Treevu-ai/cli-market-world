"""Adoption Index V1 — scoring and API."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_ROOT = REPO_ROOT.parent / "cli-market-core"
if CORE_ROOT.is_dir():
    sys.path.insert(0, str(CORE_ROOT))
sys.path.insert(0, str(REPO_ROOT))

MOCK_ADOPTION = {
    "window_days": 30,
    "pypi": {
        "ok": True,
        "project": "cli-market-core + cli-market-world",
        "projects": ["cli-market-core", "cli-market-world"],
        "total_downloads": 12000,
        "downloads_last_7d": 80,
        "downloads_last_30d": 240,
        "downloads_last_30d_no_ci": None,
        "combined": {
            "total_downloads": 12000,
            "downloads_last_7d": 80,
            "downloads_last_30d": 240,
            "downloads_last_30d_no_ci": None,
        },
        "by_project": {
            "cli-market-core": {
                "ok": True,
                "total_downloads": 10000,
                "downloads_last_7d": 60,
                "downloads_last_30d": 180,
                "downloads_last_30d_no_ci": None,
                "top_version_30d": "1.9.13",
                "latest_version": "1.9.13",
            },
            "cli-market-world": {
                "ok": True,
                "total_downloads": 2000,
                "downloads_last_7d": 20,
                "downloads_last_30d": 60,
                "downloads_last_30d_no_ci": None,
                "top_version_30d": "1.9.6",
                "latest_version": "1.9.6",
            },
        },
    },
    "funnel": {
        "install": 12,
        "register": 18,
        "first_search": 14,
        "starter_subscribe": 2,
        "request_pro": 3,
        "activated": 2,
    },
    "comparison": {
        "register_per_pypi_30d": 0.075,
        "register_per_install": 1.5,
        "search_per_register": 0.78,
        "funnel_register_to_search": 0.78,
        "funnel_search_to_pro": 0.21,
        "funnel_pro_to_activated": 0.67,
        "pricing_health": 0.14,
    },
    "notes": [],
    "fetched_at": "2026-06-08T12:00:00+00:00",
}

MOCK_FUNNEL = {
    "window_days": 30,
    "events": {"register": 18, "first_search": 14, "request_pro": 3, "activated": 2},
    "unique_users": {
        "with_search": 14,
        "with_starter_subscribe": 2,
        "with_pro_request": 3,
        "activated": 2,
    },
    "conversion": {
        "register_to_search": 0.78,
        "search_to_starter": 0.14,
        "search_to_pro": 0.21,
        "pro_to_activated": 0.67,
    },
    "ttfv_median_minutes": 4.5,
    "ttc_median_hours": 2.0,
    "funnel_steps": [],
}

MOCK_RETENTION = {
    "window_days": 30,
    "return_within_days": 7,
    "cohort_first_search": 10,
    "retained": 4,
    "retention_rate": 0.4,
}


@patch("market_adoption_index._observatory_maa", return_value=(None, None))
@patch("market_adoption_index.funnel_retention_summary", return_value=MOCK_RETENTION)
@patch("market_adoption_index.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_adoption_index.adoption_summary", return_value=MOCK_ADOPTION)
def test_compute_adoption_index_scores(mock_adopt, mock_funnel, mock_ret, _mock_maa):
    from market_adoption_index import compute_adoption_index

    data = compute_adoption_index(days=30, include_github=False)
    assert 0 <= data["score"] <= 100
    assert data["grade"] in {"A", "B", "C", "D", "F"}
    assert data["version"] == "v1"
    assert set(data["breakdown"]) == {
        "downloads",
        "real_usage",
        "growth",
        "activation",
        "revenue_intent",
    }
    weights = sum(b["weight"] for b in data["breakdown"].values())
    assert abs(weights - 1.0) < 0.001
    assert data["signals"]["agent_usage_proxy"]["value"] == 14
    # Multi PyPI awareness: combined used for score, packages pulled out
    pypi_sig = data["signals"].get("pypi", {})
    assert pypi_sig.get("downloads_30d") == 240
    assert "by_project" in pypi_sig
    assert "cli-market-core" in (pypi_sig.get("by_project") or {})
    assert pypi_sig.get("projects") == ["cli-market-core", "cli-market-world"]


@patch("market_adoption_index._observatory_maa", return_value=(25, "maa"))
@patch("market_adoption_index.funnel_retention_summary", return_value=MOCK_RETENTION)
@patch("market_adoption_index.funnel_summary", return_value=MOCK_FUNNEL)
@patch("market_adoption_index.adoption_summary", return_value=MOCK_ADOPTION)
def test_compute_adoption_index_uses_maa_when_observatory_active(
    mock_adopt, mock_funnel, mock_ret, _mock_maa
):
    from market_adoption_index import compute_adoption_index

    data = compute_adoption_index(days=30, include_github=False)
    proxy = data["signals"]["agent_usage_proxy"]
    assert proxy["value"] == 25
    assert proxy["source"] == "maa"
    assert data["signals"]["maa"] == 25


def test_growth_score_positive():
    from market_adoption_index import _growth_score

    score, pct = _growth_score(100, 300)
    assert score > 50
    assert pct is not None


def test_score_grade_buckets():
    from market_adoption_index import score_grade

    assert score_grade(90) == "A"
    assert score_grade(75) == "B"
    assert score_grade(60) == "C"
    assert score_grade(45) == "D"
    assert score_grade(20) == "F"


def test_adoption_index_markdown_renders():
    from market_adoption_index import adoption_index_markdown

    md = adoption_index_markdown(
        {
            "score": 72.5,
            "grade": "B",
            "version": "v1",
            "computed_at": "2026-06-08T12:00:00+00:00",
            "breakdown": {
                "downloads": {"weight": 0.3, "score": 80},
                "real_usage": {"weight": 0.25, "score": 40},
                "growth": {"weight": 0.2, "score": 70},
                "activation": {"weight": 0.15, "score": 55},
                "revenue_intent": {"weight": 0.1, "score": 30},
            },
            "signals": {
                "pypi": {"downloads_30d": 200, "downloads_7d": 50, "growth_pct_7d_vs_baseline": 12.5},
                "funnel": {"register": 10, "first_search": 8, "request_pro": 2, "activated": 1},
                "retention_7d": {"retention_rate": 0.4, "retained": 3, "cohort_first_search": 8},
                "agent_usage_proxy": {"value": 8},
            },
        }
    )
    assert "Adoption Index" in md
    assert "72.5" in md


def test_persist_snapshot_sqlite(tmp_path, monkeypatch):
    monkeypatch.setenv("MARKET_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from market_adoption_index import compute_adoption_index, latest_snapshot, persist_snapshot

    with patch("market_adoption_index.adoption_summary", return_value=MOCK_ADOPTION), patch(
        "market_adoption_index.funnel_summary", return_value=MOCK_FUNNEL
    ), patch("market_adoption_index.funnel_retention_summary", return_value=MOCK_RETENTION):
        payload = compute_adoption_index(days=30)
    saved = persist_snapshot(payload)
    assert saved.get("id") is not None
    snap = latest_snapshot()
    assert snap is not None
    assert snap["score"] == payload["score"]
    assert isinstance(snap["signals"], dict)