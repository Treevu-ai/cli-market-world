"""Slack publish pack — gate + live metrics + channel copy."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from publish_pack import (
    apply_live_metrics,
    build_publish_checklist_message,
    build_slack_publish_messages,
    gate_slack_lines,
    marketing_metrics_from_dashboard,
    moat_paste_line,
)


def test_marketing_metrics_from_dashboard():
    data = {
        "kpis": {
            "total_indexed": 50902,
            "snapshots_24h": 40126,
            "coverage_7d_pct": 100,
            "stores_indexed": 38,
        },
        "collector": {"status": "ok"},
    }
    m = marketing_metrics_from_dashboard(data)
    assert m["gate_pass"] is True
    assert m["total_indexed"] == 50902
    assert m["snapshots_24h"] == 40126


def test_gate_closed_when_low_coverage():
    data = {"kpis": {"total_indexed": 50000, "coverage_7d_pct": 50, "snapshots_24h": 1000}}
    m = marketing_metrics_from_dashboard(data)
    assert m["gate_pass"] is False
    lines = gate_slack_lines(m)
    assert any("CERRADO" in ln for ln in lines)


def test_apply_live_metrics_rewrites_moat_line():
    text = "**36,800** precios en refresh 24h · **50,100** indexados · **38** retailers fresh"
    metrics = {
        "snapshots_24h": 40126,
        "total_indexed": 50902,
        "stores_indexed": 38,
        "coverage_7d_pct": 100,
    }
    out = apply_live_metrics(text, metrics)
    assert "40,126" in out
    assert "50,902" in out


def test_moat_paste_line_format():
    line = moat_paste_line(
        {
            "snapshots_24h": 1000,
            "total_indexed": 2000,
            "stores_indexed": 38,
            "coverage_7d_pct": 99.2,
        }
    )
    assert "1,000" in line
    assert "2,000" in line


def test_build_slack_publish_messages_has_order_and_gate():
    msgs = build_slack_publish_messages(
        ds="2026-06-08",
        campaign_day=8,
        for_date=date(2026, 6, 8),
        metrics={
            "gate_pass": True,
            "total_indexed": 50902,
            "snapshots_24h": 40126,
            "coverage_7d_pct": 100,
            "stores_indexed": 38,
            "collector_status": "ok",
        },
        post_utc_hour=13,
    )
    assert msgs
    joined = "\n".join(msgs)
    assert "Orden" in joined
    assert "Data-gate" in joined
    assert "50,902" in joined
    assert all(len(m) <= 4000 for m in msgs)
    assert "Checklist publicación" in msgs[-1]
    assert "LI Personal" in msgs[-1]


def test_publish_checklist_message():
    text = build_publish_checklist_message(
        campaign_day=8,
        for_date=date(2026, 6, 8),
        gate_pass=True,
    )
    assert "☐ LI Personal — post" in text
    assert "☐ LI Personal — comentario" in text
    assert "make publish day=8" in text