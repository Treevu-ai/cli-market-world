"""Adoption Index integration in Command & Control panel."""

import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parent.parent.parent / "cli-market-core"
if CORE_ROOT.is_dir():
    sys.path.insert(0, str(CORE_ROOT))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from command_control_daily import (  # noqa: E402
    _adoption_index_section,
    _normalize_adoption_index_payload,
    _pypi_ci_suffix,
    _scoreboard,
)


def test_normalize_adoption_index_payload():
    data = _normalize_adoption_index_payload(
        {
            "score": 72.5,
            "grade": "B",
            "source": "snapshot",
            "computed_at": "2026-06-08T12:00:00+00:00",
            "breakdown": {"real_usage": {"score": 40}, "downloads": {"score": 90}},
            "signals": {
                "pypi": {"downloads_30d": 240, "downloads_7d": 80, "growth_pct_7d_vs_baseline": 12.0},
                "funnel": {"register": 10, "first_search": 8, "request_pro": 2, "activated": 1},
            },
        }
    )
    assert data["ok"] is True
    assert data["score"] == 72.5
    assert data["first_search"] == 8
    assert data["real_usage_score"] == 40


def test_pypi_ci_suffix_renders_pro_annotation():
    text = _pypi_ci_suffix(
        {
            "downloads_30d_raw": 3462,
            "ci_share_pct_30d": 6.8,
            "pypi_windows_source": "pro_no_ci",
        }
    )
    assert "raw 3,462" in text
    assert "CI 7%" in text
    assert "no-CI" in text


def test_adoption_index_section_renders_score():
    metrics = {
        "adoption_index": _normalize_adoption_index_payload(
            {
                "score": 66.4,
                "grade": "C",
                "source": "live",
                "breakdown": {"real_usage": {"score": 17}, "downloads": {"score": 100}},
                "signals": {
                    "pypi": {
                        "downloads_30d": 3226,
                        "downloads_7d": 3226,
                        "downloads_30d_raw": 3462,
                        "ci_share_pct_30d": 6.8,
                        "windows_source": "pro_no_ci",
                        "growth_pct_7d_vs_baseline": 50,
                    },
                    "funnel": {"register": 52, "first_search": 1, "request_pro": 1, "activated": 1},
                },
            }
        )
    }
    history = [{"adoption_index": {"score": 64.0}}]
    text = "\n".join(_adoption_index_section(metrics, history))
    assert "Adoption Index V1" in text
    assert "66.4/100" in text
    assert "grade *C*" in text
    assert "first_search *1*" in text
    assert "raw 3,462" in text
    assert "no-CI" in text


def test_scoreboard_includes_adoption_index():
    metrics = {
        "moat": {
            "total_indexed": 1000,
            "snapshots_24h": 100,
            "coverage_7d_pct": 80,
            "collector_stale": False,
        },
        "index": {"registry_size": 500, "linkage_pct": 85.0},
        "golive": {"overall": "healthy"},
        "pam": {"pass": 10, "fail": 0, "skip": 2},
        "adoption_index": {"ok": True, "score": 70.0, "grade": "B"},
    }
    text = "\n".join(_scoreboard(metrics))
    assert "Adoption Index 70/100 (B)" in text