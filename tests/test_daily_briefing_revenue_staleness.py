"""Regression test: the Slack "Bitácora producto" revenue line must flag a
GTM-Hub.md that hasn't been touched in a long time, not just one still
carrying the literal "[ACTUALIZAR]" placeholder.

_read_revenue_from_gtm_hub() parses a hand-maintained markdown table for
MRR/ARR/clientes. The only staleness signal previously checked was whether
"[ACTUALIZAR]" was still literally present — if a human fills in a real
number once and never updates it again, the message keeps showing that
number as current indefinitely with no warning, since nothing detects the
*value* itself is stale. Add a file-mtime-based signal as a second,
independent check.

Tests call _read_revenue_from_gtm_hub()/_format_revenue_lines() directly
rather than the full build_slack_product_message() — that function also
pulls in _load_monday()/calendar_channels, which caches env-derived state
at first import and isn't safe to invoke from more than one test file in
the same pytest session (see test_daily_briefing_paths.py, which owns that
code path already).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "ops"))

# Imported inside each test, not here at module level — see module docstring.


def _write_gtm_hub(tmp_path: Path, monkeypatch) -> Path:
    content = tmp_path / "cli-market-content"
    (content / "linkedin").mkdir(parents=True)
    strategy = content / "strategy"
    strategy.mkdir()
    gtm = strategy / "GTM-Hub.md"
    gtm.write_text(
        "| Metric | Value |\n"
        "|---|---|\n"
        "| **MRR total** | $500 |\n"
        "| **ARR implícito** | $6000 |\n"
        "| Clientes activos (pagos) | 12 |\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CLI_MARKET_CONTENT_DIR", str(content))
    return gtm


def test_fresh_gtm_hub_has_no_stale_days(tmp_path, monkeypatch):
    gtm = _write_gtm_hub(tmp_path, monkeypatch)
    now = time.time()
    os.utime(gtm, (now, now))

    import daily_briefing

    revenue = daily_briefing._read_revenue_from_gtm_hub()
    assert revenue["stale_days"] is None

    lines = daily_briefing._format_revenue_lines(revenue)
    assert any("💰" in line for line in lines)
    assert not any("desactualizado" in line.lower() for line in lines)


def test_stale_gtm_hub_flags_even_without_the_actualizar_placeholder(tmp_path, monkeypatch):
    gtm = _write_gtm_hub(tmp_path, monkeypatch)
    old = time.time() - 30 * 86_400  # 30 days ago
    os.utime(gtm, (old, old))

    import daily_briefing

    revenue = daily_briefing._read_revenue_from_gtm_hub()
    assert revenue["stale_days"] is not None
    assert revenue["stale_days"] >= 29

    lines = daily_briefing._format_revenue_lines(revenue)
    assert any("⚠️" in line for line in lines)
    assert any("desactualizado" in line.lower() for line in lines)
