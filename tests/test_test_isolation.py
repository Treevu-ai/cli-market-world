"""Regression tests: every credential that gates a real outbound network call
(Slack, SMTP, Procure Copilot webhook) must be scrubbed from the test process
env by conftest.py — same incident class as the SLACK_BOT_TOKEN leak that
caused tests to post fake pending-payment messages to production Slack.

Found in the same audit: PROCURE_WEBHOOK_URL/PROCURE_WEBHOOK_SECRET
(routers/billing/notifications.py::_notify_procure_payment, reachable
unmocked from tests/test_checkout_payments.py and tests/test_server.py) and
SMTP_HOST/SMTP_USER/SMTP_PASSWORD (market_connectors.email_outbound._send,
gated only by per-test-file manual mocking, not a global scrub) are the same
shape of gap: an os.getenv(...) check that silently fires a real network
call with real credentials if a developer's shell happens to have them set,
and no test in this repo exercises the failure path deliberately."""

from __future__ import annotations

import os


def test_procure_webhook_credentials_are_scrubbed_in_test_session():
    assert not os.environ.get("PROCURE_WEBHOOK_URL", ""), "PROCURE_WEBHOOK_URL leaked into test env"
    assert not os.environ.get("PROCURE_WEBHOOK_SECRET", "")


def test_smtp_credentials_are_scrubbed_in_test_session():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from market_connectors.email_outbound import _smtp_configured

    assert not os.environ.get("SMTP_HOST", "")
    assert not os.environ.get("SMTP_USER", "")
    assert not os.environ.get("SMTP_PASSWORD", "")
    assert _smtp_configured() is False
