"""Regression tests for ops/ceo_metrics_report.py's MRR-estimate math.

Zero test coverage existed for this file before — a hardcoded ``* 49``
literal for the MRR status-emoji threshold sat three lines below code that
correctly used the live ``PUBLIC_PRO_PRICE_USD`` constant, and would have
gone undetected by any test. These tests pin both the emoji math and the
module-level-import staleness risk flagged in the same audit.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

import ceo_metrics_report as cmr
import market_billing


def _row_block(report: str, metric: str) -> str:
    """_row() renders a 4-line block per metric; return the block containing
    ``metric`` so assertions can check the status emoji and the dollar
    figure together, since they're on separate physical lines."""
    lines = report.splitlines()
    start = next(i for i, line in enumerate(lines) if metric in line)
    return "\n".join(lines[start : start + 4])


def _stub_fetches(monkeypatch, *, activated: int):
    monkeypatch.setattr(cmr, "_fetch_dashboard", lambda: {})
    monkeypatch.setattr(
        cmr, "_fetch_funnel", lambda: {"kpis": {"revenue": {"activated": activated}}}
    )
    monkeypatch.setattr(cmr, "_fetch_adoption", lambda: {})
    monkeypatch.setattr(cmr, "_fetch_index_stats", lambda: {})
    monkeypatch.setattr(cmr, "_fetch_pypi", lambda: {})
    monkeypatch.setattr(cmr, "_fetch_pypi_consolidated", lambda: {})
    monkeypatch.setattr(cmr, "_content_today", lambda: {})


def test_mrr_status_emoji_uses_live_price_not_hardcoded_49(monkeypatch):
    """15 activations * $100/mo = $1500 >= $1000 target -> should be ✅.
    The old hardcoded ``* 49`` would compute 15*49=735 < 1000 -> ⚠️ instead —
    a status emoji silently wrong relative to the dollar figure printed right
    next to it on the same line."""
    monkeypatch.setattr(market_billing, "PUBLIC_PRO_PRICE_USD", 100)
    _stub_fetches(monkeypatch, activated=15)

    report = cmr.build_report(remote=True)

    mrr_block = _row_block(report, "MRR estimado")
    assert "$1500" in mrr_block
    assert "✅" in mrr_block


def test_mrr_status_emoji_reflects_price_drop_below_target(monkeypatch):
    """Same activation count, lower price -> must NOT hit the $1000 target,
    proving the emoji tracks the live price rather than a fixed threshold."""
    monkeypatch.setattr(market_billing, "PUBLIC_PRO_PRICE_USD", 20)
    _stub_fetches(monkeypatch, activated=15)

    report = cmr.build_report(remote=True)

    mrr_block = _row_block(report, "MRR estimado")
    assert "$300" in mrr_block
    assert "⚠️" in mrr_block
