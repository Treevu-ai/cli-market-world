"""N-5 — linkage_pct alerts in Command & Control."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from command_control_daily import (  # noqa: E402
    LINKAGE_DROP_ALERT_PP,
    LINKAGE_TARGET,
    LINKAGE_WARN_BELOW,
    _enrich_index_metrics,
    _linkage_alerts,
    _linkage_alerts_section,
    _priority_actions,
)


def _metrics(linkage_pct: float) -> dict:
    return {
        "moat": {
            "coverage_7d_pct": 90,
            "store_success_pct": 80,
            "healthy_stores": 8,
            "total_stores": 10,
            "collector_stale": False,
        },
        "index": {"registry_size": 1000, "linkage_pct": linkage_pct},
        "golive": {"overall": "healthy", "alerts": []},
        "pam": {"pass": 10, "fail": 0, "skip": 0},
    }


def test_linkage_alerts_warn_below_target():
    alerts = _linkage_alerts(_metrics(82.0), [])
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "warn"
    assert f"< meta {LINKAGE_TARGET:.0f}%" in alerts[0]["message"]


def test_linkage_alerts_critical_below_floor():
    alerts = _linkage_alerts(_metrics(65.0), [])
    assert alerts[0]["severity"] == "critical"
    assert f"< {LINKAGE_WARN_BELOW:.0f}%" in alerts[0]["message"]


def test_linkage_alerts_drop_vs_yesterday():
    history = [{"index": {"linkage_pct": 88.0}}]
    alerts = _linkage_alerts(_metrics(85.0), history)
    assert any("cayó" in a["message"] for a in alerts)


def test_linkage_alerts_no_drop_when_within_threshold():
    history = [{"index": {"linkage_pct": 85.5}}]
    alerts = _linkage_alerts(_metrics(85.0), history)
    assert not any("cayó" in a["message"] for a in alerts)


def test_linkage_alerts_section_renders():
    text = "\n".join(_linkage_alerts_section(_metrics(65.0), []))
    assert "Alertas Golden Records" in text
    assert "🔴" in text


def test_linkage_alerts_section_empty_when_ok():
    assert _linkage_alerts_section(_metrics(90.0), []) == []


def test_enrich_index_metrics_includes_alerts():
    enriched = _enrich_index_metrics(_metrics(82.0), [])
    assert enriched["index"]["linkage_level"] == "warn"
    assert enriched["index"]["linkage_alerts"]


def test_priority_actions_includes_linkage_alert():
    text = "\n".join(_priority_actions(_metrics(82.0), []))
    assert "Linkage" in text
    assert "Prioridad hoy" in text


def test_linkage_drop_critical_when_large():
    history = [{"index": {"linkage_pct": 90.0}}]
    drop = 90.0 - (LINKAGE_TARGET - LINKAGE_DROP_ALERT_PP - 3.0)
    alerts = _linkage_alerts(_metrics(drop), history)
    drop_alerts = [a for a in alerts if "cayó" in a["message"]]
    assert drop_alerts
    assert drop_alerts[0]["severity"] == "critical"
