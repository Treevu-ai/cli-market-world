"""Price alert CRUD endpoints.

Endpoints:
  POST   /v1/alerts           Create a new alert (Pro+)
  GET    /v1/alerts           List user's alerts (Pro+)
  DELETE /v1/alerts/{id}      Delete an alert (Pro+)
  PATCH  /v1/alerts/{id}      Enable/disable an alert (Pro+)
  GET    /v1/alerts/{id}/events  Recent events for an alert (Pro+)

Conditions: price_jump | price_drop | price_min_30d | dispersion_anomaly
"""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, field_validator

from market_alerts import (
    SUPPORTED_CONDITIONS,
    db_create_alert,
    db_delete_alert,
    db_get_alert,
    db_list_alerts,
    db_toggle_alert,
)
from market_billing import db_get_subscription, TIERS
from market_core import get_db
from server_deps import require_pro

router = APIRouter(prefix="/v1/alerts", tags=["alerts"])


class CreateAlertRequest(BaseModel):
    name: str = ""
    condition: str
    product_query: str
    store: str = ""
    threshold_pct: float = 5.0
    notify_email: str = ""
    notify_webhook: str = ""
    cooldown_hours: int = 24

    @field_validator("condition")
    @classmethod
    def _validate_condition(cls, v: str) -> str:
        if v not in SUPPORTED_CONDITIONS:
            raise ValueError(f"condition must be one of {SUPPORTED_CONDITIONS}")
        return v

    @field_validator("product_query")
    @classmethod
    def _validate_query(cls, v: str) -> str:
        v = v.strip()[:200]
        if not v:
            raise ValueError("product_query cannot be empty")
        return v

    @field_validator("threshold_pct")
    @classmethod
    def _validate_threshold(cls, v: float) -> float:
        if not (0.1 <= v <= 100.0):
            raise ValueError("threshold_pct must be between 0.1 and 100")
        return v

    @field_validator("cooldown_hours")
    @classmethod
    def _validate_cooldown(cls, v: int) -> int:
        if not (1 <= v <= 720):
            raise ValueError("cooldown_hours must be between 1 and 720")
        return v


class ToggleAlertRequest(BaseModel):
    active: bool


def _check_alert_quota(username: str) -> None:
    """Enforce per-tier alert limit before creating a new one."""
    sub = db_get_subscription(username)
    tier = sub.get("tier", "free")
    limit = TIERS.get(tier, TIERS["free"])["alerts"]
    if limit == -1:
        return  # enterprise: unlimited
    if limit == 0:
        raise HTTPException(status_code=403, detail="Alerts not available on your plan.")
    existing = db_list_alerts(username)
    if len(existing) >= limit:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Alert limit reached ({limit} alerts on {tier} plan). "
                "Upgrade to Enterprise for unlimited alerts."
            ),
        )


@router.post("")
def create_alert(body: CreateAlertRequest, authorization: str | None = Header(None)):
    """Create a price alert. Pro: up to 10 alerts. Enterprise: unlimited."""
    username = require_pro(authorization)
    _check_alert_quota(username)

    email = body.notify_email.strip()
    webhook = body.notify_webhook.strip()

    # Enterprise-only: webhook channel
    if webhook:
        sub = db_get_subscription(username)
        if sub.get("tier", "free") != "enterprise":
            raise HTTPException(
                status_code=403,
                detail="Webhook notifications require Enterprise plan.",
            )

    if not email and not webhook:
        raise HTTPException(
            status_code=400,
            detail="Provide at least notify_email or notify_webhook.",
        )

    alert = db_create_alert(
        username=username,
        name=body.name or f"{body.condition} — {body.product_query}",
        condition=body.condition,
        product_query=body.product_query,
        store=body.store,
        threshold_pct=body.threshold_pct,
        notify_email=email,
        notify_webhook=webhook,
        cooldown_hours=body.cooldown_hours,
    )
    return {"alert": alert, "message": "Alert created. Will evaluate after next collection cycle."}


@router.get("")
def list_alerts(authorization: str | None = Header(None)):
    """List all alerts for the authenticated user."""
    username = require_pro(authorization)
    alerts = db_list_alerts(username)
    sub = db_get_subscription(username)
    tier = sub.get("tier", "free")
    limit = TIERS.get(tier, TIERS["free"])["alerts"]
    return {
        "alerts": alerts,
        "total": len(alerts),
        "limit": limit if limit != -1 else "unlimited",
    }


@router.delete("/{alert_id}")
def delete_alert(alert_id: str, authorization: str | None = Header(None)):
    """Delete an alert permanently."""
    username = require_pro(authorization)
    ok = db_delete_alert(username, alert_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {"deleted": alert_id}


@router.patch("/{alert_id}")
def toggle_alert(
    alert_id: str,
    body: ToggleAlertRequest,
    authorization: str | None = Header(None),
):
    """Enable or disable an alert without deleting it."""
    username = require_pro(authorization)
    alert = db_get_alert(alert_id)
    if not alert or alert["username"] != username:
        raise HTTPException(status_code=404, detail="Alert not found.")
    updated = db_toggle_alert(username, alert_id, body.active)
    return {"alert": updated}


@router.get("/{alert_id}/events")
def get_alert_events(
    alert_id: str,
    limit: int = 20,
    authorization: str | None = Header(None),
):
    """Recent firing events for a specific alert."""
    username = require_pro(authorization)
    alert = db_get_alert(alert_id)
    if not alert or alert["username"] != username:
        raise HTTPException(status_code=404, detail="Alert not found.")
    db = get_db()
    try:
        rows = db.execute(
            """SELECT product_name, store, condition, price_now, price_before,
                      delta_pct, notified, fired_at
               FROM alert_events WHERE alert_id=?
               ORDER BY fired_at DESC LIMIT ?""",
            (alert_id, min(limit, 100)),
        ).fetchall()
        return {"alert_id": alert_id, "events": [dict(r) for r in rows]}
    finally:
        db.close()
