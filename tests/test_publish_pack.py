"""Slack publish pack — gate + live metrics + channel copy."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from publish_pack import (
    apply_live_metrics,
    build_gtm_channel_deliveries,
    build_publish_checklist_message,
    build_slack_publish_messages,
    channels_for_date,
    gate_slack_lines,
    marketing_metrics_from_dashboard,
    moat_paste_line,
    slack_copy_block,
)
from slack_notify import slack_channel_for_gtm_label


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


def test_apply_live_metrics_coverage_instruction_marker():
    """Coverage instruction-style [ACTUALIZAR] markers are resolved."""
    text = (
        "100% de cobertura en los últimos 7 días.\n\n"
        "[ACTUALIZAR: reemplazar 100% con valor vigente de coverage_7d_pct en price-pulse semana activa]\n\n"
        "¿Qué significa ese número?\n\n"
        "Esta semana: 100% de cobertura 7d en 38 tiendas activas. "
        "[ACTUALIZAR: reemplazar 100% con coverage_7d_pct vigente y 35 con tiendas fresh vigentes]"
    )
    metrics = {
        "snapshots_24h": 40126,
        "total_indexed": 50902,
        "stores_indexed": 41,
        "coverage_7d_pct": 97,
    }
    out = apply_live_metrics(text, metrics)
    assert "97% de cobertura en los últimos 7 días." in out
    assert "[ACTUALIZAR" not in out
    assert "41 tiendas activas" in out


def test_apply_live_metrics_week_number():
    """Semana [ACTUALIZAR] is replaced with ISO week when for_date provided."""
    from datetime import date

    text = 'Título: "Spread — Semana [ACTUALIZAR]". Pie: "Fuente: CLI Market"'
    metrics = {
        "snapshots_24h": 1,
        "total_indexed": 1,
        "stores_indexed": 1,
        "coverage_7d_pct": 100,
    }
    out = apply_live_metrics(text, metrics, for_date=date(2026, 6, 24))
    assert "Semana W26" in out
    assert "[ACTUALIZAR]" not in out


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


def test_slack_channel_for_gtm_label_maps_calendar_names():
    # All GTM labels now consolidate to #publicaciones-redes (C0B6ZJ1B9B8)
    publicaciones = "C0B6ZJ1B9B8"
    assert slack_channel_for_gtm_label("LinkedIn Personal") == publicaciones
    assert slack_channel_for_gtm_label("LinkedIn Personal (AR)") == publicaciones
    assert slack_channel_for_gtm_label("LinkedIn Empresa") == publicaciones
    assert slack_channel_for_gtm_label("Twitter/X W2") == publicaciones
    assert slack_channel_for_gtm_label("Reddit (r/Python)") == publicaciones
    assert slack_channel_for_gtm_label("DEV.to") == publicaciones
    assert slack_channel_for_gtm_label("Hacker News") == publicaciones


def test_build_gtm_channel_deliveries_splits_per_channel():
    summary, deliveries = build_gtm_channel_deliveries(
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
    assert "ÍNDICE PUBLICACIONES" in summary
    assert deliveries
    labels = {d.label for d in deliveries}
    assert "LinkedIn Personal" in labels
    assert all(d.channel_id.startswith("C0") for d in deliveries)
    assert all("RICARDO" in d.text for d in deliveries)
    li = next(d for d in deliveries if d.label == "LinkedIn Personal")
    assert len(li.messages) >= 3
    joined_li = "\n".join(li.messages)
    assert "Post (copiar a LinkedIn" in joined_li or "Post" in joined_li
    assert "Primer comentario" in joined_li


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


def test_activation_blitz_june_10_channels(monkeypatch):
    """Activation Blitz routes Day-11 + one Reddit, not spike Day-10."""
    content_dir = Path(__file__).resolve().parent.parent.parent / "cli-market-content"
    if not (content_dir / "scripts" / "calendar_channels.py").is_file():
        import pytest

        pytest.skip("cli-market-content checkout required for activation schedule")
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(content_dir))
    items = channels_for_date(date(2026, 6, 10), 10)
    labels = [label for label, _ in items]
    paths = [path.name for _, path in items]
    assert "Day-11.md" in paths
    assert "Day-10.md" not in paths
    assert "Reddit (r/Python)" in labels
    assert "Reddit (r/aiagents)" not in labels
    assert "WhatsApp" in labels
    assert "Instagram" in labels


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


def test_slack_matches_all_content_repo_sections(tmp_path, monkeypatch):
    root = tmp_path
    (root / "linkedin-company").mkdir()
    (root / "linkedin").mkdir()
    (root / "twitter").mkdir()
    (root / "linkedin-company" / "Company-Day-08.md").write_text(
        """---
status: ready
published_at: 2026-06-10
---
# Company Day 08 — Arroz

**Calendario:** [[company-calendar]]

## Hook (elegir 1)

1. **Dato de mercado:** Hook A

## Post (copiar a LinkedIn — sin link en cuerpo)

Cuerpo del post.

## Primer comentario

hello@cli-market.dev

## Assets

**Ruta sugerida:** `linkedin-company/assets/company-day-08/`

## Checklist pre-publicación

- [ ] CTA activo
""",
        encoding="utf-8",
    )
    (root / "linkedin" / "Day-11.md").write_text(
        """---
status: ready
published_at: 2026-06-10
---
# Day 11 — Electro

## Post (copiar a LinkedIn — sin link en cuerpo)

Post personal.

## Primer comentario

https://cli-market.dev
""",
        encoding="utf-8",
    )
    (root / "twitter" / "tweets-w2.md").write_text(
        "---\n---\n# Twitter\n\n## Miércoles — Hot take\n\n```\ntweet body\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(root))
    monkeypatch.setenv("LINKEDIN_COMPANY_DAY_OFFSET", "-1")

    _, deliveries = build_gtm_channel_deliveries(
        campaign_day=10,
        for_date=date(2026, 6, 10),
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
    company = next(d for d in deliveries if d.label == "LinkedIn Empresa")
    joined = "\n".join(company.messages)
    assert "Hook A" in joined
    assert "Cuerpo del post" in joined
    assert "hello@cli-market.dev" in joined
    assert "company-day-08" in joined
    assert "Checklist pre-publicación" in joined
    assert "CTA activo" in joined


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