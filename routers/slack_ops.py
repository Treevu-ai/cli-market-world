"""Slack interactivity for ops (Pro activation from #cli-market-pro).

Outbound CRM endpoints:
  POST /admin/ops/activate-outbound-target   Activate a target (Day 1 sent)
  POST /admin/ops/deactivate-outbound-target Remove a target activation
  GET  /admin/ops/outbound-activations       Return all {target_id: start_date}
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import date
from urllib.parse import parse_qs

from fastapi import APIRouter, Body, Header, HTTPException, Request

from market_core import db_activate_outbound_target, db_deactivate_outbound_target, db_get_outbound_activations
from server_deps import DEFAULT_TOKEN, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(tags=["slack"])


def _verify_slack_signature(body: bytes, timestamp: str, signature: str, secret: str) -> bool:
    if not secret or not timestamp or not signature:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
    except ValueError:
        return False
    base = f"v0:{timestamp}:{body.decode('utf-8')}"
    digest = "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


@router.post("/slack/interactions")
async def slack_interactions(request: Request):
    """Handle block_actions from #suscripciones-cli-pro (activate Pro after manual payment)."""
    secret = os.getenv("SLACK_SIGNING_SECRET", "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="SLACK_SIGNING_SECRET not configured")

    raw = await request.body()
    ts = request.headers.get("X-Slack-Request-Timestamp", "")
    sig = request.headers.get("X-Slack-Signature", "")
    if not _verify_slack_signature(raw, ts, sig, secret):
        raise HTTPException(status_code=401, detail="invalid Slack signature")

    form = parse_qs(raw.decode("utf-8"))
    payload_raw = (form.get("payload") or [""])[0]
    if not payload_raw:
        raise HTTPException(status_code=400, detail="missing payload")

    payload = json.loads(payload_raw)
    if payload.get("type") != "block_actions":
        return {"ok": True}

    actions = payload.get("actions") or []
    if not actions:
        return {"ok": True}

    action = actions[0]
    if action.get("action_id") != "activate_pro_request":
        return {"ok": True}

    request_id = (action.get("value") or "").strip().upper()
    if not request_id.startswith("PRO-"):
        return {
            "response_type": "ephemeral",
            "text": f"Ref inválida: `{request_id}`",
        }

    user_id = (payload.get("user") or {}).get("id", "")
    if DEFAULT_TOKEN:
        allowed = {
            u.strip()
            for u in os.getenv("SLACK_ACTIVATE_PRO_USERS", "").split(",")
            if u.strip()
        }
        if allowed and user_id not in allowed:
            return {
                "response_type": "ephemeral",
                "text": "No autorizado para activar Pro desde Slack.",
            }

    from routers.payments import _activate_pro_from_request

    result = _activate_pro_from_request(request_id, source="slack_interaction")
    if any(a.startswith("pro_activated:") for a in result):
        username = next(a.split(":", 1)[1] for a in result if a.startswith("pro_activated:"))
        logger.info("audit slack_activate_pro request_id=%s user=%s by=%s", request_id, username, user_id)
        return {
            "response_type": "in_channel",
            "replace_original": False,
            "text": f"✅ Pro activado para `{username}` (ref `{request_id}`). Cliente: `market whoami`",
        }

    if any(a.startswith("payment_not_manual:") for a in result):
        return {
            "response_type": "ephemeral",
            "text": (
                f"`{request_id}` es PayPal/Mercado Pago — no se activa manualmente. "
                "Espere el webhook tras el pago."
            ),
        }

    return {
        "response_type": "ephemeral",
        "text": f"No se pudo activar `{request_id}`: {', '.join(result)}",
    }


# ── Outbound CRM ──────────────────────────────────────────────────────────────

@router.post("/admin/ops/activate-outbound-target")
def activate_outbound_target(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Mark a retailer target as Day 1 contacted.

    Body: {"target_id": "tottus-pe", "start_date": "2026-06-14", "notes": "..."}
    Called by Slack Workflow Builder webhook after filling the activation form.
    """
    require_admin(authorization)

    target_id = (body.get("target_id") or "").strip()
    start_date_raw = (body.get("start_date") or "").strip() or date.today().isoformat()
    notes = (body.get("notes") or "").strip()

    if not target_id:
        raise HTTPException(status_code=400, detail="target_id required")
    try:
        date.fromisoformat(start_date_raw)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"invalid start_date: {start_date_raw}")

    db_activate_outbound_target(target_id, start_date_raw, notes)
    logger.info("outbound_activate api target=%s start=%s", target_id, start_date_raw)

    from datetime import date as _date, timedelta
    start = _date.fromisoformat(start_date_raw)
    reminders = {
        day: (start + timedelta(days=day - 1)).isoformat()
        for day in (3, 7, 10, 14)
    }
    return {
        "ok": True,
        "target_id": target_id,
        "start_date": start_date_raw,
        "sequence_dates": reminders,
    }


@router.post("/admin/ops/deactivate-outbound-target")
def deactivate_outbound_target(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Remove a target from the active outbound sequence."""
    require_admin(authorization)

    target_id = (body.get("target_id") or "").strip()
    if not target_id:
        raise HTTPException(status_code=400, detail="target_id required")

    db_deactivate_outbound_target(target_id)
    return {"ok": True, "target_id": target_id}


@router.get("/admin/ops/outbound-activations")
def get_outbound_activations(
    authorization: str | None = Header(None),
):
    """Return all active outbound targets as {target_id: start_date}."""
    require_admin(authorization)
    return db_get_outbound_activations()