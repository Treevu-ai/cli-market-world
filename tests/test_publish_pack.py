"""Slack publish pack — gate + live metrics + channel copy."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from publish_pack import (
    apply_live_metrics,
    build_publish_checklist_message,
    build_slack_publish_messages,
    channels_for_date,
    gate_slack_lines,
    marketing_metrics_from_dashboard,
    moat_paste_line,
    slack_copy_block,
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
    assert "RICARDO — ESTE POST ES PARA LINKEDIN PERSONAL" in joined
    assert all(len(m) <= 4000 for m in msgs)
    assert "Checklist publicación" in msgs[-1]
    assert "2026-06-08" in msgs[0]
    assert "Día 8" not in msgs[0]
    assert "LI Personal" in msgs[-1]


def test_channels_for_date_skips_company_on_other_publish_date(tmp_path, monkeypatch):
    root = tmp_path
    (root / "linkedin").mkdir()
    (root / "linkedin-company").mkdir()
    (root / "twitter").mkdir()
    (root / "linkedin" / "Day-08.md").write_text(
        "---\nstatus: ready\n---\n# Day 08\n\n## Post (copiar a LinkedIn — sin link en cuerpo)\n\ntest\n",
        encoding="utf-8",
    )
    (root / "linkedin-company" / "Company-Day-07.md").write_text(
        "---\npublished_at: 2026-06-10\nstatus: ready\n---\n# Company 07\n\n## Post\n\ntest\n",
        encoding="utf-8",
    )
    (root / "twitter" / "tweets-w2.md").write_text(
        "---\n---\n# Twitter\n\n## Lunes — Stat drop\n\ntweet\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(root))
    monkeypatch.setenv("LINKEDIN_COMPANY_DAY_OFFSET", "-1")

    labels = [label for label, _ in channels_for_date(date(2026, 6, 8), 8)]
    assert "LinkedIn Personal" in labels
    assert "LinkedIn Empresa" not in labels


def test_channels_for_date_finds_company_by_published_at(tmp_path, monkeypatch):
    root = tmp_path
    (root / "linkedin").mkdir()
    (root / "linkedin-company").mkdir()
    (root / "linkedin" / "Day-09.md").write_text(
        "---\nstatus: ready\n---\n# Day 09\n\n## Post (copiar a LinkedIn — sin link en cuerpo)\n\ntest\n",
        encoding="utf-8",
    )
    (root / "linkedin-company" / "Company-Day-08.md").write_text(
        "---\npublished_at: 2026-06-11\nstatus: ready\n---\n# Company 08\n\n## Post\n\nwrong day\n",
        encoding="utf-8",
    )
    (root / "linkedin-company" / "Company-Day-06.md").write_text(
        "---\npublished_at: 2026-06-09\nstatus: data-gated\n---\n# Company 06\n\n## Post\n\narroz\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(root))
    monkeypatch.setenv("LINKEDIN_COMPANY_DAY_OFFSET", "-1")

    items = channels_for_date(date(2026, 6, 9), 9)
    labels = [label for label, _ in items]
    paths = [str(path) for _, path in items]
    assert "LinkedIn Personal" in labels
    assert "LinkedIn Empresa" in labels
    assert any("Company-Day-06" in p for p in paths)
    assert not any("Company-Day-08" in p for p in paths)


def test_channels_for_date_spike_reddits_on_june_10():
    items = channels_for_date(date(2026, 6, 10), 10)
    labels = [label for label, _ in items]
    assert "Reddit (r/Python)" in labels
    assert "Reddit (r/aiagents)" in labels
    assert "Hacker News" in labels


def test_slack_copy_block_preserves_bold_markers():
    block = slack_copy_block("**36,800** precios · sin link")
    assert block.startswith("```\n")
    assert block.endswith("\n```")
    assert "**36,800**" in block


def test_build_slack_publish_messages_wraps_copy_in_fences(tmp_path, monkeypatch):
    root = tmp_path
    (root / "linkedin").mkdir()
    (root / "twitter").mkdir()
    (root / "linkedin" / "Day-08.md").write_text(
        """---
status: ready
---
# Day 08

## Post (copiar a LinkedIn — sin link en cuerpo)

**Bold post** line one.

## Primer comentario

https://cli-market.dev?utm_source=linkedin
""",
        encoding="utf-8",
    )
    (root / "twitter" / "tweets-w2.md").write_text(
        "---\n---\n# Twitter\n\n## Lunes — Stat drop\n\ntweet body\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(root))

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
    joined = "\n".join(msgs)
    assert "```\n**Bold post** line one." in joined
    assert "```\nhttps://cli-market.dev?utm_source=linkedin\n```" in joined


def test_md_to_slack_preserves_fenced_copy():
    import slack_notify

    raw = "*Header*\n\n```\n**keep bold**\n```\n\n*Footer*"
    out = slack_notify._md_to_slack(raw)
    assert "**keep bold**" in out
    assert "*Header*" in out


def test_publish_checklist_message():
    text = build_publish_checklist_message(
        campaign_day=8,
        for_date=date(2026, 6, 8),
        gate_pass=True,
    )
    assert "☐ LI Personal — post + hashtags + imagen" in text
    assert "☐ LI Personal — primer comentario" in text
    assert "make publish date=2026-06-08" in text
    assert "Día 8" not in text