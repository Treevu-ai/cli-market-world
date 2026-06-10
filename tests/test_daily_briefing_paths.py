"""daily_briefing paths with external content repo."""

import os
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "ops"))


def test_build_content_report_external_root(tmp_path, monkeypatch):
    content = tmp_path / "cli-market-content"
    (content / "linkedin").mkdir(parents=True)
    (content / "linkedin" / "Day-02.md").write_text(
        """---
title: Day 02
status: ready
day: 2
published_at:
---
# Day 02 — Test title

## Hooks (elegir 1)

1. Hook test

## Post (copiar a LinkedIn — sin link en cuerpo)

Post body here.

## Primer comentario

https://cli-market.dev

## Hashtags

#AI

## Checklist

- [ ] item

## Assets

**Adjuntar:** image.png
""",
        encoding="utf-8",
    )
    (content / "linkedin" / "data-gate.md").write_text("# gate\n", encoding="utf-8")

    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(content))
    monkeypatch.setenv("LINKEDIN_CAMPAIGN_START", "2026-05-29")
    monkeypatch.chdir(REPO_ROOT)

    import daily_briefing

    report = daily_briefing.build_content_report(date(2026, 5, 30))
    assert "linkedin/Day-02.md" in report
    assert "Test title" in report
    assert "/home/" not in report or str(content) not in report


def test_product_daily_dir_is_in_product_repo(monkeypatch, tmp_path):
    content = tmp_path / "cli-market-content"
    (content / "linkedin").mkdir(parents=True)
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(content))
    monkeypatch.chdir(REPO_ROOT)

    import daily_briefing

    product_dir = daily_briefing._product_daily_dir()
    content_dir = daily_briefing._content_daily_dir()
    assert product_dir == REPO_ROOT / "ops" / "daily"
    assert content_dir == content / "generated" / "daily"


def test_repo_file_link_product_vs_content(monkeypatch):
    import daily_briefing

    monkeypatch.setenv("GITHUB_REPOSITORY", "Treevu-ai/cli-market-world")
    monkeypatch.setenv(
        "CLI_MARKET_CONTENT_GITHUB_REPO", "Treevu-ai/cli-market-content"
    )

    product_link = daily_briefing._repo_file_link("ops/daily/2026-06-09-product.md")
    assert "cli-market-world" in product_link
    assert "ops/daily/2026-06-09-product.md" in product_link

    content_link = daily_briefing._repo_file_link(
        "generated/daily/2026-06-09-content.md"
    )
    assert "cli-market-content" in content_link
    assert "generated/daily/2026-06-09-content.md" in content_link
