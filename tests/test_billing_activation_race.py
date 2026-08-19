"""Regression: TOCTOU race on subscription-request activation.

_activate_pro_from_request/_activate_procure_from_request/
_activate_retailer_growth_from_request each did "read status -> if not
activated: run full activation flow", with no atomicity between the read
and the write. Two concurrent callers for the same request_id (two ops
staff double-clicking Slack approve, or two payment-retry webhook
deliveries resolving to the same request_id) both passed the read-check
and both ran the full flow -- duplicate password re-provisioning emails,
duplicate Slack pings. Found by security-reviewer scan 2026-08-19; fixed
via routers/billing/activation.py::_claim_activation, an atomic
UPDATE ... WHERE status != 'activated'.
"""

from __future__ import annotations

import threading
from unittest.mock import patch

import pytest
from market_core import db_create_subscription_request, db_save_user, ensure_db_initialized, get_db

from routers.billing.activation import _activate_pro_from_request


@pytest.fixture(autouse=True)
def _init_db():
    ensure_db_initialized()
    yield


def test_concurrent_pro_activation_claims_exactly_once():
    username = "race-pro-user"
    db = get_db()
    db.execute("DELETE FROM app_users WHERE username = ?", (username,))
    db.execute("DELETE FROM subscription_requests WHERE username = ?", (username,))
    db.commit()
    db.close()

    db_save_user(username, "hash", None, f"{username}@test.com")
    req = db_create_subscription_request(username, f"{username}@test.com", "", prefix="PRO")
    request_id = req["id"]

    barrier = threading.Barrier(2)
    results: list[list[str]] = []
    lock = threading.Lock()

    def _run():
        barrier.wait()
        actions = _activate_pro_from_request(request_id, source="mercadopago_webhook")
        with lock:
            results.append(actions)

    # Side effects (email/Slack) aren't the point of this test -- silence
    # them so the race is isolated to the activation claim itself.
    with patch("routers.billing.activation._append_pro_activation_email_actions"), \
         patch("routers.billing.activation._slack_notify_build_pro"):
        threads = [threading.Thread(target=_run) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    winners = [a for a in results if any(x.startswith("pro_activated:") for x in a)]
    losers = [a for a in results if any(x.startswith("already_activated:") for x in a)]
    assert len(winners) == 1, f"expected exactly one winner, got: {results}"
    assert len(losers) == 1, f"expected exactly one loser, got: {results}"
