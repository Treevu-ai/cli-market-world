"""Operational / admin endpoints — used by the dashboard and ops scripts.

Endpoints:
  GET  /admin/debug-fetch     Test fetch_store + product_from_json for one store/query
  POST /admin/activate-pro-request  Activate Pro from pending PRO- request (manual)
  POST /admin/resend-pro-activation-email  Resend Pro welcome email for activated request
  POST /admin/collect         Trigger a price collection run synchronously
  POST /v1/admin/scan-stores  Probe known retailer domains for liveness
  POST /v1/admin/set-tier     Set a user's subscription tier (free|pro|enterprise)
  POST /v1/admin/revoke-api-key  Revoke a leaked or compromised sk- API key
  POST /admin/cron/funnel-digest  Post evening funnel digest to Slack (#funnel-cli-market)
  POST /admin/cron/command-control  Post morning founder panel (#command-control-cli-market)
  POST /admin/cron/adoption-index  Persist Adoption Index snapshot (nightly cron)
  POST /admin/cron/indicators-refresh  Refresh moat indicators (internal + macro + Phase 2)

Protected with MARKET_API_TOKEN (Bearer). Set on Railway before exposing publicly.
"""

from __future__ import annotations

import logging
import time

import httpx
from fastapi import APIRouter, Body, Header, HTTPException

from market_core import (
    STORES,
    db_get_subscription,
    db_get_users,
    db_set_subscription,
    fetch_store,
    product_from_json,
)
from market_billing import TIERS
from procure_billing import all_valid_tiers
from server_deps import require_admin

logger = logging.getLogger(__name__)

_VALID_TIERS = all_valid_tiers(TIERS)

router = APIRouter(prefix="", tags=["admin"])


@router.get("/admin/debug-fetch")
async def debug_fetch(
    store: str = "wong",
    query: str = "leche",
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    """Smoke test the data pipeline for one store: raw fetch → normalize."""
    raw = await fetch_store(store, query, page=1, limit=3)
    products = [product_from_json(p, store) for p in raw[:3]]
    return {"store": store, "query": query, "results": len(raw), "products": products}


@router.post("/admin/activate-pro-request")
def admin_activate_pro_request(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Activate Pro from a pending PRO- request (manual Yape/Plin or ops)."""
    require_admin(authorization)
    request_id = (body.get("request_id") or body.get("ref") or "").strip().upper()
    if not request_id.startswith("PRO-"):
        raise HTTPException(status_code=400, detail="request_id must be PRO-XXXXXXXX")
    force = bool(body.get("force"))

    from routers.payments import _activate_pro_from_request

    actions = _activate_pro_from_request(request_id, source="admin_api", force=force)
    logger.info("audit admin_activate_pro request_id=%s actions=%s", request_id, actions)
    if not any(a.startswith("pro_activated:") for a in actions):
        raise HTTPException(status_code=404, detail={"request_id": request_id, "actions": actions})
    username = next(a.split(":", 1)[1] for a in actions if a.startswith("pro_activated:"))
    return {"ok": True, "request_id": request_id, "username": username, "actions": actions}


@router.post("/admin/resend-pro-activation-email")
def admin_resend_pro_activation_email(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Resend Pro welcome email (new CLI password) for an activated PRO- request."""
    require_admin(authorization)
    request_id = (body.get("request_id") or body.get("ref") or "").strip().upper()
    if not request_id.startswith("PRO-"):
        raise HTTPException(status_code=400, detail="request_id must be PRO-XXXXXXXX")

    email_override = (body.get("email") or "").strip()
    from routers.payments import resend_pro_activation_email

    actions = resend_pro_activation_email(request_id, email_override=email_override)
    logger.info(
        "audit admin_resend_pro_activation request_id=%s email_override=%s actions=%s",
        request_id,
        bool(email_override),
        actions,
    )

    if actions[0].startswith("request_not_found:"):
        raise HTTPException(status_code=404, detail={"request_id": request_id, "actions": actions})
    if actions[0].startswith("request_not_activated:"):
        raise HTTPException(
            status_code=409,
            detail={"request_id": request_id, "actions": actions, "hint": "activate Pro first"},
        )
    if actions[0].startswith("user_not_pro:"):
        raise HTTPException(
            status_code=409,
            detail={"request_id": request_id, "actions": actions, "hint": "user tier is not pro"},
        )
    if actions[0].startswith("request_no_user:"):
        raise HTTPException(status_code=404, detail={"request_id": request_id, "actions": actions})

    sent = any(a.startswith("activation_email:") for a in actions)
    skipped = next((a for a in actions if a.startswith("activation_email_skipped:")), "")
    reason = skipped.split(":", 1)[1] if ":" in skipped else None
    from market_core import db_find_subscription_request

    req = db_find_subscription_request(request_id=request_id)
    username = (req or {}).get("username") or ""
    email = email_override or (req or {}).get("email") or ""

    return {
        "ok": sent,
        "request_id": request_id,
        "username": username,
        "email": email,
        "sent": sent,
        "reason": reason,
        "actions": actions,
    }


@router.post("/v1/admin/set-tier")
def admin_set_tier(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Set a user's subscription tier. Admin-only (MARKET_API_TOKEN).

    Body: {"username": "...", "tier": "free|pro|enterprise"}
    Use for manual Pro grants, comps, refunds, and testing without PayPal.
    """
    require_admin(authorization)
    username = (body.get("username") or "").strip()
    tier = (body.get("tier") or "").strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    if tier not in _VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"tier must be one of {sorted(_VALID_TIERS)}",
        )
    if username not in db_get_users():
        raise HTTPException(status_code=404, detail=f"user not found: {username}")
    db_set_subscription(username, tier)
    return {"username": username, "subscription": db_get_subscription(username)}


@router.post("/v1/admin/revoke-api-key")
def admin_revoke_api_key(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Revoke a compromised API key by raw sk- value (admin-only)."""
    require_admin(authorization)
    api_key = (body.get("api_key") or body.get("key") or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key required")

    from account_service import revoke_api_key_by_value

    result = revoke_api_key_by_value(api_key)
    if not result:
        raise HTTPException(status_code=404, detail="api key not found or already revoked")
    logger.info(
        "audit admin_revoke_api_key username=%s key_id=%s prefix=%s",
        result["username"],
        result["key_id"],
        api_key[:10],
    )
    return {"ok": True, **result}


@router.post("/admin/collect")
async def admin_collect(
    stores: int = 0,
    queries: int = 0,
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    """Trigger a price collection run directly (synchronous).

    Useful for manual smoke testing on Render after deploys. Use ?stores=2&queries=2
    for a quick sanity check; default runs the full catalog.
    """
    try:
        from collect_prices import (
            build_query_list,
            _get_feedback_db,
            run_collection,
        )
    except ImportError:
        return {"ok": False, "error": "collect_prices module not available (private backend not installed)"}
    from market_core import ensure_db_initialized

    ensure_db_initialized()

    sl = list(STORES.keys())
    if stores:
        sl = sl[:stores]

    db = _get_feedback_db()
    ql = build_query_list(db=db, cycle=0)
    if queries:
        ql = ql[:queries]

    t0 = time.monotonic()
    result = await run_collection(sl, ql)
    return {
        "status": "ok",
        "elapsed_s": round(time.monotonic() - t0, 1),
        "stores_attempted": result["stores_attempted"],
        "stores_succeeded": result["stores_succeeded"],
        "prices_collected": result["prices_collected"],
    }


@router.post("/v1/admin/scan-stores")
async def admin_scan_stores(
    body: dict = Body(default_factory=dict),
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    """Probe each known retailer with a tiny VTEX catalog query."""
    line_filter = body.get("line")
    candidates: list[dict] = []
    for sk, sv in STORES.items():
        if line_filter and sv.get("line") != line_filter:
            continue
        base = sv["base"]
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                r = await client.get(
                    f"{base}/api/catalog_system/pub/products/search/test?_from=0&_to=1"
                )
                candidates.append(
                    {
                        "store": sk,
                        "name": sv["name"],
                        "status": r.status_code,
                        "ok": r.status_code in (200, 206),
                    }
                )
        except Exception as e:
            candidates.append(
                {
                    "store": sk,
                    "name": sv["name"],
                    "status": 0,
                    "ok": False,
                    "error": str(e)[:100],
                }
            )
    ok = [c for c in candidates if c["ok"]]
    return {"scanned": len(candidates), "working": len(ok), "candidates": candidates}


@router.post("/admin/cron/funnel-digest")
def admin_cron_funnel_digest(
    authorization: str | None = Header(None),
    hours: int = 24,
):
    """Post adoption funnel digest to #funnel-cli-market (morning-ops-chain ~08:00 PET)."""
    require_admin(authorization)
    hours = max(1, min(hours, 168))

    import sys
    from pathlib import Path

    ops_dir = Path(__file__).resolve().parent.parent / "ops"
    if str(ops_dir) not in sys.path:
        sys.path.insert(0, str(ops_dir))
    from billing_slack import format_funnel_digest_message, notify_funnel_digest

    text = format_funnel_digest_message(hours=hours)
    if not notify_funnel_digest(hours=hours):
        raise HTTPException(
            status_code=503,
            detail="Slack funnel channel not configured or delivery failed",
        )
    return {"ok": True, "hours": hours, "posted": True, "preview": text[:800]}


@router.post("/admin/cron/adoption-index")
def admin_cron_adoption_index(
    authorization: str | None = Header(None),
    days: int = 30,
    github: bool = True,
):
    """Persist Adoption Index snapshot (nightly cron)."""
    require_admin(authorization)
    days = max(1, min(days, 90))

    from market_adoption_index import compute_adoption_index, persist_snapshot

    payload = compute_adoption_index(days=days, include_github=github)
    saved = persist_snapshot(payload)
    return {"ok": True, "score": payload["score"], "grade": payload["grade"], "snapshot": saved}


@router.post("/admin/cron/indicators-refresh")
def admin_cron_indicators_refresh(
    authorization: str | None = Header(None),
    country: str | None = None,
):
    """Refresh moat indicators across countries (nightly cron)."""
    require_admin(authorization)

    from market_indicators import refresh_after_collection, refresh_indicators

    if country:
        cc = country.upper()
        result = refresh_indicators(country=cc, line=None)
        return {"ok": True, "country": cc, **result}

    summary = refresh_after_collection()
    return {"ok": True, **summary}


@router.post("/admin/cron/command-control")
def admin_cron_command_control(
    authorization: str | None = Header(None),
    full: bool = False,
):
    """Post founder Command & Control panel (morning cron)."""
    require_admin(authorization)

    import sys
    from pathlib import Path

    ops_dir = Path(__file__).resolve().parent.parent / "ops"
    if str(ops_dir) not in sys.path:
        sys.path.insert(0, str(ops_dir))
    from command_control_daily import publish_command_control

    try:
        return publish_command_control(remote=True, brief=not full, save=True)
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Slack command-control not configured: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("command-control cron failed")
        raise HTTPException(status_code=500, detail=str(exc)[:200]) from exc
