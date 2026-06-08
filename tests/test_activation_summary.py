"""activation_summary — webhook vs manual Pro paths."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_funnel import activation_summary, ensure_funnel_schema, record_funnel_event


def test_activation_summary_counts_webhook_and_manual():
    ensure_funnel_schema()
    record_funnel_event(
        "activated",
        username="u-webhook-1",
        meta={"source": "paypal_webhook", "tier": "pro"},
        dedupe=True,
    )
    record_funnel_event(
        "activated",
        username="u-manual-1",
        meta={"source": "ops_manual"},
        dedupe=True,
    )
    data = activation_summary(days=30)
    assert data["activated_events"]["webhook"] >= 1
    assert data["activated_events"]["manual"] >= 1
    assert "webhook_share" in data
    assert "unified_webhook" in data