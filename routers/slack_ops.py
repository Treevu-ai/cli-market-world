"""Slack interactivity for ops (Pro activation from #cli-market-pro)."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request

from server_deps import DEFAULT_TOKEN

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

    return {
        "response_type": "ephemeral",
        "text": f"No se pudo activar `{request_id}`: {', '.join(result)}",
    }