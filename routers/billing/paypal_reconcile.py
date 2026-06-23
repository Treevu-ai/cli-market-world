"""Poll PayPal for ACTIVE subscriptions when webhooks are delayed or missed."""

from __future__ import annotations

import logging

from market_core import db_get_subscription, get_db
from procure_billing import is_procure_tier
from routers.billing.activation import activate_paypal_subscription

logger = logging.getLogger(__name__)

_PAID_TIERS = frozenset({"pro", "builder", "enterprise"})


def _list_paypal_billing_pending(username: str) -> list[dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT external_id, gateway, username, kind
        FROM billing_pending
        WHERE username = ? AND gateway = 'paypal'
        """,
        (username,),
    ).fetchall()
    db.close()
    return [dict(row) for row in rows]


async def fetch_paypal_subscription_status(sub_id: str) -> dict:
    """GET /v1/billing/subscriptions/{id} — returns status + custom_id."""
    from market_connectors.paypal_payments import PAYPAL_API, _get_access_token
    import httpx

    sub_id = (sub_id or "").strip()
    if not sub_id:
        return {"ok": False, "status": "", "error": "missing_subscription_id"}
    try:
        token = await _get_access_token()
    except Exception as exc:
        return {"ok": False, "status": "", "error": str(exc)}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{PAYPAL_API}/v1/billing/subscriptions/{sub_id}",
            headers=headers,
        )
    if resp.status_code != 200:
        return {"ok": False, "status": "", "error": resp.text}
    data = resp.json()
    return {
        "ok": True,
        "status": (data.get("status") or "").strip().upper(),
        "custom_id": (data.get("custom_id") or "").strip(),
    }


def _user_already_paid(username: str) -> bool:
    tier = (db_get_subscription(username).get("tier") or "free").strip().lower()
    return tier in _PAID_TIERS or is_procure_tier(tier)


async def reconcile_paypal_subscriptions_for_user(
    username: str,
    *,
    lang: str = "es",
) -> dict:
    """Activate paid PayPal subscriptions still waiting on webhook delivery."""
    username = (username or "").strip()
    if not username:
        return {"ok": False, "error": "username required", "actions": []}
    if _user_already_paid(username):
        return {"ok": True, "skipped": "already_paid", "actions": []}

    pending_rows = _list_paypal_billing_pending(username)
    if not pending_rows:
        return {"ok": True, "skipped": "no_pending", "actions": []}

    actions: list[str] = []
    activated = 0
    for row in pending_rows:
        sub_id = row.get("external_id") or ""
        status = await fetch_paypal_subscription_status(sub_id)
        if not status.get("ok"):
            actions.append(f"paypal_fetch_error:{sub_id}")
            continue
        if status.get("status") != "ACTIVE":
            actions.append(f"paypal_pending:{sub_id}:{status.get('status') or 'unknown'}")
            continue
        row_user = (row.get("username") or username).strip()
        paypal_user = (status.get("custom_id") or row_user).strip()
        if paypal_user and paypal_user != row_user:
            logger.warning(
                "paypal reconcile username mismatch pending=%s custom_id=%s sub=%s",
                row_user,
                paypal_user,
                sub_id,
            )
        acts = activate_paypal_subscription(
            username=row_user,
            sub_id=sub_id,
            kind=row.get("kind") or "subscription",
            source="paypal_reconcile",
            lang=lang,
        )
        actions.extend(acts)
        if any(a.endswith(f":{row_user}") for a in acts if "_activated:" in a):
            activated += 1

    return {
        "ok": True,
        "activated": activated,
        "pending_checked": len(pending_rows),
        "actions": actions,
    }
